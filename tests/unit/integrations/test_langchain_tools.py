from pydantic import BaseModel, Field

from app.integrations.langchain.tools import AetherToolAdapter, LangChainToolAdapter
from app.tools.base import BaseTool
from app.tools.builtin.calculator import CalculatorTool
from app.tools.models import ToolResult


class DummyInput(BaseModel):
    query: str = Field(description="Search term")


class DummyLangChainTool:
    def __init__(self) -> None:
        self.name = "web_search"
        self.description = "Searches the web"
        self.args_schema = DummyInput

    def invoke(self, args: dict) -> str:
        return f"Search results for: {args.get('query')}"


def test_aether_tool_adapter_success():
    calc = CalculatorTool()
    adapter = AetherToolAdapter(calc)

    assert adapter.name == "calculator"
    assert "arithmetic" in adapter.description.lower()

    # Invoke via dictionary
    res = adapter.invoke({"operation": "add", "left": 5, "right": 7})
    assert res == "12.0"

    # Invoke via call syntax
    res2 = adapter(operation="multiply", left=3, right=4)
    assert res2 == "12.0"


def test_aether_tool_adapter_single_field_string_input():
    class SingleArgInput(BaseModel):
        text: str

    class EchoTool(BaseTool):
        name = "echo"
        description = "Echoes text"
        args_schema = SingleArgInput

        def execute(self, args: SingleArgInput) -> ToolResult:
            return ToolResult(success=True, output=args.text)

    echo = EchoTool()
    adapter = AetherToolAdapter(echo)

    # Passing raw string converts to single field
    res = adapter.invoke("hello world")
    assert res == "hello world"


def test_aether_tool_adapter_error_handling():
    calc = CalculatorTool()
    adapter = AetherToolAdapter(calc)

    res = adapter.invoke({"operation": "divide", "left": 10, "right": 0})
    assert "error" in res.lower() or "division" in res.lower()


def test_langchain_tool_adapter_success():
    lc_tool = DummyLangChainTool()
    aether_tool = LangChainToolAdapter(lc_tool)

    assert aether_tool.name == "web_search"
    assert aether_tool.description == "Searches the web"

    args = aether_tool.args_schema(query="Aether AI")
    result = aether_tool.execute(args)

    assert result.success is True
    assert result.output == "Search results for: Aether AI"
    assert result.error is None


def test_langchain_tool_adapter_exception_handled():
    class BrokenTool:
        name = "broken"
        description = "Always breaks"

        def invoke(self, args: dict) -> str:
            raise RuntimeError("API unavailable")

    broken = BrokenTool()
    aether_tool = LangChainToolAdapter(broken)

    args = aether_tool.args_schema(query="test")
    result = aether_tool.execute(args)

    assert result.success is False
    assert result.output is None
    assert "API unavailable" in str(result.error)
