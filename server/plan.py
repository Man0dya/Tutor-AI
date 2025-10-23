"""
Subscription Plan and Usage Management Module

This module handles subscription plan management and usage tracking for the Tutor AI system.
It enforces plan-based quotas, tracks monthly usage limits, and provides subscription
validation for premium features.

Key Features:
- Plan-based feature access control (Free, Standard, Premium)
- Monthly usage quotas for free tier users
- Automatic quota reset on month boundaries
- Content generation tracking and limits
- Paid feature validation

Plan Structure:
- Free: Limited to 10 content generations per month
- Standard: Full access to all features
- Premium: Full access with additional benefits

Usage Tracking:
- Monthly content generation counters
- Automatic reset on month change
- Persistent storage in user documents
- Real-time quota validation

Dependencies:
- fastapi: For HTTP exceptions and status codes
- bson: For MongoDB ObjectId handling
- database: For user collection access
- datetime: For timezone-aware date operations

Author: Tutor AI Team
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from fastapi import HTTPException, status
from bson import ObjectId

from .database import col

# Free plan monthly content generation limit
FREE_CONTENT_LIMIT = 10

def _now_utc() -> datetime:
    """
    Get current UTC datetime with timezone awareness.

    Returns:
        datetime: Current UTC datetime with timezone information.
    """
    return datetime.now(timezone.utc)

def _is_same_month(a: datetime, b: datetime) -> bool:
    """
    Check if two datetime objects fall in the same month and year.

    Args:
        a (datetime): First datetime to compare.
        b (datetime): Second datetime to compare.

    Returns:
        bool: True if both dates are in the same month and year.
    """
    return a.year == b.year and a.month == b.month

async def _get_user_doc(user_id: str) -> Dict[str, Any]:
    """
    Safely fetch user document from database by ObjectId string.

    Args:
        user_id (str): User ID as string representation of ObjectId.

    Returns:
        dict: User document if found, empty dict if not found or invalid ID.
    """
    try:
        doc = await col("users").find_one({"_id": ObjectId(user_id)})
        return doc or {}
    except Exception:
        return {}

async def get_user_plan_and_usage(user_id: str) -> Tuple[str, Dict[str, Any]]:

    """
    Retrieve user's subscription plan and current usage statistics.

    Args:
        user_id (str): User identifier.

    Returns:
        tuple: (plan_name, usage_dict) where plan is lowercase string
               and usage contains quota tracking information.
    """

    doc = await _get_user_doc(user_id)
    plan = (doc.get("plan") or "free").lower()
    usage: Dict[str, Any] = doc.get("usage") or {}
    return plan, usage

async def ensure_content_quota(user_id: str) -> None:

    """
    Enforce monthly content generation quota for free plan users.

    Checks current usage against free tier limits and raises HTTP 402
    if quota is exceeded. No enforcement for paid plans.

    Args:
        user_id (str): User identifier.

    Raises:
        HTTPException: 402 Payment Required if free quota exceeded.
    """
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

    """
    Increment the content generation counter for the current month.

    Updates the user's usage statistics in the database, handling
    month transitions and counter resets automatically.

    Args:
        user_id (str): User identifier.
    """

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

    """
    Validate that user has access to paid features.

    Checks if user is on Standard or Premium plan before allowing
    access to premium-only functionality.

    Args:
        user_id (str): User identifier.

    Raises:
        HTTPException: 402 Payment Required if user is not on paid plan.
    """

    plan, _ = await get_user_plan_and_usage(user_id)
    if plan not in ("standard", "premium"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "PAID_FEATURE",
                "message": "This feature is available on Standard and Premium plans.",
            },
        )
