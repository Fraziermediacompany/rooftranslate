"""FastAPI app — exposes POST /translate.

Accepts multipart PDF uploads, runs them through the pipeline, and returns
a ZIP of translated PDFs. CORS open for dev.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .pipeline import process_many


MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
ALLOWED_EXTS = {".pdf"}

app = FastAPI(title="RoofTranslate API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "RoofTranslate API", "version": "0.1.0", "ok": True}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/translate")
async def translate(files: list[UploadFile] = File(...)):
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

        try:
            zip_bytes = process_many(staged_paths)
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
        # Cleanup staged uploads
        for p in staged_paths:
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass
