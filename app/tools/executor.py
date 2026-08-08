from typing import Any

from pydantic import ValidationError

from app.tools.base import BaseTool
from app.tools.errors import ToolExecutionError, ToolValidationError
from app.tools.models import ToolResult


class ToolExecutor:
    """Execute Aether tools with validated arguments."""

    def execute(
        self,
        tool: BaseTool,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Validate arguments and execute a tool."""
        try:
            args = tool.args_schema.model_validate(arguments)
        except ValidationError as exc:
            error = ToolValidationError(str(exc))

            return ToolResult(
                success=False,
                error=str(error),
            )

        try:
            return tool.execute(args)
        except Exception as exc:
            error = ToolExecutionError(str(exc))

            return ToolResult(
                success=False,
                error=str(error),
            )
