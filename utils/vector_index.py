"""
Vector index service for semantic search using FAISS (with hnswlib fallback).

- Stores L2-normalized vectors for cosine/IP similarity.
- Maintains an ID <-> doc_id mapping for lookups.
"""
from __future__ import annotations

from typing import List, Tuple, Optional
import numpy as np


class VectorIndex:
    def __init__(self, dim: int, use_hnsw: bool = True):
        self.dim = dim
        self.doc_ids: List[str] = []
        self._index = None
        self._backend = None  # 'faiss' | 'hnsw'

        # Try FAISS first
        try:
            import faiss  # type: ignore
            self._backend = 'faiss'
            # Inner product with normalized vectors = cosine similarity
            self._index = faiss.IndexFlatIP(dim)
        except Exception:
            if use_hnsw:
                try:
                    import hnswlib  # type: ignore
                    self._backend = 'hnsw'
                    self._index = hnswlib.Index(space='cosine', dim=dim)
                    self._index.init_index(max_elements=1, ef_construction=200, M=16)
                    self._index.set_ef(64)
                except Exception as e:
                    raise RuntimeError("Neither faiss nor hnswlib available: " + str(e))
            else:
                raise RuntimeError("FAISS not available and use_hnsw=False")

    def add(self, vectors: np.ndarray, ids: List[str]):
        assert vectors.shape[0] == len(ids)
        # Normalize for cosine/IP safety
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vecs = (vectors / norms).astype(np.float32)

        if self._backend == 'faiss':
            import faiss  # type: ignore
            if isinstance(self._index, faiss.IndexFlatIP):
                self._index.add(vecs)
            else:
                self._index.add(vecs)
        else:
            # hnswlib requires pre-sizing; grow if needed
            import hnswlib  # type: ignore
            if len(self.doc_ids) == 0:
                # re-init with enough room
                self._index = hnswlib.Index(space='cosine', dim=self.dim)
                self._index.init_index(max_elements=max(1, len(ids)), ef_construction=200, M=16)
                self._index.set_ef(64)
                self._index.add_items(vecs, list(range(len(ids))))
            else:
                current = len(self.doc_ids)
                need = current + len(ids)
                self._index.resize_index(need)
                self._index.add_items(vecs, list(range(current, need)))

        self.doc_ids.extend(ids)

    def search(self, query_vec: np.ndarray, k: int = 10) -> Tuple[List[str], List[float]]:
        # Normalize
        q = query_vec.astype(np.float32)
        nrm = np.linalg.norm(q)
        if nrm > 0:
            q = q / nrm

        if self._backend == 'faiss':
            import faiss  # type: ignore
            D, I = self._index.search(q.reshape(1, -1), k)
            idxs = I[0].tolist()
            sims = D[0].tolist()
        else:
            labels, distances = self._index.knn_query(q.reshape(1, -1), k=k)
            idxs = labels[0].tolist()
            sims = [1.0 - d for d in distances[0].tolist()]  # cosine distance -> sim

        results_ids: List[str] = []
        results_sims: List[float] = []
        for i, s in zip(idxs, sims):
            if 0 <= i < len(self.doc_ids):
                results_ids.append(self.doc_ids[i])
                results_sims.append(float(s))
        return results_ids, results_sims

    # --- Introspection helpers ---
    def size(self) -> int:
        return len(self.doc_ids)

    def backend(self) -> Optional[str]:
        return self._backend

    # --- Persistence ---
    def save(self, index_path: str, ids_path: str) -> None:
        """Persist index to disk along with doc_ids mapping.

        - For faiss: write_index
        - For hnswlib: save_index
        - ids_path: JSON lines or simple newline-separated file of ids
        """
        import json
        if self._backend == 'faiss':
            import faiss  # type: ignore
            faiss.write_index(self._index, index_path)
        elif self._backend == 'hnsw':
            self._index.save_index(index_path)
        else:
            raise RuntimeError("Unknown backend; cannot save")
        with open(ids_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_ids, f)

    @staticmethod
    def load(dim: int, index_path: str, ids_path: str) -> "VectorIndex":
        """Load an index and ids mapping from disk. Auto-detect backend by trying faiss then hnswlib."""
        import os
        import json
        if not (os.path.exists(index_path) and os.path.exists(ids_path)):
            raise FileNotFoundError("Index or ids file not found")
        # Try faiss first
        try:
            import faiss  # type: ignore
            idx = VectorIndex(dim=dim)
            if idx._backend != 'faiss':
                # Recreate as faiss explicitly
                idx._backend = 'faiss'
                idx._index = faiss.IndexFlatIP(dim)
            idx._index = faiss.read_index(index_path)
        except Exception:
            # Try hnswlib
            import hnswlib  # type: ignore
            idx = VectorIndex(dim=dim)
            if idx._backend != 'hnsw':
                idx._backend = 'hnsw'
                idx._index = hnswlib.Index(space='cosine', dim=dim)
                idx._index.init_index(max_elements=1, ef_construction=200, M=16)
                idx._index.set_ef(64)
            idx._index.load_index(index_path)
        with open(ids_path, 'r', encoding='utf-8') as f:
            idx.doc_ids = json.load(f)
        return idx
