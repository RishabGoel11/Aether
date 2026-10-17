"""
Data models for the Aether Multi-Agent System.

Includes:
- AgentRole: Specialist roles (Planner, Researcher, Coder, Reviewer, Coordinator).
- TaskStatus: Lifecycle states for subtasks.
- SubTask & TaskPlan: Structured task breakdown and dependencies.
- AgentMessage: Inter-agent communication messages.
- SpecialistResult: Execution output from an individual specialist.
- TeamResult: Consolidated outcome of the multi-agent collaboration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.agent.models import AgentTrace


class AgentRole(StrEnum):
    """Specialized agent roles within the multi-agent team."""

    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


class TaskStatus(StrEnum):
    """Lifecycle status of a planned subtask."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SubTask(BaseModel):
    """A discrete unit of work assigned to a specific specialist agent."""

    id: str
    title: str
    description: str
    assigned_to: AgentRole
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    error: str | None = None

    def is_ready(self, completed_task_ids: set[str]) -> bool:
        """Check if all prerequisite dependencies have been satisfied."""
        return set(self.dependencies).issubset(completed_task_ids)


class TaskPlan(BaseModel):
    """A structured execution plan produced by the Planner Agent."""

    goal: str
    tasks: list[SubTask] = Field(default_factory=list)

    def get_task(self, task_id: str) -> SubTask | None:
        """Retrieve a subtask by its identifier."""
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def completed_task_ids(self) -> set[str]:
        """Return the set of IDs for tasks that have finished successfully."""
        return {t.id for t in self.tasks if t.status == TaskStatus.COMPLETED}

    def get_ready_tasks(self) -> list[SubTask]:
        """Return pending tasks whose dependencies are fully resolved."""
        completed = self.completed_task_ids()
        return [t for t in self.tasks if t.status == TaskStatus.PENDING and t.is_ready(completed)]

    def mark_completed(self, task_id: str, result: str) -> bool:
        """Mark a task as completed with its resulting output."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.result = result
            return True
        return False

    def mark_failed(self, task_id: str, error: str) -> bool:
        """Mark a task as failed with an error description."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            return True
        return False

    def is_complete(self) -> bool:
        """Return True if all subtasks are no longer pending or in progress."""
        return all(
            t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED)
            for t in self.tasks
        )

    def to_markdown(self) -> str:
        """Render the plan as a clean Markdown list."""
        lines = [f"### Execution Plan: {self.goal}\n"]
        for t in self.tasks:
            icon = {
                TaskStatus.COMPLETED: "[x]",
                TaskStatus.IN_PROGRESS: "[-]",
                TaskStatus.FAILED: "[!]",
                TaskStatus.SKIPPED: "[s]",
                TaskStatus.PENDING: "[ ]",
            }.get(t.status, "[ ]")
            deps = f" (requires {', '.join(t.dependencies)})" if t.dependencies else ""
            lines.append(f"- {icon} **{t.id}**: {t.title} [{t.assigned_to.value}]{deps}")
            lines.append(f"  *{t.description}*")
        return "\n".join(lines)


class AgentMessage(BaseModel):
    """An inter-agent or coordinator-to-agent message."""

    sender: str
    recipient: str
    content: str
    role: AgentRole
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpecialistResult(BaseModel):
    """The result of executing a subtask with a specialized agent."""

    role: AgentRole
    task_id: str
    goal: str
    output: str
    success: bool
    trace: AgentTrace | None = None
    error: str | None = None


class TeamResult(BaseModel):
    """The final synthesized result of the multi-agent collaboration."""

    goal: str
    plan: TaskPlan | None = None
    specialist_results: list[SpecialistResult] = Field(default_factory=list)
    final_answer: str
    success: bool
    error: str | None = None
