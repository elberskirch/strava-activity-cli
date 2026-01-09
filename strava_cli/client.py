"""Client module for Strava API with token management."""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from stravalib.client import Client


class StravaClient:
    """Wrapper for Strava API client with automatic token refresh."""

    def __init__(self, token_file: Path | None = None):
        """Initialize Strava client.

        Args:
            token_file: Path to JSON file storing tokens. Defaults to strava-token.json
        """
        load_dotenv()
        self.token_file = token_file or Path("strava-token.json")
        self.client = Client()
        self._load_and_set_token()

    def _load_and_set_token(self) -> None:
        """Load tokens from file and set up client."""
        if not self.token_file.exists():
            raise FileNotFoundError(
                f"Token file not found: {self.token_file}. "
                "Please ensure strava-token.json exists with valid tokens."
            )

        with open(self.token_file) as f:
            data = json.load(f)

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expires_at = data.get("expires_at")

        if not access_token or not refresh_token:
            raise ValueError("Invalid token file: missing access_token or refresh_token")

        # Check if token needs refresh (with 5 minute buffer)
        if expires_at and time.time() > (expires_at - 300):
            self._refresh_token(refresh_token)
        else:
            self.client.access_token = access_token

    def _refresh_token(self, refresh_token: str) -> None:
        """Refresh the access token.

        Args:
            refresh_token: The refresh token to use
        """
        client_id = os.environ.get("STRAVA_CLIENT_ID")
        client_secret = os.environ.get("STRAVA_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in environment")

        token_response = self.client.refresh_access_token(
            client_id=int(client_id),
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

        # Update token file
        with open(self.token_file, "w") as f:
            json.dump(token_response, f, indent=2)

        self.client.access_token = token_response["access_token"]

    def get_client(self) -> Client:
        """Get the authenticated client instance.

        Returns:
            Authenticated stravalib Client instance
        """
        return self.client
