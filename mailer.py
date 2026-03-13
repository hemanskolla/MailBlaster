"""
Sends emails individually via the Microsoft Graph API.
Each recipient gets their own separate message — no one can see others' addresses.
"""

import os
import time
import requests
from dotenv import load_dotenv
from recipients import Recipient

load_dotenv()

GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/me/sendMail"
SEND_DELAY_SECONDS = 1.0  # Pause between sends to avoid rate limiting


def send_all(
    token: str,
    recipients: list[Recipient],
    subject: str,
    body_html: str,
    body_text: str,
    dry_run: bool = False,
    personalize_fn=None,
) -> None:
    """
    Sends one email per recipient. Each email is addressed only to that single
    recipient — no CC/BCC of other addresses.

    Args:
        token:          OAuth2 access token.
        recipients:     List of Recipient objects from recipients.py.
        subject:        Email subject line.
        body_html:      HTML version of the email body.
        body_text:      Plain-text version (used as fallback reference).
        dry_run:        If True, prints what would be sent without actually sending.
        personalize_fn: Optional callable(body_html, body_text, name, email) -> (html, text).
    """
    sender_email = os.getenv("SENDER_EMAIL", "")
    total = len(recipients)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Sending to {total} recipient(s)...\n")

    success_count = 0
    fail_count = 0

    for i, recipient in enumerate(recipients, start=1):
        html = body_html
        text = body_text

        if personalize_fn:
            html, text = personalize_fn(html, text, recipient.name, recipient.email)

        if dry_run:
            print(f"  [{i}/{total}] Would send to: {recipient.display()}")
            success_count += 1
            continue

        payload = _build_payload(sender_email, recipient, subject, html)

        try:
            _send_one(token, payload)
            print(f"  [{i}/{total}] Sent to: {recipient.display()}")
            success_count += 1
        except Exception as e:
            print(f"  [{i}/{total}] FAILED for {recipient.display()}: {e}")
            fail_count += 1

        if i < total:
            time.sleep(SEND_DELAY_SECONDS)

    print(f"\nDone. {success_count} sent, {fail_count} failed.")


def _build_payload(sender_email: str, recipient: Recipient, subject: str, body_html: str) -> dict:
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body_html,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient.email,
                        "name": recipient.name,
                    }
                }
            ],
        },
        "saveToSentItems": True,
    }
    if sender_email:
        payload["message"]["from"] = {
            "emailAddress": {"address": sender_email}
        }
    return payload


def _send_one(token: str, payload: dict) -> None:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(GRAPH_SEND_URL, headers=headers, json=payload, timeout=30)
    if response.status_code == 202:
        return  # 202 Accepted is the success response for sendMail
    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
