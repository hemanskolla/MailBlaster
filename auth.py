"""
Handles Gmail authentication via App Password.
Loads credentials from .env and returns an authenticated SMTP connection.
"""

import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def get_smtp_connection() -> smtplib.SMTP:
    """
    Returns an authenticated SMTP connection to Gmail.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD to be set in .env.
    """
    address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not address:
        raise ValueError("GMAIL_ADDRESS not set in .env")
    if not app_password:
        raise ValueError("GMAIL_APP_PASSWORD not set in .env")

    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(address, app_password)
    return smtp
