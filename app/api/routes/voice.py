"""
Voice synthesis and device endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import verify_api_key
from app.api.models import SpeakRequest, SpeakResponse
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api/voice", tags=["Voice"], dependencies=[Depends(verify_api_key)])


@router.post("/speak", response_model=SpeakResponse)
def speak(payload: SpeakRequest) -> SpeakResponse:
    """Vocalize text aloud via the offline TTS engine."""
    app = get_application()
    if not app.voice:
        raise HTTPException(status_code=500, detail="Voice pipeline is not initialized.")

    try:
        app.voice.speak(payload.text)
        return SpeakResponse(text=payload.text, success=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/devices")
def list_devices() -> list[dict[str, Any]]:
    """List detected microphone audio input devices."""
    app = get_application()
    if not app.voice:
        return []
    return app.voice.list_input_devices()
