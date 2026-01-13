# auth/verify.py

import streamlit as st
from models.user import verify_otp


def verify_email():
    st.subheader("🔐 Verify Email")

    email = st.session_state.get("pending_verification_email")

    if not email:
        st.info("No email pending verification.")
        return

    st.write(f"Verification code sent to: **{email}**")

    otp = st.text_input(
        "Enter 6-digit OTP",
        max_chars=6,
        key="otp_input"
    )

    if st.button("Verify OTP", key="verify_otp_button"):
        if not otp:
            st.error("Please enter the OTP")
            return

        if verify_otp(email, otp):
            st.success("Email verified successfully! You can now log in.")
            del st.session_state["pending_verification_email"]
        else:
            st.error("Invalid or expired OTP")