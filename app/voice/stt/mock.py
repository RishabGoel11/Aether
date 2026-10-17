from __future__ import annotations

from pathlib import Path

from app.voice.models import AudioData, TranscriptionResult
from app.voice.stt.base import BaseSTT


class MockSTT(BaseSTT):
    """Predictable mock STT engine for automated testing."""

    def __init__(
        self, default_text: str = "Hello Aether, tell me about your architecture."
    ) -> None:
        self.default_text = default_text
        self.transcribed_count = 0

    def transcribe(
        self,
        audio: AudioData | Path | str | bytes,
        language: str | None = None,
    ) -> TranscriptionResult:
        self.transcribed_count += 1
        return TranscriptionResult(
            text=self.default_text,
            language=language or "en",
            confidence=0.98,
            duration_seconds=2.5,
            metadata={"mock": True, "call_count": self.transcribed_count},
        )
