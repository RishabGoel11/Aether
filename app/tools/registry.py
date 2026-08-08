from app.tools.base import BaseTool
from app.tools.errors import ToolNotFoundError, ToolRegistrationError


class ToolRegistry:
    """Registry for discovering and managing Aether tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool by its unique name."""
        if tool.name in self._tools:
            raise ToolRegistrationError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """Return a registered tool by name."""
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool not found: {name}") from exc

    def list(self) -> list[BaseTool]:
        """Return all registered tools."""
        return list(self._tools.values())
