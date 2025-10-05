"""
Questions Router Module

This module provides question generation endpoints for the Tutor AI system. It handles
the creation of question sets from educational content using AI-powered question generation
with support for different question types, difficulty levels, and Bloom's taxonomy.

Key Features:
- AI-powered question set generation from content
- Support for multiple question types (multiple choice, short answer, etc.)
- Difficulty distribution control
- Bloom's taxonomy level specification
- Plan-based access control (paid feature requirement)

Question Generation Process:
1. Validate user has paid plan access
2. Retrieve content document from database
3. Generate questions using QuestionSetterAgent
4. Store question set in database with metadata
5. Return structured question set response

Security Considerations:
- Paid plan requirement for question generation
- User authentication required
- Content ownership validation through database queries

Dependencies:
- FastAPI for API routing and request handling
- QuestionSetterAgent for AI-powered question generation
- MongoDB for content and question set storage
- JWT authentication for user verification
- Plan validation for feature access control

Integration Points:
- Content router for content retrieval
- QuestionSetterAgent for AI question generation
- Plan module for subscription validation
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from uuid import uuid4
from datetime import datetime

from ..schemas import QuestionGenRequest, QuestionSetOut
from agents.question_setter import QuestionSetterAgent
from ..auth import get_current_user
from ..database import col
from ..plan import require_paid_feature

# Create router with questions prefix and tags for API documentation
router = APIRouter(prefix="/questions", tags=["questions"])

# Initialize question generation agent (singleton pattern for efficiency)
_question_agent = QuestionSetterAgent()

@router.post("/generate", response_model=QuestionSetOut)
async def generate_questions(payload: QuestionGenRequest, user=Depends(get_current_user)) -> QuestionSetOut:
    """
    Generate a set of questions from educational content.

    This endpoint creates customized question sets from user content using AI-powered
    question generation. It supports various question types, difficulty levels, and
    educational taxonomy specifications. The feature requires a paid subscription plan.

    Args:
        payload (QuestionGenRequest): Question generation parameters including:
            - contentId: ID of the content to generate questions from
            - questionCount: Number of questions to generate
            - questionTypes: List of question types to include
            - difficultyDistribution: Difficulty level distribution
            - bloomLevels: Bloom's taxonomy levels to target
        user: Current authenticated user information from JWT token

    Returns:
        QuestionSetOut: Generated question set with:
        - id: Unique question set identifier
        - contentId: Source content identifier
        - questions: List of generated questions
        - metadata: Generation metadata and statistics

    Raises:
        HTTPException: 403 if user doesn't have paid plan, 404 if content not found,
                      500 for question generation failures

    Process Flow:
        1. Validate paid plan access
        2. Retrieve content document
        3. Generate questions via AI agent
        4. Store question set in database
        5. Return structured response
    """
    try:
        # Validate user has access to paid features (Standard/Premium plans)
        await require_paid_feature(user.get("sub"))

        # Retrieve the source content document for question generation
        content_doc = await col("content").find_one({"_id": payload.contentId})
        if not content_doc:
            raise HTTPException(status_code=404, detail="Content not found for question generation")

        # Prepare content input for the question generation agent
        content_input = {
            "content": content_doc.get("content", ""),
            "metadata": content_doc.get("metadata", {}),
            "topic": content_doc.get("topic"),
        }

        # Generate questions using the AI question setter agent
        result = _question_agent.generate_questions(
            content=content_input,
            question_count=payload.questionCount,
            question_types=payload.questionTypes,
            difficulty_distribution=payload.difficultyDistribution,
            bloom_levels=payload.bloomLevels,
        )

        # Extract questions and metadata from agent response
        if isinstance(result, dict):
            questions: List[Dict[str, Any]] = result.get("questions", [])
            metadata: Dict[str, Any] = result.get("metadata", {})
        else:
            questions = result
            metadata = {}

        # Create question set document for database storage
        doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "contentId": payload.contentId,
            "questions": questions,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }

        # Store question set in database
        await col("question_sets").insert_one(doc)

        # Return structured response with question set details
        return QuestionSetOut(id=doc["_id"], contentId=payload.contentId, questions=questions, metadata=metadata)

    except Exception as e:
        # Handle any errors during question generation process
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")
