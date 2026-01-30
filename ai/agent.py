import os
import operator
from typing import Annotated, Any, Dict, List, TypedDict, Union

from ai.llm_client import LocalChatOllama as ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

from app.vector.chroma_store import search_documents
from ai.risk_model import predict_patient_risk
from database.db import get_connection
import pandas as pd

# ==============================================================================
# PROTOTYPE HEALTHCARE AGENT (LANGGRAPH)
# ==============================================================================
# This module implements a state-driven chatbot that can:
# 1. Categorize User Intent (RAG vs SQL Aggregation vs ML Prediction)
# 2. Retrieve Knowledge (from ChromaDB)
# 3. Aggregate Lab Data (from SQLite)
# 4. Predict Clinical Risk (via Random Forest)
# 5. Synthesize a streaming-friendly response.
# ==============================================================================

class AgentState(TypedDict):
    """
    Maintains the state across the LangGraph workflow.
    """
    question: str
    intent: str  # One of: "rag", "count", "risk", "unsupported"
    entities: Dict[str, Any]  # Extracted entities like subject_id or test name
    context: List[str]  # Chunks retrieved from RAG
    numerical_result: Union[int, float, None, str]  # Results from SQL queries
    risk_data: Dict[str, Any]  # Output from the ML risk model
    final_answer: str  # The prompt prepared for the final LLM synthesis

# LLM Initialize (LocalChatOllama ignores model param, uses tinyllama from llm_client.py)
llm = ChatOpenAI(temperature=0)

### Nodes ###

def categorize_intent(state: AgentState):
    """
    LLM-driven intent classification.
    """
    prompt = f"""Analyze the user's query and categorize it into exactly one of these intents:
1. 'rag': Clinical knowledge retrieval, explaining medical terms, or detailed patient lab lookups.
2. 'count': Quantitative/statistical questions about lab result counts or patient populations.
3. 'risk': Clinical risk level assessment for a specific patient.
4. 'unsupported': General chat, social greetings, jokes, non-medical advice, or anything unrelated to clinical lab records.

Examples of 'unsupported': "Hi", "Tell me a joke", "What's the weather?", "Who are you?", "H".

Return JSON only: {{"intent": "...", "entities": {{"subject_id": "...", "test": "...", "status": "..."}}}}

Query: {state['question']}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    import json
    import re
    
    content = response.content.strip()
    
    # A bit simplified JSON extraction
    try:
        # Try to find JSON block if it's wrapped in markers
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)
    except Exception:
        pass
        
    # Post-processing heuristics to fix common local model JSON issues
    data = data if 'data' in locals() else {"intent": "unsupported", "entities": {}}
    if "entities" not in data: data["entities"] = {}
    
    lower_content = content.lower()
    lower_question = state['question'].lower()
    
    # 1. Force RAG for "show", "list", "summarize"
    if any(word in lower_question for word in ["show", "list", "summarize", "what are", "results for"]):
        data["intent"] = "rag"
    
    # 2. Extract/Fix Status
    if "critical" in lower_question:
        data["entities"]["status"] = "CRITICAL"
    elif "abnormal" in lower_question:
        data["entities"]["status"] = "ABNORMAL"
    elif "normal" in lower_question:
        data["entities"]["status"] = "NORMAL"
        
    # 3. Extract/Fix subject_id
    id_match = re.search(r'\d{6,}', lower_question)
    if id_match:
        data["entities"]["subject_id"] = id_match.group()

    return {
        "intent": data.get("intent", "unsupported"),
        "entities": data.get("entities", {})
    }

def retrieve_knowledge(state: AgentState):
    """
    RAG Node: Retrieve semantically relevant chunks from ChromaDB with patient filtering.
    """
    query = state['question']
    entities = state.get('entities', {})
    subject_id = entities.get('subject_id')
    
    where_filter = None
    if subject_id:
        where_filter = {"subject_id": str(subject_id)}
        
    results = search_documents(query, k=5, where=where_filter)
    context = [doc['content'] for doc in results]
    return {"context": context}

def execute_aggregation(state: AgentState):
    """
    Aggregator Node: Runs optimized SQL aggregation on the database.
    Uses the centralized get_connection for thread-safe access.
    """
    entities = state['entities']
    conn = get_connection()
    cur = conn.cursor()
    
    # Safe filtering based on entities using SQL
    status = entities.get("status", "").upper()
    subject_id = entities.get("subject_id")
    
    query = "SELECT COUNT(*) FROM lab_interpretations"
    params = []
    where_clauses = []
    
    if status:
        where_clauses.append("status = ?")
        params.append(status)
    if subject_id:
        where_clauses.append("subject_id = ?")
        params.append(subject_id)
        
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    cur.execute(query, tuple(params))
    result = cur.fetchone()[0]
    
    msg = f"Found {result} records"
    if status: msg += f" with status {status}"
    if subject_id: msg += f" for patient {subject_id}"
    msg += "."
    
    conn.close()
    return {"numerical_result": msg}

def predict_risk(state: AgentState):
    """
    Risk Node: Calls the prediction model.
    """
    subject_id = state['entities'].get("subject_id")
    if not subject_id:
        # Try to extract subject_id from question if LLM missed it
        import re
        match = re.search(r'\d+', state['question'])
        if match:
            subject_id = int(match.group())
            
    if subject_id:
        risk_profile = predict_patient_risk(int(subject_id))
        return {"risk_data": risk_profile}
    else:
        return {"risk_data": {"error": "Patient ID not provided for risk assessment."}}

def generate_response(state: AgentState):
    """
    Synthesizes the final answer using retrieved data.
    """
    context_str = "\n".join(state.get('context', []))
    num_res = state.get('numerical_result', "")
    risk_res = str(state.get('risk_data', ""))
    
    # If it's a non-clinical/unsupported intent OR a short query with no context/data, return a friendly fallback.
    if state.get("intent") == "unsupported" or (not state.get("context") and not state.get("numerical_result") and not state.get("risk_data")):
        if len(state["question"]) < 10:
             return {"final_answer": "Hello! I specialized in medical lab records and clinical knowledge. How can I help you today? You can ask me to explain lab terms, check patient results, or provide risk assessments."}
        return {"final_answer": "I'm sorry, I couldn't find any specific clinical data for that query. I am a specialized assistant for medical lab records. Could you please provide more details, a patient ID, or ask a question about lab tests?"}

    prompt = f"""Base on the following data, provide a clear, professional, and explainable answer.
Query: {state['question']}

Context (Healthcare Knowledge):
{context_str}

Aggregation Result: {num_res}
Risk Prediction: {risk_res}

Explain the 'why' if providing a risk score or count. If it's a lab result, interpret what it means for the patient's health based on the context.

Answer:"""
    
    # The final prompt is passed back to main.py to be used in the streaming response generator.
    return {"final_answer": prompt}

### Build Graph ###
# ... (rest of the graph code remains same, just updating generate_response definition)

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("categorize_intent", categorize_intent)
workflow.add_node("retrieve_knowledge", retrieve_knowledge)
workflow.add_node("execute_aggregation", execute_aggregation)
workflow.add_node("predict_risk", predict_risk)
workflow.add_node("generate_response", generate_response)

# Routing Logic
def route_intent(state: AgentState):
    intent = state['intent']
    if intent == "rag":
        return "retrieve_knowledge"
    elif intent == "count":
        return "execute_aggregation"
    elif intent == "risk":
        return "predict_risk"
    else:
        return "generate_response"

# Define Edges
workflow.set_entry_point("categorize_intent")

workflow.add_conditional_edges(
    "categorize_intent",
    route_intent,
    {
        "retrieve_knowledge": "retrieve_knowledge",
        "execute_aggregation": "execute_aggregation",
        "predict_risk": "predict_risk",
        "generate_response": "generate_response"
    }
)

workflow.add_edge("retrieve_knowledge", "generate_response")
workflow.add_edge("execute_aggregation", "generate_response")
workflow.add_edge("predict_risk", "generate_response")
workflow.add_edge("generate_response", END)

# Compile
app = workflow.compile()
