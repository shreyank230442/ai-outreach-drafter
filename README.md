# 📧 AI-Assisted Outreach Drafting System

An AI-powered system that automates the drafting of personalized internship and job outreach emails using company-specific context and job descriptions.  
Emails are generated using LLMs and safely saved as **Gmail drafts** via OAuth for **human review and approval**.

---

## 🚀 Project Overview

Applying for internships and jobs often involves repetitive, manual email writing that lacks personalization.  
This system automates the **drafting (not sending)** of professional outreach emails by:

- Ingesting applicant data from Excel
- Researching companies via the web
- Cleaning noisy web data using LLMs
- Generating tailored outreach emails
- Saving drafts securely to Gmail

⚠️ **Emails are NEVER auto-sent.**  
All drafts must be manually reviewed and sent by the user.

---

## 🎯 Key Features

- 📂 Excel-based bulk outreach input
- 🌐 Automated company research
- 🧠 LLM-based noise cleaning & summarization
- ✉️ Professional, role-specific email generation
- 🔐 Secure Gmail Draft creation via OAuth
- 👤 Human-in-the-loop approval (ethical safeguard)
- 🧩 Supports multiple companies & email IDs
- 🖥️ Clean Streamlit UI

---

## 🧠 System Architecture

Excel File
↓
Excel Loader (Pandas)
↓
Web Research (DuckDuckGo)
↓
LLM Cleaning & Normalization (Groq + LangChain)
↓
Email Generation (Prompt Engineering)
↓
Streamlit UI (Edit & Review)
↓
Gmail Draft API (OAuth — NOT auto-send)


---

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit  
- **Backend**: Python  
- **LLM Provider**: Groq (LLaMA models)  
- **Prompt Framework**: LangChain  
- **Data Handling**: Pandas  
- **Web Search**: DuckDuckGo  
- **Email Drafting**: Gmail API (OAuth 2.0)

---

## 📂 Project Structure

ai-outreach-drafter/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── services/
│ ├── excel_loader.py
│ ├── web_research.py
│ ├── email_generator.py
│ ├── llm_engine.py
│ └── prompt_builder.py
│
├── gmail/
│ ├── gmail_auth.py
│ └── gmail_draft.py
│
├── assets/
│ └── styles.css
│
└── data/
├── input_excel/
└── research_cache/


---

## 📄 Excel Input Format

Your Excel file **must contain** the following columns:

| Column Name | Description |
|------------|-------------|
| email | Recipient email address |
| company | Company name |
| role | Job / Internship role |
| job_description | Job description text |
| your_skills | Your relevant skills |

Example:

| email | company | role | job_description | your_skills |
|------|--------|------|-----------------|------------|
| hr@xyz.com | Google | Backend Intern | ... | Python, SQL, Flask |

---

## ⚙️ How to Run Locally

### 1️⃣ Clone the Repository

git clone https://github.com/shreyank230442/ai-outreach-drafter.git
cd ai-outreach-drafter

### 2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Set Environment Variables
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here
(Refer .env.example)

### 5️⃣ Run the Application
streamlit run app.py

### 🔐 Gmail API Setup (Step-by-Step)

### Step 1: Enable Gmail API

Open Google Cloud Console

Enable Gmail API for your project

### Step 2: Configure OAuth Consent Screen (New UI)

Navigate to:
Google Auth Platform → OAuth overview

Fill:
App name
User support email
Developer contact email

### Step 3: Add Gmail Scope
Go to:
Data access → Add or remove scopes
Add:
https://www.googleapis.com/auth/gmail.compose

### Step 4: Add Test User
Go to:
Audience → Test users → Add user
Add your Gmail address.

### Step 5: Create OAuth Credentials
Credential type: Desktop App
Download credentials.json
Place it inside:
gmail/credentials.json

### Step 6: First-Time Authentication
Run the app
Generate outreach emails
Click Save Gmail Draft
Browser opens → Login → Allow access
token.json is auto-created

### 📌 Drafts are saved in Gmail → Drafts of the authenticated account.

⚠️ Common Errors & Fixes (Real Issues Faced)
❌ git is not recognized

✔ Git not installed
✔ Fix: Install Git from https://git-scm.com
 and restart terminal

❌ token.json not created

✔ OAuth never triggered
✔ Fix: Ensure Save Draft button is clicked and session state is preserved

❌ Error 403: access_denied

✔ Gmail account not added as Test User
✔ Fix: Add email under Audience → Test users

❌ Draft not visible in Gmail

✔ Checking wrong Gmail account
✔ Fix: Check the account used during OAuth login

❌ Save Draft button does nothing

✔ Streamlit reruns script on click
✔ Fix: Use st.session_state to persist generated emails

### 🔐 Security & Ethical Safeguards

❌ Emails are never auto-sent

👤 Manual human approval required

🔑 OAuth-based Gmail authentication

🔒 Secrets ignored using .gitignore

📄 Draft-only email creation


### 📌 Limitations

Web research may contain noise (handled via LLM cleaning)

Gmail OAuth limited to Test Users (no public verification)

Requires manual email review before sending

### 🌱 Future Enhancements

Resume auto-linking

JD–skill similarity scoring

Multiple email tone options

Bulk draft saving

Analytics dashboard

### 👤 Author

Shreyank B
Computer Science Engineering
AI & Software Systems Enthusiast
⭐ If you found this project useful, consider starring the repository!