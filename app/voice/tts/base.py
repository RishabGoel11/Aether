from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.voice.models import SpeechResult


class TTSError(Exception):
    """Raised when speech synthesis fails."""


class BaseTTS(ABC):
    """Abstract interface for Text-to-Speech (TTS) synthesis engines."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
    ) -> SpeechResult:
        """Synthesize text into speech audio."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the text aloud through the default audio output device."""
