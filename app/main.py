# ==============================================================================
# LAB REPORT INTERPRETATION SYSTEM - CORE API
# ==============================================================================
# This FastAPI application serves as the backend for the Lab Report dashboard
# and the agentic chatbot. It integrates LangGraph for complex medical queries
# and Random Forest models for risk prediction.
# ==============================================================================

import json
import re
import sqlite3
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

# --- Internal Service Imports ---
from app.services.chatbot_service import (
    generate_ai_summary_background,
    get_ai_summary_from_cache,
)
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
from app.services.risk_service import (
    get_patient_risk_score,
    get_high_risk_patients,
    get_risk_distribution,
)
from database.db import get_connection

# --- AI & Agent Imports ---
from ai.agent import app as agent_app, AgentState
from ai.llm_client import LocalChatOllama as ChatOpenAI
from ai.risk_model import predict_patient_risk
from app.vector.chroma_store import search_documents
from app.queries.sql_templates import get_count_query

# --- App Initialization ---
app = FastAPI(
    title="Lab Report Interpretation System",
    description="Human-like chatbot with AI-assisted lab summaries (Non-diagnostic)",
    version="1.2.1",
)

# --- Static Files & Template Configuration ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# =====================================================
# DASHBOARD ROUTES
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """General lab reports and statistics dashboard"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/ml-dashboard", response_class=HTMLResponse)
def ml_dashboard(request: Request):
    """ML-powered patient risk prediction dashboard"""
    return templates.TemplateResponse(
        "ml-dashboard.html",
        {"request": request}
    )



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


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")




# ==============================================================================
# REPORTING APIs (DASHBOARD INSIGHTS)
# ==============================================================================

@app.get("/reports/summary")
def reports_summary():
    """Returns a categorical count of all lab results (NORMAL, ABNORMAL, etc.)."""
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


# =====================================================
# RISK PREDICTION APIs (ML MODEL)
# =====================================================

@app.get("/predict/patient/{subject_id}/risk")
def predict_patient_risk_score(subject_id: int):
    """
    Predict risk score for a specific patient using trained ML model
    Returns: risk_level (0-2), risk_label, confidence, probabilities
    """
    return get_patient_risk_score(subject_id)


@app.get("/predict/risk-distribution")
def predict_risk_distribution():
    """
    Get distribution of patients across risk levels
    """
    return get_risk_distribution()


@app.get("/predict/high-risk")
def predict_high_risk_patients(risk_level: int = 2, limit: int = 50):
    """
    Get patients with high risk scores
    risk_level: 1 = ABNORMAL or higher, 2 = CRITICAL only
    """
    return get_high_risk_patients(risk_level, limit)




# ==============================================================================
# AGENTIC CHATBOT API (LANGGRAPH + STREAMING)
# ==============================================================================

@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest):
    """
    OPTIMIZED Streaming LangGraph Agent with Fast-Path:
    - Fast-path for simple count queries (bypasses slow LLM intent classification)
    - LLM-driven Intent Classification (for complex queries)
    - RAG retrieval (Semantic)
    - SQL Aggregation (Safe)
    - ML Risk Prediction
    - Token Streaming
    """
    import re
    from database.db import get_connection
    from app.queries.sql_templates import get_count_query
    
    question = payload.question.strip()
    
    async def event_generator():
        lower_q = question.lower().strip()
        patient_match = re.search(r'\d{6,}', question)
        
        # ============================================================
        # FAST PATH 0: GREETINGS & SHORT INPUTS (0 LLM Calls)
        # ============================================================
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "hii", "hiii", "h", "help", "ok", "yes", "no"]
        if lower_q in greetings or len(lower_q) <= 2:
            yield f"data: {json.dumps({'type': 'token', 'content': 'Hello! I am your Lab Assistant. How can I help you with your lab results or medical questions today?'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return
        
        # ============================================================
        # FAST PATH 1: COUNT Intent (1 LLM Call)
        # ============================================================
        is_count = any(w in lower_q for w in ["how many", "total", "count", "number of"])
        if is_count and patient_match:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Processing query...'})}\n\n"
            subject_id = patient_match.group()
            status = "CRITICAL" if "critical" in lower_q else "ABNORMAL" if "abnormal" in lower_q else "NORMAL" if "normal" in lower_q else None
            
            entities = {"subject_id": subject_id}
            if status: entities["status"] = status
            sql, params = get_count_query(entities)
            
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, params)
            count = cur.fetchone()[0]
            conn.close()
            
            prompt = f"Patient {subject_id} has {count} {status if status else ''} laboratory results. Provide a brief, professional explanation."
            
            yield f"data: {json.dumps({'type': 'status', 'content': 'Generating answer...'})}\n\n"
            llm = ChatOpenAI(streaming=True)
            async for chunk in llm.astream([HumanMessage(content=prompt)]):
                if chunk.content: yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # ============================================================
        # FAST PATH 2: RISK Intent (1 LLM Call)
        # ============================================================
        is_risk = any(w in lower_q for w in ["risk", "prediction", "assessment"])
        if is_risk and patient_match:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Predicting patient risk...'})}\n\n"
            subject_id = int(patient_match.group())
            risk_data = predict_patient_risk(subject_id)
            
            if "error" in risk_data:
                prompt = f"Explain that we couldn't calculate risk for patient {subject_id} due to: {risk_data['error']}"
            else:
                prompt = f"Based on our Random Forest model, patient {subject_id} has a {risk_data['risk_label']} risk level ({risk_data['confidence']}% confidence). Explain this to the user."
            
            yield f"data: {json.dumps({'type': 'status', 'content': 'Generating clinical summary...'})}\n\n"
            llm = ChatOpenAI(streaming=True)
            async for chunk in llm.astream([HumanMessage(content=prompt)]):
                if chunk.content: yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # ============================================================
        # FAST PATH 3: RAG Knowledge (1 LLM Call)
        # ============================================================
        is_knowledge = any(lower_q.startswith(w) for w in ["what is", "define", "explain", "why is"])
        if is_knowledge and not patient_match:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Searching knowledge base...'})}\n\n"
            context_docs = search_documents(question, k=3)
            context_text = "\n".join([doc["content"] for doc in context_docs])
            
            prompt = f"Answer the following question using the context provided.\nContext: {context_text}\nQuestion: {question}"
            
            yield f"data: {json.dumps({'type': 'status', 'content': 'Generating explanation...'})}\n\n"
            llm = ChatOpenAI(streaming=True)
            async for chunk in llm.astream([HumanMessage(content=prompt)]):
                if chunk.content: yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return
        
        # ============================================================
        # NORMAL PATH: Full agent graph for complex queries
        # ============================================================
        state = {"question": question, "context": [], "numerical_result": "", "risk_data": {}}
        final_prompt = ""
        
        for event in agent_app.stream(state):
            for node_name, output in event.items():
                if node_name == "generate_response":
                    final_prompt = output["final_answer"]
                else:
                    yield f"data: {json.dumps({'type': 'status', 'content': f'Node {node_name} finished...'})}\n\n"

        if final_prompt:
            llm = ChatOpenAI(streaming=True)
            yield f"data: {json.dumps({'type': 'status', 'content': 'Synthesizing final answer...'})}\n\n"
            
            async for chunk in llm.astream([HumanMessage(content=final_prompt)]):
                if chunk.content:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

