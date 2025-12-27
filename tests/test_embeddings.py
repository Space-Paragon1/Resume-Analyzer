# tests/test_embeddings.py
from __future__ import annotations
import numpy as np
import pytest

def test_embedder_empty_texts_returns_0x384_float32(monkeypatch):
    # Import inside test so monkeypatch can affect module behavior safely
    import src.embeddings as emb_mod

    # Mock SentenceTransformer constructor (should not be called for empty list,
    # but our class __init__ calls it, so we patch it anyway)
    class FakeST:
        def __init__(self, model_name):
            self.model_name = model_name
        def encode(self, texts, normalize_embeddings=True):
            raise AssertionError("encode should not be called when texts is empty")

    monkeypatch.setattr(emb_mod, "SentenceTransformer", FakeST)

    e = emb_mod.Embedder("fake-model")
    out = e.embed([])

    assert isinstance(out, np.ndarray)
    assert out.shape == (0, 384)
    assert out.dtype == np.float32

def test_embedder_calls_encode_with_normalize_true(monkeypatch):
    import src.embeddings as emb_mod

    calls = {"init": None, "encode": None}

    class FakeST:
        def __init__(self, model_name):
            calls["init"] = model_name

        def encode(self, texts, normalize_embeddings=True):
            calls["encode"] = {"texts": texts, "normalize_embeddings": normalize_embeddings}
            # Return something array-like with shape (n, 384)
            n = len(texts)
            return np.ones((n, 384), dtype=np.float64)  # float64 on purpose

    monkeypatch.setattr(emb_mod, "SentenceTransformer", FakeST)

    e = emb_mod.Embedder("my-model")
    assert calls["init"] == "my-model"

    texts = ["hello", "world"]
    out = e.embed(texts)

    assert calls["encode"]["texts"] == texts
    assert calls["encode"]["normalize_embeddings"] is True

    assert isinstance(out, np.ndarray)
    assert out.shape == (2, 384)
    # Your code forces float32
    assert out.dtype == np.float32
    # And preserves values
    assert float(out[0, 0]) == 1.0

def test_embedder_accepts_any_list_of_strings(monkeypatch):
    import src.embeddings as emb_mod

    class FakeST:
        def __init__(self, model_name):
            pass
        def encode(self, texts, normalize_embeddings=True):
            # Just return embeddings for each input
            return np.arange(len(texts) * 384).reshape(len(texts), 384)

    monkeypatch.setattr(emb_mod, "SentenceTransformer", FakeST)

    e = emb_mod.Embedder()
    out = e.embed(["a"])
    assert out.shape == (1, 384)
    assert out.dtype == np.float32
