class ToolError(Exception):
    """Base exception for tool-related errors."""


class ToolRegistrationError(ToolError):
    """Raised when a tool cannot be registered."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool does not exist."""


class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""
