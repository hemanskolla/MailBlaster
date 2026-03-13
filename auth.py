"""
Handles Microsoft OAuth2 authentication via MSAL.
Uses device code flow so you authenticate in a browser.
Tokens are cached locally in token_cache.json and refreshed silently on reuse.
"""

import os
import json
import msal
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "token_cache.json"
SCOPES = ["https://graph.microsoft.com/Mail.Send"]


def _build_app(cache: msal.SerializableTokenCache) -> msal.PublicClientApplication:
    client_id = os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID", "common")
    if not client_id:
        raise ValueError("CLIENT_ID not set. Copy .env.example to .env and fill it in.")
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    return msal.PublicClientApplication(client_id, authority=authority, token_cache=cache)


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def get_access_token() -> str:
    """
    Returns a valid access token, prompting the user to authenticate via
    browser device code flow if no cached token exists.
    """
    cache = _load_cache()
    app = _build_app(cache)

    accounts = app.get_accounts()
    result = None

    if accounts:
        # Try silent refresh first
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        # Prompt user to authenticate via browser
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to create device flow: {flow.get('error_description')}")
        print("\n--- Authentication Required ---")
        print(flow["message"])
        print("-------------------------------\n")
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(cache)

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        raise RuntimeError(f"Authentication failed: {error}")

    return result["access_token"]
