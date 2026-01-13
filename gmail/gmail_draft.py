import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build

from gmail.gmail_auth import get_gmail_service


def create_gmail_draft(to_email, subject, body):
    creds = get_gmail_service()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    draft = service.users().drafts().create(
        userId="me",
        body={
            "message": {
                "raw": raw_message
            }
        },
    ).execute()

    return draft["id"], draft["message"]["threadId"]
