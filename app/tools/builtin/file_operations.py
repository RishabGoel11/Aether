from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult

MAX_READ_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class ReadFileArgs(BaseModel):
    """Arguments accepted by the file read tool."""

    path: str = Field(
        description="Path to the file to read.",
    )
    max_lines: int | None = Field(
        default=None,
        description="Optional maximum number of lines to read.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Optional starting line offset (0-indexed).",
    )


class ReadFileTool(BaseTool[ReadFileArgs]):
    """Read the text contents of a file in the workspace."""

    name = "read_file"
    description = (
        "Read text content from a file in the workspace. "
        "Supports reading the full file or a slice of lines."
    )
    args_schema = ReadFileArgs

    def execute(self, args: ReadFileArgs) -> ToolResult:
        file_path = Path(args.path)

        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"File not found: {args.path}",
            )

        if not file_path.is_file():
            return ToolResult(
                success=False,
                error=f"Path is not a file: {args.path}",
            )

        try:
            stat = file_path.stat()
            if stat.st_size > MAX_READ_SIZE_BYTES:
                return ToolResult(
                    success=False,
                    error=(
                        f"File size ({stat.st_size} bytes) exceeds limit of "
                        f"{MAX_READ_SIZE_BYTES} bytes."
                    ),
                )

            text = file_path.read_text(encoding="utf-8", errors="replace")

            if args.offset > 0 or args.max_lines is not None:
                lines = text.splitlines(keepends=True)
                start = args.offset
                end = start + args.max_lines if args.max_lines is not None else None
                sliced_lines = lines[start:end]
                text = "".join(sliced_lines)

            return ToolResult(
                success=True,
                output=text,
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to read file '{args.path}': {exc}",
            )


class WriteFileArgs(BaseModel):
    """Arguments accepted by the file write tool."""

    path: str = Field(
        description="Path to the file to write or overwrite.",
    )
    content: str = Field(
        description="Text content to write into the file.",
    )
    append: bool = Field(
        default=False,
        description="If True, append to existing file instead of overwriting.",
    )


class WriteFileTool(BaseTool[WriteFileArgs]):
    """Write or append text content to a file in the workspace."""

    name = "write_file"
    description = (
        "Write or append text content to a file in the workspace. "
        "Automatically creates parent directories if needed."
    )
    args_schema = WriteFileArgs

    def execute(self, args: WriteFileArgs) -> ToolResult:
        file_path = Path(args.path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            mode = "a" if args.append else "w"
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(args.content)

            action = "appended to" if args.append else "wrote"
            return ToolResult(
                success=True,
                output=f"Successfully {action} {len(args.content)} characters in '{args.path}'.",
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to write file '{args.path}': {exc}",
            )


class ListDirectoryArgs(BaseModel):
    """Arguments accepted by the directory listing tool."""

    path: str = Field(
        default=".",
        description="Path to the directory to list (defaults to current directory).",
    )
    recursive: bool = Field(
        default=False,
        description="Whether to recursively list directory contents.",
    )
    max_entries: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of entries to return.",
    )


class ListDirectoryTool(BaseTool[ListDirectoryArgs]):
    """List files and subdirectories in a workspace directory."""

    name = "list_directory"
    description = "List files and subdirectories in a directory with names, types, and sizes."
    args_schema = ListDirectoryArgs

    def execute(self, args: ListDirectoryArgs) -> ToolResult:
        dir_path = Path(args.path)

        if not dir_path.exists():
            return ToolResult(
                success=False,
                error=f"Directory not found: {args.path}",
            )

        if not dir_path.is_dir():
            return ToolResult(
                success=False,
                error=f"Path is not a directory: {args.path}",
            )

        try:
            entries: list[dict[str, Any]] = []
            iterator = dir_path.rglob("*") if args.recursive else dir_path.iterdir()

            for item in iterator:
                if len(entries) >= args.max_entries:
                    break
                try:
                    stat = item.stat()
                    entries.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "type": "directory" if item.is_dir() else "file",
                            "size_bytes": stat.st_size if item.is_file() else None,
                        }
                    )
                except OSError:
                    continue

            return ToolResult(
                success=True,
                output=entries,
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to list directory '{args.path}': {exc}",
            )
