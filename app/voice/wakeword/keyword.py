from __future__ import annotations

import re

from app.voice.models import AudioData
from app.voice.wakeword.base import BaseWakeWordDetector


class KeywordWakeWordDetector(BaseWakeWordDetector):
    """Detects keyword triggers in transcribed text or audio markers."""

    def __init__(self, keywords: list[str] | None = None) -> None:
        self.keywords = [k.lower().strip() for k in (keywords or ["aether", "hey aether"])]

    def detect(self, input_signal: str | AudioData) -> bool:
        if isinstance(input_signal, AudioData):
            # When audio signal is provided without transcription, cannot match text keywords
            return False

        if not isinstance(input_signal, str):
            return False

        normalized = re.sub(r"[^\w\s]", "", input_signal.lower()).strip()
        words = normalized.split()

        for kw in self.keywords:
            kw_clean = re.sub(r"[^\w\s]", "", kw).strip()
            if kw_clean in normalized:
                return True
            if any(w == kw_clean for w in words):
                return True

        return False
