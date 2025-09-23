from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..schemas import AnswerSubmitRequest, FeedbackOut
from agents.feedback_evaluator import FeedbackEvaluatorAgent
from ..auth import get_current_user
from ..database import col

router = APIRouter(prefix="/answers", tags=["answers"]) 

_feedback_agent = FeedbackEvaluatorAgent()

@router.post("/submit", response_model=FeedbackOut)
async def submit_answers(payload: AnswerSubmitRequest, user=Depends(get_current_user)) -> FeedbackOut:
    try:
        qset = await col("question_sets").find_one({"_id": payload.questionSetId})
        if not qset:
            raise HTTPException(status_code=404, detail="Question set not found")

        questions = qset.get("questions", [])

        feedback = _feedback_agent.evaluate_answers(
            questions=questions,
            user_answers=payload.answers,
            feedback_type="Detailed",
            include_suggestions=True,
        )

        fb_doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "questionSetId": payload.questionSetId,
            "overallScore": feedback.get("overall_score", 0.0),
            "detailedFeedback": feedback.get("detailed_feedback", ""),
            "studySuggestions": feedback.get("study_suggestions"),
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("feedback").insert_one(fb_doc)

        # Optionally record answers too (Mongo requires string keys in documents)
        safe_answers = {str(k): v for k, v in payload.answers.items()}
        ans_doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "questionSetId": payload.questionSetId,
            "answers": safe_answers,
            "submittedAt": datetime.utcnow().isoformat(),
        }
        await col("answers").insert_one(ans_doc)

        return FeedbackOut(
            id=fb_doc["_id"],
            questionSetId=payload.questionSetId,
            overallScore=fb_doc["overallScore"],
            detailedFeedback=fb_doc["detailedFeedback"],
            studySuggestions=fb_doc.get("studySuggestions"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer submission failed: {e}")
