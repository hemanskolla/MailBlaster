#!/usr/bin/env python3
"""
MailBlaster — Send personalized bulk emails via Gmail SMTP.

Usage:
    python main.py --csv recipients.csv
    python main.py --csv recipients.csv --dry-run
    python main.py --csv recipients.csv --subject "Hello everyone"
"""

import argparse

from auth import get_smtp_connection
from recipients import load_recipients
from composer import compose, personalize
from mailer import send_all


def main():
    parser = argparse.ArgumentParser(
        description="Send bulk emails from Gmail without revealing recipients to each other."
    )
    parser.add_argument(
        "--csv",
        required=True,
        metavar="FILE",
        help="Path to CSV file with recipient emails (and optionally names).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be sent without actually sending any emails.",
    )
    parser.add_argument(
        "--subject",
        metavar="TEXT",
        default=None,
        help="Pre-fill the email subject (you will still be prompted if omitted).",
    )
    args = parser.parse_args()

    # 1. Load recipients from CSV
    recipients = load_recipients(args.csv)
    print(f"Loaded {len(recipients)} recipient(s) from {args.csv}.")

    # 2. Connect to Gmail SMTP
    if not args.dry_run:
        print("\nConnecting to Gmail...")
        smtp = get_smtp_connection()
        print("Connected successfully.\n")
    else:
        smtp = None
        print("(Dry run: skipping authentication)\n")

    # 3. Compose the email
    email = compose()

    # If --subject was passed, override the interactively entered subject
    if args.subject:
        email["subject"] = args.subject

    # 4. Send
    try:
        send_all(
            smtp=smtp,
            recipients=recipients,
            subject=email["subject"],
            body_html=email["body_html"],
            body_text=email["body_text"],
            dry_run=args.dry_run,
            personalize_fn=personalize,
        )
    finally:
        if smtp:
            smtp.quit()


if __name__ == "__main__":
    main()
