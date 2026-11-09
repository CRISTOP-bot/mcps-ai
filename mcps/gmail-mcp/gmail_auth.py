"""OAuth2 authentication script for Gmail MCP.

Run this once to generate the token file:
    python gmail_auth.py

This will open a browser for Google authentication.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]

CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS", "credentials.json")
TOKEN_FILE = os.getenv("GMAIL_TOKEN", "token.json")


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found.")
        print("Download it from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download as credentials.json")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"Token saved to {TOKEN_FILE}")
    print("You can now use the Gmail MCP server.")


if __name__ == "__main__":
    main()
PYEOF
echo "gmail_auth.py creado"