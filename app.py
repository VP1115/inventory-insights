from flask import Flask, request
import requests
import json
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SHEET_ID = os.environ.get("SHEET_ID")
GOOGLE_CREDS = os.environ.get("GOOGLE_CREDS")

TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"


def save_to_sheet(client_name, access_token, refresh_token, api_domain):
    try:
        creds_dict = json.loads(GOOGLE_CREDS)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        values = [[
            client_name,
            access_token,
            refresh_token,
            api_domain,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]]
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range="Sheet1!A:E",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()
        return True
    except Exception as e:
        print(f"Sheet error: {e}")
        return False


@app.route("/")
def home():
    return "<h2>Inventory Insights API is running.</h2>"


@app.route("/connect")
def connect():
    client_name = request.args.get("client", "Client")
    auth_url = (
        f"https://accounts.zoho.in/oauth/v2/auth"
        f"?scope=ZohoInventory.items.READ,ZohoInventory.invoices.READ,"
        f"ZohoInventory.salesorders.READ,ZohoInventory.contacts.READ"
        f"&client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&access_type=offline"
        f"&state={client_name}"
    )
    return f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Connect Zoho Inventory</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: -apple-system, sans-serif; background: #0F0F0F; color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
            .card {{ background: #1A1A1A; border: 1px solid #333; border-radius: 16px; padding: 40px; max-width: 420px; width: 100%; text-align: center; }}
            .logo {{ font-size: 32px; margin-bottom: 16px; }}
            h1 {{ font-size: 22px; margin-bottom: 8px; color: white; }}
            p {{ color: #888; font-size: 14px; margin-bottom: 32px; line-height: 1.6; }}
            .btn {{ background: #1A6B3C; color: white; border: none; border-radius: 10px; padding: 14px 28px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; width: 100%; }}
            .secure {{ margin-top: 20px; font-size: 12px; color: #555; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">📊</div>
            <h1>Connect Your Zoho Inventory</h1>
            <p>Hi {client_name}! Click below to securely connect your Zoho Inventory account to Inventory Insights. We only request read-only access.</p>
            <a href="{auth_url}" class="btn">Connect Zoho Inventory</a>
            <p class="secure">🔒 Secure · Read-only access · Disconnect anytime</p>
        </div>
    </body>
    </html>"""


@app.route("/callback")
def callback():
    code = request.args.get("code")
    client_name = request.args.get("state", "client")
    error = request.args.get("error")

    if error:
        return "<h2>Connection cancelled. Please try again.</h2>"

    if not code:
        return "<h2>No code received. Please try again.</h2>"

    response = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    })

    tokens = response.json()

    if "access_token" not in tokens:
        return f"<h2>Error: {tokens}</h2>"

    save_to_sheet(
        client_name,
        tokens["access_token"],
        tokens.get("refresh_token", ""),
        tokens.get("api_domain", "https://www.zohoapis.in")
    )

    return """<!DOCTYPE html>
    <html>
    <head>
        <title>Connected!</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, sans-serif; background: #0F0F0F; color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
            .card { background: #1A1A1A; border: 1px solid #1A6B3C; border-radius: 16px; padding: 40px; max-width: 420px; width: 100%; text-align: center; }
            .check { font-size: 48px; margin-bottom: 16px; }
            h1 { font-size: 22px; color: #4ADE80; margin-bottom: 8px; }
            p { color: #888; font-size: 14px; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="check">✅</div>
            <h1>Successfully Connected!</h1>
            <p>Your Zoho Inventory is now connected to Inventory Insights.<br><br>
            Vardaan will be in touch shortly with your first report. You can close this tab.</p>
        </div>
    </body>
    </html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
