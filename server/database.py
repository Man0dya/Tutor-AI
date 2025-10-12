"""
Database Connection and Management for Tutor AI

This module handles MongoDB connection using Motor (async MongoDB driver).
Provides connection lifecycle management, database access functions,
and status checking for the application.
"""

from typing import Optional
import motor.motor_asyncio
from fastapi import HTTPException
from .config import MONGODB_URI, MONGODB_DB

# Global database connection variables
_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None
_db_error: Optional[str] = None

async def init_db():
    """
    Initialize database connection on application startup.
    
    Attempts to connect to MongoDB and create necessary indexes.
    If connection fails, stores error for later status checks.
    """
    global _client, _db, _db_error
    if not MONGODB_URI:
        # Allow app to start without DB for local dev; health endpoint will indicate status
        _client = None
        _db = None
        _db_error = "MONGODB_URI not set"
        return
    try:
        # Fail fast if cluster is unreachable (e.g., Atlas IP not whitelisted)
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Probe connectivity quickly
        await _client.admin.command('ping')
        _db = _client[MONGODB_DB]
        _db_error = None
        # Ensure indices for performance
        try:
            await _db.users.create_index("email", unique=True)  # Unique email constraint
            # Speed up content reads per user and by createdAt
            await _db.content.create_index([("userId", 1), ("createdAt", -1)])
            await _db.content.create_index([("_id", 1)], unique=True)
            # Global generated content matching
            await _db.generated_content.create_index([("created_at", -1)])
            await _db.generated_content.create_index([("topic", 1)])
            await _db.generated_content.create_index([("similarity_basis", 1)])
            await _db.generated_content.create_index([("content_hash", 1)])
            # Question sets retrieval
            await _db.question_sets.create_index([("userId", 1), ("createdAt", -1)])
            await _db.question_sets.create_index([("contentId", 1), ("createdAt", -1)])
            # Answers and feedback lookups
            await _db.answers.create_index([("userId", 1), ("submittedAt", -1)])
            await _db.feedback.create_index([("userId", 1), ("createdAt", -1)])
        except Exception:
            # Index creation errors should not crash the app
            pass
    except Exception as e:
        # Could not connect to DB; continue without DB to keep API up
        _client = None
        _db = None
        _db_error = str(e)

async def close_db():
    """Close database connection on application shutdown"""
    global _client
    if _client:
        _client.close()

def get_db():
    """
    Get database instance with error handling.
    
    Returns:
        Motor database instance
        
    Raises:
        HTTPException: If database is unavailable
    """
    if _db is None:
        hint = "Database unavailable. Check MONGODB_URI, credentials, and IP allowlist."
        if _db_error:
            hint += f" Cause: {_db_error}"
        raise HTTPException(status_code=503, detail=hint)
    return _db

def is_db_connected() -> bool:
    """Check if database connection is active"""
    return _db is not None

def col(name: str):
    """
    Get a database collection with error handling.
    
    Args:
        name: Collection name
        
    Returns:
        Motor collection instance
        
    Raises:
        HTTPException: If database is unavailable
    """
    if _db is None:
        hint = "Database unavailable. Check MONGODB_URI, credentials, and IP allowlist."
        if _db_error:
            hint += f" Cause: {_db_error}"
        raise HTTPException(status_code=503, detail=hint)
    return _db[name]

def db_status() -> dict:
    """
    Get detailed database status for health checks.
    
    Returns:
        dict: Connection status and error details
    """
    return {"connected": _db is not None, "error": _db_error}
