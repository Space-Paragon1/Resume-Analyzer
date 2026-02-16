# src/embeddings.py
from __future__ import annotations
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    """Load and cache a SentenceTransformer model. Re-uses the same instance across calls."""
    return SentenceTransformer(model_name)

class Embedder:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        # Uses the module-level LRU cache so the model is loaded only once per process
        self.model = _load_model(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        emb = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32)
