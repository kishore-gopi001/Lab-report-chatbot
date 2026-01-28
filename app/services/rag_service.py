# app/services/rag_service.py

from app.vector.chroma_store import search_documents
from ai.llm_client import ask_llm

def rag_answer(question: str) -> str:
    docs = search_documents(question, k=5)

    if not docs:
        return "No relevant data found in the dataset."

    context = "\n".join(d["text"] for d in docs)

    answer = ask_llm(context=context, question=question)
    return answer
