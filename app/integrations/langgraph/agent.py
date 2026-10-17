"""Agent orchestration built on top of LangGraph StateGraph engine."""

from __future__ import annotations

from typing import Any

from app.integrations.langgraph.graph import END, StateGraph
from app.integrations.langgraph.state import append_reducer
from app.llm.base import BaseLLM
from app.llm.models import Message, Role, ToolCall
from app.tools.base import BaseTool
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class GraphReActAgent:
    """An agent orchestrator implemented as a stateful cyclic LangGraph workflow.

    Nodes:
      - 'think': Queries the model, decides whether to call tools or output an answer.
      - 'act': Executes tools and appends observations to state.
    Edges:
      - START -> 'think'
      - 'think' -> conditional ('act' if tool calls requested, else END)
      - 'act' -> 'think' (cyclic loop)
    """

    def __init__(
        self,
        llm: BaseLLM,
        tools: list[BaseTool] | None = None,
        executor: ToolExecutor | None = None,
    ) -> None:
        self.llm = llm
        self.tools = tools or []
        self.registry = ToolRegistry()
        for t in self.tools:
            self.registry.register(t)
        self.executor = executor or ToolExecutor()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        workflow = StateGraph(
            reducers={
                "messages": append_reducer,
                "steps": append_reducer,
            }
        )

        def think_node(state: dict[str, Any]) -> dict[str, Any]:
            messages: list[Message] = state.get("messages", [])
            tool_defs = [t.definition() for t in self.tools if hasattr(t, "definition")]

            response = self.llm.generate(
                messages=messages,
                tools=tool_defs if tool_defs else None,
            )

            tool_calls = response.tool_calls or []
            new_msg = Message(
                role=Role.ASSISTANT,
                content=response.content,
            )

            step_record = {
                "node": "think",
                "content": response.content,
                "tool_calls": [tc.name for tc in tool_calls if isinstance(tc, ToolCall)],
            }

            return {
                "messages": [new_msg],
                "steps": [step_record],
                "pending_tool_calls": tool_calls,
                "final_answer": response.content if not tool_calls else None,
            }

        def act_node(state: dict[str, Any]) -> dict[str, Any]:
            pending: list[ToolCall] = state.get("pending_tool_calls", [])
            obs_messages: list[Message] = []
            obs_records: list[dict[str, Any]] = []

            for tc in pending:
                try:
                    tool = self.registry.get(tc.name)
                    result = self.executor.execute(tool, tc.arguments)
                    content = str(result.output if result.success else f"Error: {result.error}")
                except Exception as exc:
                    content = f"Error: {exc}"

                obs_messages.append(
                    Message(
                        role=Role.USER,
                        content=f"Observation [{tc.name}]: {content}",
                    )
                )
                obs_records.append({"tool": tc.name, "result": content})

            return {
                "messages": obs_messages,
                "steps": [{"node": "act", "observations": obs_records}],
                "pending_tool_calls": [],
            }

        def router(state: dict[str, Any]) -> str:
            pending = state.get("pending_tool_calls", [])
            if pending:
                return "act"
            return END

        workflow.add_node("think", think_node)
        workflow.add_node("act", act_node)
        workflow.set_entry_point("think")
        workflow.add_conditional_edges("think", router, {"act": "act", END: END})
        workflow.add_edge("act", "think")

        return workflow.compile()

    def run(self, goal: str, max_steps: int = 20) -> dict[str, Any]:
        """Execute the agent workflow for a given natural-language goal."""
        initial_state = {
            "messages": [
                Message(
                    role=Role.SYSTEM,
                    content=(
                        "You are a helpful assistant with access to tools. "
                        "Solve the user's goal step-by-step."
                    ),
                ),
                Message(role=Role.USER, content=goal),
            ],
            "goal": goal,
            "steps": [],
            "pending_tool_calls": [],
            "final_answer": None,
        }

        final_state = self.graph.invoke(initial_state, max_steps=max_steps)
        return final_state
