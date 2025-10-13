"""
Content Generation Router

Handles API endpoints for generating educational content using AI.
Includes caching mechanism to avoid redundant API calls and content moderation
to prevent inappropriate requests.
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime
from bson import ObjectId

from ..schemas import ContentRequest, ContentOut, GeneratedContent
from agents.content_generator import ContentGeneratorAgent
from ..auth import get_current_user
from ..database import col
from ..plan import ensure_content_quota, record_content_generation
from utils.nlp_processor import NLPProcessor
from utils.security import SecurityManager
from ..config import PRIVACY_MODE, REDACT_CONTENT, ENABLE_ANALYTICS
from ..vector import (
    search_similar,
    add_to_index,
    has_index,
    search_similar_content,
    add_content_to_index,
)
from utils.text_utils import content_hash
from ..analytics import log_event

router = APIRouter(prefix="/content", tags=["content"])

# Initialize agent and NLP processor once per process
_content_agent = ContentGeneratorAgent()  # Handles AI content generation
_nlp_processor = NLPProcessor()  # Handles text processing, embeddings, and moderation
_security = SecurityManager()

@router.post("/generate", response_model=ContentOut)
async def generate_content(payload: ContentRequest, response: Response, user=Depends(get_current_user)) -> ContentOut:
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
        # Explicitly disable caching at HTTP level (browser/proxies)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        # Step 1: Enforce plan quota for free users
        await ensure_content_quota(user.get("sub"))

        # Step 2: Create query strings
        # Full query for moderation/logging, but use a leaner "similarity_basis" for cache matching
        objectives_str = ' '.join(payload.learningObjectives or [])
        query = f"{payload.topic} {payload.difficulty} {payload.subject} {payload.contentType} {objectives_str}".strip()
        similarity_basis = f"{payload.topic} {objectives_str}".strip()

        # Step 2.1: Basic validation that topic/query is meaningful
        topic_validation = _security.validate_input(payload.topic or '', input_type='topic')
        if not topic_validation.get('is_valid', False):
            raise HTTPException(status_code=400, detail=f"Invalid topic: {', '.join(topic_validation.get('errors', ['Invalid input']))}")

        if not _nlp_processor.is_meaningful_query(payload.topic):
            raise HTTPException(status_code=400, detail="Topic is too short or not meaningful. Please provide a clearer topic.")

        # Step 3: Moderate content for safety before processing
        moderation_result = _nlp_processor.moderate_content(query)
        if not moderation_result["safe"]:
            raise HTTPException(
                status_code=400,
                detail=f"Content request rejected: {moderation_result['reason']}. Please ensure your query aligns with educational and safe topics."
            )
        # Additional privacy check: detect PII in user-supplied query and block
        pii = _security.detect_pii(query)
        if pii:
            # In STRICT mode, always reject; in BALANCED, reject for content generation requests
            raise HTTPException(
                status_code=400,
                detail="Your request appears to include personal or sensitive information (PII). Please remove private details before generating content."
            )

    # Step 4: Prepare for similarity search using semantic index if available
    # We'll still compute text-based similarity as a fallback/second-pass filter

        # Step 5: Check for similar cached content globally (across all users)
        cached_collection = col("generated_content")
        cached_docs = []
        similar_ids = []
        similar_scores = []
        # If vector index exists, query top-K candidates to avoid scanning entire collection
        if has_index():
            similar_ids, similar_scores = search_similar(similarity_basis, k=10)
            if similar_ids:
                try:
                    obj_ids = [ObjectId(s) for s in similar_ids]
                except Exception:
                    obj_ids = []
                if obj_ids:
                    cached_docs = await cached_collection.find({"_id": {"$in": obj_ids}}).to_list(length=None)
        if not cached_docs:
            # Fallback: scan all (less efficient but safe)
            cached_docs = await cached_collection.find().to_list(length=None)

        user_id = user.get("sub")
        best_match = None
        best_similarity = 0.0
        # Set higher threshold for shorter queries to avoid spurious matches
        token_count = len(_nlp_processor.tokenize_meaningful(payload.topic))
        threshold = 0.88 if token_count >= 3 else 0.97
        vector_active = bool(similar_ids)
        # If no vector signal is available, slightly relax threshold to avoid false negatives
        if not vector_active:
            threshold = max(0.80, threshold - 0.05)

        # Search through candidates for best semantic match
        norm_basis = ' '.join((similarity_basis or '').lower().split())
        for doc in cached_docs:
            # Prefer robust TF-IDF text similarity over legacy embedding alignment
            doc_basis = doc.get("similarity_basis", doc.get("topic", ""))
            norm_doc_basis = ' '.join((doc_basis or '').lower().split())
            if norm_basis and norm_doc_basis and norm_basis == norm_doc_basis:
                similarity = 1.0
            else:
                text_sim = _nlp_processor.compute_semantic_similarity_texts(
                    similarity_basis,
                    doc_basis
                )
            # Blend with token Jaccard to penalize mismatched vocabularies further
                jaccard = _nlp_processor.token_jaccard_similarity(
                    payload.topic,
                    doc.get("topic", doc_basis)
                )
                # Optionally blend in vector score if available
                vec_boost = 0.0
                if similar_ids:
                    try:
                        idx = similar_ids.index(doc.get("_id"))
                        vec_boost = max(0.0, min(1.0, similar_scores[idx]))
                    except ValueError:
                        vec_boost = 0.0
                # Dynamic weights: sum to 1.0 with/without vector signal
                if vec_boost > 0.0:
                    similarity = 0.55 * text_sim + 0.25 * jaccard + 0.20 * vec_boost
                else:
                    similarity = 0.75 * text_sim + 0.25 * jaccard

            # Track the best match above threshold
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = doc

        # Step 6: If cache hit, return cached content
        if best_match:
            content_text = best_match["content"]
            # Ensure redaction on return even for historical cached items
            if REDACT_CONTENT:
                content_text = _security.redact_pii(content_text)
            metadata = {
                "subject": payload.subject,
                "difficulty": payload.difficulty,
                "content_type": payload.contentType,
                "learning_objectives": payload.learningObjectives,
                "cached": True,  # Indicate this came from cache
                "similarity": best_similarity  # How similar the cached content was
            }
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="content_generate_reuse",
                        properties={
                            "topic": payload.topic,
                            "subject": payload.subject,
                            "difficulty": payload.difficulty,
                            "contentType": payload.contentType,
                            "similarity": best_similarity,
                        },
                        path="/content/generate",
                    )
                except Exception:
                    pass
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
        if ENABLE_ANALYTICS:
            try:
                await log_event(
                    user_id=user_id,
                    name="content_generate_request",
                    properties={
                        "topic": payload.topic,
                        "subject": payload.subject,
                        "difficulty": payload.difficulty,
                        "contentType": payload.contentType,
                    },
                    path="/content/generate",
                )
            except Exception:
                pass

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

        # Redact any PII in generated content before persisting
        if REDACT_CONTENT:
            content_text = _security.redact_pii(content_text)

        # Step 8.1: Content-level deduplication before caching
        c_hash = content_hash(content_text)
        existing = await cached_collection.find_one({"content_hash": c_hash})
        if existing:
            # Reuse exact duplicate content and skip caching
            content_text = existing.get("content", content_text)
            if REDACT_CONTENT:
                content_text = _security.redact_pii(content_text)
            metadata["cached"] = True
            metadata["canonical_id"] = str(existing.get("_id"))
            metadata["dedup_method"] = "hash"
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="content_generate_reuse",
                        properties={
                            "topic": payload.topic,
                            "method": "hash",
                        },
                        path="/content/generate",
                    )
                except Exception:
                    pass
            doc_id = str(uuid4())
            await col("content").insert_one({
                "_id": doc_id,
                "userId": user_id,
                "topic": payload.topic,
                "content": content_text,
                "metadata": metadata,
                "createdAt": datetime.utcnow().isoformat(),
            })
            await record_content_generation(user_id)
            return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)

        # Try semantic content deduplication using content index (best-effort)
        try:
            cand_ids, cand_scores = search_similar_content(content_text, k=5)
        except Exception:
            cand_ids, cand_scores = [], []
        if cand_ids:
            try:
                obj_ids = [ObjectId(s) for s in cand_ids]
            except Exception:
                obj_ids = []
            if obj_ids:
                candidates = await cached_collection.find({"_id": {"$in": obj_ids}}, {"content": 1}).to_list(length=None)
                # Verify with TF-IDF cosine on content
                best_c, best_c_sim = None, 0.0
                for c_doc in candidates:
                    txt_sim = _nlp_processor.compute_semantic_similarity_texts(content_text, c_doc.get("content", ""))
                    if txt_sim > best_c_sim:
                        best_c_sim, best_c = txt_sim, c_doc
                if best_c and best_c_sim >= 0.93:
                    content_text = best_c.get("content", content_text)
                    if REDACT_CONTENT:
                        content_text = _security.redact_pii(content_text)
                    metadata["cached"] = True
                    metadata["canonical_id"] = str(best_c.get("_id"))
                    metadata["dedup_method"] = "content"
                    if ENABLE_ANALYTICS:
                        try:
                            await log_event(
                                user_id=user_id,
                                name="content_generate_reuse",
                                properties={
                                    "topic": payload.topic,
                                    "method": "content",
                                    "content_similarity": best_c_sim,
                                },
                                path="/content/generate",
                            )
                        except Exception:
                            pass
                    doc_id = str(uuid4())
                    await col("content").insert_one({
                        "_id": doc_id,
                        "userId": user_id,
                        "topic": payload.topic,
                        "content": content_text,
                        "metadata": metadata,
                        "createdAt": datetime.utcnow().isoformat(),
                    })
                    await record_content_generation(user_id)
                    return ContentOut(id=doc_id, topic=payload.topic, content=content_text, metadata=metadata)

        # Step 9: Save to global cache for future requests
        cache_doc = {
            "query": query,
            # embedding field kept for backward compatibility; will be vector-backed via index service
            "embedding": None,
            "content": content_text,
            "topic": payload.topic,
            "similarity_basis": similarity_basis,
            "difficulty": payload.difficulty,
            "objectives": payload.learningObjectives,
            "similarity_threshold": threshold,
            "created_at": datetime.utcnow().isoformat(),
            "content_hash": c_hash,
        }
        # Only cache if topic is meaningful enough (avoid caching noise)
        if _nlp_processor.is_meaningful_query(payload.topic):
            res = await cached_collection.insert_one(cache_doc)
            # Add to vector index in background (best-effort)
            try:
                add_to_index(str(res.inserted_id), similarity_basis)
            except Exception:
                pass
            try:
                add_content_to_index(str(res.inserted_id), content_text)
            except Exception:
                pass
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="content_generate_success",
                        properties={
                            "topic": payload.topic,
                            "subject": payload.subject,
                            "difficulty": payload.difficulty,
                            "contentType": payload.contentType,
                            "cached": False,
                        },
                        path="/content/generate",
                    )
                except Exception:
                    pass

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
async def get_content_by_id(id: str, response: Response, user=Depends(get_current_user)) -> ContentOut:
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
        # Explicitly disable caching at HTTP level (browser/proxies)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        # Find content by ID and ensure user owns it
        doc = await col("content").find_one({"_id": id, "userId": user.get("sub")})
        if not doc:
            raise HTTPException(status_code=404, detail="Content not found")
        # Redact on return if enabled to ensure legacy items don't leak PII
        returned_content = doc.get("content", "")
        if REDACT_CONTENT:
            returned_content = _security.redact_pii(returned_content)
        return ContentOut(
            id=doc.get("_id"),
            topic=doc.get("topic", ""),
            content=returned_content,
            metadata=doc.get("metadata", {}) or {},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {e}")
