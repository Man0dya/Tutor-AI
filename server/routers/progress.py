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

    # Recent content items (latest 10)
    recent_contents: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "topic": d.get("topic"),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("content").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Recent question sets (latest 10)
    recent_question_sets: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "contentId": d.get("contentId"),
            "questionCount": len(d.get("questions", [])),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("question_sets").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Recent feedback summaries (latest 10)
    recent_feedback: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "questionSetId": d.get("questionSetId"),
            "overallScore": float(d.get("overallScore", 0.0)),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("feedback").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Build threads: content -> question sets -> answers/feedback
    # Fetch all user's docs in memory to build associations efficiently
    all_contents = [
        d async for d in col("content").find({"userId": user_id})
    ]
    all_qsets = [
        d async for d in col("question_sets").find({"userId": user_id})
    ]
    all_answers = [
        d async for d in col("answers").find({"userId": user_id})
    ]
    all_feedback = [
        d async for d in col("feedback").find({"userId": user_id})
    ]

    # Group maps
    from collections import defaultdict
    qsets_by_content: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for q in all_qsets:
        qsets_by_content[q.get("contentId", "")].append(q)

    answers_by_qset: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for a in all_answers:
        answers_by_qset[a.get("questionSetId", "")].append(a)

    feedback_by_qset: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in all_feedback:
        feedback_by_qset[f.get("questionSetId", "")].append(f)

    threads: List[Dict[str, Any]] = []
    for c in sorted(all_contents, key=lambda d: d.get("createdAt", ""), reverse=True):
        c_id = c.get("_id")
        qs_for_c = qsets_by_content.get(c_id, [])
        thread_qsets: List[Dict[str, Any]] = []
        for qs in sorted(qs_for_c, key=lambda d: d.get("createdAt", "")):
            qs_id = qs.get("_id")
            qs_entry = {
                "id": qs_id,
                "createdAt": qs.get("createdAt"),
                "questionCount": len(qs.get("questions", [])),
                "answers": [
                    {
                        "id": a.get("_id"),
                        "submittedAt": a.get("submittedAt"),
                    }
                    for a in sorted(answers_by_qset.get(qs_id, []), key=lambda d: d.get("submittedAt", ""))
                ],
                "feedback": [
                    {
                        "id": f.get("_id"),
                        "overallScore": float(f.get("overallScore", 0.0)),
                        "createdAt": f.get("createdAt"),
                    }
                    for f in sorted(feedback_by_qset.get(qs_id, []), key=lambda d: d.get("createdAt", ""))
                ],
            }
            thread_qsets.append(qs_entry)
        threads.append(
            {
                "content": {
                    "id": c_id,
                    "topic": c.get("topic"),
                    "createdAt": c.get("createdAt"),
                },
                "questionSets": thread_qsets,
            }
        )

    return {
        "content_count": content_count,
        "questions_answered": questions_answered,
        "average_score": avg,
        "study_streak": 0,  # placeholder
        "score_history": score_history,
        "subject_performance": {},  # optional aggregation by subject
        "recent_activity": [],  # can be filled by an activity log collection
        "recent_contents": recent_contents,
        "recent_question_sets": recent_question_sets,
        "recent_feedback": recent_feedback,
        "threads": threads,
    }
