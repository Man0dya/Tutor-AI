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
from .config import ATLAS_SEARCH_ENABLED, ATLAS_SEARCH_INDEX

_VECTOR_INDEX: Optional[VectorIndex] = None
_DIM: int = 384  # all-MiniLM-L6-v2
_INDEX_PATH = None  # set to actual file paths if persistence is configured
_IDS_PATH = None

# Content-based index (for dedup after generation)
_CONTENT_INDEX: Optional[VectorIndex] = None
_CONTENT_INDEX_PATH = None
_CONTENT_IDS_PATH = None


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


async def search_similar(text: str, k: int = 5) -> Tuple[List[str], List[float]]:
    """Search similar docs by text using the vector index if available.

    Returns ids and similarity scores in descending order, or empty lists if index not ready.
    """
    # Prefer Atlas Vector Search if enabled
    if ATLAS_SEARCH_ENABLED:
        ids, scores = await atlas_search_candidates(text, k=k)
        if ids:
            return ids, scores
    # Fallback to in-memory index
    if _VECTOR_INDEX is None:
        return [], []
    try:
        vec = embed_text(text)
        return _VECTOR_INDEX.search(vec, k=k)
    except Exception:
        return [], []


async def atlas_search_candidates(text: str, k: int = 5) -> Tuple[List[str], List[float]]:
    """Use MongoDB Atlas Search knnBeta on generated_content.similarity_embedding.

    Requires an Atlas Search index with a vector field named 'similarity_embedding'.
    This returns candidate ids and scores (cosine similarity approximation based on knnBeta)."""
    if not text:
        return [], []
    try:
        # Compute embedding for the query
        vec = embed_text(text).tolist()
        gc = col("generated_content")
        pipeline = [
            {
                "$search": {
                    "index": ATLAS_SEARCH_INDEX,
                    "knnBeta": {
                        "vector": vec,
                        "path": "similarity_embedding",
                        "k": max(1, int(k)),
                    },
                }
            },
            {"$project": {"_id": 1, "score": {"$meta": "searchScore"}}},
            {"$limit": max(1, int(k))},
        ]
        cur = gc.aggregate(pipeline)
        docs = await cur.to_list(length=None)
        ids = [str(d.get("_id")) for d in docs]
        scores = [float(d.get("score", 0.0)) for d in docs]
        return ids, scores
    except Exception:
        return [], []


async def build_content_index(batch: int = 64) -> None:
    """Build the content vector index from generated_content documents using content field."""
    global _CONTENT_INDEX
    try:
        idx = VectorIndex(dim=_DIM)
    except Exception:
        _CONTENT_INDEX = None
        return
    gc = col("generated_content")
    cursor = gc.find({}, {"_id": 1, "content": 1})
    docs = await cursor.to_list(length=None)
    if not docs:
        _CONTENT_INDEX = idx
        return
    texts = [d.get("content") or "" for d in docs]
    ids = [str(d.get("_id")) for d in docs]
    for i in range(0, len(texts), batch):
        chunk_t = texts[i : i + batch]
        chunk_i = ids[i : i + batch]
        vecs = embed_texts(chunk_t)
        idx.add(vecs, chunk_i)
    _CONTENT_INDEX = idx


def add_content_to_index(doc_id: str, content: str) -> None:
    if _CONTENT_INDEX is None:
        return
    try:
        vec = embed_text(content)
        _CONTENT_INDEX.add(vec.reshape(1, -1), [doc_id])
    except Exception:
        return


async def search_similar_content(content: str, k: int = 5) -> Tuple[List[str], List[float]]:
    # Prefer Atlas Vector Search against content embeddings
    if ATLAS_SEARCH_ENABLED:
        ids, scores = await atlas_search_content_candidates(content, k=k)
        if ids:
            return ids, scores
    # Fallback to in-memory content index
    if _CONTENT_INDEX is None:
        return [], []
    try:
        vec = embed_text(content)
        return _CONTENT_INDEX.search(vec, k=k)
    except Exception:
        return [], []


async def atlas_search_content_candidates(text: str, k: int = 5) -> Tuple[List[str], List[float]]:
    """Use MongoDB Atlas Search knnBeta on generated_content.content_embedding."""
    if not text:
        return [], []
    try:
        vec = embed_text(text).tolist()
        gc = col("generated_content")
        pipeline = [
            {
                "$search": {
                    "index": ATLAS_SEARCH_INDEX,
                    "knnBeta": {
                        "vector": vec,
                        "path": "content_embedding",
                        "k": max(1, int(k)),
                    },
                }
            },
            {"$project": {"_id": 1, "score": {"$meta": "searchScore"}}},
            {"$limit": max(1, int(k))},
        ]
        cur = gc.aggregate(pipeline)
        docs = await cur.to_list(length=None)
        ids = [str(d.get("_id")) for d in docs]
        scores = [float(d.get("score", 0.0)) for d in docs]
        return ids, scores
    except Exception:
        return [], []


def index_status() -> dict:
    """Return current index status for diagnostics."""
    status = {
        "query": {
            "available": _VECTOR_INDEX is not None,
            "backend": _VECTOR_INDEX.backend() if _VECTOR_INDEX else None,
            "size": _VECTOR_INDEX.size() if _VECTOR_INDEX else 0,
            "dim": _DIM,
        },
        "content": {
            "available": _CONTENT_INDEX is not None,
            "backend": _CONTENT_INDEX.backend() if _CONTENT_INDEX else None,
            "size": _CONTENT_INDEX.size() if _CONTENT_INDEX else 0,
            "dim": _DIM,
        },
    }
    return status


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
