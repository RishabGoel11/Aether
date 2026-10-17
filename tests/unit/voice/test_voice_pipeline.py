from unittest.mock import MagicMock

from app.core.engine import ConversationEngine
from app.llm.models import LLMResponse
from app.voice.pipeline import VoicePipeline
from app.voice.stt.mock import MockSTT
from app.voice.tts.mock import MockTTS
from app.voice.wakeword.keyword import KeywordWakeWordDetector


def test_voice_pipeline_transcribe_and_speak():
    mock_stt = MockSTT(default_text="Hello from mic")
    mock_tts = MockTTS()
    pipeline = VoicePipeline(stt=mock_stt, tts=mock_tts)

    transcription = pipeline.transcribe(b"audio-data")
    assert transcription.text == "Hello from mic"

    pipeline.speak("Vocal answer")
    assert mock_tts.spoken_texts == ["Vocal answer"]


def test_voice_pipeline_check_wake_word():
    detector = KeywordWakeWordDetector(keywords=["aether"])
    pipeline = VoicePipeline(wakeword=detector)

    assert pipeline.check_wake_word("Aether wake up") is True
    assert pipeline.check_wake_word("Ignore this") is False


def test_voice_pipeline_process_voice_turn_with_engine():
    mock_stt = MockSTT(default_text="What is your purpose?")
    mock_tts = MockTTS()
    mock_engine = MagicMock(spec=ConversationEngine)
    mock_engine.chat.return_value = LLMResponse(content="I am Aether, an intelligent platform.")

    pipeline = VoicePipeline(
        stt=mock_stt,
        tts=mock_tts,
        engine=mock_engine,
    )

    turn = pipeline.process_voice_turn(b"audio", speak_response=True)

    assert turn["user_text"] == "What is your purpose?"
    assert turn["response_text"] == "I am Aether, an intelligent platform."
    assert mock_tts.spoken_texts == ["I am Aether, an intelligent platform."]
