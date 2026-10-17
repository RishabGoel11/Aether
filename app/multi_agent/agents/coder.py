"""
CoderAgent — Specialist agent for software development and script execution.
"""

from __future__ import annotations

from app.llm.base import BaseLLM
from app.logger.logger import get_logger
from app.multi_agent.base import BaseSpecialistAgent
from app.multi_agent.models import AgentRole, SpecialistResult
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)

_CODER_SYSTEM_PROMPT = """\
You are the Coder Specialist Agent in the Aether Multi-Agent System.

Your core mission is to design, write, test, and implement robust software solutions.

Capabilities & Guidelines:
- Write clean, modular, production-grade code adhering to best practices.
- Read files to understand existing structures before making modifications.
- Create or update workspace files cleanly using file tools.
- Execute Python snippets or run terminal checks when verification is needed.
- Return structured explanations accompanied by complete code blocks with syntax highlighting.
"""


class CoderAgent(BaseSpecialistAgent):
    """Specialist responsible for code authoring, script execution, and implementation."""

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
        policy: ToolPolicy | None = None,
        max_steps: int = 10,
    ) -> None:
        super().__init__(
            role=AgentRole.CODER,
            name="Coder",
            system_prompt=_CODER_SYSTEM_PROMPT,
            llm=llm,
            tools=tools,
            executor=executor,
            policy=policy,
            max_steps=max_steps,
        )

    def run(self, task: str, task_id: str = "task_code", context: str = "") -> SpecialistResult:
        """Run the coder agent to implement the requested task."""
        goal_text = task
        if context:
            goal_text = f"{task}\n\nContext & Research Findings:\n{context}"

        if self._runner:
            result = self._runner.run(goal_text)
            return SpecialistResult(
                role=self.role,
                task_id=task_id,
                goal=task,
                output=result.answer,
                success=result.success,
                trace=result.trace,
                error=result.error,
            )

        return self._execute_direct(prompt=task, task_id=task_id, goal=task, context=context)
