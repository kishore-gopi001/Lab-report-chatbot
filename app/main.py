from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#ai-related imports
from fastapi import BackgroundTasks
from app.services.chatbot_service import (
    generate_ai_summary_background,
    get_ai_summary_from_cache,
)

# ---------------- SERVICE IMPORTS ----------------

from app.services.chatbot_service import (
    get_patient_labs,
    get_patient_abnormal,
    get_patient_critical
)

from app.services.report_service import (
    report_summary,
    report_by_lab,
    report_by_gender,
    unreviewed_critical,
)

# ---------------- APP INIT ----------------

app = FastAPI(
    title="Lab Report Interpretation System",
    description="Chatbot + Reporting APIs (Non-diagnostic)",
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

# ---------------- CHATBOT APIs ----------------

@app.get("/chat/patient/{subject_id}")
def patient_labs(subject_id: int):
    return get_patient_labs(subject_id)


@app.get("/chat/patient/{subject_id}/abnormal")
def patient_abnormal(subject_id: int):
    return get_patient_abnormal(subject_id)


@app.get("/chat/patient/{subject_id}/critical")
def patient_critical(subject_id: int):
    return get_patient_critical(subject_id)





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

#---------------- AI SUMMARY API ----------------

@app.get("/chat/patient/{subject_id}/ai-summary")
def patient_ai_summary(subject_id: int, background_tasks: BackgroundTasks):
    cached = get_ai_summary_from_cache(subject_id)

    if cached:
        return cached

    background_tasks.add_task(
        generate_ai_summary_background,
        subject_id
    )

    return {
        "message": "AI summary is being generated. Please refresh shortly."
    }
