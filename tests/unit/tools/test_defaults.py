from app.tools.builtin import CalculatorTool
from app.tools.defaults import create_default_registry


def test_default_registry_contains_calculator():
    registry = create_default_registry()

    calculator = registry.get("calculator")

    assert isinstance(calculator, CalculatorTool)


def test_default_registry_contains_expected_tools():
    registry = create_default_registry()

    tools = registry.list()

    assert len(tools) == 2

    names = {tool.name for tool in tools}

    assert names == {
        "calculator",
        "datetime",
    }