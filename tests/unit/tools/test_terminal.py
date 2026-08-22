import pytest

from app.tools.builtin import TerminalTool
from app.tools.executor import ToolExecutor


@pytest.fixture
def executor() -> ToolExecutor:
    return ToolExecutor()


@pytest.fixture
def terminal() -> TerminalTool:
    return TerminalTool()


def test_terminal_execution(
    executor: ToolExecutor,
    terminal: TerminalTool,
):
    result = executor.execute(
        terminal,
        {
            "command": "echo hello",
        },
    )

    assert result.success is True
    assert result.output == "hello"


def test_terminal_invalid_command(
    executor: ToolExecutor,
    terminal: TerminalTool,
):
    result = executor.execute(
        terminal,
        {
            "command": "invalidcommand",
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error is not None


def test_terminal_empty_command(
    executor: ToolExecutor,
    terminal: TerminalTool,
):
    result = executor.execute(
        terminal,
        {
            "command": "",
        },
    )

    assert result.success is False
    assert result.output is None
    assert result.error is not None