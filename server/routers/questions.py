from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from uuid import uuid4
from datetime import datetime

from ..schemas import QuestionGenRequest, QuestionSetOut
from agents.question_setter import QuestionSetterAgent
from ..auth import get_current_user
from ..database import col

router = APIRouter(prefix="/questions", tags=["questions"])

_question_agent = QuestionSetterAgent()

@router.post("/generate", response_model=QuestionSetOut)
async def generate_questions(payload: QuestionGenRequest, user=Depends(get_current_user)) -> QuestionSetOut:
    try:
        # Fetch content text for the given contentId
        content_doc = await col("content").find_one({"_id": payload.contentId})
        if not content_doc:
            raise HTTPException(status_code=404, detail="Content not found for question generation")

        content_input = {
            "content": content_doc.get("content", ""),
            "metadata": content_doc.get("metadata", {}),
            "topic": content_doc.get("topic"),
        }

        result = _question_agent.generate_questions(
            content=content_input,
            question_count=payload.questionCount,
            question_types=payload.questionTypes,
            difficulty_distribution=payload.difficultyDistribution,
            bloom_levels=payload.bloomLevels,
        )

        if isinstance(result, dict):
            questions: List[Dict[str, Any]] = result.get("questions", [])
            metadata: Dict[str, Any] = result.get("metadata", {})
        else:
            questions = result
            metadata = {}

        doc = {
            "_id": str(uuid4()),
            "userId": user.get("sub"),
            "contentId": payload.contentId,
            "questions": questions,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("question_sets").insert_one(doc)

        return QuestionSetOut(id=doc["_id"], contentId=payload.contentId, questions=questions, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")
