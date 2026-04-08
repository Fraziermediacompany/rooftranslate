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


# ---- Claude mode (batched: one API call per document) ----

_CLAUDE_SYSTEM = """You are a professional construction document translator for
roofing crews. You translate fragments of an English construction document into
Mexican Spanish.

INPUT FORMAT
You will receive a JSON array of objects: [{"i": <int>, "t": "<english>"}, ...]
Each object is one text fragment from the SAME document. Fragments are short
(checkbox labels, headers, table cells, single sentences) and may lack context
on their own — that is normal. They came from a structured form.

OUTPUT FORMAT (strict)
Return ONLY a JSON array of objects with the same indices:
[{"i": <int>, "t": "<spanish>"}, ...]
No prose, no markdown, no code fences, no explanations. Just the JSON.

TRANSLATION RULES
- Translate every fragment. Never ask clarifying questions.
- If a fragment is empty, whitespace, a number, a code, an address, a phone, an
  email, or a proper name, return it UNCHANGED.
- Preserve punctuation, colons, parentheses, and bullet markers exactly.
- Keep imperial units (inches, feet, sq ft) and product model names unchanged
  (e.g. Seal-A-Ridge, TimberTex, PWI/PWARR, RCV, ACV, RSPS, Direct TV).
- Preserve checkbox label structure: "Yes" -> "Sí", "No" -> "No", "N/A" -> "N/A".
- Use Mexican Spanish appropriate for construction crews (informal "tú" form,
  trade vocabulary).
- Keep translations roughly the same length as the source where possible.

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
- Job Notes -> Notas del Trabajo
- Homeowner -> Propietario
- Adjuster -> Ajustador
- Scope -> Alcance
- Claim -> Reclamación
"""


# Heuristics: blocks we never translate. Saves tokens and prevents Claude from
# trying to "translate" things like phone numbers or addresses.
import re as _re

_NON_TRANSLATABLE_RE = _re.compile(
    r"^[\s\W\d]*$"  # only whitespace, punctuation, digits
    r"|^[A-Z]{1,5}$"  # ACV, RCV, RSPS, etc.
    r"|^\+?\d[\d\s().\-]{6,}$"  # phone numbers
    r"|^[\w.+-]+@[\w.-]+\.\w+$"  # email
    r"|^https?://"  # URL
)


def _is_non_translatable(text: str) -> bool:
    s = (text or "").strip()
    if not s:
        return True
    if _looks_translated(s):
        return True
    if _NON_TRANSLATABLE_RE.match(s):
        return True
    return False


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

    # Partition blocks into translatable vs pass-through
    payload: list[dict[str, Any]] = []
    for i, b in enumerate(blocks):
        text = b.get("text", "")
        if _is_non_translatable(text):
            continue
        payload.append({"i": i, "t": text})

    translations: dict[int, str] = {}
    if payload:
        # One API call for the whole document.
        user_msg = json.dumps(payload, ensure_ascii=False)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system=_CLAUDE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = msg.content[0].text.strip()
        # Strip code fences if Claude wrapped the JSON
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            parsed = json.loads(raw)
            for item in parsed:
                if isinstance(item, dict) and "i" in item and "t" in item:
                    translations[int(item["i"])] = str(item["t"])
        except (json.JSONDecodeError, ValueError, TypeError):
            # If parsing fails, fall back to leaving English in place rather
            # than stamping conversational error text onto the PDF.
            pass

    out = []
    for i, b in enumerate(blocks):
        new = dict(b)
        if i in translations:
            new["text"] = translations[i]
        # else: leave the original English text untouched
        out.append(new)
    return out
