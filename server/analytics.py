"""
Lightweight backend analytics helper to log user events into MongoDB.

Features:
- PII-safe: uses SecurityManager.redact_pii on properties
- Best-effort: failures never break request flow
- Minimal schema: { userId, name, ts, path, sessionId, properties, ua }
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .database import col
from utils.security import SecurityManager

_SEC = SecurityManager()


async def log_event(
    *,
    user_id: Optional[str],
    name: str,
    properties: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    session_id: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Insert an analytics event document. Swallows all errors.

    Args:
        user_id: user id (may be None for unauthenticated events)
        name: event name, e.g., 'content_generate_success'
        properties: additional metadata (will be redacted for PII and size-limited)
        path: request path if available
        session_id: client session identifier
        user_agent: user-agent string
    """
    try:
        props = dict(properties or {})
        # Redact potential PII in values
        try:
            for k, v in list(props.items()):
                if isinstance(v, str):
                    props[k] = _SEC.redact_pii(v)
                elif isinstance(v, (int, float, bool)) or v is None:
                    continue
                else:
                    # JSON-friendly and size limit
                    s = str(v)
                    props[k] = _SEC.redact_pii(s[:2048])
        except Exception:
            pass

        doc = {
            "userId": user_id,
            "name": name,
            "ts": datetime.utcnow().isoformat(),
            "path": path,
            "sessionId": session_id,
            "ua": (user_agent or "")[:512],
            "properties": props,
        }
        await col("events").insert_one(doc)
    except Exception:
        # Never block main flow due to analytics failures
        return
