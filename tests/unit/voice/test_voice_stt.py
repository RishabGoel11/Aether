from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.voice.stt.base import STTError
from app.voice.stt.mock import MockSTT
from app.voice.stt.whisper import WhisperSTT


def test_mock_stt_transcribes():
    stt = MockSTT(default_text="Testing voice input")
    result = stt.transcribe(b"dummy-audio-bytes")

    assert result.text == "Testing voice input"
    assert result.confidence == 0.98
    assert stt.transcribed_count == 1


def test_whisper_stt_missing_dependencies_raises():
    stt = WhisperSTT()
    with patch.dict("sys.modules", {"faster_whisper": None, "whisper": None}):
        with pytest.raises(STTError, match="Neither 'faster-whisper' nor 'whisper' is installed"):
            stt._load_model()


def test_whisper_stt_missing_audio_file_raises():
    stt = WhisperSTT()
    stt._model = MagicMock()
    stt._backend = "faster-whisper"

    with pytest.raises(FileNotFoundError):
        stt.transcribe(Path("nonexistent_recording.wav"))
