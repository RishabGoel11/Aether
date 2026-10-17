"""
BaseSpecialistAgent — Abstract foundation for role-based agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.agent.runner import AgentRunner
from app.llm.base import BaseLLM
from app.llm.models import Message, Role
from app.logger.logger import get_logger
from app.multi_agent.models import AgentRole, SpecialistResult
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)


class BaseSpecialistAgent(ABC):
    """
    Abstract base class for all specialist agents in the multi-agent system.

    Parameters
    ----------
    role:
        The specialist role (Planner, Researcher, Coder, Reviewer, Coordinator).
    name:
        Descriptive name of the agent.
    system_prompt:
        Role-specific behavioral instructions.
    llm:
        Language model instance used for inference.
    tools:
        Optional tool registry containing tools accessible to this specialist.
    executor:
        Optional tool executor.
    policy:
        Optional tool policy for access control.
    """

    def __init__(
        self,
        role: AgentRole,
        name: str,
        system_prompt: str,
        llm: BaseLLM,
        tools: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
        policy: ToolPolicy | None = None,
        max_steps: int = 10,
    ) -> None:
        self.role = role
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools
        self.executor = executor
        self.policy = policy
        self.max_steps = max_steps

        # Internal ReAct runner if tools and executor are available
        self._runner: AgentRunner | None = None
        if self.tools is not None and self.executor is not None:
            self._runner = AgentRunner(
                llm=self.llm,
                tools=self.tools,
                tool_executor=self.executor,
                tool_policy=self.policy or ToolPolicy(),
                max_steps=self.max_steps,
            )

    @abstractmethod
    def run(self, task: str, task_id: str = "task_0", context: str = "") -> SpecialistResult:
        """
        Execute a specialized task given prior context.

        Parameters
        ----------
        task:
            The specific task description or prompt to complete.
        task_id:
            Identifier of the task.
        context:
            Contextual information or findings from earlier completed tasks.

        Returns
        -------
        SpecialistResult:
            Structured output containing role, output text, and trace.
        """

    def _execute_direct(
        self, prompt: str, task_id: str, goal: str, context: str = ""
    ) -> SpecialistResult:
        """Fallback direct generation using the LLM without tools."""
        system_content = self.system_prompt
        if context:
            system_content += f"\n\nContext from previous work:\n{context}"

        messages = [
            Message(role=Role.SYSTEM, content=system_content),
            Message(role=Role.USER, content=prompt),
        ]

        try:
            response = self.llm.generate(messages)
            return SpecialistResult(
                role=self.role,
                task_id=task_id,
                goal=goal,
                output=response.content,
                success=True,
            )
        except Exception as exc:
            logger.error("Error running %s agent: %s", self.name, exc)
            return SpecialistResult(
                role=self.role,
                task_id=task_id,
                goal=goal,
                output="",
                success=False,
                error=str(exc),
            )
