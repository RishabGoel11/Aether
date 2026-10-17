"""
DelegateTaskTool — Agent tool allowing dynamic subtask delegation to specialists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from app.multi_agent.models import AgentRole
from app.tools.base import BaseTool
from app.tools.models import ToolResult

if TYPE_CHECKING:
    from app.multi_agent.team import AgentTeam


class DelegateTaskArgs(BaseModel):
    """Arguments for delegating a task to an agent specialist."""

    role: str = Field(
        ...,
        description="Specialist role to delegate to: 'planner', 'researcher', 'coder', 'reviewer'",
    )
    task: str = Field(..., description="The task description or instructions to execute")


class DelegateTaskTool(BaseTool[DelegateTaskArgs]):
    """
    Delegates a specialized subtask to an Aether specialist agent.
    """

    name = "delegate_task"
    description = (
        "Delegates a subtask to a specialist agent (planner, researcher, coder, reviewer). "
        "Returns the specialist's output and analysis."
    )
    args_schema = DelegateTaskArgs

    def __init__(self, team: AgentTeam) -> None:
        self._team = team

    def execute(self, args: DelegateTaskArgs) -> ToolResult:
        """Execute the delegated task via the AgentTeam."""
        role_str = args.role.strip().lower()
        valid_roles = [r.value for r in AgentRole]

        if role_str not in valid_roles:
            return ToolResult(
                output="",
                error=(
                    f"Invalid agent role '{args.role}'. Available roles: {', '.join(valid_roles)}"
                ),
                success=False,
            )

        try:
            result = self._team.delegate(role=role_str, task=args.task)
            return ToolResult(
                output=result.output or "Specialist completed task with no text output.",
                success=result.success,
                error=result.error,
            )
        except Exception as exc:
            return ToolResult(
                output="",
                error=f"Delegation failed: {exc}",
                success=False,
            )
