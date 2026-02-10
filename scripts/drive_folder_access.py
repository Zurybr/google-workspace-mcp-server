#!/usr/bin/env python3
"""
Access Google Drive folder content using Google CLI credentials

This script uses console-based OAuth flow (no browser required).

Usage:
    python drive_folder_access.py <folder_id>
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client", "google-auth-oauthlib"])
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

# Google Drive API scopes
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Path to gogcli credentials
GOGCLI_CONFIG = Path.home() / '.config' / 'gogcli'
TOKEN_FILE = Path(__file__).parent.parent / '.drive_token.json'


def get_credentials_console():
    """Get OAuth credentials using console-based flow (no browser)"""

    # Check if we have saved credentials
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            creds = Credentials.from_oauth2_info(token_data)
            if creds.expired and creds.refresh_token:
                print("Refreshing credentials...")
                creds.refresh(Request())
                # Save refreshed token
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(creds.to_json(), f)
                return creds
            if not creds.expired:
                return creds
        except Exception as e:
            print(f"Could not load saved credentials: {e}")

    # Fall back to OAuth flow
    creds_file = GOGCLI_CONFIG / 'credentials_installed.json'
    if not creds_file.exists():
        creds_file = GOGCLI_CONFIG / 'credentials.json'

    if not creds_file.exists():
        print("Error: No Google OAuth credentials found.")
        print("Please run './install.sh' to set up OAuth credentials first.")
        sys.exit(1)

    print(f"Using credentials from: {creds_file}")

    # Use console-based flow
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), DRIVE_SCOPES)

    # Run console flow
    creds = flow.run_console()

    # Save credentials for next time
    with open(TOKEN_FILE, 'w') as f:
        json.dump(creds.to_json(), f)

    return creds


def list_folder(service, folder_id):
    """List all files in a Google Drive folder"""
    results = []
    page_token = None

    query = f"'{folder_id}' in parents"

    while True:
        try:
            response = service.files().list(
                q=query,
                fields='nextPageToken,files(id,name,mimeType,webViewLink,webContentLink,size,modifiedTime,description)',
                pageToken=page_token,
                pageSize=100
            ).execute()

            files = response.get('files', [])
            results.extend(files)
            page_token = response.get('nextPageToken')

            if not page_token:
                break

        except Exception as e:
            print(f"Error listing files: {e}")
            break

    return results


def print_file_info(file):
    """Print file information in a readable format"""
    print(f"\n{'='*60}")
    print(f"📄 {file['name']}")
    print(f"{'='*60}")
    print(f"Type: {file['mimeType']}")
    print(f"ID: {file['id']}")
    if 'webViewLink' in file:
        print(f"View: {file['webViewLink']}")
    if 'webContentLink' in file:
        print(f"Download: {file['webContentLink']}")
    if 'size' in file:
        size_mb = int(file['size']) / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB")
    if 'modifiedTime' in file:
        print(f"Modified: {file['modifiedTime']}")
    if 'description' in file and file['description']:
        print(f"Description: {file['description'][:100]}...")


def main():
    if len(sys.argv) < 2:
        print("Usage: python drive_folder_access.py <folder_id>")
        print("\nExample: python drive_folder_access.py 1mn8-zgwthQ78eryzn6PUWwDr9Gvy4mSN")
        sys.exit(1)

    folder_id = sys.argv[1]

    print(f"🔐 Authenticating with Google Drive...")
    print("Note: First time will require OAuth authorization in console")
    creds = get_credentials_console()

    print(f"📂 Listing files in folder: {folder_id}")
    service = build('drive', 'v3', credentials=creds)

    files = list_folder(service, folder_id)

    if not files:
        print("No files found in this folder.")
        return

    print(f"\n✅ Found {len(files)} file(s):\n")

    for file in files:
        print_file_info(file)

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(files)} file(s) in folder")
    print(f"{'='*60}")

    # Also print as JSON for easy parsing
    print(f"\n📋 JSON Output:")
    print(json.dumps(files, indent=2))


if __name__ == "__main__":
    main()
