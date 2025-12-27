# src/embeddings.py
from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

class Embedder:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        emb = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32)
