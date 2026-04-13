"""Send digest via Resend HTTP API."""
from __future__ import annotations

import logging
import os

import httpx

log = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def send_email(subject: str, html: str) -> None:
    api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["SENDER_EMAIL"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    resp = httpx.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        json={"from": sender, "to": [recipient], "subject": subject, "html": html},
        timeout=20.0,
    )
    if not resp.is_success:
        log.error("Resend error %s: %s", resp.status_code, resp.text)
    resp.raise_for_status()
    log.info("Email sent to %s (id=%s)", recipient, resp.json().get("id"))
