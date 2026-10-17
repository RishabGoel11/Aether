"""
Blackboard — Shared context and communication bus for multi-agent collaboration.

Provides a structured shared memory where agents can:
1. Post completed task outputs.
2. Store and retrieve key-value artifacts (e.g. code, schemas, search notes).
3. Read the collective history of the multi-agent run.
"""

from __future__ import annotations

from typing import Any

from app.multi_agent.models import AgentMessage, AgentRole, SubTask


class Blackboard:
    """
    Central shared state repository accessible by all agents in the team.
    """

    def __init__(self) -> None:
        self._artifacts: dict[str, Any] = {}
        self._messages: list[AgentMessage] = []
        self._task_results: dict[str, str] = {}

    def set_artifact(self, key: str, value: Any) -> None:
        """Store an artifact in shared blackboard storage."""
        self._artifacts[key] = value

    def get_artifact(self, key: str, default: Any = None) -> Any:
        """Retrieve an artifact from shared blackboard storage."""
        return self._artifacts.get(key, default)

    def post_task_result(self, task_id: str, result: str) -> None:
        """Record the output of a completed subtask."""
        self._task_results[task_id] = result

    def get_task_result(self, task_id: str) -> str | None:
        """Retrieve the output of a specific subtask."""
        return self._task_results.get(task_id)

    def record_message(self, message: AgentMessage) -> None:
        """Append an inter-agent communication message."""
        self._messages.append(message)

    def get_messages(
        self, recipient: str | None = None, role: AgentRole | None = None
    ) -> list[AgentMessage]:
        """Filter messages by recipient name or role."""
        msgs = self._messages
        if recipient:
            msgs = [m for m in msgs if m.recipient == recipient]
        if role:
            msgs = [m for m in msgs if m.role == role]
        return msgs

    def build_context_summary(self, current_task: SubTask | None = None) -> str:
        """
        Build a concise Markdown summary of all completed work for prompt injection.
        """
        lines: list[str] = []

        if self._task_results:
            lines.append("### Completed Subtasks and Outputs:")
            for tid, res in self._task_results.items():
                snippet = res.strip()
                if len(snippet) > 1000:
                    snippet = snippet[:1000] + "... [truncated]"
                lines.append(f"#### Task `{tid}` Output:\n{snippet}\n")

        if self._artifacts:
            lines.append("### Shared Artifacts:")
            for k, v in self._artifacts.items():
                val_str = str(v)[:500]
                lines.append(f"- **{k}**: {val_str}")

        if current_task and current_task.dependencies:
            lines.append(f"\nPrerequisites for current task `{current_task.id}`:")
            for dep in current_task.dependencies:
                dep_res = self._task_results.get(dep, "No output recorded.")
                lines.append(f"- `{dep}`: {dep_res[:300]}")

        return "\n".join(lines) if lines else "No previous task outputs recorded yet."

    def clear(self) -> None:
        """Reset the blackboard state."""
        self._artifacts.clear()
        self._messages.clear()
        self._task_results.clear()
