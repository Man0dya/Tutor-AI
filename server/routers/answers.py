"""
Answers Router Module

This module provides API endpoints for answer submission and feedback retrieval
in the Tutor AI system. It handles the complete workflow of evaluating student
answers against question sets and providing detailed feedback with suggestions.

Key Features:
- Answer submission with automatic evaluation
- AI-powered feedback generation using feedback evaluator agent
- Feedback retrieval and history access
- Plan-based feature access control (paid plans only)
- Comprehensive answer and feedback storage

Endpoints:
- POST /answers/submit: Submit answers for evaluation
- GET /answers/feedback/{feedback_id}: Retrieve specific feedback

Security:
- JWT authentication required for all endpoints
- User isolation (users can only access their own feedback)
- Paid plan validation for answer submission

Data Flow:
1. User submits answers for a question set
2. System validates question set exists
3. Feedback evaluator agent processes answers
4. Feedback and answers are stored in database
5. Structured feedback response returned to user

Dependencies:
- fastapi: For API routing and request handling
- feedback_evaluator: For AI-powered answer evaluation
- database: For MongoDB collections access
- auth: For JWT user authentication
- plan: For subscription plan validation

Author: Tutor AI Team
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..schemas import AnswerSubmitRequest, FeedbackOut
from agents.feedback_evaluator import FeedbackEvaluatorAgent
from ..auth import get_current_user
from ..database import col
from ..plan import require_paid_feature

# Create router with answers prefix and tags for API documentation
router = APIRouter(prefix="/answers", tags=["answers"])

# Initialize feedback evaluator agent for answer assessment
_feedback_agent = FeedbackEvaluatorAgent()

@router.post("/submit", response_model=FeedbackOut)
async def submit_answers(payload: AnswerSubmitRequest, user=Depends(get_current_user)) -> FeedbackOut:
    """
    Submit student answers for AI-powered evaluation and feedback.

    This endpoint processes student answers against a question set, generates
    detailed feedback using the feedback evaluator agent, and stores both
    the answers and feedback in the database.

    Args:
        payload (AnswerSubmitRequest): Answer submission data containing
            questionSetId and answers dictionary.
        user (dict): Authenticated user information from JWT token.

    Returns:
        FeedbackOut: Structured feedback response with scores, detailed
            feedback, study suggestions, and individual question evaluations.

    Raises:
        HTTPException: 404 if question set not found, 500 for processing errors,
            402 if user doesn't have paid plan access.
    """
    try:
        # Validate user has paid plan access (Standard/Premium required)
        await require_paid_feature(user.get("sub"))

        # Retrieve question set from database
        qset = await col("question_sets").find_one({"_id": payload.questionSetId})
        if not qset:
            raise HTTPException(status_code=404, detail="Question set not found")

        questions = qset.get("questions", [])

        # Generate comprehensive feedback using AI agent
        feedback = _feedback_agent.evaluate_answers(
            questions=questions,
            user_answers=payload.answers,
            feedback_type="Detailed",
            include_suggestions=True,
        )

        # Prepare feedback document for database storage
        fb_doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "questionSetId": payload.questionSetId,
            "overallScore": feedback.get("overall_score", 0.0),
            "detailedFeedback": feedback.get("detailed_feedback", ""),
            "studySuggestions": feedback.get("study_suggestions"),
            "individualEvaluations": feedback.get("individual_evaluations"),
            "createdAt": datetime.utcnow().isoformat(),
        }

        # Store feedback in database
        await col("feedback").insert_one(fb_doc)

        # Store answers with string keys (MongoDB requirement)
        safe_answers = {str(k): v for k, v in payload.answers.items()}
        ans_doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "questionSetId": payload.questionSetId,
            "answers": safe_answers,
            "submittedAt": datetime.utcnow().isoformat(),
        }

        # Store answers in database
        await col("answers").insert_one(ans_doc)

        # Return structured feedback response
        return FeedbackOut(
            id=fb_doc["_id"],
            questionSetId=payload.questionSetId,
            overallScore=fb_doc["overallScore"],
            detailedFeedback=fb_doc["detailedFeedback"],
            studySuggestions=fb_doc.get("studySuggestions"),
            individualEvaluations=fb_doc.get("individualEvaluations"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer submission failed: {e}")

@router.get("/feedback/{feedback_id}", response_model=FeedbackOut)
async def get_feedback(feedback_id: str, user=Depends(get_current_user)) -> FeedbackOut:
    """
    Retrieve specific feedback by ID for the authenticated user.

    Allows users to access their previously generated feedback and review
    their performance on assessments.

    Args:
        feedback_id (str): Unique identifier of the feedback document.
        user (dict): Authenticated user information from JWT token.

    Returns:
        FeedbackOut: Complete feedback information including scores,
            detailed feedback, and study suggestions.

    Raises:
        HTTPException: 404 if feedback not found or doesn't belong to user.
    """
    # Retrieve feedback document with user ownership validation
    doc = await col("feedback").find_one({"_id": feedback_id, "userId": user.get("sub")})
    if not doc:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # Return structured feedback response
    return FeedbackOut(
        id=doc["_id"],
        questionSetId=doc["questionSetId"],
        overallScore=doc.get("overallScore", 0.0),
        detailedFeedback=doc.get("detailedFeedback", ""),
        studySuggestions=doc.get("studySuggestions"),
        individualEvaluations=doc.get("individualEvaluations"),
    )
