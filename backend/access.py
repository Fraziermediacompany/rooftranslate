"""Access code management for RoofTranslate paywall.

Stores issued access codes with metadata (email, company, phone, expiry, etc).
Uses in-memory dict + env var backup for persistence across Render deploys.
"""
from __future__ import annotations

import json
import os
import random
import string
from datetime import datetime, timedelta, timezone


def generate_code() -> str:
    """Generate a code in format RT-XXXX-XXXX (uppercase, no ambiguous chars).

    Excludes O, 0, I, 1, L to avoid confusion.
    Returns e.g. 'RT-A3K7-B9M2'
    """
    allowed = string.ascii_uppercase + string.digits
    # Remove ambiguous characters: O, 0 (zero), I, 1 (one), L
    allowed = allowed.replace("O", "").replace("0", "").replace("I", "").replace("1", "").replace("L", "")

    part1 = "".join(random.choice(allowed) for _ in range(4))
    part2 = "".join(random.choice(allowed) for _ in range(4))
    return f"RT-{part1}-{part2}"


class AccessStore:
    """In-memory store for access codes with env var backup."""

    def __init__(self, founding_limit: int = 100, validity_days: int = 365):
        """Initialize the access store.

        Args:
            founding_limit: Max number of founding codes to issue.
            validity_days: Days until codes expire.
        """
        self.founding_limit = founding_limit
        self.validity_days = validity_days
        self.codes: dict[str, dict] = {}

        # Try to load from env var backup (JSON string)
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load codes from ACCESS_CODES_BACKUP env var (JSON string)."""
        backup = os.getenv("ACCESS_CODES_BACKUP", "").strip()
        if not backup:
            return

        try:
            data = json.loads(backup)
            if isinstance(data, dict):
                self.codes = data
        except (json.JSONDecodeError, ValueError):
            # Silently fail if backup is malformed; start fresh
            pass

    def issue_code(
        self,
        email: str,
        company: str,
        phone: str,
        stripe_session_id: str,
    ) -> tuple[str, int]:
        """Issue a new access code.

        Args:
            email: Customer email.
            company: Company name.
            phone: Phone number.
            stripe_session_id: Stripe checkout session ID for reference.

        Returns:
            Tuple of (code, founding_number) where founding_number is the
            ordinal position (1-100) in the founding crew sequence.
        """
        # Check if we're at capacity
        founding_number = len(self.codes) + 1
        if founding_number > self.founding_limit:
            # Still issue a code but set founding_number to -1 to indicate over-limit
            founding_number = -1

        code = generate_code()
        # Ensure uniqueness (though extremely unlikely)
        while code in self.codes:
            code = generate_code()

        expires_at = (datetime.now(timezone.utc) + timedelta(days=self.validity_days)).isoformat()

        self.codes[code] = {
            "email": email,
            "company": company,
            "phone": phone,
            "expires_at": expires_at,
            "founding_number": founding_number,
            "stripe_session_id": stripe_session_id,
            "issued_at": datetime.now(timezone.utc).isoformat(),
        }

        return code, founding_number

    def verify_code(self, code: str) -> dict:
        """Verify a code and return its status.

        Args:
            code: The access code to verify.

        Returns:
            Dict with keys:
            - valid: bool
            - expires_in_days: int (only if valid)
            - company: str (only if valid)
            - founding_number: int (only if valid)
            Or {valid: false} if expired/unknown.
        """
        if code not in self.codes:
            return {"valid": False}

        entry = self.codes[code]
        expires_at = datetime.fromisoformat(entry["expires_at"])
        now = datetime.now(timezone.utc)

        if now > expires_at:
            return {"valid": False}

        expires_in_days = (expires_at - now).days
        return {
            "valid": True,
            "expires_in_days": expires_in_days,
            "company": entry["company"],
            "founding_number": entry["founding_number"],
        }

    def get_count(self) -> int:
        """Return the number of issued codes."""
        return len(self.codes)

    def export_json(self) -> str:
        """Export all codes as JSON string for backing up to env var."""
        return json.dumps(self.codes)
