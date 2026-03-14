"""
Sends emails individually via Gmail SMTP.
Each recipient gets their own separate message — no one can see others' addresses.
"""

import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from recipients import Recipient

load_dotenv()

SEND_DELAY_SECONDS = 1.0  # Pause between sends to avoid rate limiting


def send_all(
    smtp: smtplib.SMTP,
    recipients: list[Recipient],
    subject: str,
    body_html: str,
    body_text: str,
    dry_run: bool = False,
    personalize_fn=None,
) -> None:
    """
    Sends one email per recipient via Gmail SMTP. Each email is addressed only
    to that single recipient — no one can see others' addresses.
    """
    sender = os.getenv("GMAIL_ADDRESS", "")
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

        try:
            msg = _build_message(sender, recipient, subject, html, text)
            smtp.sendmail(sender, recipient.email, msg.as_string())
            print(f"  [{i}/{total}] Sent to: {recipient.display()}")
            success_count += 1
        except Exception as e:
            print(f"  [{i}/{total}] FAILED for {recipient.display()}: {e}")
            fail_count += 1

        if i < total:
            time.sleep(SEND_DELAY_SECONDS)

    print(f"\nDone. {success_count} sent, {fail_count} failed.")


def _build_message(
    sender: str, recipient: Recipient, subject: str, body_html: str, body_text: str
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient.display()

    # Attach plain text first, HTML second (email clients prefer the last part)
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    return msg
