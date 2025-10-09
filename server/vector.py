"""
Vector store singleton for semantic search over generated content.

Builds an in-memory index on startup from MongoDB `generated_content` collection.
Uses sentence-transformers embeddings and FAISS (or hnswlib) for similarity.
"""
from __future__ import annotations

from typing import List, Tuple, Optional

from utils.embedding import embed_text, embed_texts
from utils.vector_index import VectorIndex
from .database import col

_VECTOR_INDEX: Optional[VectorIndex] = None
_DIM: int = 384  # all-MiniLM-L6-v2
_INDEX_PATH = None  # set to actual file paths if persistence is configured
_IDS_PATH = None


def has_index() -> bool:
    return _VECTOR_INDEX is not None


async def build_vector_index(batch: int = 256) -> None:
    """Build the vector index from existing cached documents."""
    global _VECTOR_INDEX
    try:
        idx = VectorIndex(dim=_DIM)
    except Exception:
        # Backend not available; skip building
        _VECTOR_INDEX = None
        return

    gc = col("generated_content")
    cursor = gc.find({}, {"_id": 1, "similarity_basis": 1, "topic": 1})
    docs: List[dict] = await cursor.to_list(length=None)
    if not docs:
        _VECTOR_INDEX = idx
        return

    # Chunk embeddings to avoid memory spikes
    texts: List[str] = [d.get("similarity_basis") or d.get("topic") or "" for d in docs]
    ids: List[str] = [str(d.get("_id")) for d in docs]

    for i in range(0, len(texts), batch):
        chunk_texts = texts[i : i + batch]
        chunk_ids = ids[i : i + batch]
        vecs = embed_texts(chunk_texts)
        idx.add(vecs, chunk_ids)

    _VECTOR_INDEX = idx


def add_to_index(doc_id: str, text: str) -> None:
    """Add a single document to the vector index if available."""
    if _VECTOR_INDEX is None:
        return
    try:
        vec = embed_text(text)
        _VECTOR_INDEX.add(vec.reshape(1, -1), [doc_id])
    except Exception:
        # Best-effort; ignore index add failure
        return


def search_similar(text: str, k: int = 5) -> Tuple[List[str], List[float]]:
    """Search similar docs by text using the vector index if available.

    Returns ids and similarity scores in descending order, or empty lists if index not ready.
    """
    if _VECTOR_INDEX is None:
        return [], []
    try:
        vec = embed_text(text)
        return _VECTOR_INDEX.search(vec, k=k)
    except Exception:
        return [], []


def index_status() -> dict:
    """Return current index status for diagnostics."""
    if _VECTOR_INDEX is None:
        return {"available": False}
    return {
        "available": True,
        "backend": _VECTOR_INDEX.backend(),
        "size": _VECTOR_INDEX.size(),
        "dim": _DIM,
    }


def save_index(index_path: str, ids_path: str) -> bool:
    """Persist index if available; returns True on success."""
    global _INDEX_PATH, _IDS_PATH
    if _VECTOR_INDEX is None:
        return False
    try:
        import os
        os.makedirs(os.path.dirname(index_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(ids_path) or '.', exist_ok=True)
        _VECTOR_INDEX.save(index_path, ids_path)
        _INDEX_PATH, _IDS_PATH = index_path, ids_path
        return True
    except Exception:
        return False


def load_index(index_path: str, ids_path: str) -> bool:
    """Load index from disk; returns True on success."""
    global _VECTOR_INDEX, _INDEX_PATH, _IDS_PATH
    try:
        _VECTOR_INDEX = VectorIndex.load(dim=_DIM, index_path=index_path, ids_path=ids_path)
        _INDEX_PATH, _IDS_PATH = index_path, ids_path
        return True
    except Exception:
        return False
