"""Drip email scheduler — sends timed emails to Founding Crew contacts via GHL.

How it works:
  - Each contact gets a `drip-enrolled:YYYY-MM-DD` tag when they purchase
  - A daily cron ping hits POST /drip/process
  - For each enrolled contact, we check how many days since enrollment
  - If a drip email is due and hasn't been sent yet (tracked via `drip-sent-dayN` tags),
    we send it and add the sent tag

This replaces the GHL workflow approach — everything is code-controlled,
version-controlled, and works through the GHL API.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

from .drip_emails import DRIP_SCHEDULE

logger = logging.getLogger(__name__)

GHL_API_KEY = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "2kDMnxQzxbmBOTz5Ikrh")
GHL_BASE = "https://services.leadconnectorhq.com"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json",
        "Version": "2021-07-28",
    }


def _get_enrollment_date(tags: list[str]) -> datetime | None:
    """Extract the enrollment date from a contact's drip-enrolled tag."""
    for tag in tags:
        if tag.startswith("drip-enrolled:"):
            date_str = tag[len("drip-enrolled:"):]
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def _get_sent_days(tags: list[str]) -> set[int]:
    """Extract which drip days have already been sent from tags."""
    sent = set()
    for tag in tags:
        if tag.startswith("drip-sent-day"):
            try:
                day = int(tag[len("drip-sent-day"):])
                sent.add(day)
            except ValueError:
                pass
    return sent


def _send_email_to_contact(
    client: httpx.Client,
    contact_id: str,
    subject: str,
    html_body: str,
) -> bool:
    """Send an email to a contact via GHL conversations API."""
    try:
        resp = client.post(
            f"{GHL_BASE}/conversations/messages",
            headers=_headers(),
            json={
                "type": "Email",
                "contactId": contact_id,
                "subject": subject,
                "html": html_body,
            },
        )
        if resp.status_code in (200, 201):
            logger.info(f"Drip email sent to {contact_id}: {subject}")
            return True
        else:
            logger.error(f"Drip email failed for {contact_id}: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"Drip email error for {contact_id}: {e}")
        return False


def _add_tag(client: httpx.Client, contact_id: str, tag: str, existing_tags: list[str]) -> bool:
    """Add a tag to a contact (merging with existing tags)."""
    try:
        merged = list(set(existing_tags + [tag]))
        resp = client.put(
            f"{GHL_BASE}/contacts/{contact_id}",
            headers=_headers(),
            json={"tags": merged},
        )
        return resp.status_code in (200, 201)
    except Exception:
        return False


def enroll_contact(contact_id: str, existing_tags: list[str]) -> None:
    """Add drip enrollment tag to a newly purchased contact.

    Called from notify_purchase() in ghl.py.
    """
    if not GHL_API_KEY:
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tag = f"drip-enrolled:{today}"

    # Check if already enrolled
    for t in existing_tags:
        if t.startswith("drip-enrolled:"):
            logger.info(f"Contact {contact_id} already enrolled in drip.")
            return

    try:
        with httpx.Client(timeout=10) as client:
            _add_tag(client, contact_id, tag, existing_tags)
            logger.info(f"Enrolled contact {contact_id} in drip: {tag}")
    except Exception as e:
        logger.error(f"Drip enrollment error: {e}")


def process_drip() -> dict[str, Any]:
    """Process all enrolled contacts and send any due drip emails.

    Returns a summary of what was sent.
    """
    if not GHL_API_KEY:
        return {"status": "disabled", "reason": "No GHL_API_KEY"}

    now = datetime.now(timezone.utc)
    sent_count = 0
    checked_count = 0
    errors = 0

    try:
        with httpx.Client(timeout=30) as client:
            # Fetch all contacts — paginate
            start_after = None
            all_contacts = []

            for page in range(10):  # max 1000 contacts
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
                    logger.error(f"Drip: Failed to fetch contacts: {resp.status_code}")
                    break

                contacts = resp.json().get("contacts", [])
                if not contacts:
                    break

                all_contacts.extend(contacts)
                if len(contacts) < 100:
                    break
                start_after = contacts[-1].get("id")

            # Process each contact
            for contact in all_contacts:
                tags = contact.get("tags", [])

                # Must have founding-crew tag and drip enrollment
                if "founding-crew" not in tags:
                    continue

                enrolled_date = _get_enrollment_date(tags)
                if not enrolled_date:
                    continue

                checked_count += 1
                days_since = (now - enrolled_date).days
                sent_days = _get_sent_days(tags)
                contact_id = contact.get("id", "")

                # Check each drip email in the schedule
                for day_offset, email_fn in DRIP_SCHEDULE:
                    if days_since >= day_offset and day_offset not in sent_days:
                        # This email is due and hasn't been sent
                        try:
                            subject, html_body = email_fn()
                            success = _send_email_to_contact(
                                client, contact_id, subject, html_body
                            )
                            if success:
                                # Mark as sent
                                sent_tag = f"drip-sent-day{day_offset}"
                                _add_tag(client, contact_id, sent_tag, tags)
                                tags.append(sent_tag)  # update local copy
                                sent_count += 1
                            else:
                                errors += 1
                        except Exception as e:
                            logger.error(f"Drip error for {contact_id} day {day_offset}: {e}")
                            errors += 1

    except Exception as e:
        logger.error(f"Drip process error: {e}")
        return {"status": "error", "error": str(e)}

    return {
        "status": "ok",
        "contacts_checked": checked_count,
        "emails_sent": sent_count,
        "errors": errors,
    }
