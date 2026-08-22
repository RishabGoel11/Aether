import pytest

from app.tools.builtin import PythonTool
from app.tools.executor import ToolExecutor


@pytest.fixture
def executor() -> ToolExecutor:
    return ToolExecutor()


@pytest.fixture
def python_tool() -> PythonTool:
    return PythonTool()


def test_python_execution(
    executor: ToolExecutor,
    python_tool: PythonTool,
):
    result = executor.execute(
        python_tool,
        {
            "code": "print(2 + 3)",
        },
    )

    assert result.success is True
    assert result.output == "5"


def test_python_runtime_error(
    executor: ToolExecutor,
    python_tool: PythonTool,
):
    result = executor.execute(
        python_tool,
        {
            "code": "print(1 / 0)",
        },
    )

    assert result.success is False
    assert result.output is None
    assert "ZeroDivisionError" in result.error


def test_python_empty_code(
    executor: ToolExecutor,
    python_tool: PythonTool,
):
    result = executor.execute(
        python_tool,
        {
            "code": "",
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error is not None

def test_python_blocks_unsafe_module(
    executor: ToolExecutor,
    python_tool: PythonTool,
):
    result = executor.execute(
        python_tool,
        {
            "code": "import os",
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error == "Blocked unsafe module: os"


def test_python_blocks_unsafe_function(
    executor: ToolExecutor,
    python_tool: PythonTool,
):
    result = executor.execute(
        python_tool,
        {
            "code": 'eval("2 + 2")',
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error == "Blocked unsafe function: eval"  