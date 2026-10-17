"""Bidirectional tool adapters bridging Aether BaseTool and LangChain tools."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, create_model

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class AetherToolAdapter:
    """Wraps an Aether BaseTool into a LangChain-compatible tool interface.

    Allows any Aether tool (Calculator, Python, Terminal, etc.) to be passed
    directly into LangChain agent loops, chains, or model tool lists.
    """

    def __init__(self, tool: BaseTool) -> None:
        self._tool = tool
        self.name = tool.name
        self.description = tool.description
        self.args_schema = tool.args_schema

    @property
    def aether_tool(self) -> BaseTool:
        """Access the underlying Aether tool."""
        return self._tool

    def invoke(self, input_data: dict[str, Any] | BaseModel | str) -> str:
        """Execute the underlying Aether tool using LangChain's invoke protocol."""
        if isinstance(input_data, BaseModel):
            parsed_args = input_data
        elif isinstance(input_data, dict):
            parsed_args = self.args_schema(**input_data)
        elif isinstance(input_data, str):
            # Attempt to parse or pass as first field if single-arg schema
            fields = list(self.args_schema.model_fields.keys())
            if len(fields) == 1:
                parsed_args = self.args_schema(**{fields[0]: input_data})
            else:
                raise ValueError(
                    f"Tool '{self.name}' expects structured input matching {fields}, "
                    f"got string: {input_data}"
                )
        else:
            raise TypeError(f"Unsupported tool input type: {type(input_data)}")

        result: ToolResult = self._tool.execute(parsed_args)
        if not result.success:
            return f"Error executing {self.name}: {result.error}"
        return str(result.output)

    def run(self, tool_input: dict[str, Any] | BaseModel | str) -> str:
        """Alias for invoke() matching LangChain legacy run interface."""
        return self.invoke(tool_input)

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        if kwargs:
            return self.invoke(kwargs)
        if args and isinstance(args[0], (dict, BaseModel, str)):
            return self.invoke(args[0])
        return self.invoke({})


class LangChainToolAdapter(BaseTool):
    """Wraps an external LangChain tool into an Aether BaseTool.

    Allows Aether's ToolRegistry, ToolExecutor, and AgentRunner to seamlessly
    invoke tools written for the LangChain ecosystem.
    """

    def __init__(
        self, lc_tool: Any, name: str | None = None, description: str | None = None
    ) -> None:
        self._lc_tool = lc_tool
        self.name = name or getattr(lc_tool, "name", lc_tool.__class__.__name__)
        self.description = description or getattr(lc_tool, "description", "")
        self.args_schema = self._determine_args_schema(lc_tool)

    def _determine_args_schema(self, lc_tool: Any) -> type[BaseModel]:
        """Extract or synthesize a Pydantic schema from the LangChain tool."""
        if hasattr(lc_tool, "args_schema") and lc_tool.args_schema is not None:
            schema = lc_tool.args_schema
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema

        # Fallback dynamic model for tools without explicit args_schema
        return create_model(
            f"{self.name.capitalize()}Input",
            query=(str, ...),
        )

    def execute(self, args: BaseModel) -> ToolResult:
        """Execute the LangChain tool and format into an Aether ToolResult."""
        try:
            dumped = args.model_dump()
            if hasattr(self._lc_tool, "invoke"):
                output = self._lc_tool.invoke(dumped)
            elif hasattr(self._lc_tool, "run"):
                output = self._lc_tool.run(dumped)
            elif hasattr(self._lc_tool, "_run"):
                output = self._lc_tool._run(**dumped)
            elif callable(self._lc_tool):
                output = self._lc_tool(**dumped)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"LangChain tool '{self.name}' has no invoke, run, or call method.",
                )

            return ToolResult(
                success=True,
                output=output,
                error=None,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                output=None,
                error=f"LangChain tool '{self.name}' failed: {exc}",
            )
