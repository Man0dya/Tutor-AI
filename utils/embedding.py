"""
Embedding utilities using sentence-transformers.

Provides a singleton encoder and helper to compute normalized embeddings
for semantic search (cosine similarity compatible).
"""
from __future__ import annotations

import threading
from typing import List

import numpy as np

_model = None
_lock = threading.Lock()


def _load_model():
    global _model
    with _lock:
        if _model is None:
            # Lightweight, fast model (384-d)
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """Embed a list of texts into L2-normalized vectors (np.ndarray, shape [n, d])."""
    if not isinstance(texts, list):
        texts = [str(texts)]
    model = _load_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    # Ensure numpy array float32
    arr = np.asarray(vecs, dtype=np.float32)
    # If the model didn't normalize, do L2 normalize
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    arr = arr / norms
    return arr


def embed_text(text: str) -> np.ndarray:
    return embed_texts([text])[0]
