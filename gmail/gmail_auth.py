import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_credentials():
    """
    Low-level helper that returns valid Gmail OAuth credentials
    """
    creds = None

    token_path = os.path.join("gmail", "token.json")
    creds_path = os.path.join("gmail", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


# ✅ REQUIRED BY gmail_draft.py
def get_gmail_service():
    """
    Public API expected by gmail_draft.py.
    Returns valid Gmail OAuth credentials.
    """
    return get_gmail_credentials()


# ✅ BACKWARD COMPATIBILITY (safe to keep)
def authorize_gmail_and_get_tokens():
    """
    Compatibility wrapper for older imports.
    """
    return get_gmail_credentials()
