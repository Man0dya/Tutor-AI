"""
Text utilities for canonicalization and hashing.

Used for exact content deduplication by hashing a normalized version of text.
"""
from __future__ import annotations

import re
import hashlib


_ws_re = re.compile(r"\s+", re.MULTILINE)


def normalize_text_for_hash(text: str) -> str:
    
    """Normalize text to a canonical form for hashing.

    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse all internal whitespace to single spaces
    - Remove zero-width characters
    - Normalize common punctuation spacing
    """
    if not isinstance(text, str):
        text = str(text or "")
    t = text.replace("\u200b", "").replace("\ufeff", "")
    t = t.strip().lower()
    t = _ws_re.sub(" ", t)
    # Space around punctuation normalization (basic)
    t = re.sub(r"\s*([,;:.!?])\s*", r"\1 ", t)
    t = _ws_re.sub(" ", t).strip()
    return t


def content_hash(text: str) -> str:
    
    """Return a SHA-256 hex digest of the normalized text."""
    
    norm = normalize_text_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()
