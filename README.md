# Inventory Insights — Zoho OAuth Connector

`Python` | `Flask` | `Zoho Inventory API` | `Google Sheets API` | `Heroku`

A lightweight Flask service that handles the Zoho Inventory OAuth 2.0 authorization flow and centralizes client credentials in a Google Sheet for downstream automated reporting.

---

## What it does

Clients visit a personalized `/connect?client=Name` URL, see a branded landing page, and are walked through Zoho's OAuth consent screen. On successful authorization, the service exchanges the code for access and refresh tokens and appends them to a central Google Sheet alongside the client name, API domain, and timestamp. This gives a single place to read client credentials when pulling inventory data on their behalf.

---

## Key features

- **Full OAuth 2.0 authorization code flow** — handles the redirect, state parameter, and token exchange against Zoho's India endpoint (`accounts.zoho.in`)
- **Read-only scopes** — requests only `items.READ`, `invoices.READ`, `salesorders.READ`, and `contacts.READ`; no write access to client Zoho data
- **Google Sheets credential log** — on successful auth, appends one row (client name, access token, refresh token, API domain, timestamp) via a service account
- **Client-branded connection page** — the `/connect` route renders a personalized page using the `client` query parameter
- **Environment-driven config** — all credentials are read from environment variables; nothing sensitive is hardcoded

---

## Tech stack

- **Language:** Python 3
- **Framework:** Flask
- **APIs:** Zoho Inventory OAuth 2.0, Google Sheets API v4
- **Auth:** Google service account (`google-auth`, `google-api-python-client`)
- **Deployment:** Heroku (Procfile included)

---

## How it works

```
GET /connect?client=ClientName
    Renders branded landing page with a Zoho OAuth authorization URL.

Zoho redirects to GET /callback?code=...&state=ClientName
    Exchanges authorization code for tokens (POST to accounts.zoho.in).
    Calls save_to_sheet(): appends row to Google Sheet via service account.
    Renders success confirmation page.
```

---

## Setup

```bash
git clone https://github.com/VP1115/inventory-insights
cd inventory-insights
pip install -r requirements.txt
```

Set environment variables:

```bash
ZOHO_CLIENT_ID=...
ZOHO_CLIENT_SECRET=...
REDIRECT_URI=https://your-app.herokuapp.com/callback
SHEET_ID=your_google_sheet_id
GOOGLE_CREDS='{"type":"service_account",...}'   # full service account JSON as a string
```

Run locally:
```bash
python app.py
```

Deploy to Heroku:
```bash
heroku create
heroku config:set ZOHO_CLIENT_ID=... ZOHO_CLIENT_SECRET=... REDIRECT_URI=... SHEET_ID=... GOOGLE_CREDS=...
git push heroku main
```

---

## Status

Personal tool built for a client onboarding workflow. Deployed on Heroku. Not actively maintained.
