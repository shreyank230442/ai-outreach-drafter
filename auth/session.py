# auth/session.py
import streamlit as st

def login_user(user_id: str):
    st.session_state["user_id"] = user_id

def logout_user():
    st.session_state.pop("user_id", None)

def get_current_user():
    return st.session_state.get("user_id")

def is_authenticated():
    return "user_id" in st.session_state