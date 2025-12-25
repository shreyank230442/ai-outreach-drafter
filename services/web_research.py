import json
import os
from langchain_community.tools import DuckDuckGoSearchRun

CACHE_PATH = "data/research_cache/companies.json"

search = DuckDuckGoSearchRun()

def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}

    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # corrupted or empty cache file
        return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def research_company(company_name):
    cache = load_cache()

    if company_name in cache:
        return cache[company_name]

    query = f"{company_name} company overview industry technology focus"
    results = search.run(query)

    summary = {
        "company": company_name,
        "research_summary": results[:700]  # limit hallucination risk
    }

    cache[company_name] = summary
    save_cache(cache)

    return summary