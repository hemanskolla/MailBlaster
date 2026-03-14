"""
Interactive email composer.
Accepts pasted Markdown content and converts it to an HTML email body.
Supports **bold**, *italic*, [links](url), and other standard Markdown.
"""

import sys
import markdown


HELP_TEXT = """
Formatting guide (Markdown syntax):
  **bold text**
  *italic text*
  [link text](https://example.com)
  - bullet item
  1. numbered item

Personalization:
  Use {name} in your body to insert each recipient's name.
  (Falls back to their email address if name is not in CSV.)
"""


def _prompt_multiline(prompt: str) -> str:
    """
    Reads multiple lines of input until the user enters a line containing
    only 'END' (case-insensitive).
    """
    print(prompt)
    print("  (When finished, type END on its own line and press Enter)\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def compose(attachments: list[str] | None = None) -> dict:
    """
    Interactively prompts the user for subject and body, then returns a dict:
      {
        "subject": str,
        "body_text": str,   # raw Markdown
        "body_html": str,   # converted HTML
      }
    """
    import os

    attachments = attachments or []

    print("=" * 60)
    print("  MailBlaster — Email Composer")
    print("=" * 60)
    print(HELP_TEXT)

    # Validate attachments early so the user knows before composing
    if attachments:
        print("Attachments:")
        for path in attachments:
            if not os.path.isfile(path):
                print(f"  ERROR: attachment not found: {path}")
                sys.exit(1)
            size_kb = os.path.getsize(path) / 1024
            print(f"  - {path} ({size_kb:.1f} KB)")
        print()

    # Subject
    subject = ""
    while not subject.strip():
        subject = input("Subject: ").strip()
        if not subject:
            print("  Subject cannot be empty.\n")

    # Body
    body_text = _prompt_multiline("\nPaste your email body below:")

    if not body_text.strip():
        print("Error: email body cannot be empty.")
        sys.exit(1)

    body_html = _markdown_to_html(body_text)

    # Preview
    print("\n" + "=" * 60)
    print("PREVIEW")
    print("=" * 60)
    print(f"Subject : {subject}")
    if attachments:
        print(f"Attachments: {', '.join(os.path.basename(p) for p in attachments)}")
    print(f"\nBody (plain):\n{body_text}\n")
    print(f"Body (HTML rendered):\n{body_html}")
    print("=" * 60)

    confirm = input("\nSend this email? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    return {
        "subject": subject,
        "body_text": body_text,
        "body_html": body_html,
    }


def _markdown_to_html(text: str) -> str:
    """Converts Markdown text to HTML, wrapped in basic email-safe styling."""
    html_body = markdown.markdown(text, extensions=["extra"])
    return f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #222;">
{html_body}
</body>
</html>"""


def personalize(body_html: str, body_text: str, name: str, email: str) -> tuple[str, str]:
    """
    Replaces {name} placeholder with the recipient's name (or email if no name).
    Returns (personalized_html, personalized_text).
    """
    display_name = name if name else email
    return (
        body_html.replace("{name}", display_name),
        body_text.replace("{name}", display_name),
    )
