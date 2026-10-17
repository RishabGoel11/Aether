from __future__ import annotations

from pathlib import Path

from app.voice.models import AudioData, SpeechResult
from app.voice.tts.base import BaseTTS


class MockTTS(BaseTTS):
    """Predictable mock TTS engine for automated testing."""

    def __init__(self, voice: str = "mock-voice") -> None:
        self.voice = voice
        self.spoken_texts: list[str] = []

    def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
    ) -> SpeechResult:
        self.spoken_texts.append(text)
        dummy_audio = AudioData(
            data=b"RIFFmockwavdata",
            path=str(output_path) if output_path else None,
            format="wav",
            duration_seconds=len(text) * 0.05,
        )
        if output_path:
            Path(output_path).write_bytes(dummy_audio.data)

        return SpeechResult(
            text=text,
            audio_data=dummy_audio,
            duration_seconds=dummy_audio.duration_seconds,
            voice=self.voice,
        )

    def speak(self, text: str) -> None:
        self.spoken_texts.append(text)
