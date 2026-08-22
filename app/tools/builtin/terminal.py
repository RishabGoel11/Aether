import subprocess

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class TerminalArgs(BaseModel):
    """Arguments accepted by the terminal execution tool."""

    command: str = Field(
        min_length=1,
        description="Terminal command to execute.",
    )


class TerminalTool(BaseTool[TerminalArgs]):
    """Execute a terminal command."""

    name = "terminal"
    description = (
        "Execute a terminal command and return its output. "
        "Use this tool when a system command is needed."
    )
    args_schema = TerminalArgs

    def execute(self, args: TerminalArgs) -> ToolResult:
        """Execute the requested terminal command."""

        try:
            result = subprocess.run(
                args.command,
                capture_output=True,
                text=True,
                shell=True,
                timeout=10,
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=result.stderr.strip()
                    or f"Command exited with code {result.returncode}.",
                )

            return ToolResult(
                success=True,
                output=result.stdout.strip(),
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error="Terminal command timed out.",
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to execute terminal command: {exc}",
            )