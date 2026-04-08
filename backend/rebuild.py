"""PDF rebuild module — overlay approach (v1.1).

Strategy (v1.1, "overlay rebuild"):
    1. Open the original PDF with pypdf — this preserves EVERYTHING:
       logos, table borders, checkboxes, vector graphics, embedded images.
    2. For each page, generate a transparent reportlab overlay that:
       a) Draws white-filled rectangles over each English text bbox
          (covers the original English without disturbing surrounding graphics).
       b) Draws the Spanish translation on top at the same coordinates,
          with auto-fit (shrink + wrap) so longer Spanish strings don't collide.
    3. Merge the overlay onto the original page via pypdf.merge_page().

This is a major upgrade from the v1.0 "blank canvas rebuild" which lost all
non-text content (logo, borders, checkboxes, highlights).

Coordinate translation:
    pdfplumber: y=0 at top of page, y grows downward
    reportlab:  y=0 at bottom of page, y grows upward
    Convert: rl_y = page_height - pdf_y - block_height
"""
from __future__ import annotations

import io

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas as rl_canvas


# Padding (points) added around each English bbox when whiting out, to make
# sure we don't leave behind any pixel-edge ghosts of the original text.
WHITEOUT_PAD_X = 1.5
WHITEOUT_PAD_Y = 1.0

# Minimum font size we'll shrink to. Below this and we wrap instead.
MIN_FONT_SIZE = 5.0

# Unicode ligatures pdfplumber sometimes hands us as single chars. Helvetica
# (and most ReportLab built-in fonts) don't have these glyphs, so they render
# as a black square. Substitute with plain ASCII before drawing.
_LIGATURES = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "st",
    "\ufb06": "st",
}


def _normalize_text(s: str) -> str:
    if not s:
        return s
    for k, v in _LIGATURES.items():
        if k in s:
            s = s.replace(k, v)
    return s


# ---------- font + text helpers ----------

def _pick_font(orig_font: str | None, bold: bool) -> str:
    """Map original PDF font to a ReportLab built-in Helvetica variant."""
    if not orig_font:
        return "Helvetica-Bold" if bold else "Helvetica"
    f = (orig_font or "").lower()
    if bold or "bold" in f or "black" in f or "heavy" in f or "medium" in f:
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


def _fit_single_line(c: rl_canvas.Canvas, text: str, font: str, size: float, max_width: float) -> float:
    """Shrink font (down to MIN_FONT_SIZE) until single-line text fits max_width."""
    if max_width <= 0:
        return size
    s = size
    while s > MIN_FONT_SIZE and c.stringWidth(text, font, s) > max_width:
        s -= 0.25
    return s


# ---------- whiteout + draw ----------

def _whiteout_block(c: rl_canvas.Canvas, block: dict, page_height: float) -> None:
    """Draw a white rectangle over the original English bbox."""
    if block.get("_drop"):
        return
    x = float(block.get("x", 0))
    y_top = float(block.get("y", 0))
    bw = float(block.get("width", 0)) or 0
    bh = float(block.get("height", 0)) or float(block.get("size", 10) or 10)
    if bw <= 0 or bh <= 0:
        return
    rl_y = page_height - y_top - bh - WHITEOUT_PAD_Y
    c.setFillColor(white)
    c.setStrokeColor(white)
    c.rect(
        x - WHITEOUT_PAD_X,
        rl_y,
        bw + (2 * WHITEOUT_PAD_X),
        bh + (2 * WHITEOUT_PAD_Y),
        fill=1,
        stroke=0,
    )


def _draw_block(c: rl_canvas.Canvas, block: dict, page_width: float, page_height: float) -> None:
    """Stamp the (translated) text on top of the whited-out region.

    Uses original block bbox as the target. If the Spanish runs too long for the
    original width, first try shrinking the font (auto-fit). If that would
    shrink below the readable floor, fall back to multi-line wrapping at the
    smallest tolerable font.
    """
    text = _normalize_text(block.get("text", ""))
    if not text or block.get("_drop"):
        return

    font = _pick_font(block.get("font"), block.get("bold", False))
    size = float(block.get("size", 10) or 10)

    x = float(block.get("x", 0))
    y_top = float(block.get("y", 0))
    bw = float(block.get("width", 0)) or 0
    bh = float(block.get("height", 0)) or size

    # Available width: stay inside the original block width whenever possible
    # (so we don't bleed into adjacent columns). Only allow some growth if
    # the original block was already near the right margin and Spanish runs over.
    right_margin = 24  # ~1/3 inch
    page_max = page_width - x - right_margin
    target_width = bw if bw > 0 else page_max
    # Hard cap so we never spill across the page edge
    target_width = min(target_width, max(page_max, bw))

    # 1. If single line fits at original size, use it.
    if c.stringWidth(text, font, size) <= target_width:
        lines = [text]
    else:
        # 2. Try shrinking the font to fit a single line.
        shrunk = _fit_single_line(c, text, font, size, target_width)
        if c.stringWidth(text, font, shrunk) <= target_width:
            size = shrunk
            lines = [text]
        else:
            # 3. Wrap at the shrunk size (or original if shrink hit floor).
            size = max(shrunk, MIN_FONT_SIZE)
            lines = _wrap_text(c, text, font, size, target_width)

    leading = size * 1.18
    # ReportLab draws at the baseline; pdfplumber gives us the top of the bbox.
    base_y = page_height - y_top - size * 0.85

    c.setFont(font, size)
    c.setFillColor(black)
    yy = base_y
    for line in lines:
        c.drawString(x, yy, line)
        yy -= leading


# ---------- main entry point ----------

def _build_overlay(blocks: list[dict], page_width: float, page_height: float) -> bytes:
    """Build a single-page reportlab PDF (whiteout + Spanish text) for one page.

    Returned as raw PDF bytes for pypdf to merge onto the original.
    """
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(page_width, page_height))

    # Layer 1: whiteout all original English text bboxes
    for block in blocks:
        _whiteout_block(c, block, page_height)

    # Layer 2: draw translated Spanish text on top
    for block in blocks:
        _draw_block(c, block, page_width, page_height)

    c.showPage()
    c.save()
    return buf.getvalue()


def rebuild_pdf(original_path: str, translated_pages: list[dict], output_path: str) -> None:
    """Rebuild a translated PDF using the v1.1 overlay approach.

    Loads the original with pypdf (preserves logos, borders, checkboxes, all
    vector graphics), then merges a per-page reportlab overlay containing
    whiteout rectangles and the Spanish text.
    """
    reader = PdfReader(original_path)
    writer = PdfWriter()

    if not reader.pages:
        raise ValueError("Empty PDF")

    for i, orig_page in enumerate(reader.pages):
        # Page dimensions from the original (in PDF points)
        try:
            pw = float(orig_page.mediabox.width)
            ph = float(orig_page.mediabox.height)
        except Exception:
            # Fallback to US Letter if mediabox is missing
            pw, ph = 612.0, 792.0

        page_data = translated_pages[i] if i < len(translated_pages) else {"blocks": []}
        blocks = page_data.get("blocks", []) or []

        if blocks:
            overlay_bytes = _build_overlay(blocks, pw, ph)
            overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
            if overlay_reader.pages:
                overlay_page = overlay_reader.pages[0]
                # Merge overlay ON TOP of the original page content.
                # This preserves the logo, borders, checkboxes, highlights, etc.
                try:
                    orig_page.merge_page(overlay_page)
                except Exception:
                    # If merge fails for any reason, fall back to original page
                    # (better to ship English than crash the whole job).
                    pass

        writer.add_page(orig_page)

    with open(output_path, "wb") as f:
        writer.write(f)


# Convenience helper kept for compatibility with pipeline.py
def rebuild_from_extract(original_path: str, extracted: dict, output_path: str) -> None:
    rebuild_pdf(original_path, extracted.get("pages", []), output_path)
