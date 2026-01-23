from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------- CHATBOT SERVICES ----------------

from app.services.chatbot_service import (
    get_patient_labs,
    get_patient_abnormal,
    get_patient_critical,
    generate_ai_summary_background,
    get_ai_summary_from_cache,
    answer_user_question,
)

# ---------------- REPORT SERVICES ----------------

from app.services.report_service import (
    report_summary,
    report_by_lab,
    report_by_gender,
    unreviewed_critical,
    report_patient_risk_distribution,
    report_high_risk_patients,
    unreviewed_critical_summary,
    recent_critical_activity,
)

# ---------------- APP INIT ----------------

app = FastAPI(
    title="Lab Report Interpretation System",
    description="Human-like chatbot with AI-assisted lab summaries (Non-diagnostic)",
    version="1.2.1",
)

# ---------------- STATIC & TEMPLATES ----------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ---------------- DASHBOARD ----------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

# =====================================================
# BASIC CHATBOT DATA APIs
# =====================================================

@app.get("/chat/patient/{subject_id}")
def patient_labs(subject_id: int):
    return get_patient_labs(subject_id)


@app.get("/chat/patient/{subject_id}/abnormal")
def patient_abnormal(subject_id: int):
    return get_patient_abnormal(subject_id)


@app.get("/chat/patient/{subject_id}/critical")
def patient_critical(subject_id: int):
    return get_patient_critical(subject_id)


# =====================================================
# AI SUMMARY API (BACKGROUND + POLLING)
# =====================================================

@app.get("/chat/patient/{subject_id}/ai-summary")
def patient_ai_summary(subject_id: int, background_tasks: BackgroundTasks):
    """
    Returns AI summary if ready.
    Otherwise triggers background generation.
    """

    cached = get_ai_summary_from_cache(subject_id)

    if cached:
        return cached

    background_tasks.add_task(
        generate_ai_summary_background,
        subject_id
    )

    return {
        "message": (
            "Generating AI summary. "
            "This may take a few seconds. Please refresh shortly."
        )
    }


# =====================================================
# HUMAN-LIKE CHATBOT API (SAFE + CONFIDENCE SCORE)
# =====================================================

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question")


@app.post("/chat/patient/{subject_id}/ask")
def chat_with_patient(subject_id: int, payload: ChatRequest):
    """
    Rule-based chatbot with confidence score.
    Vector DB similarity score will replace this later.
    """

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # ---------------- GET ANSWER ----------------
    result = answer_user_question(
        subject_id=subject_id,
        question=question
    )

    # ---------------- NORMALIZE RESPONSE ----------------
    if isinstance(result, dict):
        answer_text = result.get("answer", "")
    else:
        answer_text = result

    # ---------------- CONFIDENCE SCORE ----------------
    confidence_score = 0.85

    answer_lower = answer_text.lower()

    if "consult a qualified healthcare professional" in answer_lower:
        confidence_score = 0.30
    elif "critical" in answer_lower:
        confidence_score = 0.95
    elif "abnormal" in answer_lower:
        confidence_score = 0.90

    return {
        "subject_id": subject_id,
        "question": question,
        "answer": answer_text,
        "confidence_score": round(confidence_score, 2)
    }


# =====================================================
# REPORTING APIs (DASHBOARD INSIGHTS)
# =====================================================

@app.get("/reports/summary")
def reports_summary():
    return report_summary()


@app.get("/reports/patient-risk")
def reports_patient_risk():
    return report_patient_risk_distribution()


@app.get("/reports/high-risk-patients")
def reports_high_risk_patients():
    return report_high_risk_patients()


@app.get("/reports/by-lab")
def reports_by_lab():
    return report_by_lab()


@app.get("/reports/by-gender")
def reports_by_gender():
    return report_by_gender()


@app.get("/reports/unreviewed-critical")
def reports_unreviewed_critical():
    return unreviewed_critical()


@app.get("/reports/unreviewed-critical-summary")
def reports_unreviewed_critical_summary():
    return unreviewed_critical_summary()


@app.get("/reports/recent-critical")
def reports_recent_critical():
    return recent_critical_activity()
