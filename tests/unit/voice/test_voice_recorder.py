"""
Unit tests for MicrophoneRecorder and VoicePipeline audio capture.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.voice.audio.recorder import MicrophoneRecorder
from app.voice.models import AudioData
from app.voice.pipeline import VoicePipeline


def test_microphone_recorder_init():
    rec = MicrophoneRecorder(sample_rate=16000, channels=1, device=2)
    assert rec.sample_rate == 16000
    assert rec.channels == 1
    assert rec.device == 2


def test_microphone_recorder_list_devices():
    rec = MicrophoneRecorder()
    mock_devices = [
        {"name": "Mic 1", "max_input_channels": 1, "default_samplerate": 16000},
        {"name": "Speaker 1", "max_input_channels": 0, "default_samplerate": 44100},
    ]

    with patch("sounddevice.query_devices", return_value=mock_devices):
        devs = rec.list_devices()
        assert len(devs) == 1
        assert devs[0]["name"] == "Mic 1"
        assert devs[0]["index"] == 0


def test_microphone_recorder_fixed_duration():
    import numpy as np

    rec = MicrophoneRecorder(sample_rate=16000)
    fake_audio = np.zeros((16000, 1), dtype=np.int16)

    with patch("sounddevice.rec", return_value=fake_audio), patch("sounddevice.wait"):
        audio = rec.record(duration=1.0)
        assert isinstance(audio, AudioData)
        assert audio.format == "wav"
        assert audio.sample_rate == 16000
        assert len(audio.data) > 0


def test_voice_pipeline_microphone_methods():
    rec_mock = MagicMock()
    fake_audio = AudioData(data=b"mock-wav-bytes", format="wav", duration_seconds=2.0)
    rec_mock.record.return_value = fake_audio
    rec_mock.list_devices.return_value = [{"name": "Default Mic", "index": 0}]

    pipeline = VoicePipeline(recorder=rec_mock)

    devices = pipeline.list_input_devices()
    assert len(devices) == 1
    assert devices[0]["name"] == "Default Mic"

    audio = pipeline.listen(duration=2.0)
    assert audio.data == b"mock-wav-bytes"
    rec_mock.record.assert_called_once_with(duration=2.0)
