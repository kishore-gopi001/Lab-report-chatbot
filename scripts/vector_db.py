from app.vector.chroma_store import search_documents

results = search_documents(
    "Summarize the critical patients"
)

for r in results:
    print(r["text"])
    print(r["metadata"])
    print("score:", r["score"])
    print("------")
