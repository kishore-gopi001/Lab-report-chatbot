"""
Optimized streaming endpoint with fast-path for count queries
"""
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from ai.agent import app as agent_app, AgentState
from ai.llm_client import LocalChatOllama as ChatOpenAI
from langchain_core.messages import HumanMessage
import json
import re
import sqlite3

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User question")

async def optimized_chat_stream(question: str):
    """
    Optimized streaming with fast-path for simple count queries
    """
    lower_q = question.lower()
    
    # FAST PATH: Detect simple count queries
    is_count_query = any(word in lower_q for word in ["how many", "total", "count", "number of"])
    patient_id_match = re.search(r'\d{6,}', question)
    
    if is_count_query and patient_id_match:
        # FAST PATH: Skip LLM intent classification, go straight to SQL
        yield f"data: {json.dumps({'type': 'status', 'content': 'Processing query...'})}\\n\\n"
        
        # Extract entities
        subject_id = patient_id_match.group()
        status = None
        if "critical" in lower_q:
            status = "CRITICAL"
        elif "abnormal" in lower_q:
            status = "ABNORMAL"
        elif "normal" in lower_q:
            status = "NORMAL"
        
        # Execute SQL
        conn = sqlite3.connect("database/lab_results.db")
        cur = conn.cursor()
        
        query = "SELECT COUNT(*) FROM lab_interpretations WHERE subject_id = ?"
        params = [subject_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        cur.execute(query, tuple(params))
        count = cur.fetchone()[0]
        conn.close()
        
        # Generate response
        status_text = f"{status} " if status else ""
        prompt = f"Patient {subject_id} has {count} {status_text}laboratory results. Provide a brief, professional explanation of what this means."
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'Generating answer...'})}\\n\\n"
        
        # Stream LLM response
        llm = ChatOpenAI(streaming=True)
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\\n\\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\\n\\n"
        return
    
    # NORMAL PATH: Full agent graph
    state = {"question": question, "context": [], "numerical_result": "", "risk_data": {}}
    final_prompt = ""
    
    for event in agent_app.stream(state):
        for node_name, output in event.items():
            if node_name == "generate_response":
                final_prompt = output["final_answer"]
            else:
                yield f"data: {json.dumps({'type': 'status', 'content': f'Node {node_name} finished...'})}\\n\\n"
    
    if final_prompt:
        llm = ChatOpenAI(streaming=True)
        yield f"data: {json.dumps({'type': 'status', 'content': 'Synthesizing final answer...'})}\\n\\n"
        
        async for chunk in llm.astream([HumanMessage(content=final_prompt)]):
            if chunk.content:
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\\n\\n"
    
    yield f"data: {json.dumps({'type': 'done'})}\\n\\n"
