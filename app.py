import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import streamlit as st
import requests

from auth.login import login
from auth.register import register
from auth.session import (
    is_authenticated,
    logout_user,
    get_current_user
)
from gmail.gmail_auth import authorize_gmail_and_get_tokens
from models.gmail_credentials import save_gmail_credentials, has_gmail_connected
from services.excel_loader import load_and_validate_excel
from services.web_research import research_company
from services.email_generator import (
    clean_company_research,
    generate_outreach_with_followups
)
from gmail.gmail_draft import create_gmail_draft
from firebase_init import init_firebase
init_firebase()

# 🔹 Profile + RAG imports
from models.profile import init_profile_table, upsert_profile, get_profile
from rag.resume_loader import extract_text_from_pdf
from rag.indexer import build_user_index
from rag.retriever import retrieve_context
if "generated_emails" not in st.session_state:
    st.session_state.generated_emails = []


# ---------- CLOUD FUNCTION ----------
CLOUD_REGISTER_URL = "https://us-central1-ai-outreach-followups.cloudfunctions.net/registerOutreach"

from datetime import datetime, timedelta, timezone

def register_outreach_in_cloud(
    user_id: str,
    company: str,
    role: str,
    to_email: str,
    gmail_thread_id: str,
    followups: dict
):
    now = datetime.now(timezone.utc)

    payload = {
        "user_email": user_id,
        "to_email": to_email,
        "company": company,
        "role": role,
        "thread_id": gmail_thread_id,

        # 🔥 follow_ups MUST be a LIST of OBJECTS
        "follow_ups": [
            {
                "type": "5_min",
                "scheduled_at": (now + timedelta(minutes=5)).isoformat(),
                "body": followups["after_5_minutes"],
                "cancelled": False,
                "saved_to_drafts": False
            },
            {
                "type": "5_day",
                "scheduled_at": (now + timedelta(days=5)).isoformat(),
                "body": followups["after_5_days"],
                "cancelled": False,
                "saved_to_drafts": False
            },
            {
                "type": "10_day",
                "scheduled_at": (now + timedelta(days=10)).isoformat(),
                "body": followups["after_10_days"],
                "cancelled": False,
                "saved_to_drafts": False
            }
        ]
    }

    response = requests.post(
        CLOUD_REGISTER_URL,
        json=payload,
        timeout=10
    )
    response.raise_for_status()

# ---------- INIT DB ----------
init_profile_table()


# ---------- AUTH GATE ----------
if not is_authenticated():
    st.set_page_config(
        page_title="AI Outreach Drafter",
        page_icon="📧",
        layout="centered"
    )

    st.title("📧 AI-Assisted Outreach Drafting System")

    from auth.verify import verify_email
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        if "pending_verification_email" in st.session_state:
            verify_email()
        else:
            register()

    st.stop()


# ---------- CURRENT USER ----------
user_id = get_current_user()


# ===================== SIDEBAR: USER PROFILE =====================
with st.sidebar:
    st.header("👤 My Profile")

    existing_profile = get_profile(user_id)

    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    skills = st.text_area(
        "Your Skills",
        value=existing_profile["skills"] if existing_profile else ""
    )

    projects = st.text_area(
        "Your Projects",
        value=existing_profile["projects"] if existing_profile else ""
    )

    tone = st.selectbox(
        "Preferred Email Tone",
        ["Professional", "Friendly", "Concise"],
        index=(
            ["Professional", "Friendly", "Concise"].index(existing_profile["tone"])
            if existing_profile and existing_profile["tone"]
            else 0
        )
    )

    if st.button("💾 Save Profile"):
        resume_text = ""

        if resume_file:
            resume_text = extract_text_from_pdf(resume_file)
        elif existing_profile:
            resume_text = existing_profile["resume_text"]

        upsert_profile(
            user_id=user_id,
            resume_text=resume_text,
            skills=skills,
            projects=projects,
            tone=tone
        )

        documents = []
        if resume_text:
            documents.append(resume_text)
        if skills:
            documents.append(f"Skills: {skills}")
        if projects:
            documents.append(f"Projects: {projects}")

        if documents:
            build_user_index(user_id, documents)

        st.success("✅ Profile saved & memory updated")

    # ---------- GMAIL CONNECTION ----------
    st.markdown("---")
    st.subheader("📬 Gmail Connection")

    if has_gmail_connected(user_id):
        st.success("✅ Gmail connected")
    else:
        if st.button("🔗 Connect Gmail"):
            with st.spinner("Authorizing Gmail..."):
                creds = authorize_gmail_and_get_tokens()
                save_gmail_credentials(user_id, creds)

            st.success("✅ Gmail connected successfully")
            st.rerun()



# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Outreach Drafter",
    page_icon="📧",
    layout="wide"
)


# ---------- HEADER ----------
st.title("📧 AI-Assisted Outreach Drafting System")
st.subheader(
    "Generate personalized internship/job outreach emails — safely saved as Gmail drafts"
)

if st.button("Logout"):
    logout_user()
    st.rerun()

st.markdown("---")


# ---------- UPLOAD SECTION ----------
st.markdown("### 📂 Upload Excel File")

uploaded_file = st.file_uploader(
    "Upload Excel (.xlsx) with outreach data",
    type=["xlsx"]
)


# ---------- MAIN FLOW ----------
if uploaded_file:
    with st.spinner("Validating Excel file..."):
        df, error = load_and_validate_excel(uploaded_file)

    if error:
        st.error(f"❌ {error}")
    else:
        st.success("✅ Excel file validated successfully!")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        st.markdown("### 🔍 Company Research (Optional Cache Warm-up)")
        if st.button("🔍 Research Companies"):
            companies = df["company"].unique()
            with st.spinner("Researching companies..."):
                for company in companies:
                    research_company(company)
            st.success("✅ Company research completed")

        st.markdown("---")

        st.markdown("### ✉️ Generate Outreach Emails")

        if st.button("✉️ Generate Outreach Emails"):
            st.session_state.generated_emails = []

            for idx, row in df.iterrows():
                company = row["company"]
                role = row["role"]
                jd = row["job_description"]
                skills_input = row["your_skills"]
                to_email = row["email"]

                raw_research = research_company(company)["research_summary"]

                with st.spinner(f"Generating emails for {company}..."):
                    clean_summary = clean_company_research(company, raw_research)

                    personal_context = retrieve_context(
                        user_id=user_id,
                        query=f"Relevant experience for {role}"
                    )

                    generated = generate_outreach_with_followups(
                        company=company,
                        role=role,
                        company_summary=clean_summary,
                        job_description=jd,
                        skills=skills_input,
                        personal_context=personal_context
                    )

                st.session_state.generated_emails.append({
                    "idx": idx,
                    "company": company,
                    "role": role,
                    "to_email": to_email,
                    "summary": clean_summary,
                    "initial_email": generated["initial_email"],
                    "followups": generated["followups"]
                })

            st.success("✅ Emails and follow-ups generated. Review & save drafts below.")


# ---------- SAVE GMAIL DRAFTS ----------
if st.session_state.generated_emails:
    st.markdown("---")
    st.markdown("### 📬 Generated Emails & Gmail Draft Saving")

    saved_count = 0

    for item in st.session_state.generated_emails:
        idx = item["idx"]

        st.subheader(f"📌 {item['company']} — {item['role']}")
        st.info(item["summary"])

        edited_email = st.text_area(
            f"Email draft for {item['company']}",
            item["initial_email"],
            height=260,
            key=f"email_text_{idx}"
        )

        subject = f"Application for {item['role']} at {item['company']}"

        if st.button(
            f"💾 Save Gmail Draft – {item['company']}",
            key=f"save_draft_{idx}"
        ):
            draft_id, thread_id = create_gmail_draft(
                to_email=item["to_email"],
                subject=subject,
                body=edited_email
            )

            register_outreach_in_cloud(
                user_id=user_id,
                company=item["company"],
                role=item["role"],
                to_email=item["to_email"],
                gmail_thread_id=thread_id,
                followups=item["followups"]
            )

            saved_count += 1
            st.success("✅ Draft saved & follow-ups scheduled in cloud")

        st.markdown("---")

    if saved_count > 0:
        st.toast(
            f"📬 {saved_count} outreach(s) registered successfully!",
            icon="✅"
        )
