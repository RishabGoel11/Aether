from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from app.voice.models import AudioData, SpeechResult
from app.voice.tts.base import BaseTTS, TTSError


class Pyttsx3TTS(BaseTTS):
    """Local, offline Text-to-Speech synthesis backed by pyttsx3."""

    def __init__(
        self,
        voice_id: str | None = None,
        rate: int = 175,
        volume: float = 1.0,
    ) -> None:
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self._engine: Any = None

    def _get_engine(self) -> Any:
        if self._engine is not None:
            return self._engine

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            if self.voice_id:
                engine.setProperty("voice", self.voice_id)

            self._engine = engine
            return self._engine
        except Exception as exc:
            raise TTSError(f"Failed to initialize pyttsx3 TTS engine: {exc}") from exc

    def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
    ) -> SpeechResult:
        if not text or not text.strip():
            return SpeechResult(text="", duration_seconds=0.0)

        target_file = Path(output_path) if output_path else Path(tempfile.mktemp(suffix=".wav"))
        target_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            engine = self._get_engine()
            engine.save_to_file(text, str(target_file))
            engine.runAndWait()

            audio_bytes = target_file.read_bytes() if target_file.exists() else b""
            audio_data = AudioData(
                data=audio_bytes,
                path=str(target_file),
                format="wav",
                duration_seconds=len(text) * 0.06,
            )

            return SpeechResult(
                text=text,
                audio_data=audio_data,
                duration_seconds=audio_data.duration_seconds,
                voice=self.voice_id or "default",
            )
        except Exception as exc:
            raise TTSError(f"TTS synthesis failed for text: '{text[:50]}...': {exc}") from exc

    def speak(self, text: str) -> None:
        if not text or not text.strip():
            return

        try:
            engine = self._get_engine()
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            raise TTSError(f"TTS playback failed: {exc}") from exc
