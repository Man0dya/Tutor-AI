from typing import Optional
import motor.motor_asyncio
from fastapi import HTTPException
from .config import MONGODB_URI, MONGODB_DB

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None
_db_error: Optional[str] = None

async def init_db():
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
        # Ensure indices
        try:
            await _db.users.create_index("email", unique=True)
        except Exception:
            # Index creation errors should not crash the app
            pass
    except Exception as e:
        # Could not connect to DB; continue without DB to keep API up
        _client = None
        _db = None
        _db_error = str(e)

async def close_db():
    global _client
    if _client:
        _client.close()

def get_db():
    if _db is None:
        hint = "Database unavailable. Check MONGODB_URI, credentials, and IP allowlist."
        if _db_error:
            hint += f" Cause: {_db_error}"
        raise HTTPException(status_code=503, detail=hint)
    return _db

def is_db_connected() -> bool:
    return _db is not None

def col(name: str):
    if _db is None:
        hint = "Database unavailable. Check MONGODB_URI, credentials, and IP allowlist."
        if _db_error:
            hint += f" Cause: {_db_error}"
        raise HTTPException(status_code=503, detail=hint)
    return _db[name]

def db_status() -> dict:
    return {"connected": _db is not None, "error": _db_error}
