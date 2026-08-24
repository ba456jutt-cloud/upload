#!/usr/bin/env python3
"""
YouTube OAuth Refresh Token Generator (1-Time Local Setup)
===========================================================
Run this script ONCE on your local machine to log in to YouTube 
and generate your YOUTUBE_REFRESH_TOKEN string for GitHub Actions.
"""

import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_refresh_token(client_secrets_file: str = "client_secrets.json"):
    print("======================================================")
    print("🔑 YOUTUBE OAUTH 2.0 REFRESH TOKEN GENERATOR")
    print("======================================================")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        credentials = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        
        print("\n[+] AUTHENTICATION SUCCESSFUL!")
        print("======================================================")
        print(f"📌 Client ID:     {credentials.client_id}")
        print(f"🔑 Refresh Token: {credentials.refresh_token}")
        print("======================================================")
        print("\n👉 COPY the 'Refresh Token' above and save it in your GitHub Repository Secrets as:")
        print("   YOUTUBE_REFRESH_TOKEN")
        print("\n👉 ALSO save the text content of 'client_secrets.json' in GitHub Repository Secrets as:")
        print("   YOUTUBE_CLIENT_SECRET_JSON")
        print("======================================================")
        
    except Exception as e:
        print(f"[-] Error generating token: {e}")
        print("\nMake sure you have downloaded 'client_secrets.json' from Google Cloud Console!")

if __name__ == "__main__":
    secrets_path = sys.argv[1] if len(sys.argv) > 1 else "client_secrets.json"
    generate_refresh_token(secrets_path)
