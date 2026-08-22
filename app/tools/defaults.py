from app.tools import ToolRegistry
from app.tools.builtin import (
    CalculatorTool,
    DateTimeTool,
    FileInfoTool,
    PythonTool,
)


def create_default_registry() -> ToolRegistry:
    """Create a registry containing Aether's built-in tools."""
    registry = ToolRegistry()

    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(FileInfoTool())
    registry.register(PythonTool())

    return registry
    