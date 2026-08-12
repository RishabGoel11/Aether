from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class DateTimeArgs(BaseModel):
    """Arguments accepted by the date/time tool."""

    timezone: str = Field(
        default="UTC",
        description=(
            "IANA timezone name, such as "
            "'UTC', 'Asia/Kolkata', or 'America/New_York'."
        ),
    )


class DateTimeTool(BaseTool[DateTimeArgs]):
    """Provide the current date and time in a requested timezone."""

    name = "datetime"
    description = (
        "Get the current date and time in a requested timezone. "
        "Use an IANA timezone name such as 'UTC' or 'Asia/Kolkata'."
    )
    args_schema = DateTimeArgs

    def execute(self, args: DateTimeArgs) -> ToolResult:
        """Return the current date and time in the requested timezone."""
        try:
            tz = ZoneInfo(args.timezone)
        except ZoneInfoNotFoundError:
            return ToolResult(
                success=False,
                error=f"Unknown timezone: {args.timezone}",
            )

        now = datetime.now(timezone.utc).astimezone(tz)

        return ToolResult(
            success=True,
            output=now.isoformat(),
        )