from app.tools import ToolRegistry
from app.tools.builtin import CalculatorTool, DateTimeTool
from app.tools.builtin.file_info import FileInfoTool


def create_default_registry() -> ToolRegistry:
    """Create a registry containing Aether's built-in tools."""
    registry = ToolRegistry()

    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(FileInfoTool())

    return registry
