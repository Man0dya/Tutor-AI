"""
Embedding utilities using sentence-transformers.

Provides a singleton encoder and helper to compute normalized embeddings
for semantic search (cosine similarity compatible).

This module handles environments where sentence-transformers isn't available by
raising a clear runtime error with installation guidance. It also silences
static analyzer warnings when the package is present in runtime but not resolved
by the editor's interpreter.
"""
# pyright: reportMissingImports=false
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
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except Exception as e:  # ImportError or environment issues
                raise RuntimeError(
                    "sentence-transformers is not installed or not available in the active interpreter. "
                    "Please install it (e.g., pip install sentence-transformers) and ensure your editor "
                    "is using the same Python environment."
                ) from e
            # Force CPU to avoid CUDA dependency surprises
            _model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2", device="cpu"
            )
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
