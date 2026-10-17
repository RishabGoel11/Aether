"""
ResearchAgent — Specialist agent for information gathering and analysis.
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

_RESEARCHER_SYSTEM_PROMPT = """\
You are the Research Specialist Agent in the Aether Multi-Agent System.

Your core mission is to investigate, gather factual data, discover documentation,
and synthesize comprehensive findings for the team.

Capabilities & Guidelines:
- Use web search and web scraping tools to find up-to-date information.
- Inspect workspace documents and files when relevant.
- Be precise, cite sources and URLs when available.
- Structure your output clearly with bullet points, summaries, and key takeaways.
- Provide actionable findings that the Coder and Reviewer agents can immediately build upon.
"""


class ResearchAgent(BaseSpecialistAgent):
    """Specialist responsible for fact gathering, document search, and web research."""

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
        policy: ToolPolicy | None = None,
        max_steps: int = 10,
    ) -> None:
        super().__init__(
            role=AgentRole.RESEARCHER,
            name="Researcher",
            system_prompt=_RESEARCHER_SYSTEM_PROMPT,
            llm=llm,
            tools=tools,
            executor=executor,
            policy=policy,
            max_steps=max_steps,
        )

    def run(self, task: str, task_id: str = "task_res", context: str = "") -> SpecialistResult:
        """Run the research agent to investigate the specified task."""
        goal_text = task
        if context:
            goal_text = f"{task}\n\nRelevant Context from Blackboard:\n{context}"

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
