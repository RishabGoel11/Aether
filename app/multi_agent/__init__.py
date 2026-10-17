"""
Aether Multi-Agent Subsystem.

Provides collaborative multi-agent problem solving through specialized agents:
- PlannerAgent: Structured task planning and decomposition.
- ResearchAgent: Web and document research.
- CoderAgent: Code design, implementation, and script execution.
- ReviewerAgent: Code review, verification, and quality critique.
- CoordinatorAgent: Synthesis and high-level team leadership.
- AgentTeam: High-level team orchestration.
- DelegateTaskTool: Tool allowing agents to delegate subtasks to specialists.
"""

from app.multi_agent.agents import (
    CoderAgent,
    CoordinatorAgent,
    PlannerAgent,
    ResearchAgent,
    ReviewerAgent,
)
from app.multi_agent.base import BaseSpecialistAgent
from app.multi_agent.blackboard import Blackboard
from app.multi_agent.models import (
    AgentMessage,
    AgentRole,
    SpecialistResult,
    SubTask,
    TaskPlan,
    TaskStatus,
    TeamResult,
)
from app.multi_agent.team import AgentTeam
from app.multi_agent.tools import DelegateTaskArgs, DelegateTaskTool

__all__ = [
    "AgentMessage",
    "AgentRole",
    "AgentTeam",
    "BaseSpecialistAgent",
    "Blackboard",
    "CoderAgent",
    "CoordinatorAgent",
    "DelegateTaskArgs",
    "DelegateTaskTool",
    "PlannerAgent",
    "ResearchAgent",
    "ReviewerAgent",
    "SpecialistResult",
    "SubTask",
    "TaskPlan",
    "TaskStatus",
    "TeamResult",
]
