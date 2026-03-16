# MailBlaster

Send personalized bulk emails from your Gmail account without revealing recipients to each other. Each person gets their own individual email.

## Features

- Sends from your Gmail via SMTP — no Azure setup required
- Write your email in **Markdown** — bold, italic, links, lists all work
- Use `{name}` in your body to personalize each email with the recipient's name
- Load recipients from a CSV file
- Each recipient gets a separate email — no one can see others' addresses
- Attach one or more files to every email with `--attachments`
- Set a friendly sender display name via `SENDER_NAME` in your `.env`
- `--dry-run` mode to preview everything before sending

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate a Gmail App Password (one-time setup)

Regular Gmail passwords won't work — Google requires an **App Password** for SMTP access.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** if not already on
3. Go to **Security → App Passwords** (search "App Passwords" in the search bar)
4. Select app: **Mail**, Select device: **Other** → type "MailBlaster" → click **Generate**
5. Copy the 16-character password shown

### 3. Configure your `.env`

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
SENDER_NAME=Your Name or Team Name   # optional — shown as the "From" display name
```

If `SENDER_NAME` is set, recipients will see something like **"Innovation Weekend Message \<you@gmail.com\>"** instead of the raw address.

## CSV Format

Your CSV must have at minimum an `email` column. A `name` column is optional but enables personalization.

```csv
email,name
alice@example.com,Alice
bob@example.com,Bob
carol@example.com,
```

## Usage

```bash
python main.py --csv recipients.csv
```

### Options

| Flag | Description |
|------|-------------|
| `--csv FILE` | **(Required)** Path to your recipients CSV |
| `--dry-run` | Preview sends without actually sending |
| `--subject "..."` | Pre-fill subject from the command line |
| `--attachments FILE [FILE ...]` | One or more files to attach to every email |

### Example

```bash
# Dry run to verify everything looks right
python main.py --csv my_list.csv --dry-run

# Real send
python main.py --csv my_list.csv

# Send with attachments
python main.py --csv my_list.csv --attachments report.pdf image.png

# Pre-fill the subject
python main.py --csv my_list.csv --subject "Hello everyone"
```

## Formatting Reference

In the email body, use standard Markdown:

```
**bold text**
*italic text*
[click here](https://example.com)
- bullet point
1. numbered item

Dear {name}, ...   ← replaced with each recipient's name
```