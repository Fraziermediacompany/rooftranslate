"""PDF extraction module.

Exports:
    extract_pdf(path) -> dict with shape:
        {
          "pages": [
            {
              "width": float,
              "height": float,
              "blocks": [
                {"text": str, "x": float, "y": float,
                 "font": str, "size": float, "bold": bool,
                 "width": float, "height": float}
              ]
            }
          ]
        }

Strategy: use pdfplumber's page.chars and group characters into text blocks
by line proximity and horizontal continuity.
"""
from __future__ import annotations

import pdfplumber
from typing import Any

# Tunables
LINE_TOLERANCE = 3.0   # vertical distance (points) to consider chars on same line
WORD_GAP = 2.5         # multiplier of avg-char-width that ends a block horizontally


def _is_bold(fontname: str) -> bool:
    if not fontname:
        return False
    f = fontname.lower()
    return "bold" in f or "black" in f or "heavy" in f


def _group_chars_to_blocks(chars: list[dict]) -> list[dict]:
    """Group raw chars into blocks of contiguous text on the same line."""
    if not chars:
        return []

    # Sort by line (y), then by x
    chars = sorted(chars, key=lambda c: (round(c["top"] / LINE_TOLERANCE), c["x0"]))

    blocks: list[dict] = []
    cur_chars: list[dict] = []

    def flush():
        if not cur_chars:
            return
        text = "".join(c["text"] for c in cur_chars).strip()
        if not text:
            return
        x0 = min(c["x0"] for c in cur_chars)
        x1 = max(c["x1"] for c in cur_chars)
        top = min(c["top"] for c in cur_chars)
        bottom = max(c["bottom"] for c in cur_chars)
        size = round(sum(c["size"] for c in cur_chars) / len(cur_chars), 2)
        font = cur_chars[0].get("fontname", "Helvetica")
        blocks.append(
            {
                "text": text,
                "x": round(x0, 2),
                "y": round(top, 2),
                "width": round(x1 - x0, 2),
                "height": round(bottom - top, 2),
                "font": font,
                "size": size,
                "bold": _is_bold(font),
            }
        )

    prev = None
    for ch in chars:
        if prev is None:
            cur_chars = [ch]
            prev = ch
            continue

        same_line = abs(ch["top"] - prev["top"]) <= LINE_TOLERANCE
        gap = ch["x0"] - prev["x1"]
        avg_w = max(prev["width"], 1.0)
        same_block = same_line and gap < (avg_w * WORD_GAP)

        if same_block:
            cur_chars.append(ch)
        else:
            flush()
            cur_chars = [ch]
        prev = ch

    flush()
    return blocks


def extract_pdf(path: str) -> dict[str, Any]:
    """Extract text blocks with positions from a PDF.

    Returns a dict with `pages`, each containing width/height/blocks.
    """
    out_pages: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            blocks = _group_chars_to_blocks(page.chars or [])
            out_pages.append(
                {
                    "width": float(page.width),
                    "height": float(page.height),
                    "blocks": blocks,
                }
            )
    return {"pages": out_pages}


if __name__ == "__main__":
    import json
    import sys

    p = sys.argv[1] if len(sys.argv) > 1 else "fixtures/crew-instructions.pdf"
    data = extract_pdf(p)
    print(f"Pages: {len(data['pages'])}")
    for i, pg in enumerate(data["pages"]):
        print(f"  Page {i+1}: {pg['width']:.0f}x{pg['height']:.0f}, {len(pg['blocks'])} blocks")
        for b in pg["blocks"][:3]:
            print(f"    {b}")
