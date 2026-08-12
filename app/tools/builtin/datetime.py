from datetime import datetime, timezone

from pydantic import BaseModel

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class DateTimeArgs(BaseModel):
    """Arguments accepted by the date/time tool."""


class DateTimeTool(BaseTool[DateTimeArgs]):
    """Provide the current UTC date and time."""

    name = "datetime"
    description = "Get the current date and time in UTC."
    args_schema = DateTimeArgs

    def execute(self, args: DateTimeArgs) -> ToolResult:
        """Return the current UTC date and time."""
        now = datetime.now(timezone.utc)

        return ToolResult(
            success=True,
            output=now.isoformat(),
        )