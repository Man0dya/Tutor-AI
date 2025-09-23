from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime

from ..auth import get_current_user
from ..database import col

router = APIRouter(prefix="/progress", tags=["progress"]) 

@router.get("/me")
async def get_progress_me(user=Depends(get_current_user)) -> Dict[str, Any]:
    user_id = user.get("sub")

    content_count = await col("content").count_documents({"userId": user_id})
    questions_answered = await col("answers").count_documents({"userId": user_id})

    # Compute average score from feedback
    cursor = col("feedback").find({"userId": user_id})
    scores: List[float] = []
    async for doc in cursor:
        if isinstance(doc.get("overallScore"), (int, float)):
            scores.append(float(doc["overallScore"]))
    avg = sum(scores) / len(scores) if scores else 0.0

    # Simple score history
    score_history = [
        {"date": doc.get("createdAt", datetime.utcnow().isoformat()), "score": float(doc.get("overallScore", 0))}
        async for doc in col("feedback").find({"userId": user_id}).sort("createdAt", 1)
    ]

    return {
        "content_count": content_count,
        "questions_answered": questions_answered,
        "average_score": avg,
        "study_streak": 0,  # placeholder
        "score_history": score_history,
        "subject_performance": {},  # optional aggregation by subject
        "recent_activity": [],  # can be filled by an activity log collection
    }
