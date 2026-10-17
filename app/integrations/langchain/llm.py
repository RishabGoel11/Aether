"""Chat model adapter exposing Aether BaseLLM to LangChain interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, Role, ToolCall
from app.tools.base import BaseTool


@dataclass
class LangChainAIMessage:
    """Standard output message format compatible with LangChain."""

    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    response_metadata: dict[str, Any] = field(default_factory=dict)


class AetherLangChainLLM:
    """Wraps an Aether BaseLLM to provide LangChain-compatible chat model methods.

    Supports invoke(), generate(), and bind_tools() while delegating inference
    directly to Aether's configured local or remote LLM provider.
    """

    def __init__(
        self,
        llm: BaseLLM,
        tools: list[BaseTool | Any] | None = None,
    ) -> None:
        self.llm = llm
        self.tools = tools or []

    def bind_tools(self, tools: list[BaseTool | Any]) -> AetherLangChainLLM:
        """Return a new instance bound to the provided tools."""
        return AetherLangChainLLM(llm=self.llm, tools=tools)

    def _convert_input_to_messages(
        self, input_data: list[Message] | list[dict[str, Any]] | str
    ) -> list[Message]:
        """Normalize varied input formats into Aether Message instances."""
        if isinstance(input_data, str):
            return [Message(role=Role.USER, content=input_data)]

        messages: list[Message] = []
        for item in input_data:
            if isinstance(item, Message):
                messages.append(item)
            elif isinstance(item, dict):
                role_val = item.get("role", "user").lower()
                role = Role.USER
                if role_val == "system":
                    role = Role.SYSTEM
                elif role_val in ("assistant", "ai"):
                    role = Role.ASSISTANT
                messages.append(Message(role=role, content=item.get("content", "")))
            elif hasattr(item, "content") and hasattr(item, "type"):
                # Duck-typed LangChain BaseMessage (HumanMessage, SystemMessage, AIMessage)
                msg_type = getattr(item, "type", "human").lower()
                role = Role.USER
                if msg_type in ("system", "systemmessage"):
                    role = Role.SYSTEM
                elif msg_type in ("ai", "aimessage", "assistant"):
                    role = Role.ASSISTANT
                messages.append(Message(role=role, content=getattr(item, "content", "")))
            else:
                messages.append(Message(role=Role.USER, content=str(item)))

        return messages

    def invoke(
        self,
        input_data: list[Message] | list[dict[str, Any]] | str,
        **kwargs: Any,
    ) -> LangChainAIMessage:
        """Invoke the model synchronously on the provided input."""
        messages = self._convert_input_to_messages(input_data)

        # Convert bound tools to definitions if present
        tool_defs = []
        for t in self.tools:
            if hasattr(t, "definition"):
                tool_defs.append(t.definition())
            elif hasattr(t, "to_definition"):
                tool_defs.append(t.to_definition())
            elif hasattr(t, "aether_tool") and hasattr(t.aether_tool, "definition"):
                tool_defs.append(t.aether_tool.definition())

        response: LLMResponse = self.llm.generate(
            messages=messages,
            tools=tool_defs if tool_defs else None,
            **kwargs,
        )

        formatted_tool_calls = []
        if response.tool_calls:
            for tc in response.tool_calls:
                if isinstance(tc, ToolCall):
                    formatted_tool_calls.append(
                        {
                            "name": tc.name,
                            "args": tc.arguments,
                            "id": tc.id,
                        }
                    )
                elif isinstance(tc, dict):
                    formatted_tool_calls.append(tc)

        metadata: dict[str, Any] = {}
        raw = getattr(response, "raw_response", None)
        if raw and isinstance(raw, dict):
            metadata = raw

        return LangChainAIMessage(
            content=response.content,
            tool_calls=formatted_tool_calls,
            response_metadata=metadata,
        )

    def __call__(
        self, input_data: list[Message] | list[dict[str, Any]] | str, **kwargs: Any
    ) -> LangChainAIMessage:
        return self.invoke(input_data, **kwargs)
