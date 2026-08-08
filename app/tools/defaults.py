from app.tools import ToolRegistry
from app.tools.builtin import CalculatorTool


def create_default_registry() -> ToolRegistry:
    """Create a registry containing Aether's built-in tools."""
    registry = ToolRegistry()

    registry.register(CalculatorTool())

    return registry
