"""FastAPI app — exposes POST /translate with paywall.

Accepts multipart PDF uploads, runs them through the pipeline, and returns
a ZIP of translated PDFs (or a single 422 if a single-file request fails
at the pipeline level — e.g. a scanned/image-only PDF).
"""

import os
import tempfile
from pathlib import Path
from typing import List

import stripe
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .access import AccessStore
from .pipeline import ScannedPDFError, process_many, process_pdf


MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
ALLOWED_EXTS = {".pdf"}

# Allowed origins for the live frontend. Add new domains here as needed.
ALLOWED_ORIGINS = [
    "https://rooftranslate.com",
    "https://www.rooftranslate.com",
    "http://localhost:3000",
    "http://localhost:3001",
]
# Allow any *.vercel.app preview deploy too (regex match in CORS).
ALLOW_ORIGIN_REGEX = r"https://.*\.vercel\.app"

# Initialize Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PAYWALL_ENABLED = os.getenv("PAYWALL_ENABLED", "").lower() == "true"

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Initialize access code store
access_store = AccessStore()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="RoofTranslate API", version="0.2.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "RoofTranslate API", "version": "0.2.0", "ok": True}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/verify-code/{code}")
def verify_code(code: str):
    """Verify an access code and return its status."""
    return access_store.verify_code(code)


@app.get("/founding-crew-count")
def founding_crew_count():
    """Return count of issued codes and limit."""
    return {"count": access_store.get_count(), "limit": 100}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (checkout.session.completed).

    Validates the webhook signature and issues access codes for completed payments.
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="Webhook secret not configured.")

    body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(body, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload.")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature.")

    # Handle checkout.session.completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_details", {}).get("email", "")
        name = session.get("customer_details", {}).get("name", "")
        phone = session.get("customer_details", {}).get("phone", "")

        if email and name:
            # Extract company from name or use a default
            company = name.split()[0] if name else "N/A"

            # Issue access code
            code, founding_number = access_store.issue_code(
                email=email,
                company=company,
                phone=phone or "",
                stripe_session_id=session.get("id", ""),
            )

    return {"ok": True}


@app.post("/translate")
@limiter.limit("10/hour")
async def translate(request: Request, files: List[UploadFile] = File(...)):
    # Verify access code if paywall is enabled
    if PAYWALL_ENABLED:
        access_code = request.headers.get("X-Access-Code", "").strip()
        if not access_code:
            raise HTTPException(
                status_code=403,
                detail="Access code required. Visit rooftranslate.com to get started.",
            )

        result = access_store.verify_code(access_code)
        if not result.get("valid"):
            raise HTTPException(
                status_code=403,
                detail="Invalid or expired access code.",
            )

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files per request.")

    # Validate and stage uploads to disk
    tmp_dir = tempfile.mkdtemp(prefix="rooftranslate_")
    staged_paths: list[str] = []
    try:
        for f in files:
            ext = Path(f.filename or "").suffix.lower()
            if ext not in ALLOWED_EXTS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF files supported. Got: {f.filename}",
                )
            data = await f.read()
            if len(data) > MAX_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large (>10 MB): {f.filename}",
                )
            if not data:
                raise HTTPException(
                    status_code=400, detail=f"Empty file: {f.filename}"
                )
            # quick PDF magic-byte sanity
            if not data.startswith(b"%PDF"):
                raise HTTPException(
                    status_code=400,
                    detail=f"File doesn't look like a valid PDF: {f.filename}",
                )
            dst = os.path.join(tmp_dir, f.filename or "upload.pdf")
            with open(dst, "wb") as out:
                out.write(data)
            staged_paths.append(dst)

        # Single-file fast path: if it fails (scanned PDF, Anthropic outage),
        # surface a friendly 422 instead of stuffing an error.txt in a zip.
        if len(staged_paths) == 1:
            single_in = staged_paths[0]
            stem = Path(single_in).stem
            tmp_out = os.path.join(tmp_dir, f"_out_{stem}.pdf")
            result = process_pdf(single_in, tmp_out)
            if not result["success"]:
                err = result.get("error") or "Translation failed."
                # Detect known failure modes for cleaner messages
                if "no extractable text" in err.lower() or "scanned" in err.lower():
                    msg = (
                        "This PDF looks like a scanned image. RoofTranslate "
                        "currently only works on text-based PDFs. Try exporting "
                        "from the original document instead of scanning a printout."
                    )
                elif "anthropic" in err.lower() or "api" in err.lower() or "rate" in err.lower():
                    msg = (
                        "Our translation service is temporarily unavailable. "
                        "Please try again in a minute."
                    )
                else:
                    msg = f"Translation failed: {err}"
                return JSONResponse(status_code=422, content={"detail": msg})

            # Success: read the single output and return it as a 1-file ZIP
            # so the frontend code path stays uniform.
            import io
            import zipfile

            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                with open(tmp_out, "rb") as fh:
                    zf.writestr(f"{stem} - Spanish.pdf", fh.read())
            try:
                os.remove(tmp_out)
            except OSError:
                pass
            return Response(
                content=zbuf.getvalue(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": 'attachment; filename="rooftranslate-bundle.zip"'
                },
            )

        # Multi-file path: ZIP everything together; per-file errors land as
        # ERROR.txt entries inside the bundle so the user still gets the
        # files that did succeed.
        try:
            zip_bytes = process_many(staged_paths)
        except ScannedPDFError as e:
            return JSONResponse(status_code=422, content={"detail": str(e)})
        except Exception as e:  # noqa: BLE001
            return JSONResponse(
                status_code=500,
                content={"detail": f"Translation pipeline failed: {e}"},
            )

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="rooftranslate-bundle.zip"'
            },
        )
    finally:
        # Cleanup staged uploads (privacy promise: nothing persists past the
        # request lifecycle on the server).
        for p in staged_paths:
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass
