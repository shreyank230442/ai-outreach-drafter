# auth/register.py

import streamlit as st
import re
import random
from datetime import datetime, timedelta

from models.user import create_user, set_otp
from services.email_sender import send_otp_email


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def register():
    st.subheader("📝 Register")

    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input(
        "Confirm Password", type="password", key="register_confirm_password"
    )

    if st.button("Create Account", key="register_button"):
        # basic checks
        if not email or not password or not confirm_password:
            st.error("All fields are required")
            return

        if not re.match(EMAIL_REGEX, email):
            st.error("Please enter a valid email address")
            return

        if password != confirm_password:
            st.error("Passwords do not match")
            return

        # create user
        user_id = create_user(email, password)
        if not user_id:
            st.error("Email already exists")
            return

        # generate OTP
        otp_code = f"{random.randint(100000, 999999)}"
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        set_otp(user_id, otp_code, expires_at)

        # send OTP email
        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            st.error(f"Failed to send OTP email: {e}")
            return

        # move to verification screen
        st.session_state["pending_verification_email"] = email
        st.success("OTP sent to your email. Please verify.")
        st.rerun()