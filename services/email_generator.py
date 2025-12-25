from services.llm_engine import get_llm
from services.prompt_builder import (
    COMPANY_CLEAN_PROMPT,
    EMAIL_GENERATION_PROMPT
)

def clean_company_research(company, raw_research):
    llm = get_llm(temperature=0.2)
    chain = COMPANY_CLEAN_PROMPT | llm
    return chain.invoke({
        "company": company,
        "raw_research": raw_research
    }).content


def generate_outreach_email(
    company,
    role,
    company_summary,
    job_description,
    skills
):
    llm = get_llm(temperature=0.4)
    chain = EMAIL_GENERATION_PROMPT | llm

    return chain.invoke({
        "company": company,
        "role": role,
        "company_summary": company_summary,
        "job_description": job_description,
        "skills": skills
    }).content
