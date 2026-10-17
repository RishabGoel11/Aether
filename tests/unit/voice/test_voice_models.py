from pathlib import Path

from app.voice.models import AudioData, SpeechResult, TranscriptionResult, VoiceConfig


def test_audio_data_save(tmp_path: Path):
    target = tmp_path / "audio.wav"
    audio = AudioData(data=b"fake-wav-data", format="wav", duration_seconds=1.5)

    saved_path = audio.save(target)

    assert saved_path == target
    assert target.exists()
    assert target.read_bytes() == b"fake-wav-data"


def test_transcription_result_properties():
    res = TranscriptionResult(text="Hello Aether", confidence=0.95, language="en")
    assert res.text == "Hello Aether"
    assert res.confidence == 0.95
    assert res.language == "en"


def test_speech_result_properties():
    audio = AudioData(data=b"audio-bytes", duration_seconds=2.0)
    res = SpeechResult(text="Spoken response", audio_data=audio, duration_seconds=2.0)
    assert res.text == "Spoken response"
    assert res.audio_data is not None
    assert res.audio_data.data == b"audio-bytes"


def test_voice_config_defaults():
    config = VoiceConfig()
    assert config.enabled is True
    assert config.stt_provider == "whisper"
    assert config.tts_provider == "pyttsx3"
    assert config.wake_word == "aether"
