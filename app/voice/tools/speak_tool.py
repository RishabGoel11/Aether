from __future__ import annotations

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult
from app.voice.tts.base import BaseTTS, TTSError
from app.voice.tts.engine import Pyttsx3TTS


class SpeakArgs(BaseModel):
    """Arguments accepted by the speak tool."""

    message: str = Field(
        min_length=1,
        description="Text message to vocalize aloud via Text-to-Speech.",
    )


class SpeakTool(BaseTool[SpeakArgs]):
    """Vocalize a message to the user aloud via Text-to-Speech synthesis."""

    name = "speak"
    description = (
        "Speak a message aloud to the user using local text-to-speech synthesis. "
        "Use this tool when audio feedback or verbal communication is appropriate."
    )
    args_schema = SpeakArgs

    def __init__(self, tts: BaseTTS | None = None) -> None:
        self.tts = tts or Pyttsx3TTS()

    def execute(self, args: SpeakArgs) -> ToolResult:
        try:
            self.tts.speak(args.message)
            return ToolResult(
                success=True,
                output=f"Successfully spoke message aloud ({len(args.message)} chars).",
            )
        except TTSError as exc:
            return ToolResult(
                success=False,
                error=f"Speech synthesis error: {exc}",
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Unexpected error vocalizing message: {exc}",
            )
