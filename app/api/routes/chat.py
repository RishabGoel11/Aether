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
    active_sid = getattr(getattr(app, "session", None), "active_session_id", "default")
    session_id_str = active_sid if isinstance(active_sid, str) else "default"
    try:
        raw_response = app.chat(payload.message, session_id=payload.session_id)
        if hasattr(raw_response, "content"):
            response_text = str(raw_response.content)
        else:
            response_text = str(raw_response)
        return ChatResponse(
            response=response_text,
            session_id=session_id_str,
            success=True,
        )
    except Exception as exc:
        logger.error("Chat turn failed: %s", exc, exc_info=True)
        return ChatResponse(
            response=f"An error occurred while processing your message: {exc}",
            session_id=session_id_str,
            success=False,
            error=str(exc),
        )


@router.post("/clear")
def clear_conversation() -> dict[str, str]:
    """Clear the active conversation session."""
    app = get_application()
    app.clear_conversation()
    return {"message": "Session cleared successfully."}
