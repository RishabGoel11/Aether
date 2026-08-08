from app.tools.errors import (
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistrationError,
    ToolValidationError,
)


def test_tool_errors_share_base_exception():
    errors = [
        ToolRegistrationError(),
        ToolNotFoundError(),
        ToolValidationError(),
        ToolExecutionError(),
    ]

    assert all(isinstance(error, ToolError) for error in errors)
