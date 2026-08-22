import re
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

    blocked_commands = {
        "del",
        "erase",
        "rmdir",
        "rd",
        "format",
        "shutdown",
        "restart",
    }

    command_separators = r"[&|;]"

    def execute(self, args: TerminalArgs) -> ToolResult:
        """Execute the requested terminal command."""

        command = args.command.strip()

        commands = re.split(
            self.command_separators,
            command,
        )

        for part in commands:
            part = part.strip()

            if not part:
                continue

            command_name = part.split()[0].lower()

            if command_name in self.blocked_commands:
                return ToolResult(
                    success=False,
                    error=(
                        f"Blocked unsafe command: "
                        f"{command_name}"
                    ),
                )

        try:
            result = subprocess.run(
                command,
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