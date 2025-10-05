"""
Progress Router Module

This module provides user progress tracking and analytics endpoints for the Tutor AI system.
It aggregates user activity data including content creation, question answering, feedback scores,
and learning progress to provide comprehensive progress reports and study insights.

Key Features:
- User progress overview with statistics and metrics
- Score history and performance tracking
- Recent activity summaries (content, questions, feedback)
- Learning thread visualization (content -> questions -> answers -> feedback)
- Study streak and performance analytics

Data Aggregation:
- Content count and question answering statistics
- Average feedback scores and score history
- Recent activity feeds with chronological ordering
- Thread-based learning progression mapping

Performance Metrics:
- Overall score averages from AI feedback evaluation
- Question set completion tracking
- Content creation frequency analysis
- Learning pattern identification through thread analysis

Dependencies:
- FastAPI for API routing and request handling
- MongoDB for user activity data storage
- JWT authentication for user verification
- Collections module for database access
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime

from ..auth import get_current_user
from ..database import col

# Create router with progress prefix and tags for API documentation
router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/me")
async def get_progress_me(user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get comprehensive user progress and learning analytics.

    This endpoint aggregates all user activity data to provide a complete overview
    of learning progress, including statistics, recent activity, and learning threads.
    It builds a hierarchical view of the user's learning journey from content creation
    through question sets to answers and feedback.

    Args:
        user: Current authenticated user information from JWT token

    Returns:
        Dict containing comprehensive progress data:
        - content_count: Total content items created
        - questions_answered: Total questions answered
        - average_score: Average feedback score across all evaluations
        - study_streak: Learning streak counter (placeholder)
        - score_history: Chronological score progression
        - subject_performance: Performance by subject (placeholder)
        - recent_activity: Recent learning activities (placeholder)
        - recent_contents: Latest 10 content items
        - recent_question_sets: Latest 10 question sets
        - recent_feedback: Latest 10 feedback evaluations
        - threads: Hierarchical learning progression threads
    """
    user_id = user.get("sub")

    # Count total content items created by user
    content_count = await col("content").count_documents({"userId": user_id})

    # Count total questions answered by user
    questions_answered = await col("answers").count_documents({"userId": user_id})

    # Compute average score from all feedback evaluations
    cursor = col("feedback").find({"userId": user_id})
    scores: List[float] = []
    async for doc in cursor:
        if isinstance(doc.get("overallScore"), (int, float)):
            scores.append(float(doc["overallScore"]))
    avg = sum(scores) / len(scores) if scores else 0.0

    # Build chronological score history from feedback
    score_history = [
        {"date": doc.get("createdAt", datetime.utcnow().isoformat()), "score": float(doc.get("overallScore", 0))}
        async for doc in col("feedback").find({"userId": user_id}).sort("createdAt", 1)
    ]

    # Fetch recent content items (latest 10, most recent first)
    recent_contents: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "topic": d.get("topic"),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("content").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Fetch recent question sets (latest 10, most recent first)
    recent_question_sets: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "contentId": d.get("contentId"),
            "questionCount": len(d.get("questions", [])),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("question_sets").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Fetch recent feedback summaries (latest 10, most recent first)
    recent_feedback: List[Dict[str, Any]] = [
        {
            "id": d.get("_id"),
            "questionSetId": d.get("questionSetId"),
            "overallScore": float(d.get("overallScore", 0.0)),
            "createdAt": d.get("createdAt"),
        }
        async for d in col("feedback").find({"userId": user_id}).sort("createdAt", -1).limit(10)
    ]

    # Build learning threads: content -> question sets -> answers/feedback
    # Fetch all user's documents to build associations efficiently
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

    # Group question sets by content ID for thread building
    from collections import defaultdict
    qsets_by_content: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for q in all_qsets:
        qsets_by_content[q.get("contentId", "")].append(q)

    # Group answers by question set ID
    answers_by_qset: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for a in all_answers:
        answers_by_qset[a.get("questionSetId", "")].append(a)

    # Group feedback by question set ID
    feedback_by_qset: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in all_feedback:
        feedback_by_qset[f.get("questionSetId", "")].append(f)

    # Build hierarchical learning threads
    threads: List[Dict[str, Any]] = []
    for c in sorted(all_contents, key=lambda d: d.get("createdAt", ""), reverse=True):
        c_id = c.get("_id")
        qs_for_c = qsets_by_content.get(c_id, [])

        # Build question sets for this content
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

        # Add content thread with associated question sets
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

    # Return comprehensive progress report
    return {
        "content_count": content_count,
        "questions_answered": questions_answered,
        "average_score": avg,
        "study_streak": 0,  # placeholder for future streak calculation
        "score_history": score_history,
        "subject_performance": {},  # placeholder for subject-based analytics
        "recent_activity": [],  # placeholder for activity log integration
        "recent_contents": recent_contents,
        "recent_question_sets": recent_question_sets,
        "recent_feedback": recent_feedback,
        "threads": threads,
    }
