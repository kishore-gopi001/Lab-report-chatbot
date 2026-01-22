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
)

# ---------------- APP INIT ----------------

app = FastAPI(
    title="Lab Report Interpretation System",
    description="Human-like chatbot with AI-assisted lab summaries (Non-diagnostic)",
    version="1.0.0",
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

# ---------------- BASIC CHATBOT DATA APIs ----------------

@app.get("/chat/patient/{subject_id}")
def patient_labs(subject_id: int):
    return get_patient_labs(subject_id)


@app.get("/chat/patient/{subject_id}/abnormal")
def patient_abnormal(subject_id: int):
    return get_patient_abnormal(subject_id)


@app.get("/chat/patient/{subject_id}/critical")
def patient_critical(subject_id: int):
    return get_patient_critical(subject_id)


# ---------------- AI SUMMARY API ----------------

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


# ---------------- HUMAN-LIKE CHATBOT API ----------------

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question")


@app.post("/chat/patient/{subject_id}/ask")
def chat_with_patient(subject_id: int, payload: ChatRequest):
    """
    Human-like chatbot:
    - Answers using DB facts
    - No hallucination
    - Polite out-of-scope replies
    """

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    response = answer_user_question(
        subject_id=subject_id,
        question=question
    )

    return {
        "subject_id": subject_id,
        "question": question,
        "answer": response
    }


# ---------------- REPORTING APIs ----------------

@app.get("/reports/summary")
def reports_summary():
    return report_summary()


@app.get("/reports/by-lab")
def reports_by_lab():
    return report_by_lab()


@app.get("/reports/by-gender")
def reports_by_gender():
    return report_by_gender()


@app.get("/reports/unreviewed-critical")
def reports_unreviewed_critical():
    return unreviewed_critical()
