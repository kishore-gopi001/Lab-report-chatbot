from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> np.ndarray:
    return _model.encode(text, normalize_embeddings=True)
