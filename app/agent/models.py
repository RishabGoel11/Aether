"""
Data models for the Aether Agentic ReAct loop.

AgentStep  — one step in the reasoning/action trace.
AgentTrace — the full ordered sequence of steps for a single task run.
AgentResult — final outcome returned to the caller.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class StepType(StrEnum):
    """The role of a single step in the agent trace."""

    THOUGHT = "thought"  # Internal reasoning produced by the LLM
    ACTION = "action"  # A tool call the LLM decided to make
    OBSERVATION = "observation"  # Result of executing a tool
    ANSWER = "answer"  # Final natural-language answer to the user


class AgentStep(BaseModel):
    """One discrete step in the agent reasoning trace."""

    type: StepType
    content: str
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None


class AgentTrace(BaseModel):
    """Complete ordered sequence of steps for one agent run."""

    goal: str
    steps: list[AgentStep] = Field(default_factory=list)

    def add(self, step: AgentStep) -> None:
        """Append a step to the trace."""
        self.steps.append(step)

    def thoughts(self) -> list[AgentStep]:
        """Return only the THOUGHT steps."""
        return [s for s in self.steps if s.type == StepType.THOUGHT]

    def actions(self) -> list[AgentStep]:
        """Return only the ACTION steps."""
        return [s for s in self.steps if s.type == StepType.ACTION]

    def observations(self) -> list[AgentStep]:
        """Return only the OBSERVATION steps."""
        return [s for s in self.steps if s.type == StepType.OBSERVATION]

    def last_answer(self) -> AgentStep | None:
        """Return the most recent ANSWER step, or None."""
        answers = [s for s in self.steps if s.type == StepType.ANSWER]
        return answers[-1] if answers else None

    def summary(self) -> str:
        """Return a compact text representation of the trace."""
        lines: list[str] = []
        for i, step in enumerate(self.steps, 1):
            prefix = step.type.value.upper()
            lines.append(f"[{i}] {prefix}: {step.content[:120]}")
        return "\n".join(lines)


class AgentResult(BaseModel):
    """
    Final result returned after an agent run completes.

    Attributes
    ----------
    success:
        True if the agent produced a final answer without hitting limits.
    answer:
        The natural-language response synthesised by the agent.
    trace:
        Full step-by-step reasoning trace for the run.
    error:
        Human-readable error description when success is False.
    """

    success: bool
    answer: str
    trace: AgentTrace
    error: str | None = None
