# scripts/query_patient_chroma.py
import sys
import os

# Add the project root to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.vector.chroma_store import collection

def query_patient(subject_id):
    # Chroma stores metadata values as matches
    # Based on agent.py, we should check if it's stored as string or int
    # We will try both or use the list of metadatas
    
    print(f"Searching for patient_id: {subject_id}")
    
    # query uses embeddings, but we want all documents for a metadata filter
    # So we use .get() which allows filtering without needing a query vector
    results = collection.get(
        where={"subject_id": subject_id}
    )
    
    if not results["documents"]:
        # Try as string if int fails
        results = collection.get(
            where={"subject_id": str(subject_id)}
        )

    if not results["documents"]:
        print("No documents found for this patient ID.")
        return

    print(f"Found {len(results['documents'])} documents:")
    for i, doc in enumerate(results["documents"]):
        metadata = results["metadatas"][i]
        print(f"\n--- Document {i+1} ---")
        print(f"Content: {doc}")
        print(f"Metadata: {metadata}")

if __name__ == "__main__":
    patient_id = "10001725"
    if len(sys.argv) > 1:
        patient_id = sys.argv[1]
    query_patient(patient_id)
