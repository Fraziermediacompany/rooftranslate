"""Translation module — pluggable English -> Spanish translator.

Two modes:
    "fixture": look up Spanish strings from fixtures/translations.json. Used in dev.
    "claude":  call the Anthropic API. Used in production. Wired in Phase 5.

Public API:
    translate_blocks(blocks: list[dict], mode: str = "fixture") -> list[dict]

Each input block is a dict with at least a "text" field. Output blocks are
copies of the input with "text" replaced by the Spanish translation.

Blocks whose text is empty after translation are flagged with
`"_drop": True` so the rebuild step can omit them. This lets the fixture file
collapse a multi-line English bullet into a single Spanish bullet by mapping
the first line to the full Spanish and the continuation lines to "".
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_FIXTURE_CACHE: dict[str, str] | None = None


def _load_fixture() -> dict[str, str]:
    global _FIXTURE_CACHE
    if _FIXTURE_CACHE is not None:
        return _FIXTURE_CACHE
    here = Path(__file__).resolve().parent.parent
    path = here / "fixtures" / "translations.json"
    with open(path) as f:
        data = json.load(f)
    # Strip metadata keys
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    _FIXTURE_CACHE = data
    return data


def _looks_translated(text: str) -> bool:
    """Heuristic: text already in Spanish (or bilingual) — pass through unchanged."""
    spanish_markers = "ñáéíóúü¡¿"
    return any(c in text for c in spanish_markers)


def _translate_one_fixture(text: str, table: dict[str, str]) -> tuple[str, bool]:
    """Returns (translated_text, drop_flag)."""
    if text in table:
        out = table[text]
        return out, (out == "")
    # Pass-through for things like addresses, codes, numbers, blank labels
    if not text.strip():
        return text, False
    # If it already contains Spanish characters, leave it alone
    if _looks_translated(text):
        return text, False
    # Unknown English string — leave it (will show in QA as untranslated)
    return text, False


def translate_blocks(blocks: list[dict], mode: str = "fixture") -> list[dict]:
    if mode == "fixture":
        table = _load_fixture()
        out = []
        for b in blocks:
            new = dict(b)
            new["text"], drop = _translate_one_fixture(b.get("text", ""), table)
            if drop:
                new["_drop"] = True
            out.append(new)
        return out
    elif mode == "claude":
        return _translate_claude(blocks)
    else:
        raise ValueError(f"Unknown translation mode: {mode}")


# ---- Claude mode (wired in Phase 5) ----

_CLAUDE_SYSTEM = """You are a professional construction document translator.
Translate the user's English construction text into Mexican Spanish using the
following glossary and rules:

GLOSSARY (use consistently):
- Shingle -> Teja
- Drip edge -> Borde de goteo
- Flashing -> Tapajuntas
- Ridge -> Cumbrera
- Eave -> Alero
- Gable / Rake -> Hastial / Rastrillo
- Valley -> Valle
- Gutter -> Canal
- Decking -> Entablado / Plataforma
- Ice & Water Shield -> Barrera de hielo y agua
- Felt -> Fieltro
- Harness -> Arnés
- Skylight -> Tragaluz
- Crew -> Cuadrilla
- Re-Deck -> Redeccionar
- Tear off -> Desprendimiento
- Box vent -> Ventilación de caja
- Dryer vent -> Ventilación de secadora

DO NOT TRANSLATE: proper names, addresses, phone numbers, emails, URLs,
product model numbers (Seal-A-Ridge, TimberTex, PWI/PWARR), insurance
abbreviations (RCV, ACV, RSPS), measurements (keep imperial units).

Return ONLY the Spanish translation, no explanations.
"""


def _translate_claude(blocks: list[dict]) -> list[dict]:
    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "anthropic SDK not installed. `pip install anthropic` for claude mode."
        ) from e

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment.")

    client = Anthropic(api_key=api_key)
    out = []
    for b in blocks:
        text = b.get("text", "")
        new = dict(b)
        if not text.strip() or _looks_translated(text):
            new["text"] = text
            out.append(new)
            continue
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=_CLAUDE_SYSTEM,
            messages=[{"role": "user", "content": text}],
        )
        new["text"] = msg.content[0].text.strip()
        out.append(new)
    return out
