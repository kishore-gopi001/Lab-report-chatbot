import faiss
import numpy as np
from ai.embedding_service import embed_text

# --------------------------------------------------
# Intent Definitions
# --------------------------------------------------

INTENTS = [
    {
        "intent": "list_tests",
        "examples": [
            "what tests were done",
            "which labs were performed",
            "list all lab tests",
            "show lab investigations"
        ]
    },
    {
        "intent": "abnormal_labs",
        "examples": [
            "which tests are abnormal",
            "show abnormal labs",
            "any abnormal results"
        ]
    },
    {
        "intent": "critical_labs",
        "examples": [
            "any critical results",
            "show critical labs",
            "which tests are critical"
        ]
    },
    {
        "intent": "specific_test",
        "examples": [
            "what is my hemoglobin",
            "hemoglobin value",
            "wbc result",
            "platelet count",
            "sodium level",
            "potassium value",
            "creatinine result",
            "glucose reading",
            "chloride value",
            "blood urea nitrogen"
        ]
    }
]

# --------------------------------------------------
# Build FAISS Index
# --------------------------------------------------

_vectors = []
_metadata = []

for item in INTENTS:
    for example in item["examples"]:
        vec = embed_text(example)

        # 🔑 FORCE numpy float32
        vec = np.array(vec, dtype="float32")

        _vectors.append(vec)
        _metadata.append(item["intent"])

_vectors = np.vstack(_vectors)  # shape: (N, dim)

# Inner Product = cosine similarity (assuming normalized embeddings)
index = faiss.IndexFlatIP(_vectors.shape[1])
index.add(_vectors)

# --------------------------------------------------
# Intent Search
# --------------------------------------------------

def search_intent(question: str):
    vec = embed_text(question)

    # 🔑 SAFE CONVERSION
    vec = np.array(vec, dtype="float32").reshape(1, -1)

    scores, indices = index.search(vec, 1)

    return {
        "intent": _metadata[int(indices[0][0])],
        "score": float(scores[0][0])
    }
