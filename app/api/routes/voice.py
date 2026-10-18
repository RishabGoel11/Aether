from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.auth import verify_api_key
from app.api.models import ListenRequest, SpeakRequest, SpeakResponse, VoiceListenResponse
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


@router.post("/listen", response_model=VoiceListenResponse)
def listen(payload: ListenRequest) -> VoiceListenResponse:
    """Record microphone audio from the host machine and transcribe it with Whisper."""
    app = get_application()
    if not app.voice:
        raise HTTPException(status_code=500, detail="Voice pipeline is not initialized.")

    try:
        audio = app.voice.listen(duration=payload.duration, until_silence=payload.until_silence)
        transcription = app.voice.transcribe(audio)
        user_text = transcription.text.strip()

        reply_text = None
        if payload.process_turn and user_text:
            raw_response = app.chat(user_text)
            reply_text = (
                raw_response.content if hasattr(raw_response, "content") else str(raw_response)
            )
            try:
                app.voice.speak(reply_text)
            except Exception:
                pass

        return VoiceListenResponse(
            text=user_text,
            success=True,
            reply=reply_text,
        )
    except Exception as exc:
        return VoiceListenResponse(
            text="",
            success=False,
            error=str(exc),
        )


@router.post("/transcribe", response_model=VoiceListenResponse)
async def transcribe_audio_file(file: UploadFile = File(...)) -> VoiceListenResponse:
    """Transcribe an uploaded audio file (WAV, MP3, etc.) using Whisper."""
    app = get_application()
    if not app.voice:
        raise HTTPException(status_code=500, detail="Voice pipeline is not initialized.")

    try:
        content = await file.read()
        transcription = app.voice.transcribe(content)
        return VoiceListenResponse(
            text=transcription.text.strip(),
            success=True,
        )
    except Exception as exc:
        return VoiceListenResponse(
            text="",
            success=False,
            error=str(exc),
        )


@router.get("/devices")
def list_devices() -> list[dict[str, Any]]:
    """List detected microphone audio input devices."""
    app = get_application()
    if not app.voice:
        return []
    return app.voice.list_input_devices()
