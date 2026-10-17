from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.voice.tts.base import TTSError
from app.voice.tts.engine import Pyttsx3TTS
from app.voice.tts.mock import MockTTS


def test_mock_tts_synthesize(tmp_path: Path):
    target = tmp_path / "speech.wav"
    tts = MockTTS()

    res = tts.synthesize("Hello world", output_path=target)

    assert res.text == "Hello world"
    assert target.exists()
    assert target.read_bytes() == b"RIFFmockwavdata"
    assert tts.spoken_texts == ["Hello world"]


def test_mock_tts_speak():
    tts = MockTTS()
    tts.speak("Direct verbal output")
    assert tts.spoken_texts == ["Direct verbal output"]


def test_pyttsx3_tts_handles_empty_text():
    tts = Pyttsx3TTS()
    res = tts.synthesize("")
    assert res.text == ""
    assert res.duration_seconds == 0.0


def test_pyttsx3_tts_synthesize_with_mocked_engine(tmp_path: Path):
    tts = Pyttsx3TTS()
    mock_engine = MagicMock()
    tts._engine = mock_engine

    target = tmp_path / "out.wav"
    target.write_bytes(b"test-audio")

    res = tts.synthesize("Aether speaking", output_path=target)

    assert res.text == "Aether speaking"
    assert res.audio_data is not None
    assert res.audio_data.data == b"test-audio"
    mock_engine.save_to_file.assert_called_once()
    mock_engine.runAndWait.assert_called_once()


def test_pyttsx3_tts_speak_with_mocked_engine():
    tts = Pyttsx3TTS()
    mock_engine = MagicMock()
    tts._engine = mock_engine

    tts.speak("Spoken output")

    mock_engine.say.assert_called_once_with("Spoken output")
    mock_engine.runAndWait.assert_called_once()


def test_pyttsx3_tts_initialization_error():
    tts = Pyttsx3TTS()
    with patch("pyttsx3.init", side_effect=Exception("Driver not found")):
        with pytest.raises(TTSError, match="Failed to initialize pyttsx3"):
            tts._get_engine()
