"""
Tutor AI Backend Server

This is the main entry point for the FastAPI backend of the Tutor AI application.
It sets up the web server, includes all API routers, handles CORS, database connections,
and provides health check endpoints.

Features:
- FastAPI for high-performance async APIs
- MongoDB integration via Motor
- JWT-based authentication
- CORS support for frontend integration
- Automatic API documentation via Swagger/OpenAPI
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, close_db, is_db_connected, db_status
from .config import ALLOWED_ORIGINS
from .routers.auth import router as auth_router
from .routers.content import router as content_router
from .routers.questions import router as questions_router
from .routers.answers import router as answers_router
from .routers.progress import router as progress_router
from .routers.billing import router as billing_router

# Create FastAPI application instance with metadata
app = FastAPI(
    title="Tutor-AI API",
    version="0.1.0",
    description="AI-powered tutoring system with content generation, question creation, and feedback evaluation"
)

# Configure CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],  # Allow specified origins or all in dev
    allow_credentials=True,  # Allow cookies/credentials for auth
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

# Event handlers for database lifecycle
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on app startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on app shutdown"""
    await close_db()

@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring service status
    
    Returns:
        dict: Status information including database connectivity
    """
    status = {"status": "ok", "mongo": is_db_connected()}
    status.update({"db": db_status()})
    return status

# Include all feature routers
app.include_router(auth_router)       # User authentication endpoints
app.include_router(content_router)    # Content generation endpoints
app.include_router(questions_router)  # Question generation endpoints
app.include_router(answers_router)    # Answer submission and feedback
app.include_router(progress_router)   # User progress tracking
app.include_router(billing_router)    # Subscription and billing management

# Run server when executed directly (development mode)
if __name__ == "__main__":
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
