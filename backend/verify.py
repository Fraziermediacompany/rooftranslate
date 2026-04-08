"""Translation verification via back-translation.

In fixture mode, confidence is hardcoded to 0.95 — we hand-curated those
translations from the prior Frontline session, so they're known good.

In claude mode, we ask Claude to back-translate the Spanish to English and
compute a similarity ratio against the original English.
"""
from __future__ import annotations

import os
from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def verify_translation(
    original_en: str,
    translated_es: str,
    mode: str = "fixture",
) -> dict:
    """Returns {confidence: float, back_translation: str, flagged: bool}."""
    if not original_en.strip() or not translated_es.strip():
        return {"confidence": 1.0, "back_translation": "", "flagged": False}

    if mode == "fixture":
        return {
            "confidence": 0.95,
            "back_translation": original_en,  # we trust the fixture
            "flagged": False,
        }

    if mode == "claude":
        try:
            from anthropic import Anthropic  # type: ignore
        except ImportError as e:
            raise RuntimeError("anthropic SDK required for claude mode") from e
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        client = Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "You are a translator. Translate the user's Spanish text into "
                "natural English. Return ONLY the English translation."
            ),
            messages=[{"role": "user", "content": translated_es}],
        )
        back = msg.content[0].text.strip()
        conf = _similarity(original_en, back)
        return {
            "confidence": round(conf, 3),
            "back_translation": back,
            "flagged": conf < 0.80,
        }

    raise ValueError(f"Unknown verify mode: {mode}")
