"""Pipeline orchestrator — chains extract -> translate -> verify -> rebuild.

Public API:
    process_pdf(input_path, output_path) -> {success, confidence, error}
    process_many(input_paths) -> bytes  (a ZIP of translated PDFs)

The translation mode is read from the ROOFTRANSLATE_MODE env var.
Defaults to "fixture" so dev never accidentally hits the API.
"""
from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path
from typing import Any

from .extract import extract_pdf
from .translate import translate_blocks
from .verify import verify_translation
from .rebuild import rebuild_pdf


def _mode() -> str:
    return os.environ.get("ROOFTRANSLATE_MODE", "fixture")


class ScannedPDFError(RuntimeError):
    """Raised when a PDF has no extractable text (likely scanned/image-only)."""


def process_pdf(input_path: str, output_path: str) -> dict[str, Any]:
    mode = _mode()
    try:
        extracted = extract_pdf(input_path)
        total_blocks = sum(len(p["blocks"]) for p in extracted["pages"])
        if total_blocks == 0:
            raise ScannedPDFError(
                "This PDF has no extractable text. It may be a scanned image — "
                "RoofTranslate V1 only supports text-based PDFs."
            )

        # Translate page-by-page so we keep page structure
        translated_pages: list[dict] = []
        confidences: list[float] = []
        for p in extracted["pages"]:
            tb = translate_blocks(p["blocks"], mode=mode)
            translated_pages.append(
                {"width": p["width"], "height": p["height"], "blocks": tb}
            )
            # Sample-verify the first 3 blocks per page to keep API costs sane
            for orig, new in list(zip(p["blocks"], tb))[:3]:
                if orig["text"] and new.get("text") and orig["text"] != new["text"]:
                    v = verify_translation(orig["text"], new["text"], mode=mode)
                    confidences.append(v["confidence"])

        rebuild_pdf(input_path, translated_pages, output_path)

        avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.95
        return {"success": True, "confidence": avg_conf, "error": None}

    except ScannedPDFError as e:
        return {"success": False, "confidence": 0.0, "error": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "confidence": 0.0, "error": f"{type(e).__name__}: {e}"}


def process_many(input_paths: list[str]) -> bytes:
    """Process a list of PDFs and return a ZIP of translated outputs as bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for in_path in input_paths:
            stem = Path(in_path).stem
            out_name = f"{stem} - Spanish.pdf"
            tmp_out = f"/tmp/_rt_{stem}.pdf"
            result = process_pdf(in_path, tmp_out)
            if result["success"] and os.path.exists(tmp_out):
                with open(tmp_out, "rb") as f:
                    zf.writestr(out_name, f.read())
                try:
                    os.remove(tmp_out)
                except OSError:
                    pass
            else:
                # Include an error.txt next to the failed file
                zf.writestr(
                    f"{stem} - ERROR.txt",
                    f"Failed to translate {Path(in_path).name}\n\n{result['error']}\n",
                )
    return buf.getvalue()
