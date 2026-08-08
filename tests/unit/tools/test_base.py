from pydantic import BaseModel

from app.tools import BaseTool, ToolResult


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


def test_tool_definition():
    tool = EchoTool()

    definition = tool.definition()

    assert definition.name == "echo"
    assert definition.description == "Return the provided text."
    assert definition.input_schema["title"] == "EchoArgs"
    assert "text" in definition.input_schema["properties"]


def test_tool_execution():
    tool = EchoTool()

    result = tool.execute(EchoArgs(text="hello"))

    assert result.success is True
    assert result.output == "hello"
    assert result.error is None
