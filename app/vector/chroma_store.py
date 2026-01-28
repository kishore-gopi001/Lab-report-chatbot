# app/vector/chroma_store.py

import uuid
import chromadb
from chromadb.config import Settings
from ai.embedding_service import embed_text, embed_texts

# Persistent Chroma DB
client = chromadb.PersistentClient(
    path="data/chroma",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="lab_rag_knowledge"
)

def add_documents(texts: list[str], metadatas: list[dict]):
    embeddings = embed_texts(texts)
    ids = [str(uuid.uuid4()) for _ in texts]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

def search_documents(query: str, k: int = 5):
    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas"]
    )

    docs = []
    if results["documents"]:
        for i in range(len(results["documents"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i]
            })

    return docs
