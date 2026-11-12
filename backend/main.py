from contextlib import asynccontextmanager
from datetime import datetime, timezone
from backend.api.user_management import router as user_router

from fastapi import FastAPI

from backend.core.resources import rag
from backend.api.chat import router as chat_router
from backend.api.doc_upload import router as document_router
from backend.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        yield

    finally:
        rag.close()


app = FastAPI(
    title="Enterprise Knowledge AI",
    version="1.0.0",
    lifespan=lifespan
)




@app.get("/")
def home():
    return {
        "message": "Enterprise Knowledge AI Backend",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)


app.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["User Management"]
)