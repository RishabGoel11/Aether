from app.tools.models import ToolDefinition


class ToolPolicy:
    """Controls which registered tools may be executed."""

    def __init__(
        self,
        allowed_tools: set[str] | None = None,
    ) -> None:
        self.allowed_tools = allowed_tools

    def is_allowed(self, tool: ToolDefinition) -> bool:
        """Return whether a tool is permitted to execute."""
        if self.allowed_tools is None:
            return True

        return tool.name in self.allowed_tools