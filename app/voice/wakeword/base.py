from __future__ import annotations

from abc import ABC, abstractmethod

from app.voice.models import AudioData


class BaseWakeWordDetector(ABC):
    """Abstract interface for wake word activation detection."""

    @abstractmethod
    def detect(self, input_signal: str | AudioData) -> bool:
        """Return True if wake word / activation phrase is detected."""
