"""
Content Generation Router

Handles API endpoints for generating educational content using AI.
Includes caching mechanism to avoid redundant API calls and content moderation
to prevent inappropriate requests.
"""

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

# Initialize agent and NLP processor once per process
_content_agent = ContentGeneratorAgent()  # Handles AI content generation
_nlp_processor = NLPProcessor()  # Handles text processing, embeddings, and moderation

@router.post("/generate", response_model=ContentOut)
async def generate_content(payload: ContentRequest, user=Depends(get_current_user)) -> ContentOut:
    """
    Generate educational content based on user request.
    
    This endpoint:
    1. Checks user quota and moderates content for safety
    2. Searches cache for similar existing content
    3. Generates new content if no cache hit
    4. Stores result in cache for future use
    
    Args:
        payload: Content generation parameters
        user: Authenticated user info
        
    Returns:
        Generated content with metadata
        
    Raises:
        HTTPException: For quota exceeded, unsafe content, or generation errors
    """
    try:
        # Step 1: Enforce plan quota for free users
        await ensure_content_quota(user.get("sub"))

        # Step 2: Create query string for similarity check and moderation
        query = f"{payload.topic} {payload.difficulty} {payload.subject} {payload.contentType} {' '.join(payload.learningObjectives or [])}".strip()

        # Step 3: Moderate content for safety before processing
        moderation_result = _nlp_processor.moderate_content(query)
        if not moderation_result["safe"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Content request rejected: {moderation_result['reason']}. Please ensure your query aligns with educational and safe topics."
            )

        # Step 4: Generate embedding for semantic similarity search
        query_embedding = _nlp_processor.get_embedding(query)

        # Step 5: Check for similar cached content globally (across all users)
        cached_collection = col("generated_content")
        cached_docs = await cached_collection.find().to_list(length=None)
        
        user_id = user.get("sub")
        best_match = None
        best_similarity = 0.0
        threshold = 0.8  # Similarity threshold for cache hit
        
        # Search through cached content for best semantic match
        for doc in cached_docs:
            stored_embedding = doc.get("embedding", [])
            if stored_embedding and query_embedding:
                # Use semantic similarity (cosine) if embeddings available
                similarity = _nlp_processor.compute_semantic_similarity(query_embedding, stored_embedding)
            else:
                # Fallback to text similarity if no embeddings
                similarity = _nlp_processor.compute_similarity(query, doc.get("query", ""))
            
            # Track the best match above threshold
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = doc

        # Step 6: If cache hit, return cached content
        if best_match:
            content_text = best_match["content"]
            metadata = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
                "cached": True,  # Indicate this came from cache
                "similarity": best_similarity  # How similar the cached content was
            }
            doc_id = str(uuid4())
            # Still persist to content collection for user-specific tracking
            doc = {
                "_id": doc_id,
                "userId": user_id,
                "topic": payload.topic,
                "content": content_text,
                "metadata": metadata,
                "createdAt": datetime.utcnow().isoformat(),
            }
            await col("content").insert_one(doc)
            # Record quota usage
            await record_content_generation(user_id)
            return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)

        # Step 7: Cache miss - generate new content via AI
        result = _content_agent.generate_content(
            topic=payload.topic,
            difficulty=payload.difficulty,
            subject=payload.subject,
            content_type=payload.contentType,
            learning_objectives=payload.learningObjectives,
        )

        # Step 8: Process and normalize the AI response
        if isinstance(result, dict):
            content_text = result.get("content", str(result))
            metadata: Dict[str, Any] = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
            }
            # Merge any additional metadata from AI response
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

        # Step 9: Save to global cache for future requests
        cache_doc = {
            "query": query,
            "embedding": query_embedding,  # Store embedding for similarity search
            "content": content_text,
            "topic": payload.topic,
            "difficulty": payload.difficulty,
            "objectives": payload.learningObjectives,
            "similarity_threshold": threshold,
            "created_at": datetime.utcnow().isoformat(),
        }
        await cached_collection.insert_one(cache_doc)

        # Step 10: Save to user-specific content collection
        doc_id = str(uuid4())
        doc = {
            "_id": doc_id,
            "userId": user_id,
            "topic": payload.topic,
            "content": content_text,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("content").insert_one(doc)
        # Record quota usage
        await record_content_generation(user_id)
        return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)
    except HTTPException:
        # Re-raise explicit HTTP errors (quota, moderation)
        raise
    except Exception as e:
        # Catch unexpected errors and return 500
        raise HTTPException(status_code=500, detail=f"Content generation failed: {e}")


@router.get("/{id}", response_model=ContentOut)
async def get_content_by_id(id: str, user=Depends(get_current_user)) -> ContentOut:
    """
    Retrieve specific content by ID for the authenticated user.
    
    Args:
        id: Content document ID
        user: Authenticated user info
        
    Returns:
        Content details
        
    Raises:
        HTTPException: If content not found or access denied
    """
    try:
        # Find content by ID and ensure user owns it
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
