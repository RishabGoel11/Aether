import pytest
from pydantic import BaseModel

from app.tools import BaseTool, ToolResult
from app.tools.errors import ToolNotFoundError, ToolRegistrationError
from app.tools.registry import ToolRegistry


class EchoArgs(BaseModel):
    text: str


class EchoTool(BaseTool[EchoArgs]):
    name = "echo"
    description = "Return the provided text."
    args_schema = EchoArgs

    def execute(self, args: EchoArgs) -> ToolResult:
        return ToolResult(success=True, output=args.text)


class CalculatorTool(BaseTool[EchoArgs]):
    name = "calculator"
    description = "Perform a calculation."
    args_schema = EchoArgs

    def execute(self, args: EchoArgs) -> ToolResult:
        return ToolResult(success=True, output=args.text)


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = EchoTool()

    registry.register(tool)

    assert registry.get("echo") is tool


def test_list_tools():
    registry = ToolRegistry()
    echo = EchoTool()
    calculator = CalculatorTool()

    registry.register(echo)
    registry.register(calculator)

    assert registry.list() == [echo, calculator]


def test_duplicate_tool_registration_raises_error():
    registry = ToolRegistry()

    registry.register(EchoTool())

    with pytest.raises(
        ToolRegistrationError,
        match="Tool already registered: echo",
    ):
        registry.register(EchoTool())


def test_missing_tool_raises_error():
    registry = ToolRegistry()

    with pytest.raises(
        ToolNotFoundError,
        match="Tool not found: missing",
    ):
        registry.get("missing")
