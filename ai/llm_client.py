import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "tinyllama"

def generate_ai_summary(lab_results: list[dict]) -> str:
    if not lab_results:
        return "No abnormal or critical lab findings were detected."

    findings = "\n".join(
        f"- {lab['test_name']} is {lab['status']} "
        f"(value: {lab['value']} {lab['unit']})"
        for lab in lab_results
    )

    prompt = f"""
You are a clinical explanation assistant.

Rules:
- Do NOT diagnose diseases
- Do NOT recommend treatments
- Use cautious language
- Encourage clinician review

Lab findings:
{findings}

Provide a short explanation (3–4 sentences).
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 120,
            "temperature": 0.2
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )
    response.raise_for_status()

    return response.json().get("response", "").strip() or (
        "Several lab values are outside expected ranges. "
        "Clinical review is advised."
    )
