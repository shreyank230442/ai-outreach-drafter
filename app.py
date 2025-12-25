import streamlit as st

from services.excel_loader import load_and_validate_excel
from services.web_research import research_company
from services.email_generator import (
    clean_company_research,
    generate_outreach_email
)
from gmail.gmail_draft import create_gmail_draft


# ---------- SESSION STATE ----------
if "generated_emails" not in st.session_state:
    st.session_state.generated_emails = []


# ---------- Page Config ----------
st.set_page_config(
    page_title="AI Outreach Drafter",
    page_icon="📧",
    layout="wide"
)

# ---------- Load CSS ----------
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.title("📧 AI-Assisted Outreach Drafting System")
st.subheader(
    "Generate personalized internship/job outreach emails — safely saved as Gmail drafts"
)

st.markdown("---")

# ---------- Upload Section ----------
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

        # ---------- Preview ----------
        st.markdown("### 👀 Preview Data")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        # ---------- STEP 3: COMPANY RESEARCH ----------
        st.markdown("### 🔍 Company Research (Optional Cache Warm-up)")

        if st.button("🔍 Research Companies"):
            companies = df["company"].unique()
            with st.spinner("Researching companies from the web..."):
                for company in companies:
                    research_company(company)
            st.success("✅ Company research completed and cached!")

        st.markdown("---")

        # ---------- STEP 4: GENERATE EMAILS (STORE IN STATE) ----------
        st.markdown("### ✉️ Generate Outreach Emails")

        if st.button("✉️ Generate Outreach Emails"):
            st.session_state.generated_emails = []

            for idx, row in df.iterrows():
                company = row["company"]
                role = row["role"]
                jd = row["job_description"]
                skills = row["your_skills"]
                to_email = row["email"]

                raw_research = research_company(company)["research_summary"]

                with st.spinner(f"Generating email for {company}..."):
                    clean_summary = clean_company_research(
                        company, raw_research
                    )

                    email = generate_outreach_email(
                        company=company,
                        role=role,
                        company_summary=clean_summary,
                        job_description=jd,
                        skills=skills
                    )

                st.session_state.generated_emails.append({
                    "idx": idx,
                    "company": company,
                    "role": role,
                    "to_email": to_email,
                    "summary": clean_summary,
                    "email": email
                })

            st.success("✅ Emails generated. Review & save drafts below.")

# ---------- STEP 5: RENDER EMAILS + SAVE TO GMAIL ----------
if st.session_state.generated_emails:
    st.markdown("---")
    st.markdown("### 📬 Generated Emails & Gmail Draft Saving")

    saved_count = 0

    for item in st.session_state.generated_emails:
        idx = item["idx"]
        company = item["company"]
        role = item["role"]

        st.subheader(f"📌 {company} — {role}")

        st.markdown("**🧠 Cleaned Company Summary:**")
        st.info(item["summary"])

        edited_email = st.text_area(
            f"Email draft for {company}",
            item["email"],
            height=260,
            key=f"email_text_{idx}"
        )

        subject = f"Application for {role} at {company}"

        if st.button(
            f"💾 Save Gmail Draft – {company}",
            key=f"save_draft_{idx}"
        ):
            create_gmail_draft(
                to_email=item["to_email"],
                subject=subject,
                body=edited_email
            )
            saved_count += 1
            st.success("✅ DRAFT SUCCESSFULLY SAVED TO GMAIL")

        st.markdown("---")

    if saved_count > 0:
        st.toast(
            f"📬 {saved_count} Gmail draft(s) saved successfully!",
            icon="✅"
        )
