from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ..schemas import ContentRequest, ContentOut, GeneratedContent
from agents.content_generator import ContentGeneratorAgent
from ..auth import get_current_user
from ..database import col
from ..plan import ensure_content_quota, record_content_generation
from utils.nlp_processor import NLPProcessor

router = APIRouter(prefix="/content", tags=["content"])

# Initialize agent once per process
_content_agent = ContentGeneratorAgent()
_nlp_processor = NLPProcessor()

@router.post("/generate", response_model=ContentOut)
async def generate_content(payload: ContentRequest, user=Depends(get_current_user)) -> ContentOut:
    try:
        # Enforce plan quota for free users
        await ensure_content_quota(user.get("sub"))

        # Create query string for similarity check
        query = f"{payload.topic} {payload.difficulty} {payload.subject} {payload.contentType} {' '.join(payload.learningObjectives or [])}".strip()

        # Generate embedding for the query
        query_embedding = _nlp_processor.get_embedding(query)

        # Check for similar cached content globally
        cached_collection = col("generated_content")
        cached_docs = await cached_collection.find().to_list(length=None)
        
        user_id = user.get("sub")
        
        best_match = None
        best_similarity = 0.0
        threshold = 0.8  # Similarity threshold
        
        for doc in cached_docs:
            stored_embedding = doc.get("embedding", [])
            if stored_embedding and query_embedding:
                similarity = _nlp_processor.compute_semantic_similarity(query_embedding, stored_embedding)
            else:
                # Fallback to text similarity if no embedding
                similarity = _nlp_processor.compute_similarity(query, doc.get("query", ""))
            
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = doc

        if best_match:
            # Return cached content
            content_text = best_match["content"]
            metadata = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
                "cached": True,
                "similarity": best_similarity
            }
            doc_id = str(uuid4())
            # Still persist to content collection for consistency
            doc = {
                "_id": doc_id,
                "userId": user_id,
                "topic": payload.topic,
                "content": content_text,
                "metadata": metadata,
                "createdAt": datetime.utcnow().isoformat(),
            }
            await col("content").insert_one(doc)
            await record_content_generation(user_id)
            return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)

        # No cache hit, generate new content
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

        # Save to cache
        cache_doc = {
            "query": query,
            "embedding": query_embedding,
            "content": content_text,
            "topic": payload.topic,
            "difficulty": payload.difficulty,
            "objectives": payload.learningObjectives,
            "similarity_threshold": threshold,
            "created_at": datetime.utcnow().isoformat(),
        }
        await cached_collection.insert_one(cache_doc)

        doc_id = str(uuid4())
        # Persist content
        doc = {
            "_id": doc_id,
            "userId": user_id,
            "topic": payload.topic,
            "content": content_text,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("content").insert_one(doc)
        # Record successful content generation towards quota
        await record_content_generation(user_id)
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
