"""GoHighLevel integration — durable contact + code storage + welcome emails.

GHL is the source of truth for access codes. Codes are stored as contact tags
in the format `rt:RT-XXXX-XXXX`. On server startup, the in-memory AccessStore
is hydrated from GHL so codes survive Render restarts.

Public API:
    notify_purchase(email, name, phone, company, access_code, founding_number)
    hydrate_codes_from_ghl() -> dict[str, dict]  (code -> metadata)

Requires GHL_API_KEY and GHL_LOCATION_ID env vars.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GHL_API_KEY = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "2kDMnxQzxbmBOTz5Ikrh")
GHL_BASE = "https://services.leadconnectorhq.com"

EVENT_PAYMENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08"

# Tag prefix for access codes stored on GHL contacts
CODE_TAG_PREFIX = "rt:"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }


def _extract_code_from_tags(tags: list[str]) -> str | None:
    """Extract the RT-XXXX-XXXX code from a contact's tag list."""
    for tag in tags:
        if tag.startswith(CODE_TAG_PREFIX):
            return tag[len(CODE_TAG_PREFIX):]
    return None


def _extract_founding_number(tags: list[str]) -> int:
    """Extract founding number from tags like 'founding-007'."""
    for tag in tags:
        m = re.match(r"founding-(\d+)", tag)
        if m:
            return int(m.group(1))
    return -1


# ---------------------------------------------------------------------------
# Hydration: pull all RoofTranslate contacts from GHL on startup
# ---------------------------------------------------------------------------

def hydrate_codes_from_ghl() -> dict[str, dict]:
    """Fetch all contacts tagged 'rooftranslate' from GHL and rebuild code map.

    Returns a dict of {code: {email, company, phone, founding_number, ...}}
    compatible with AccessStore.codes format.
    """
    if not GHL_API_KEY:
        logger.info("GHL hydration skipped (no GHL_API_KEY).")
        return {}

    codes: dict[str, dict] = {}
    try:
        with httpx.Client(timeout=30) as client:
            # GHL V2 search endpoint — filter by tag
            # We paginate through all results
            start_after = None
            page = 0
            while page < 10:  # safety: max 10 pages (1000 contacts)
                params: dict[str, Any] = {
                    "locationId": GHL_LOCATION_ID,
                    "query": "rooftranslate",
                    "limit": 100,
                }
                if start_after:
                    params["startAfterId"] = start_after

                resp = client.get(
                    f"{GHL_BASE}/contacts/",
                    headers=_headers(),
                    params=params,
                )

                if resp.status_code != 200:
                    logger.error(f"GHL hydration failed: {resp.status_code} {resp.text[:200]}")
                    break

                data = resp.json()
                contacts = data.get("contacts", [])
                if not contacts:
                    break

                for c in contacts:
                    tags = c.get("tags", [])
                    # Only process contacts that actually have the rooftranslate tag
                    if "rooftranslate" not in tags:
                        continue

                    code = _extract_code_from_tags(tags)
                    if not code:
                        continue

                    founding_number = _extract_founding_number(tags)
                    codes[code] = {
                        "email": c.get("email", ""),
                        "company": c.get("companyName", ""),
                        "phone": c.get("phone", ""),
                        "founding_number": founding_number,
                        "ghl_contact_id": c.get("id", ""),
                        "issued_at": c.get("dateAdded", ""),
                        # Set a far-future expiry; real expiry logic uses issued_at + 365 days
                        "expires_at": "",
                        "stripe_session_id": "",
                    }

                # Pagination
                if len(contacts) < 100:
                    break
                start_after = contacts[-1].get("id")
                page += 1

        logger.info(f"GHL hydration complete: {len(codes)} codes loaded.")
    except Exception as e:
        logger.error(f"GHL hydration error: {e}")

    return codes


# ---------------------------------------------------------------------------
# Contact creation + code tagging
# ---------------------------------------------------------------------------

def _create_or_update_contact(
    email: str,
    first_name: str,
    last_name: str,
    phone: str,
    company: str,
    tags: list[str],
    source: str = "RoofTranslate",
) -> str | None:
    """Create a contact in GHL or update if email exists. Returns contact ID."""
    if not GHL_API_KEY:
        logger.warning("GHL_API_KEY not set — skipping contact creation.")
        return None

    payload: dict[str, Any] = {
        "locationId": GHL_LOCATION_ID,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "phone": phone,
        "companyName": company,
        "tags": tags,
        "source": source,
    }

    try:
        with httpx.Client(timeout=15) as client:
            # Try create first
            resp = client.post(
                f"{GHL_BASE}/contacts/",
                headers=_headers(),
                json=payload,
            )

            if resp.status_code in (200, 201):
                data = resp.json()
                contact_id = data.get("contact", {}).get("id")
                logger.info(f"GHL contact created: {contact_id}")
                return contact_id

            if resp.status_code == 400 and "duplicate" in resp.text.lower():
                # Contact exists — find and update
                search_resp = client.get(
                    f"{GHL_BASE}/contacts/search/duplicate",
                    headers=_headers(),
                    params={"locationId": GHL_LOCATION_ID, "email": email},
                )
                if search_resp.status_code == 200:
                    contact_data = search_resp.json().get("contact", {})
                    contact_id = contact_data.get("id") if isinstance(contact_data, dict) else None
                    if contact_id:
                        # Merge new tags with existing ones
                        existing_tags = contact_data.get("tags", []) if isinstance(contact_data, dict) else []
                        merged_tags = list(set(existing_tags + tags))
                        client.put(
                            f"{GHL_BASE}/contacts/{contact_id}",
                            headers=_headers(),
                            json={"tags": merged_tags},
                        )
                        logger.info(f"GHL contact updated with tags: {contact_id}")
                        return contact_id

            logger.error(f"GHL contact create failed: {resp.status_code} {resp.text[:200]}")
            return None

    except Exception as e:
        logger.error(f"GHL contact error: {e}")
        return None


# ---------------------------------------------------------------------------
# Welcome email
# ---------------------------------------------------------------------------

def _send_welcome_email(contact_id: str, access_code: str, founding_number: int) -> bool:
    """Send the Founding Crew welcome email with the access code."""
    if not GHL_API_KEY or not contact_id:
        return False

    try:
        from .drip_emails import welcome_email
        subject, body = welcome_email(access_code, founding_number)
    except Exception as e:
        logger.error(f"Failed to render welcome email template: {e}")
        return False

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f"{GHL_BASE}/conversations/messages",
                headers=_headers(),
                json={
                    "type": "Email",
                    "contactId": contact_id,
                    "subject": subject,
                    "html": body,
                },
            )
            if resp.status_code in (200, 201):
                logger.info(f"Welcome email sent to contact {contact_id}")
                return True
            else:
                logger.error(f"GHL email failed: {resp.status_code} {resp.text[:200]}")
                return False
    except Exception as e:
        logger.error(f"GHL email error: {e}")
        return False


# ---------------------------------------------------------------------------
# Main entry point — called by Stripe webhook/claim-code handlers
# ---------------------------------------------------------------------------

def notify_purchase(
    email: str,
    name: str,
    phone: str,
    company: str,
    access_code: str,
    founding_number: int,
) -> None:
    """Called after a successful Stripe purchase + code issuance.

    Creates/updates GHL contact, stores the code as a tag, and sends welcome email.
    Failures are logged but never raise — this is a best-effort side effect
    that must not break the purchase flow.
    """
    if not GHL_API_KEY:
        logger.info("GHL integration disabled (no GHL_API_KEY).")
        return

    parts = name.split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""

    # Tags include the access code for durable storage
    tags = [
        "rooftranslate",
        "founding-crew",
        f"{CODE_TAG_PREFIX}{access_code}",  # e.g. "rt:RT-A3K7-B9M2"
    ]
    if founding_number > 0:
        tags.append(f"founding-{founding_number:03d}")

    contact_id = _create_or_update_contact(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        company=company,
        tags=tags,
    )

    if contact_id:
        _send_welcome_email(contact_id, access_code, founding_number)

        # Enroll in drip sequence
        try:
            from .drip_scheduler import enroll_contact
            enroll_contact(contact_id, tags)
        except Exception as e:
            logger.error(f"Drip enrollment failed: {e}")
