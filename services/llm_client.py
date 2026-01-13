# services/llm_client.py

import os
import requests

# Optional OpenAI (kept for future switch)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ---------- CONFIG ----------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # default = ollama

# Ollama config
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"

# OpenAI config (future)
OPENAI_MODEL = "gpt-4o-mini"
_openai_client = None


# ---------- OLLAMA ----------
def _generate_with_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


# ---------- OPENAI (OPTIONAL) ----------
def _get_openai_client():
    global _openai_client

    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        _openai_client = OpenAI(api_key=api_key)

    return _openai_client


def _generate_with_openai(system_prompt: str, user_prompt: str) -> str:
    client = _get_openai_client()

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


# ---------- MAIN INTERFACE ----------
def generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Unified LLM interface.
    Switchable between Ollama and OpenAI.
    """
    if LLM_PROVIDER == "ollama":
        full_prompt = f"""
{system_prompt}

---

{user_prompt}
""".strip()

        return _generate_with_ollama(full_prompt)

    elif LLM_PROVIDER == "openai":
        return _generate_with_openai(system_prompt, user_prompt)

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
