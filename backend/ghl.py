"""GoHighLevel integration — creates contacts and sends welcome emails on purchase.

Public API:
    notify_purchase(email, name, phone, company, access_code, founding_number)

Requires GHL_API_KEY and GHL_LOCATION_ID env vars.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GHL_API_KEY = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "2kDMnxQzxbmBOTz5Ikrh")
GHL_BASE = "https://services.leadconnectorhq.com"

EVENT_PAYMENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }


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

            if resp.status_code == 200:
                data = resp.json()
                contact_id = data.get("contact", {}).get("id")
                logger.info(f"GHL contact created: {contact_id}")
                return contact_id

            if resp.status_code == 400 and "duplicate" in resp.text.lower():
                # Contact exists — search and update tags
                search_resp = client.get(
                    f"{GHL_BASE}/contacts/search/duplicate",
                    headers=_headers(),
                    params={"locationId": GHL_LOCATION_ID, "email": email},
                )
                if search_resp.status_code == 200:
                    contacts = search_resp.json().get("contact", {})
                    contact_id = contacts.get("id") if isinstance(contacts, dict) else None
                    if contact_id:
                        # Add tags to existing contact
                        client.put(
                            f"{GHL_BASE}/contacts/{contact_id}",
                            headers=_headers(),
                            json={"tags": tags},
                        )
                        logger.info(f"GHL contact updated with tags: {contact_id}")
                        return contact_id

            logger.error(f"GHL contact create failed: {resp.status_code} {resp.text[:200]}")
            return None

    except Exception as e:
        logger.error(f"GHL contact error: {e}")
        return None


def _send_welcome_email(contact_id: str, access_code: str, founding_number: int) -> bool:
    """Send the Founding Crew welcome email with the access code."""
    if not GHL_API_KEY or not contact_id:
        return False

    subject = "Welcome to the Founding Crew \u2014 Your RoofTranslate Access Code"

    # Founding number display
    fn_display = f"#{founding_number}" if founding_number > 0 else ""

    body = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e4e4e7; border-radius: 12px; overflow: hidden;">

  <div style="background: #161618; padding: 32px 24px; text-align: center; border-bottom: 1px solid #27272a;">
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #a1a1aa; margin-bottom: 8px;">\u25b2 Frazier Media</div>
    <h1 style="font-size: 28px; font-weight: 600; margin: 0; color: #ffffff;">Welcome to the Founding Crew</h1>
  </div>

  <div style="padding: 32px 24px;">
    <p style="font-size: 16px; line-height: 1.6; color: #d4d4d8; margin-top: 0;">
      You're officially in{' \u2014 Founding Crew Member ' + fn_display if fn_display else ''}. Thank you for being one of the first 100 contractors to join RoofTranslate.
    </p>

    <p style="font-size: 16px; line-height: 1.6; color: #d4d4d8;">
      Here's your access code \u2014 save it somewhere safe. You'll use it to log in at <a href="https://rooftranslate.com" style="color: #60a5fa; text-decoration: none;">rooftranslate.com</a>.
    </p>

    <div style="background: #161618; border: 1px solid #3f3f46; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
      <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #a1a1aa; margin-bottom: 12px;">Your Access Code</div>
      <div style="font-family: 'SF Mono', 'Fira Code', monospace; font-size: 28px; font-weight: 700; letter-spacing: 4px; color: #ffffff;">{access_code}</div>
      <div style="font-size: 13px; color: #71717a; margin-top: 8px;">Valid for 1 year from purchase</div>
    </div>

    <p style="font-size: 16px; line-height: 1.6; color: #d4d4d8;">
      <strong style="color: #ffffff;">How it works:</strong> Upload any English roofing document (scope of work, job notes, crew sheets) and get a professional Spanish translation back in seconds. Your crew gets clear instructions \u2014 no miscommunication on the job site.
    </p>

    <div style="text-align: center; margin: 32px 0;">
      <a href="https://rooftranslate.com" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none;">Start Translating \u2192</a>
    </div>

    <hr style="border: none; border-top: 1px solid #27272a; margin: 32px 0;" />

    <div style="background: #161618; border: 1px solid #27272a; border-radius: 12px; padding: 24px; text-align: center;">
      <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #a1a1aa; margin-bottom: 8px;">Founding Crew Exclusive</div>
      <h2 style="font-size: 22px; font-weight: 600; margin: 0 0 8px 0; color: #ffffff;">2-Day Live Training \u2014 Naples, FL</h2>
      <p style="font-size: 15px; color: #a1a1aa; margin: 0 0 8px 0;">May 1-2, 2026 \u00b7 Lee's HQ</p>
      <p style="font-size: 18px; font-weight: 600; color: #4ade80; margin: 0 0 16px 0;">Your price: $4,500 (save $500)</p>
      <a href="{EVENT_PAYMENT_LINK}" style="color: #60a5fa; font-size: 14px; text-decoration: none; font-weight: 500;">Learn more &amp; register \u2192</a>
    </div>
  </div>

  <div style="background: #161618; padding: 24px; text-align: center; border-top: 1px solid #27272a;">
    <div style="font-size: 12px; color: #52525b; margin-bottom: 8px;">\u25b2 RoofTranslate \u00b7 A Frazier Media Tool</div>
    <div style="font-size: 11px; color: #3f3f46;">Your files are processed in memory and never stored. Privacy first.</div>
  </div>

</div>"""

    try:
        with httpx.Client(timeout=15) as client:
            # GHL send email via conversations API
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


def notify_purchase(
    email: str,
    name: str,
    phone: str,
    company: str,
    access_code: str,
    founding_number: int,
) -> None:
    """Called after a successful Stripe purchase + code issuance.

    Creates/updates GHL contact, tags them, and sends the welcome email.
    Failures are logged but never raise — this is a best-effort side effect
    that must not break the purchase flow.
    """
    if not GHL_API_KEY:
        logger.info("GHL integration disabled (no GHL_API_KEY).")
        return

    parts = name.split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""

    tags = ["rooftranslate", "founding-crew"]
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
