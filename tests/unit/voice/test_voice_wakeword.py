from app.voice.models import AudioData
from app.voice.wakeword.keyword import KeywordWakeWordDetector


def test_wakeword_detector_matches_keywords():
    detector = KeywordWakeWordDetector(keywords=["aether", "hey aether"])

    assert detector.detect("Aether, what time is it?") is True
    assert detector.detect("Hey Aether! How are you?") is True
    assert detector.detect("aether") is True
    assert detector.detect("Just a regular sentence.") is False


def test_wakeword_detector_handles_audio_data():
    detector = KeywordWakeWordDetector()
    audio = AudioData(data=b"dummy")
    assert detector.detect(audio) is False
