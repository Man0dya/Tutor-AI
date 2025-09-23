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

app = FastAPI(title="Tutor-AI API", version="0.1.0")

# CORS for future React app and local Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/health")
async def health():
    status = {"status": "ok", "mongo": is_db_connected()}
    status.update({"db": db_status()})
    return status

# Routers
app.include_router(auth_router)
app.include_router(content_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(progress_router)

if __name__ == "__main__":
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
