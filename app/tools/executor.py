from typing import Any

from pydantic import ValidationError

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class ToolExecutor:
    """Execute registered Aether tools with validated arguments."""

    def execute(
        self,
        tool: BaseTool,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Validate arguments and execute a tool."""
        try:
            args = tool.args_schema.model_validate(arguments)
        except ValidationError as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )

        try:
            return tool.execute(args)
        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )
