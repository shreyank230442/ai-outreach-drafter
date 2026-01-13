# auth/login.py

import streamlit as st
import random
from datetime import datetime, timedelta

from models.user import authenticate_user, set_otp
from services.email_sender import send_otp_email
from auth.session import login_user


def login():
    st.subheader("🔐 Login")

    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login", key="login_button"):
        result = authenticate_user(email, password)

        # ✅ Login success
        if isinstance(result, int):
            login_user(result)
            st.success("Logged in successfully")
            st.rerun()

        # ⚠️ Email exists but not verified
        elif result == "NOT_VERIFIED":
            st.warning("Your email is not verified. Please verify to continue.")

            if st.button("Resend OTP", key="resend_otp_button"):
                # generate new OTP
                otp_code = f"{random.randint(100000, 999999)}"
                expires_at = datetime.utcnow() + timedelta(minutes=10)

                # fetch user_id indirectly by re-auth attempt
                # (safe because password was correct)
                user_id = authenticate_user(email, password)

                set_otp(user_id, otp_code, expires_at)

                try:
                    send_otp_email(email, otp_code)
                    st.success("A new OTP has been sent to your email.")
                    st.session_state["pending_verification_email"] = email
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to send OTP: {e}")

        # ❌ Invalid credentials
        else:
            st.error("Invalid email or password")