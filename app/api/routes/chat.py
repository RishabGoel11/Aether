"""
Chat endpoint for the Aether REST API.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.api.auth import verify_api_key
from app.api.models import ChatRequest, ChatResponse
from app.bootstrap.application import Application
from app.bootstrap.builder import ApplicationBuilder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"], dependencies=[Depends(verify_api_key)])

_app_instance: Application | None = None


def get_application() -> Application:
    """Singleton getter for the Aether Application instance."""
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationBuilder().build()
    return _app_instance


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Send a message to Aether and receive an intelligent response."""
    app = get_application()
    try:
        response_text = app.chat(payload.message)
        return ChatResponse(response=response_text, success=True)
    except Exception as exc:
        logger.error("Chat turn failed: %s", exc, exc_info=True)
        return ChatResponse(
            response=f"An error occurred while processing your message: {exc}",
            success=False,
            error=str(exc),
        )


@router.post("/clear")
def clear_conversation() -> dict[str, str]:
    """Clear the active conversation session."""
    app = get_application()
    app.clear_conversation()
    return {"message": "Session cleared successfully."}
