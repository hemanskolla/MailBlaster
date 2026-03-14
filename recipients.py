"""
Parses and validates a CSV file of email recipients.
Expected CSV columns: email (required), name (optional).
"""

import csv
import re
import sys
from dataclasses import dataclass, field
from typing import List

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Recipient:
    email: str
    name: str = ""

    def display(self) -> str:
        return f"{self.name} <{self.email}>" if self.name else self.email


def load_recipients(csv_path: str) -> List[Recipient]:
    """
    Reads a CSV file and returns a list of validated Recipient objects.
    Exits with an error message if the file is missing required columns
    or contains no valid rows.
    """
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or "email" not in [
                col.strip().lower() for col in reader.fieldnames
            ]:
                print(f"Error: CSV must have an 'email' column. Found: {reader.fieldnames}")
                sys.exit(1)

            # Normalize fieldnames to lowercase for flexible column naming
            normalized_rows = [
                {k.strip().lower(): v.strip() for k, v in row.items()}
                for row in reader
            ]

    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    recipients = []
    bad_rows = []

    for i, row in enumerate(normalized_rows, start=2):  # start=2 accounts for header row
        email = row.get("email", "").strip()
        name = row.get("name", "").strip()

        if not email:
            bad_rows.append((i, "empty email"))
            continue
        if not EMAIL_RE.match(email):
            bad_rows.append((i, f"invalid email: {email!r}"))
            continue

        recipients.append(Recipient(email=email, name=name))

    if bad_rows:
        print("Warning: skipping invalid rows:")
        for row_num, reason in bad_rows:
            print(f"  Row {row_num}: {reason}")

    if not recipients:
        print("Error: no valid recipients found in CSV.")
        sys.exit(1)

    return recipients
