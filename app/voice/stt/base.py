from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.voice.models import AudioData, TranscriptionResult


class STTError(Exception):
    """Raised when speech transcription fails."""


class BaseSTT(ABC):
    """Abstract interface for Speech-to-Text (STT) transcription engines."""

    @abstractmethod
    def transcribe(
        self,
        audio: AudioData | Path | str | bytes,
        language: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio input into text."""
