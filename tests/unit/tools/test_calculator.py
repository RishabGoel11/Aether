import pytest

from app.tools.builtin import CalculatorTool
from app.tools.executor import ToolExecutor


@pytest.fixture
def executor() -> ToolExecutor:
    return ToolExecutor()


@pytest.fixture
def calculator() -> CalculatorTool:
    return CalculatorTool()


def test_addition(executor: ToolExecutor, calculator: CalculatorTool):
    result = executor.execute(
        calculator,
        {
            "operation": "add",
            "left": 10,
            "right": 5,
        },
    )

    assert result.success is True
    assert result.output == 15


def test_subtraction(executor: ToolExecutor, calculator: CalculatorTool):
    result = executor.execute(
        calculator,
        {
            "operation": "subtract",
            "left": 10,
            "right": 5,
        },
    )

    assert result.success is True
    assert result.output == 5


def test_multiplication(executor: ToolExecutor, calculator: CalculatorTool):
    result = executor.execute(
        calculator,
        {
            "operation": "multiply",
            "left": 10,
            "right": 5,
        },
    )

    assert result.success is True
    assert result.output == 50


def test_division(executor: ToolExecutor, calculator: CalculatorTool):
    result = executor.execute(
        calculator,
        {
            "operation": "divide",
            "left": 10,
            "right": 5,
        },
    )

    assert result.success is True
    assert result.output == 2


def test_division_by_zero(
    executor: ToolExecutor,
    calculator: CalculatorTool,
):
    result = executor.execute(
        calculator,
        {
            "operation": "divide",
            "left": 10,
            "right": 0,
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error == "Cannot divide by zero."


def test_unsupported_operation(
    executor: ToolExecutor,
    calculator: CalculatorTool,
):
    result = executor.execute(
        calculator,
        {
            "operation": "power",
            "left": 2,
            "right": 3,
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error == "Unsupported operation: power"
