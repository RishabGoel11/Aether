from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from app.voice.models import AudioData, TranscriptionResult
from app.voice.stt.base import BaseSTT, STTError


class WhisperSTT(BaseSTT):
    """Local Whisper-based Speech-to-Text provider supporting faster-whisper and whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        # Attempt faster-whisper first
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device=self.device if self.device != "auto" else "cpu",
                compute_type=self.compute_type if self.compute_type != "auto" else "int8",
            )
            self._backend = "faster-whisper"
            return self._model
        except ImportError:
            pass

        # Fallback to openai-whisper
        try:
            import whisper

            self._model = whisper.load_model(self.model_size)
            self._backend = "whisper"
            return self._model
        except ImportError as exc:
            raise STTError(
                "Neither 'faster-whisper' nor 'whisper' is installed. "
                "Install with: uv add faster-whisper"
            ) from exc

    def transcribe(
        self,
        audio: AudioData | Path | str | bytes,
        language: str | None = None,
    ) -> TranscriptionResult:
        model = self._load_model()

        # Handle different input representations
        temp_file: Path | None = None
        try:
            if isinstance(audio, (str, Path)):
                audio_path = Path(audio)
                if not audio_path.exists():
                    raise FileNotFoundError(f"Audio file not found: {audio_path}")
            elif isinstance(audio, AudioData):
                if audio.path and Path(audio.path).exists():
                    audio_path = Path(audio.path)
                else:
                    with tempfile.NamedTemporaryFile(suffix=f".{audio.format}", delete=False) as f:
                        f.write(audio.data)
                        temp_file = Path(f.name)
                        audio_path = temp_file
            elif isinstance(audio, bytes):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio)
                    temp_file = Path(f.name)
                    audio_path = temp_file
            else:
                raise TypeError(f"Unsupported audio type: {type(audio)}")

            if getattr(self, "_backend", None) == "faster-whisper":
                segments, info = model.transcribe(str(audio_path), language=language)
                text = " ".join(s.text.strip() for s in segments)
                return TranscriptionResult(
                    text=text,
                    language=info.language if hasattr(info, "language") else "en",
                    confidence=info.language_probability
                    if hasattr(info, "language_probability")
                    else 1.0,
                    duration_seconds=info.duration if hasattr(info, "duration") else 0.0,
                    metadata={"backend": "faster-whisper", "model": self.model_size},
                )
            else:
                result = model.transcribe(str(audio_path), language=language)
                return TranscriptionResult(
                    text=result.get("text", "").strip(),
                    language=result.get("language", "en"),
                    metadata={"backend": "whisper", "model": self.model_size},
                )

        finally:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
