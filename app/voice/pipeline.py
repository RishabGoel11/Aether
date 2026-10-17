from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.engine import ConversationEngine
from app.voice.models import AudioData, SpeechResult, TranscriptionResult
from app.voice.stt.base import BaseSTT
from app.voice.stt.mock import MockSTT
from app.voice.tts.base import BaseTTS
from app.voice.tts.engine import Pyttsx3TTS
from app.voice.wakeword.base import BaseWakeWordDetector
from app.voice.wakeword.keyword import KeywordWakeWordDetector


class VoicePipeline:
    """Coordinates Speech-to-Text, Wake Word Detection, and Text-to-Speech synthesis."""

    def __init__(
        self,
        stt: BaseSTT | None = None,
        tts: BaseTTS | None = None,
        wakeword: BaseWakeWordDetector | None = None,
        engine: ConversationEngine | None = None,
    ) -> None:
        self.stt = stt or MockSTT()
        self.tts = tts or Pyttsx3TTS()
        self.wakeword = wakeword or KeywordWakeWordDetector()
        self.engine = engine

    def transcribe(
        self,
        audio: AudioData | Path | str | bytes,
        language: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe speech audio into text."""
        return self.stt.transcribe(audio, language=language)

    def speak(self, text: str) -> None:
        """Speak text aloud using the TTS engine."""
        self.tts.speak(text)

    def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
    ) -> SpeechResult:
        """Synthesize text into an audio file."""
        return self.tts.synthesize(text, output_path=output_path)

    def check_wake_word(self, input_signal: str | AudioData) -> bool:
        """Check if wake word trigger is present in the input."""
        return self.wakeword.detect(input_signal)

    def process_voice_turn(
        self,
        audio: AudioData | Path | str | bytes,
        speak_response: bool = False,
    ) -> dict[str, Any]:
        """Transcribe user audio, query ConversationEngine, and optionally speak response."""
        transcription = self.transcribe(audio)
        user_text = transcription.text

        response_text = ""
        if self.engine:
            llm_response = self.engine.chat(user_text)
            response_text = (
                llm_response.content if hasattr(llm_response, "content") else str(llm_response)
            )
        else:
            response_text = f"Transcribed: '{user_text}'"

        speech_result: SpeechResult | None = None
        if speak_response and response_text:
            try:
                self.speak(response_text)
                speech_result = SpeechResult(text=response_text)
            except Exception:
                pass

        return {
            "transcription": transcription,
            "user_text": user_text,
            "response_text": response_text,
            "speech": speech_result,
        }
