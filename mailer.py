"""
Sends emails individually via Gmail SMTP.
Each recipient gets their own separate message — no one can see others' addresses.
"""

import os
import time
import smtplib
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
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
    attachments: list[str] | None = None,
    dry_run: bool = False,
    personalize_fn=None,
) -> None:
    """
    Sends one email per recipient via Gmail SMTP. Each email is addressed only
    to that single recipient — no one can see others' addresses.
    """
    sender = os.getenv("GMAIL_ADDRESS", "")
    total = len(recipients)
    attachments = attachments or []

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
            msg = _build_message(sender, recipient, subject, html, text, attachments)
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
    sender: str,
    recipient: Recipient,
    subject: str,
    body_html: str,
    body_text: str,
    attachments: list[str] | None = None,
) -> MIMEMultipart:
    attachments = attachments or []

    if attachments:
        # mixed outer → alternative inner (text+html) + file parts
        msg = MIMEMultipart("mixed")
        body_part = MIMEMultipart("alternative")
        body_part.attach(MIMEText(body_text, "plain"))
        body_part.attach(MIMEText(body_html, "html"))
        msg.attach(body_part)

        for path in attachments:
            mime_type, _ = mimetypes.guess_type(path)
            main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)
            with open(path, "rb") as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(path),
            )
            msg.attach(part)
    else:
        msg = MIMEMultipart("alternative")
        # Attach plain text first, HTML second (email clients prefer the last part)
        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient.display()

    return msg
