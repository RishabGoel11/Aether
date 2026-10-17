"""
ReviewerAgent — Specialist agent for critique, code review, and QA verification.
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

_REVIEWER_SYSTEM_PROMPT = """\
You are the Reviewer Specialist Agent in the Aether Multi-Agent System.

Your core mission is to critically inspect and verify the deliverables produced
by your teammates (Coder and Researcher).

Evaluation Criteria:
1. Correctness: Does the implementation fulfill all requirements and handle edge cases?
2. Code Quality: Is the code clean, readable, well-commented, and maintainable?
3. Safety: Are there security concerns, resource leaks, or destructive operations?
4. Completeness: Is anything missing from the original goal?

Structure your review:
- **Verdict**: [APPROVED | NEEDS_REVISION]
- **Summary**: Concise assessment of the deliverable.
- **Strengths**: What was done well.
- **Concerns / Bugs**: Specific issues or edge cases discovered.
- **Recommended Improvements**: Clear, actionable advice.
"""


class ReviewerAgent(BaseSpecialistAgent):
    """Specialist responsible for quality assurance, code review, and critique."""

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
        policy: ToolPolicy | None = None,
        max_steps: int = 10,
    ) -> None:
        super().__init__(
            role=AgentRole.REVIEWER,
            name="Reviewer",
            system_prompt=_REVIEWER_SYSTEM_PROMPT,
            llm=llm,
            tools=tools,
            executor=executor,
            policy=policy,
            max_steps=max_steps,
        )

    def run(self, task: str, task_id: str = "task_rev", context: str = "") -> SpecialistResult:
        """Run the reviewer agent to inspect the deliverables."""
        review_prompt = f"Please review and verify the following deliverable:\n{task}"
        if context:
            review_prompt += f"\n\nContext & Prior Deliverables:\n{context}"

        if self._runner:
            result = self._runner.run(review_prompt)
            return SpecialistResult(
                role=self.role,
                task_id=task_id,
                goal=task,
                output=result.answer,
                success=result.success,
                trace=result.trace,
                error=result.error,
            )

        return self._execute_direct(
            prompt=review_prompt, task_id=task_id, goal=task, context=context
        )
