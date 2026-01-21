from fastapi import FastAPI # type: ignore

from app.services.chatbot_service import (
    get_patient_labs,
    get_patient_abnormal,
    get_patient_critical
)

from app.services.report_service import (
    report_summary,
    report_by_lab,
    report_by_gender,
    unreviewed_critical
)

app = FastAPI(
    title="Lab Report Interpretation System",
    description="Chatbot + Reporting APIs (Non-diagnostic)",
    version="1.0"
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
