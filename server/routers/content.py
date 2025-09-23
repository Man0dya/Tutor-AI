from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..schemas import ContentRequest, ContentOut
from agents.content_generator import ContentGeneratorAgent
from ..auth import get_current_user
from ..database import col

router = APIRouter(prefix="/content", tags=["content"])

# Initialize agent once per process
_content_agent = ContentGeneratorAgent()

@router.post("/generate", response_model=ContentOut)
async def generate_content(payload: ContentRequest, user=Depends(get_current_user)) -> ContentOut:
    try:
        result = _content_agent.generate_content(
            topic=payload.topic,
            difficulty=payload.difficulty,
            subject=payload.subject,
            content_type=payload.contentType,
            learning_objectives=payload.learningObjectives,
        )

        # Normalize response
        if isinstance(result, dict):
            content_text = result.get("content", str(result))
            metadata: Dict[str, Any] = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
            }
            # merge any useful metadata keys from agent output
            for k in ("key_concepts", "study_materials", "sources"):
                if k in result:
                    metadata[k] = result[k]
        else:
            content_text = str(result)
            metadata = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
            }

        doc_id = str(uuid4())
        # Persist content
        doc = {
            "_id": doc_id,
            "userId": user.get("sub"),
            "topic": payload.topic,
            "content": content_text,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("content").insert_one(doc)

        return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {e}")
