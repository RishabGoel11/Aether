"""
Session management endpoints for multi-session chat switching.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.auth import verify_api_key
from app.api.models import (
    CreateSessionRequest,
    SessionDetailResponse,
    SessionListResponse,
    SessionSummary,
)
from app.api.routes.chat import get_application

router = APIRouter(
    prefix="/api/sessions",
    tags=["Sessions"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=SessionListResponse)
def list_sessions() -> SessionListResponse:
    """List all available conversation sessions."""
    app = get_application()
    sessions_data = app.list_sessions()
    summaries = [SessionSummary.model_validate(s) for s in sessions_data]
    return SessionListResponse(
        active_session_id=app.session.active_session_id,
        sessions=summaries,
    )


@router.post("", response_model=SessionSummary)
def create_session(payload: CreateSessionRequest) -> SessionSummary:
    """Create a new chat session and make it active."""
    app = get_application()
    new_id = app.create_session(title=payload.title)
    all_sessions = app.list_sessions()
    for s in all_sessions:
        if s["id"] == new_id:
            return SessionSummary.model_validate(s)
    return SessionSummary(
        id=new_id,
        title=payload.title,
        message_count=0,
        created_at="",
        updated_at="",
        active=True,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str) -> SessionDetailResponse:
    """Retrieve full message history for a specific session."""
    app = get_application()
    all_sessions = app.list_sessions()
    title = session_id
    for s in all_sessions:
        if s["id"] == session_id:
            title = s["title"]
            break

    session = app.session.load(session_id)
    messages = [
        {
            "role": getattr(m.role, "value", str(m.role)),
            "content": m.content,
        }
        for m in session.get_messages()
    ]
    return SessionDetailResponse(
        id=session_id,
        title=title,
        active=(session_id == app.session.active_session_id),
        messages=messages,
    )


@router.post("/{session_id}/activate", response_model=SessionDetailResponse)
def activate_session(session_id: str) -> SessionDetailResponse:
    """Switch active conversation to the specified session."""
    app = get_application()
    session = app.switch_session(session_id)
    all_sessions = app.list_sessions()
    title = session_id
    for s in all_sessions:
        if s["id"] == session_id:
            title = s["title"]
            break

    messages = [
        {
            "role": getattr(m.role, "value", str(m.role)),
            "content": m.content,
        }
        for m in session.get_messages()
    ]
    return SessionDetailResponse(
        id=session_id,
        title=title,
        active=True,
        messages=messages,
    )


@router.delete("/{session_id}")
def delete_session(session_id: str) -> dict[str, Any]:
    """Delete a conversation session."""
    app = get_application()
    success = app.delete_session(session_id)
    return {
        "id": session_id,
        "deleted": success,
        "active_session_id": app.session.active_session_id,
    }
