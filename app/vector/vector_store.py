import faiss
import numpy as np
from ai.embedding_service import embed_text

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
            "wbc result",
            "platelet count"
        ]
    }
]

_vectors = []
_metadata = []

for item in INTENTS:
    for example in item["examples"]:
        _vectors.append(embed_text(example))
        _metadata.append(item["intent"])

_vectors = np.array(_vectors).astype("float32")

index = faiss.IndexFlatIP(_vectors.shape[1])
index.add(_vectors)

def search_intent(question: str):
    q_vec = embed_text(question).reshape(1, -1).astype("float32")
    scores, indices = index.search(q_vec, 1)

    return {
        "intent": _metadata[indices[0][0]],
        "score": float(scores[0][0])
    }
