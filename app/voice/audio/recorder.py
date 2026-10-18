"""
MicrophoneRecorder — Captures live audio from system microphones.
"""

from __future__ import annotations

import io
import time
import wave
from typing import Any

from app.logger.logger import get_logger
from app.voice.models import AudioData

logger = get_logger(__name__)


class RecorderError(Exception):
    """Raised when audio capture or device querying fails."""


class MicrophoneRecorder:
    """
    Captures live audio from the user's default or selected microphone.

    Parameters
    ----------
    sample_rate:
        Sampling frequency in Hz (default: 16000 Hz, optimal for Whisper STT).
    channels:
        Number of audio channels (default: 1, mono).
    device:
        Optional device index or name. None selects the system default.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: int | str | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

    def list_devices(self) -> list[dict[str, Any]]:
        """List all available audio input devices on the system."""
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            input_devices: list[dict[str, Any]] = []
            for i, dev in enumerate(devices):
                if dev.get("max_input_channels", 0) > 0:
                    input_devices.append(
                        {
                            "index": i,
                            "name": dev.get("name", f"Device {i}"),
                            "channels": dev.get("max_input_channels"),
                            "default_sample_rate": dev.get("default_samplerate"),
                        }
                    )
            return input_devices
        except Exception as exc:
            logger.error("Failed to query audio devices: %s", exc)
            return []

    def record(self, duration: float = 5.0) -> AudioData:
        """
        Record audio from the microphone for a fixed duration.

        Parameters
        ----------
        duration:
            Length of the recording in seconds.

        Returns
        -------
        AudioData:
            Container with WAV-encoded audio bytes and metadata.
        """
        try:
            import sounddevice as sd
        except (ImportError, OSError) as exc:
            raise RecorderError(
                f"Live microphone recording is unavailable: {exc}. "
                "Ensure 'sounddevice' and system audio libraries (PortAudio) are installed."
            ) from exc

        frames_to_record = int(duration * self.sample_rate)
        logger.info("Recording %s seconds from microphone...", duration)

        try:
            recording = sd.rec(
                frames_to_record,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device,
            )
            sd.wait()
        except Exception as exc:
            raise RecorderError(f"Microphone recording failed: {exc}") from exc

        wav_bytes = self._encode_wav(recording)
        return AudioData(
            data=wav_bytes,
            format="wav",
            sample_rate=self.sample_rate,
            channels=self.channels,
            duration_seconds=duration,
        )

    def record_until_silence(
        self,
        max_duration: float = 15.0,
        silence_threshold: float = 500.0,
        silence_duration: float = 1.2,
    ) -> AudioData:
        """
        Record audio dynamically until silence is detected after speech.

        Parameters
        ----------
        max_duration:
            Maximum recording time before stopping.
        silence_threshold:
            Energy threshold (RMS) below which sound is considered silence.
        silence_duration:
            Consecutive seconds of silence required to trigger recording completion.
        """
        try:
            import numpy as np
            import sounddevice as sd
        except (ImportError, OSError) as exc:
            raise RecorderError(f"Live microphone recording is unavailable: {exc}.") from exc

        chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks
        chunks: list[np.ndarray] = []
        speech_started = False
        silence_start_time: float | None = None
        start_time = time.time()

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device,
            ) as stream:
                while time.time() - start_time < max_duration:
                    data, _ = stream.read(chunk_size)
                    chunks.append(data.copy())

                    # Calculate Root Mean Square (RMS) energy
                    rms = np.sqrt(np.mean(data.astype(np.float64) ** 2))

                    if rms > silence_threshold:
                        speech_started = True
                        silence_start_time = None
                    elif speech_started:
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time >= silence_duration:
                            # Finished speaking
                            break
        except Exception as exc:
            raise RecorderError(f"Error during streaming audio capture: {exc}") from exc

        if not chunks:
            return AudioData(
                data=b"",
                format="wav",
                sample_rate=self.sample_rate,
                channels=self.channels,
            )

        recorded_array = np.concatenate(chunks, axis=0)
        actual_duration = len(recorded_array) / self.sample_rate
        wav_bytes = self._encode_wav(recorded_array)

        return AudioData(
            data=wav_bytes,
            format="wav",
            sample_rate=self.sample_rate,
            channels=self.channels,
            duration_seconds=actual_duration,
        )

    def _encode_wav(self, audio_array: Any) -> bytes:
        """Encode int16 numpy array into in-memory WAV container bytes."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit PCM = 2 bytes per sample
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.tobytes())
        return buffer.getvalue()
