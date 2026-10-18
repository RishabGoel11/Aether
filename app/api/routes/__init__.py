"""
REST API route definitions.
"""

from app.api.routes.agent import router as agent_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.memory import router as memory_router
from app.api.routes.rag import router as rag_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.team import router as team_router
from app.api.routes.voice import router as voice_router

__all__ = [
    "agent_router",
    "chat_router",
    "health_router",
    "memory_router",
    "rag_router",
    "sessions_router",
    "team_router",
    "voice_router",
]
