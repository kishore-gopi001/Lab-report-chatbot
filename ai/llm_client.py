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
    - keep meaning intact
    """

    if not text:
        return SAFE_FALLBACK

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Soften unsafe language instead of deleting meaning
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

    return text if text else SAFE_FALLBACK


def generate_ai_summary(lab_results: list[dict]) -> str:
    """
    Generate a safe, non-diagnostic AI summary.
    Used ONLY for lab explanation, not diagnosis.
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
- If information is insufficient, say so politely
- Always advise clinician review

LAB FINDINGS:
{findings}

Provide a short explanation (2–3 sentences).
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 100,
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        return _clean_text(raw_text)

    except Exception:
        # Never break the API
        return SAFE_FALLBACK
