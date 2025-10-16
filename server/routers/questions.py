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
import hashlib
import json

from ..schemas import QuestionGenRequest, QuestionSetOut
from agents.question_setter import QuestionSetterAgent
from ..auth import get_current_user
from ..database import col
from ..plan import require_paid_feature
from utils.security import SecurityManager
from utils.nlp_processor import NLPProcessor
from ..config import PRIVACY_MODE, REDACT_QUESTIONS, ENABLE_ANALYTICS
from ..analytics import log_event

# Create router with questions prefix and tags for API documentation
router = APIRouter(prefix="/questions", tags=["questions"])

# Initialize question generation agent (singleton pattern for efficiency)
_question_agent = QuestionSetterAgent()
_security = SecurityManager()
_nlp_processor = NLPProcessor()

@router.post("/generate", response_model=QuestionSetOut)
async def generate_questions(payload: QuestionGenRequest, user=Depends(get_current_user)) -> QuestionSetOut:
    """
    Generate a set of questions from educational content with caching support.

    This endpoint creates customized question sets from user content using AI-powered
    question generation. It first checks for cached question sets with similar parameters
    to avoid redundant generation, improving response time and reducing API costs.

    Caching Strategy:
    - Uses contentId + question parameters (count, types, difficulty, bloom levels) as similarity basis
    - Searches generated_questions collection for matching cached sets
    - Returns cached set if high similarity match found
    - Generates and caches new set if no match
    - Both cached and newly generated sets are stored in user's question_sets collection

    Args:
        payload (QuestionGenRequest): Question generation parameters
        user: Current authenticated user information from JWT token

    Returns:
        QuestionSetOut: Generated or cached question set with metadata

    Raises:
        HTTPException: 403 if user doesn't have paid plan, 404 if content not found,
                      500 for question generation failures
    """
    try:
        # Validate user has access to paid features (Standard/Premium plans)
        await require_paid_feature(user.get("sub"))

        # Retrieve the source content document for question generation
        content_doc = await col("content").find_one({"_id": payload.contentId})
        if not content_doc:
            raise HTTPException(status_code=404, detail="Content not found for question generation")

        # In STRICT privacy mode, block when the source content contains PII
        if PRIVACY_MODE == 'STRICT':
            if _security.detect_pii(content_doc.get("content", "")):
                raise HTTPException(status_code=400, detail="Source content contains personal information. Please remove private details before generating questions.")

        user_id = user.get("sub")

        # Create similarity basis for cache matching (contentId + parameters)
        # This identifies "same content with same requirements"
        question_types_str = ','.join(sorted(payload.questionTypes or []))
        bloom_levels_str = ','.join(sorted(payload.bloomLevels or []))
        diff_dist = payload.difficultyDistribution or {}
        diff_str = f"E{diff_dist.get('Easy', 0.3)}_M{diff_dist.get('Medium', 0.5)}_H{diff_dist.get('Hard', 0.2)}"
        
        similarity_basis = f"{payload.contentId}|count:{payload.questionCount}|types:{question_types_str}|bloom:{bloom_levels_str}|diff:{diff_str}"
        
        # Create a hash of the parameters for exact matching
        params_dict = {
            "contentId": payload.contentId,
            "questionCount": payload.questionCount,
            "questionTypes": sorted(payload.questionTypes or []),
            "difficultyDistribution": diff_dist,
            "bloomLevels": sorted(payload.bloomLevels or [])
        }
        params_hash = hashlib.sha256(json.dumps(params_dict, sort_keys=True).encode()).hexdigest()

        # Step 1: Check global cache for similar question sets
        cached_collection = col("generated_questions")
        
        # Try exact match first (same parameters)
        cached_exact = await cached_collection.find_one({"question_params_hash": params_hash})
        
        if cached_exact:
            # Exact match found - reuse immediately
            questions = cached_exact.get("questions", [])
            metadata = cached_exact.get("metadata", {})
            metadata["cached"] = True
            metadata["cache_match"] = "exact"
            
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="question_generate_reuse",
                        properties={
                            "contentId": payload.contentId,
                            "questionCount": payload.questionCount,
                            "cache_match": "exact"
                        },
                        path="/questions/generate",
                    )
                except Exception:
                    pass
            
            # Store in user's question_sets collection for tracking
            doc_id = str(uuid4())
            doc = {
                "_id": doc_id,
                "userId": user_id,
                "contentId": payload.contentId,
                "questions": questions,
                "metadata": metadata,
                "createdAt": datetime.utcnow().isoformat(),
            }
            await col("question_sets").insert_one(doc)
            
            return QuestionSetOut(id=doc_id, contentId=payload.contentId, questions=questions, metadata=metadata)

        # Step 2: Try fuzzy match (similar contentId, close parameters)
        # For question sets, we're more strict than content - parameters matter
        cached_similar = await cached_collection.find({"contentId": payload.contentId}).to_list(length=None)
        
        best_match = None
        best_similarity = 0.0
        threshold = 0.90  # High threshold for question sets since parameters are specific
        
        for doc in cached_similar:
            # Compare parameters using text similarity
            doc_basis = doc.get("similarity_basis", "")
            if not doc_basis:
                continue
                
            # Simple token overlap similarity for parameter matching
            basis_tokens = set(similarity_basis.lower().split('|'))
            doc_tokens = set(doc_basis.lower().split('|'))
            
            if basis_tokens and doc_tokens:
                overlap = len(basis_tokens & doc_tokens)
                total = len(basis_tokens | doc_tokens)
                similarity = overlap / total if total > 0 else 0.0
                
                # Boost if question count matches exactly
                if doc.get("questionCount") == payload.questionCount:
                    similarity += 0.1
                
                if similarity > threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = doc
        
        # Step 3: If good match found, return cached
        if best_match:
            questions = best_match.get("questions", [])
            metadata = best_match.get("metadata", {})
            metadata["cached"] = True
            metadata["cache_match"] = "similar"
            metadata["similarity"] = best_similarity
            
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="question_generate_reuse",
                        properties={
                            "contentId": payload.contentId,
                            "questionCount": payload.questionCount,
                            "cache_match": "similar",
                            "similarity": best_similarity
                        },
                        path="/questions/generate",
                    )
                except Exception:
                    pass
            
            # Store in user's question_sets collection
            doc_id = str(uuid4())
            doc = {
                "_id": doc_id,
                "userId": user_id,
                "contentId": payload.contentId,
                "questions": questions,
                "metadata": metadata,
                "createdAt": datetime.utcnow().isoformat(),
            }
            await col("question_sets").insert_one(doc)
            
            return QuestionSetOut(id=doc_id, contentId=payload.contentId, questions=questions, metadata=metadata)

        # Step 4: Cache miss - generate new questions
        if ENABLE_ANALYTICS:
            try:
                await log_event(
                    user_id=user_id,
                    name="question_generate_request",
                    properties={
                        "contentId": payload.contentId,
                        "questionCount": payload.questionCount,
                        "questionTypes": payload.questionTypes,
                    },
                    path="/questions/generate",
                )
            except Exception:
                pass

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

        # Optionally redact any PII in the questions and metadata before storing/returning
        if REDACT_QUESTIONS:
            try:
                questions = _security.redact_pii_in_obj(questions)
                metadata = _security.redact_pii_in_obj(metadata)
            except Exception:
                pass

        # Step 5: Store in global cache for future reuse (across all users)
        cache_doc = {
            "contentId": payload.contentId,
            "similarity_basis": similarity_basis,
            "question_params_hash": params_hash,
            "questionCount": payload.questionCount,
            "questionTypes": payload.questionTypes,
            "difficultyDistribution": payload.difficultyDistribution,
            "bloomLevels": payload.bloomLevels,
            "questions": questions,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        try:
            await cached_collection.insert_one(cache_doc)
            if ENABLE_ANALYTICS:
                try:
                    await log_event(
                        user_id=user_id,
                        name="question_generate_success",
                        properties={
                            "contentId": payload.contentId,
                            "questionCount": payload.questionCount,
                            "cached": False,
                        },
                        path="/questions/generate",
                    )
                except Exception:
                    pass
        except Exception:
            # Cache insert failure should not break the flow
            pass

        # Step 6: Store in user's question_sets collection
        doc_id = str(uuid4())
        doc = {
            "_id": doc_id,
            "userId": user_id,
            "contentId": payload.contentId,
            "questions": questions,
            "metadata": metadata,
            "createdAt": datetime.utcnow().isoformat(),
        }
        await col("question_sets").insert_one(doc)

        return QuestionSetOut(id=doc_id, contentId=payload.contentId, questions=questions, metadata=metadata)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")
