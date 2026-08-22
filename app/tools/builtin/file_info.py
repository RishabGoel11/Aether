from pathlib import Path

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class FileInfoArgs(BaseModel):
    """Arguments accepted by the file information tool."""

    path: str = Field(
        description="Path of the file or directory to inspect.",
    )


class FileInfoTool(BaseTool[FileInfoArgs]):
    """Return metadata about a file or directory."""

    name = "file_info"
    description = (
        "Inspect basic metadata about a file or directory. Does not read or modify its contents."
    )
    args_schema = FileInfoArgs

    def execute(self, args: FileInfoArgs) -> ToolResult:
        """Inspect the requested path."""
        path = Path(args.path)

        if not path.exists():
            return ToolResult(
                success=False,
                error=f"Path does not exist: {args.path}",
            )

        try:
            stat = path.stat()

            output = {
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "size_bytes": stat.st_size,
            }

            return ToolResult(
                success=True,
                output=output,
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to inspect path: {exc}",
            )
