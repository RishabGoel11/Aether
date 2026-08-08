from pydantic import BaseModel

from app.tools import BaseTool, ToolExecutor, ToolResult


class EchoArgs(BaseModel):
    text: str


class EchoTool(BaseTool[EchoArgs]):
    name = "echo"
    description = "Return the provided text."
    args_schema = EchoArgs

    def execute(self, args: EchoArgs) -> ToolResult:
        return ToolResult(
            success=True,
            output=args.text,
        )


class FailingTool(BaseTool[EchoArgs]):
    name = "failing"
    description = "A tool that fails."
    args_schema = EchoArgs

    def execute(self, args: EchoArgs) -> ToolResult:
        raise RuntimeError("tool failed")


def test_execute_valid_tool():
    executor = ToolExecutor()

    result = executor.execute(
        EchoTool(),
        {"text": "hello"},
    )

    assert result.success is True
    assert result.output == "hello"
    assert result.error is None


def test_invalid_arguments_return_failure():
    executor = ToolExecutor()

    result = executor.execute(
        EchoTool(),
        {},
    )

    assert result.success is False
    assert result.output is None
    assert result.error is not None


def test_tool_exception_returns_failure():
    executor = ToolExecutor()

    result = executor.execute(
        FailingTool(),
        {"text": "hello"},
    )

    assert result.success is False
    assert result.output is None
    assert result.error == "tool failed"
