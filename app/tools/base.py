from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.tools.models import ToolDefinition, ToolResult

ArgsT = TypeVar("ArgsT", bound=BaseModel)


class BaseTool(ABC, Generic[ArgsT]):
    """Abstract base class for all Aether tools."""

    name: str
    description: str
    args_schema: type[ArgsT]

    def definition(self) -> ToolDefinition:
        """Return the serializable definition of this tool."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema=self.args_schema.model_json_schema(),
        )

    @abstractmethod
    def execute(self, args: ArgsT) -> ToolResult:
        """Execute the tool with validated arguments."""
        raise NotImplementedError
