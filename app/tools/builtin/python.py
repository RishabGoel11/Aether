import ast
import subprocess
import sys
import tempfile
from pathlib import Path

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class PythonArgs(BaseModel):
    """Arguments accepted by the Python execution tool."""

    code: str = Field(
        min_length=1,
        description="Python code to execute.",
    )


class PythonTool(BaseTool[PythonArgs]):
    """Execute Python code in a separate process."""

    name = "python"
    description = (
        "Execute Python code and return its output. "
        "Use this tool when Python execution is needed."
    )
    args_schema = PythonArgs

    blocked_modules = {
        "os",
        "subprocess",
        "shutil",
        "socket",
    }

    blocked_functions = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    def _is_safe(self, code: str) -> str | None:
        """Return an error message if Python code is unsafe."""

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return f"Invalid Python code: {exc.msg}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]

                    if module in self.blocked_modules:
                        return f"Blocked unsafe module: {module}"

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]

                    if module in self.blocked_modules:
                        return f"Blocked unsafe module: {module}"

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.blocked_functions:
                        return (
                            "Blocked unsafe function: "
                            f"{node.func.id}"
                        )

        return None

    def execute(self, args: PythonArgs) -> ToolResult:
        """Execute Python code in a separate process."""

        safety_error = self._is_safe(args.code)

        if safety_error:
            return ToolResult(
                success=False,
                error=safety_error,
            )

        temp_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                temp_file.write(args.code)
                temp_path = Path(temp_file.name)

            result = subprocess.run(
                [sys.executable, str(temp_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=result.stderr.strip(),
                )

            return ToolResult(
                success=True,
                output=result.stdout.strip(),
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error="Python execution timed out.",
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                error=f"Unable to execute Python code: {exc}",
            )

        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()