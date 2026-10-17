from unittest.mock import MagicMock

from app.voice.tools.speak_tool import SpeakArgs, SpeakTool
from app.voice.tts.base import BaseTTS, TTSError


def test_speak_tool_executes_successfully():
    mock_tts = MagicMock(spec=BaseTTS)
    tool = SpeakTool(tts=mock_tts)

    result = tool.execute(SpeakArgs(message="System initialized."))

    assert result.success is True
    assert "Successfully spoke message aloud" in result.output
    mock_tts.speak.assert_called_once_with("System initialized.")


def test_speak_tool_handles_error():
    mock_tts = MagicMock(spec=BaseTTS)
    mock_tts.speak.side_effect = TTSError("Audio driver failed")
    tool = SpeakTool(tts=mock_tts)

    result = tool.execute(SpeakArgs(message="Error message"))

    assert result.success is False
    assert "Speech synthesis error" in result.error
