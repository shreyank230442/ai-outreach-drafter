# services/email_sender.py

import os
import smtplib
from email.message import EmailMessage


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_otp_email(to_email: str, otp_code: str):
    """
    Sends an OTP email to the given email address.
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise RuntimeError("SMTP_EMAIL or SMTP_PASSWORD not set")

    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Your Email Verification Code"

    msg.set_content(f"""
Hello,

Your One-Time Password (OTP) for verifying your account is:

    {otp_code}

This OTP is valid for 10 minutes.

If you did not try to create an account, you can safely ignore this email.

Regards,
AI Outreach System
""")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        raise RuntimeError(f"Failed to send OTP email: {e}")