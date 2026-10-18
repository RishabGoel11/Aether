"""
FastAPI application server for Aether AI Platform.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    agent_router,
    chat_router,
    health_router,
    memory_router,
    rag_router,
    sessions_router,
    team_router,
    voice_router,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    application = FastAPI(
        title="Aether AI Engineering Platform",
        description=(
            "Local-first AI platform with RAG, ReAct reasoning, Voice, and Multi-Agent teams."
        ),
        version="0.11.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include REST API Routers
    application.include_router(health_router)
    application.include_router(chat_router)
    application.include_router(sessions_router)
    application.include_router(agent_router)
    application.include_router(team_router)
    application.include_router(rag_router)
    application.include_router(memory_router)
    application.include_router(voice_router)

    # Mount static assets if directory exists
    if STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @application.get("/", include_in_schema=False)
    async def serve_index() -> Response:
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return Response(content="Aether API Server running.", media_type="text/plain")

    @application.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> Response:
        return Response(status_code=204)

    return application


app = create_app()
