from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from fastapi import HTTPException, status
from bson import ObjectId

from .database import col


FREE_CONTENT_LIMIT = 10


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _is_same_month(a: datetime, b: datetime) -> bool:
    return a.year == b.year and a.month == b.month


async def _get_user_doc(user_id: str) -> Dict[str, Any]:
    """Fetch user doc safely by ObjectId string; returns {} if not found."""
    try:
        doc = await col("users").find_one({"_id": ObjectId(user_id)})
        return doc or {}
    except Exception:
        return {}


async def get_user_plan_and_usage(user_id: str) -> Tuple[str, Dict[str, Any]]:
    doc = await _get_user_doc(user_id)
    plan = (doc.get("plan") or "free").lower()
    usage: Dict[str, Any] = doc.get("usage") or {}
    return plan, usage


async def ensure_content_quota(user_id: str) -> None:
    """For free plan, enforce monthly content generation cap. No-op for paid plans."""
    plan, usage = await get_user_plan_and_usage(user_id)
    if plan != "free":
        return

    content_usage = usage.get("content") or {}
    count = int(content_usage.get("count") or 0)
    period_start_iso = content_usage.get("periodStart")

    now = _now_utc()
    if period_start_iso:
        try:
            period_start = datetime.fromisoformat(period_start_iso)
        except Exception:
            period_start = now
    else:
        period_start = now

    # Reset counter if month changed
    if not _is_same_month(now, period_start):
        count = 0
        period_start = now

    if count >= FREE_CONTENT_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "Free plan limit reached (10 content generations per month). Upgrade to continue.",
                "limit": FREE_CONTENT_LIMIT,
            },
        )


async def record_content_generation(user_id: str) -> None:
    """Increment content generation counter for the current month."""
    _, usage = await get_user_plan_and_usage(user_id)
    now = _now_utc()
    content_usage = usage.get("content") or {}
    period_start_iso = content_usage.get("periodStart")
    if period_start_iso:
        try:
            period_start = datetime.fromisoformat(period_start_iso)
        except Exception:
            period_start = now
    else:
        period_start = now

    if not _is_same_month(now, period_start):
        # Reset for new month
        content_usage = {"count": 0, "periodStart": now.isoformat()}

    new_count = int(content_usage.get("count") or 0) + 1
    content_usage.update({"count": new_count, "periodStart": period_start.isoformat()})

    await col("users").update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"usage.content": content_usage}},
        upsert=False,
    )


async def require_paid_feature(user_id: str) -> None:
    plan, _ = await get_user_plan_and_usage(user_id)
    if plan not in ("standard", "premium"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "PAID_FEATURE",
                "message": "This feature is available on Standard and Premium plans.",
            },
        )
