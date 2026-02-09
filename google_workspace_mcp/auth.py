"""
Google OAuth Authentication Handler

Manages OAuth 2.0 flow for Google Workspace APIs.
"""

import os
import json
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth scopes for each service
SCOPES = {
    "gmail": "https://www.googleapis.com/auth/gmail.modify",
    "gmail_readonly": "https://www.googleapis.com/auth/gmail.readonly",
    "sheets": "https://www.googleapis.com/auth/spreadsheets",
    "docs": "https://www.googleapis.com/auth/documents",
    "drive": "https://www.googleapis.com/auth/drive",
    "drive_readonly": "https://www.googleapis.com/auth/drive.readonly",
    "slides": "https://www.googleapis.com/auth/presentations",
}

# Combined scopes for full workspace access
FULL_WORKSPACE_SCOPES = [
    SCOPES["gmail"],
    SCOPES["sheets"],
    SCOPES["docs"],
    SCOPES["drive"],
    SCOPES["slides"],
]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


class GoogleAuth:
    """Handles Google OAuth 2.0 authentication"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_file: str = TOKEN_FILE,
    ):
        """
        Initialize Google OAuth handler

        Args:
            client_id: OAuth client ID (from env or parameter)
            client_secret: OAuth client secret (from env or parameter)
            token_file: Path to store OAuth token
        """
        self.client_id = client_id or os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set "
                "in environment variables or passed as parameters"
            )

        self.token_file = Path(token_file)
        self.credentials: Optional[Credentials] = None

    def _load_token(self) -> Optional[Credentials]:
        """Load token from file if it exists"""
        if self.token_file.exists():
            try:
                with open(self.token_file, "r") as f:
                    token_data = json.load(f)
                return Credentials.from_authorized_user_info(token_data)
            except Exception:
                return None
        return None

    def _save_token(self, credentials: Credentials) -> None:
        """Save token to file"""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, "w") as f:
            json.dump({
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }, f, indent=2)

    def _create_credentials_dict(self) -> dict:
        """Create credentials dict for OAuth flow"""
        return {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["http://localhost"]
            }
        }

    def authenticate(self, scopes: Optional[list[str]] = None) -> Credentials:
        """
        Authenticate with Google OAuth 2.0

        Args:
            scopes: List of OAuth scopes to request

        Returns:
            Authenticated credentials
        """
        if scopes is None:
            scopes = FULL_WORKSPACE_SCOPES

        # Try to load existing token
        self.credentials = self._load_token()

        # Check if credentials are valid
        if self.credentials and self.credentials.valid:
            return self.credentials

        # Refresh if expired but we have a refresh token
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self._save_token(self.credentials)
                return self.credentials
            except Exception:
                print("Token refresh failed, starting new authentication flow...")

        # Start new authentication flow
        print("Starting OAuth authentication flow...")

        # Create client config dict
        client_config = self._create_credentials_dict()

        # Create flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=scopes,
        )

        # Run the flow - this will open a browser
        self.credentials = flow.run_local_server(
            port=0,
            open_browser=True,
            prompt="consent",
        )

        # Save the credentials
        self._save_token(self.credentials)

        print(f"\n✓ Authentication successful for: {self.credentials.client_id}")
        return self.credentials

    def get_credentials(self, force_refresh: bool = False) -> Credentials:
        """
        Get authenticated credentials, refreshing if needed

        Args:
            force_refresh: Force credential refresh even if valid

        Returns:
            Valid credentials
        """
        if not self.credentials:
            self.credentials = self.authenticate()

        if force_refresh or (self.credentials.expired and self.credentials.refresh_token):
            try:
                self.credentials.refresh(Request())
                self._save_token(self.credentials)
            except Exception as e:
                print(f"Credential refresh failed: {e}")
                self.credentials = self.authenticate()

        return self.credentials


def get_auth() -> GoogleAuth:
    """Get or create global auth instance"""
    global _auth_instance
    if "_auth_instance" not in globals():
        _auth_instance = GoogleAuth()
    return _auth_instance


# Global auth instance (initialized on first use)
_auth_instance: Optional[GoogleAuth] = None
