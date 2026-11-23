"""
Chat endpoint for the Aether REST API.
"""

from __future__ import annotations

import logging
from threading import Lock

from fastapi import APIRouter, Depends

from app.api.auth import verify_api_key
from app.api.models import ChatRequest, ChatResponse, SessionId
from app.bootstrap.application import Application
from app.bootstrap.builder import ApplicationBuilder
from app.core.exceptions import LLMConnectionError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"], dependencies=[Depends(verify_api_key)])

_app_instance: Application | None = None
_app_lock = Lock()


def get_application() -> Application:
    """Singleton getter for the Aether Application instance."""
    global _app_instance
    with _app_lock:
        if _app_instance is None:
            _app_instance = ApplicationBuilder().build()
        return _app_instance


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Send a message to Aether and receive an intelligent response."""
    session_id_str = payload.session_id or "default"
    try:
        app = get_application()
        active_sid = app.session.active_session_id
        if not payload.session_id and isinstance(active_sid, str):
            session_id_str = active_sid
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
        error = (
            "Could not connect to Ollama. Start Ollama and try again."
            if isinstance(exc, LLMConnectionError)
            else "Check the Aether server logs for details."
        )
        return ChatResponse(
            response=f"Could not process your message. {error}",
            session_id=session_id_str,
            success=False,
            error=error,
        )


@router.post("/clear")
def clear_conversation(session_id: SessionId | None = None) -> dict[str, str]:
    """Clear the specified conversation, or the active one if omitted."""
    app = get_application()
    if session_id is None:
        app.clear_conversation()
    else:
        app.clear_conversation(session_id)
    return {"message": "Session cleared successfully."}
