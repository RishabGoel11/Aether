from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AudioData(BaseModel):
    """Container for raw audio data and metadata."""

    data: bytes = Field(default=b"", description="Raw binary audio bytes.")
    path: str | None = Field(default=None, description="Path to audio file on disk.")
    format: str = Field(default="wav", description="Audio format (wav, mp3, etc.).")
    sample_rate: int = Field(default=16000, description="Sample rate in Hz.")
    channels: int = Field(default=1, description="Number of audio channels (1=mono, 2=stereo).")
    duration_seconds: float = Field(default=0.0, description="Audio duration in seconds.")

    def save(self, destination: str | Path) -> Path:
        """Write the audio bytes to disk."""
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self.data)
        return target


class TranscriptionResult(BaseModel):
    """Result returned by a Speech-to-Text (STT) engine."""

    text: str = Field(description="The transcribed textual output.")
    language: str = Field(default="en", description="Detected or specified audio language.")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Transcription confidence score."
    )
    duration_seconds: float = Field(default=0.0, description="Duration of processed audio.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Engine-specific metadata.")


class SpeechResult(BaseModel):
    """Result returned by a Text-to-Speech (TTS) engine."""

    text: str = Field(description="The original text synthesized.")
    audio_data: AudioData | None = Field(default=None, description="Generated audio output.")
    duration_seconds: float = Field(default=0.0, description="Estimated or actual audio duration.")
    voice: str = Field(default="default", description="Voice identifier used for synthesis.")


class VoiceConfig(BaseModel):
    """Configuration settings for the voice subsystem."""

    enabled: bool = Field(default=True, description="Whether voice subsystem is enabled.")
    stt_provider: str = Field(default="whisper", description="Speech-to-Text provider engine.")
    stt_model_size: str = Field(
        default="base", description="Whisper model size (tiny, base, small)."
    )
    tts_provider: str = Field(default="pyttsx3", description="Text-to-Speech provider engine.")
    tts_voice: str | None = Field(default=None, description="Specific voice ID to use.")
    tts_rate: int = Field(default=175, description="Speaking rate in words per minute.")
    tts_volume: float = Field(default=1.0, ge=0.0, le=1.0, description="Speaking volume.")
    wake_word: str = Field(default="aether", description="Keyword used for wake word activation.")
