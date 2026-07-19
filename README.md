# Complete Project Setup

Follow these steps to run the project from scratch.

## 1. Clone Repository

```bash
git clone <repository-url>
cd <project-folder>
```

## 2. Install Python

Install Python 3.12 or above.

Verify installation:

```bash
python --version
```

## 3. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Install PostgreSQL

- Install PostgreSQL.
- Create a new database.
- Copy the database connection URL.

Example:

```text
postgresql://username:password@localhost:5432/salon_ai_bot
```

## 6. Create Meta Developer App

- Create a Meta Developer account.
- Create a new Business App.
- Add the WhatsApp product.
- Add a test phone number.
- Copy:
  - Access Token
  - Phone Number ID
  - Verify Token (create your own)

## 7. Configure Environment Variables

Create a `.env` file in the project root.

```env
WHATSAPP_TOKEN=
PHONE_NUMBER_ID=

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

## 8. Setup Google Cloud

- Create a Google Cloud Project.
- Enable Google Sheets API.
- Enable Google Drive API.
- Create a Service Account.
- Download `credentials.json`.
- Place it in the project root.
- Share the Google Sheet with the service account email.

## 9. Seed Database

Run all seed files once.

```bash
python -m database.seed_admin
python -m database.seed_staff
python -m database.seed_services
python -m database.seed_settings
python -m database.seed_customer_history
```

## 10. Start FastAPI Server

```bash
uvicorn main:app --reload
```

## 11. Install Cloudflared

Verify installation:

```bash
cloudflared --version
```

## 12. Start Cloudflared Tunnel

Open a new terminal.

```bash
cloudflared tunnel --url http://localhost:8000
```

Copy the generated HTTPS URL.

Example:

```text
https://xxxxx.trycloudflare.com
```

## 13. Configure Meta Webhook

Webhook URL

```text
https://xxxxx.trycloudflare.com/webhook
```

Verify Token

```text
<VERIFY_TOKEN_FROM_ENV>
```

Click **Verify & Save** and subscribe to:

- messages

## 14. Add Test Phone Number

Add your personal number as a test recipient in the WhatsApp Cloud API dashboard.

## 15. Start Using the Bot

Send a WhatsApp message to the Meta test number.

The bot is now ready.

---

## Repair Google Sheets

If Google Sheets becomes inconsistent with PostgreSQL:

```bash
python -m sync.repair_sync
```

This rebuilds all Google Sheets directly from PostgreSQL.

---

## First Time Setup

> **Important:** Steps **1–14** are required only once during the initial setup.

After that, you only need to:

- Activate the virtual environment.
- Start the FastAPI server.
- Start Cloudflared.

---

## Daily Startup

Activate virtual environment

```bash
venv\Scripts\activate
```

Start FastAPI

```bash
uvicorn main:app --reload
```

Start Cloudflared (new terminal)

```bash
cloudflared tunnel --url http://localhost:8000
```

If the Cloudflared URL changes, update the Webhook URL in the Meta Developer Dashboard.

---

## Project Architecture

```text
WhatsApp
    │
    ▼
FastAPI
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
PostgreSQL
    │
    ▼
Sync Layer
    │
    ▼
Google Sheets
```