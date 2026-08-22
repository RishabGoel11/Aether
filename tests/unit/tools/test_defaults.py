from app.tools.builtin import CalculatorTool, PythonTool
from app.tools.defaults import create_default_registry


def test_default_registry_contains_calculator():
    registry = create_default_registry()

    calculator = registry.get("calculator")

    assert isinstance(calculator, CalculatorTool)


def test_default_registry_contains_python():
    registry = create_default_registry()

    python_tool = registry.get("python")

    assert isinstance(python_tool, PythonTool)


def test_default_registry_contains_expected_tools():
    registry = create_default_registry()

    tools = registry.list()

    assert len(tools) == 4

    names = {tool.name for tool in tools}

    assert names == {
        "calculator",
        "datetime",
        "file_info",
        "python",
    }