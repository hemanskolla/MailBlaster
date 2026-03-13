# MailBlaster

Send personalized bulk emails from your Outlook/RPI email account without revealing recipients to each other. Each person gets their own individual email.

## Features

- Authenticate once via browser — token is cached for future runs
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

### 2. Register an Azure app (one-time setup)

1. Go to [portal.azure.com](https://portal.azure.com) and sign in with your RPI account
2. Navigate to **Azure Active Directory → App registrations → New registration**
3. Name it anything (e.g. "MailBlaster"), select **"Accounts in this organizational directory only"**
4. Under **Authentication**, add a platform: choose **"Mobile and desktop applications"** and enable `https://login.microsoftonline.com/common/oauth2/nativeclient`
5. Under **API permissions**, add `Microsoft Graph → Delegated → Mail.Send`
6. Copy the **Application (client) ID** and **Directory (tenant) ID**

### 3. Configure your `.env`

```bash
cp .env.example .env
```

Edit `.env` and fill in your `CLIENT_ID`, `TENANT_ID`, and `SENDER_EMAIL`.

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

## First Run

On your first run, you'll see a message like:

```
--- Authentication Required ---
To sign in, use a web browser to open https://microsoft.com/devicelogin
and enter the code XXXXXXXX to authenticate.
-------------------------------
```

Open the URL, enter the code, and sign in with your RPI account. The token is cached in `token_cache.json` (git-ignored) so you won't need to do this again until it expires.