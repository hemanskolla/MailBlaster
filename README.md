# MailBlaster

Send personalized bulk emails from your Gmail account without revealing recipients to each other. Each person gets their own individual email.

## Features

- Sends from your Gmail via SMTP — no Azure setup required
- Write your email in **Markdown** — bold, italic, links, lists all work
- Use `{name}` in your body to personalize each email with the recipient's name
- Load recipients from a CSV file
- Each recipient gets a separate email — no one can see others' addresses
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

Edit `.env` and fill in your Gmail address and the App Password from step 2.

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

### Example

```bash
# Dry run to verify everything looks right
python main.py --csv my_list.csv --dry-run

# Real send
python main.py --csv my_list.csv
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