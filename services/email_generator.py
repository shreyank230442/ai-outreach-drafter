# services/email_generator.py

from services.llm_client import generate_text


# -------------------------------
# EXISTING FUNCTIONS (UNCHANGED)
# -------------------------------

def clean_company_research(company: str, raw_text: str) -> str:
    system_prompt = """
You are an assistant summarizing company research for email personalization.
"""

    user_prompt = f"""
Company: {company}

Raw Research:
{raw_text}

Task:
- Extract only the most relevant information
- Focus on mission, product, or hiring relevance
- Keep it under 3 short sentences
- Do NOT include fluff or marketing language

Return only the cleaned summary.
"""

    return generate_text(system_prompt, user_prompt)


def generate_outreach_email(
    company: str,
    role: str,
    company_summary: str,
    job_description: str,
    skills: str,
    personal_context: str = ""
) -> str:
    system_prompt = """
You are a professional career outreach assistant.

Write a calm, concise, and highly professional cold email
for an internship or job opportunity.

STRICT RULES:
- DO NOT sound enthusiastic or emotional
- DO NOT use phrases like:
  "I'm excited", "I'd love", "thrilled", "impressed by"
- Tone must be confident, neutral, and respectful
- Sound like a serious candidate, not a fan
- Avoid marketing language
- Avoid flattery
- Avoid exaggeration
- Keep under 150 words
- Write in formal business English
"""

    user_prompt = f"""
Company: {company}
Role: {role}

Company Context:
{company_summary}

Job Description (for understanding only):
{job_description}

Candidate Skills (high-level):
{skills}
"""

    if personal_context.strip():
        user_prompt += f"""

Relevant Personal Background (use selectively):
{personal_context}
"""

    user_prompt += """

Write a professional outreach email that:
- Explains interest in the role and company
- Shows alignment between candidate background and role
- Mentions 1–2 relevant strengths or experiences naturally
- Politely asks about internship/job opportunities or next steps

Return ONLY the email body. No subject line.
"""

    return generate_text(system_prompt, user_prompt)


# --------------------------------
# NEW: FOLLOW-UP GENERATION LOGIC
# --------------------------------

def generate_followup_email(
    company: str,
    role: str,
    followup_type: str
) -> str:
    """
    followup_type must be one of:
    - "after_5_minutes"
    - "after_5_days"
    - "after_10_days"
    """

    system_prompt = """
You are a professional career outreach assistant.

Write a short, calm, and strictly professional follow-up email.

STRICT RULES:
- DO NOT sound enthusiastic or emotional
- DO NOT use phrases like:
  "I'm excited", "I'd love", "thrilled", "just checking in"
- Tone must be neutral, respectful, and professional
- Do NOT pressure the recipient
- Do NOT repeat the full original email
- Keep under 80 words
- Formal business English only
"""

    timing_context = {
        "after_5_minutes": "a short time ago",
        "after_5_days": "earlier this week",
        "after_10_days": "some time ago"
    }

    user_prompt = f"""
Company: {company}
Role: {role}

Context:
The candidate previously sent a professional outreach email {timing_context[followup_type]}.

Task:
Write a polite follow-up email that:
- Briefly references the previous message
- Reiterates interest in the role
- Politely asks if there are any updates or next steps
- Does NOT sound impatient or repetitive

Return ONLY the email body. No subject line.
"""

    return generate_text(system_prompt, user_prompt)


# --------------------------------
# NEW: MASTER FUNCTION (STEP 1)
# --------------------------------

def generate_outreach_with_followups(
    company: str,
    role: str,
    company_summary: str,
    job_description: str,
    skills: str,
    personal_context: str = ""
) -> dict:
    """
    Generates:
    - Initial outreach email
    - Follow-up after 5 minutes (demo)
    - Follow-up after 5 days
    - Follow-up after 10 days
    """

    initial_email = generate_outreach_email(
        company=company,
        role=role,
        company_summary=company_summary,
        job_description=job_description,
        skills=skills,
        personal_context=personal_context
    )

    followup_5_min = generate_followup_email(
        company=company,
        role=role,
        followup_type="after_5_minutes"
    )

    followup_5_days = generate_followup_email(
        company=company,
        role=role,
        followup_type="after_5_days"
    )

    followup_10_days = generate_followup_email(
        company=company,
        role=role,
        followup_type="after_10_days"
    )

    return {
        "initial_email": initial_email,
        "followups": {
            "after_5_minutes": followup_5_min,
            "after_5_days": followup_5_days,
            "after_10_days": followup_10_days
        }
    }
