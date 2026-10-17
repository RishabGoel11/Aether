"""
CoordinatorAgent — High-level supervisor directing the multi-agent team.
"""

from __future__ import annotations

from app.llm.base import BaseLLM
from app.logger.logger import get_logger
from app.multi_agent.base import BaseSpecialistAgent
from app.multi_agent.models import AgentRole, SpecialistResult

logger = get_logger(__name__)

_COORDINATOR_SYSTEM_PROMPT = """\
You are the Coordinator Agent leading the Aether Multi-Agent System.

Your core mission is to supervise the team, integrate findings from the Planner,
Researcher, Coder, and Reviewer agents, and produce a unified, polished,
production-quality final response for the user.

Guidelines:
- Carefully review all specialist outputs and review critiques.
- Reconcile any differences or unresolved questions.
- Present a cohesive, professional answer that directly and fully addresses the
  user's original goal.
- Highlight key accomplishments, code artifacts, and findings cleanly with Markdown.
"""


class CoordinatorAgent(BaseSpecialistAgent):
    """Supervisor agent responsible for synthesizing deliverables and leading the team."""

    def __init__(self, llm: BaseLLM) -> None:
        super().__init__(
            role=AgentRole.COORDINATOR,
            name="Coordinator",
            system_prompt=_COORDINATOR_SYSTEM_PROMPT,
            llm=llm,
        )

    def synthesize(
        self,
        goal: str,
        plan_summary: str,
        results_summary: str,
        review_summary: str = "",
    ) -> str:
        """Synthesize a unified, comprehensive final response for the user."""
        prompt = (
            f"The team has completed work on the user's goal: '{goal}'.\n\n"
            f"Execution Plan:\n{plan_summary}\n\n"
            f"Team Outputs:\n{results_summary}\n\n"
        )
        if review_summary:
            prompt += f"Review & QA Critique:\n{review_summary}\n\n"

        prompt += (
            "Please synthesize a clear, comprehensive, and cohesive final deliverable "
            "for the user incorporating all the findings and code."
        )

        result = self._execute_direct(prompt=prompt, task_id="synth_0", goal=goal, context="")
        return result.output

    def run(self, task: str, task_id: str = "task_coord", context: str = "") -> SpecialistResult:
        """Run the coordinator directly."""
        return self._execute_direct(prompt=task, task_id=task_id, goal=task, context=context)
