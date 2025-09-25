from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..schemas import ContentRequest, ContentOut
from agents.content_generator import ContentGeneratorAgent
from ..auth import get_current_user
from ..database import col
from ..plan import ensure_content_quota, record_content_generation

router = APIRouter(prefix="/content", tags=["content"])

# Initialize agent once per process
_content_agent = ContentGeneratorAgent()

@router.post("/generate", response_model=ContentOut)
async def generate_content(payload: ContentRequest, user=Depends(get_current_user)) -> ContentOut:
    try:
        # Enforce plan quota for free users
        await ensure_content_quota(user.get("sub"))

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
        # Record successful content generation towards quota
        await record_content_generation(user.get("sub"))
        return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)
    except HTTPException:
        # Preserve explicit HTTP errors (e.g., 402 quota exceeded)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {e}")


@router.get("/{id}", response_model=ContentOut)
async def get_content_by_id(id: str, user=Depends(get_current_user)) -> ContentOut:
    try:
        doc = await col("content").find_one({"_id": id, "userId": user.get("sub")})
        if not doc:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentOut(
            id=doc.get("_id"),
            topic=doc.get("topic", ""),
            content=doc.get("content", ""),
            metadata=doc.get("metadata", {}) or {},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {e}")
