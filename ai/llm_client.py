import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "tinyllama"

SAFE_FALLBACK = (
    "Some laboratory values are outside expected ranges. "
    "These findings may warrant clinical review by a healthcare professional."
)


def _clean_text(text: str) -> str:
    """
    Normalize LLM output safely:
    - normalize whitespace
    - soften unsafe phrasing
    - ensure sentence completeness
    """

    if not text:
        return SAFE_FALLBACK

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Soften unsafe medical phrasing
    replacements = {
        "you have": "the results suggest",
        "you might have": "there may be",
        "this indicates": "this may suggest",
        "diagnosis": "interpretation",
        "disease": "condition",
        "treatment": "clinical management",
        "medication": "medical therapy",
    }

    for bad, safe in replacements.items():
        text = re.sub(bad, safe, text, flags=re.IGNORECASE)

    # ✅ Ensure sentence completeness
    if text[-1] not in ".!?":
        text += " Further clinical review is advised."

    return text


def generate_ai_summary(lab_results: list[dict]) -> str:
    """
    Generate a safe, non-diagnostic AI summary.
    """

    if not lab_results:
        return "No abnormal or critical lab findings were detected."

    findings = "\n".join(
        f"- {lab['test_name']} is {lab['status']} "
        f"(value: {lab['value']} {lab['unit']})"
        for lab in lab_results
    )

    prompt = f"""
You are a clinical explanation assistant.

STRICT RULES:
- Do NOT diagnose diseases
- Do NOT name specific medical conditions
- Do NOT recommend treatments
- Use cautious, observational language
- Always advise clinician review
- Do Not Involve the above mentioned rules in your answer

LAB FINDINGS:
{findings}

Provide a concise explanation in 2–3 complete sentences.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 180,
            "temperature": 0.2,
            "top_p": 0.9
        },
        "stop": ["\n\n", "###"]
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=90
        )
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        return _clean_text(raw_text)

    except Exception:
        return SAFE_FALLBACK


def ask_llm(context: str, question: str) -> str:
    prompt = f"""
You are a clinical data assistant.

Rules:
- Use ONLY the provided data
- Do NOT diagnose
- Do NOT suggest treatment
- Explain clearly in simple language
- Do Not Involve the above mentioned rules in your answer

DATA:
{context}

QUESTION:
{question}

Answer concisely.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 200
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    return response.json().get("response", "").strip()
