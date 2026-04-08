"""PDF rebuild module — the highest-risk step in the pipeline.

Strategy:
    1. Open the original PDF with pdfplumber to get page dimensions and any
       images/lines we want to preserve.
    2. Create a new PDF with ReportLab Canvas at the same dimensions.
    3. For each translated block, draw the Spanish text at the original
       coordinates with the original font size (or a slightly smaller size if
       Spanish runs longer). Word-wrap if it overflows the original block width.
    4. Re-emit images from the original at their original positions.

Coordinate translation:
    pdfplumber: y=0 at top of page, y grows downward
    reportlab:  y=0 at bottom of page, y grows upward
    Convert: rl_y = page_height - pdf_y - block_height
"""
from __future__ import annotations

import io
from typing import Any

import pdfplumber
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas as rl_canvas


# Font fallback: original PDFs often use embedded fonts (Lora, custom subsets)
# that ReportLab doesn't have. Map to Helvetica family.
def _pick_font(orig_font: str | None, bold: bool) -> str:
    if not orig_font:
        return "Helvetica-Bold" if bold else "Helvetica"
    f = (orig_font or "").lower()
    if bold or "bold" in f or "black" in f or "medium" in f:
        return "Helvetica-Bold"
    if "italic" in f or "oblique" in f:
        return "Helvetica-Oblique"
    return "Helvetica"


def _wrap_text(c: rl_canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    """Greedy word-wrap returning a list of lines that fit max_width."""
    if max_width <= 0:
        return [text]
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        if c.stringWidth(test, font, size) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_size(c: rl_canvas.Canvas, text: str, font: str, size: float, max_width: float) -> float:
    """If a single-line text overflows max_width, shrink the font until it fits."""
    if max_width <= 0:
        return size
    s = size
    while s > 5 and c.stringWidth(text, font, s) > max_width:
        s -= 0.5
    return s


def _draw_block(
    c: rl_canvas.Canvas,
    block: dict,
    page_width: float,
    page_height: float,
) -> None:
    text = block.get("text", "")
    if not text or block.get("_drop"):
        return

    font = _pick_font(block.get("font"), block.get("bold", False))
    size = float(block.get("size", 10) or 10)

    # Original block bbox
    x = float(block.get("x", 0))
    y_top = float(block.get("y", 0))           # pdfplumber: top
    bw = float(block.get("width", 0)) or 0
    bh = float(block.get("height", size)) or size

    # Available width: prefer original block width, but allow some growth
    # to the right margin since Spanish often runs ~15-25% longer.
    right_margin = 36  # half-inch
    max_width = max(bw, page_width - x - right_margin)

    # Try a single line first; if it overflows, wrap.
    if c.stringWidth(text, font, size) <= max_width:
        lines = [text]
    else:
        # First try shrinking — if that doesn't fit either, wrap.
        shrunk = _fit_size(c, text, font, size, max_width)
        if shrunk >= size - 1.0 or c.stringWidth(text, font, shrunk) <= max_width:
            size = shrunk
            lines = _wrap_text(c, text, font, size, max_width)
        else:
            lines = _wrap_text(c, text, font, size, max_width)

    leading = size * 1.18
    # Convert pdf top-y -> reportlab baseline-y for first line
    # In pdfplumber coords, "top" is the y of the top of the text bbox.
    # ReportLab drawString draws at the baseline. We approximate baseline =
    # page_height - top - size*0.85 (descender allowance).
    base_y = page_height - y_top - size * 0.85

    c.setFont(font, size)
    c.setFillColor(black)
    yy = base_y
    for line in lines:
        c.drawString(x, yy, line)
        yy -= leading


def _draw_images(c: rl_canvas.Canvas, page, page_height: float) -> None:
    """Best-effort image preservation. Many PDFs use vector logos which
    pdfplumber can't extract; we silently skip those for V1."""
    try:
        for img in page.images or []:
            try:
                x0 = float(img.get("x0", 0))
                top = float(img.get("top", 0))
                w = float(img.get("width", 0))
                h = float(img.get("height", 0))
                stream = img.get("stream")
                if not (stream and w > 0 and h > 0):
                    continue
                raw = stream.get_data() if hasattr(stream, "get_data") else None
                if not raw:
                    continue
                from reportlab.lib.utils import ImageReader  # type: ignore
                ir = ImageReader(io.BytesIO(raw))
                rl_y = page_height - top - h
                c.drawImage(ir, x0, rl_y, width=w, height=h, mask="auto")
            except Exception:
                continue
    except Exception:
        pass


def rebuild_pdf(original_path: str, translated_pages: list[dict], output_path: str) -> None:
    """Rebuild a translated PDF.

    `translated_pages` is the list of page dicts from extract_pdf, with each
    block's `text` field already replaced by the Spanish translation. We use
    the original PDF only for page dimensions and image preservation.
    """
    with pdfplumber.open(original_path) as pdf:
        if not pdf.pages:
            raise ValueError("Empty PDF")
        # Use first page size for canvas init; we'll setPageSize per page
        first = pdf.pages[0]
        c = rl_canvas.Canvas(output_path, pagesize=(float(first.width), float(first.height)))

        for i, orig_page in enumerate(pdf.pages):
            pw = float(orig_page.width)
            ph = float(orig_page.height)
            c.setPageSize((pw, ph))

            # Draw images first (background layer)
            _draw_images(c, orig_page, ph)

            # Then text
            page_data = translated_pages[i] if i < len(translated_pages) else {"blocks": []}
            for block in page_data.get("blocks", []):
                _draw_block(c, block, pw, ph)

            c.showPage()

        c.save()


# Convenience helper: end-to-end rebuild from extracted+translated structure
def rebuild_from_extract(original_path: str, extracted: dict, output_path: str) -> None:
    rebuild_pdf(original_path, extracted.get("pages", []), output_path)
