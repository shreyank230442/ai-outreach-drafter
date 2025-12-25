from langchain_core.prompts import PromptTemplate

# 1️⃣ CLEAN COMPANY CONTEXT PROMPT
COMPANY_CLEAN_PROMPT = PromptTemplate(
    input_variables=["company", "raw_research"],
    template="""
You are an AI assistant extracting ONLY relevant hiring-related information.

Company name: {company}

Raw web research text:
{raw_research}

TASK:
Extract a concise, factual company summary STRICTLY in this format:

- Industry:
- What the company does (1 sentence):
- Key technology / domain focus:
- Why this company is relevant for a job applicant:

RULES:
- Do NOT add facts not present
- Do NOT include history, NGOs, funding, or academic papers
- Keep it under 120 words total
"""
)

# 2️⃣ OUTREACH EMAIL PROMPT
EMAIL_GENERATION_PROMPT = PromptTemplate(
    input_variables=[
        "company",
        "role",
        "company_summary",
        "job_description",
        "skills"
    ],
    template="""
You are a final-year engineering student applying for an internship/job.

Write a PROFESSIONAL, FORMAL outreach email.

Company: {company}
Role: {role}

Company context:
{company_summary}

Job description:
{job_description}

My skills:
{skills}

EMAIL RULES:
- 120–160 words
- Formal but confident tone
- Mention ONLY 2–3 relevant skills
- No exaggeration
- No buzzwords
- End with a polite call to action
- Do NOT mention "AI", "LLM", or automation

Output ONLY the email body (no subject).
"""
)
