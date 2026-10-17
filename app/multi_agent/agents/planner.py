"""
PlannerAgent — Breaks down complex goals into structured subtasks.
"""

from __future__ import annotations

import json
import re

from app.llm.base import BaseLLM
from app.logger.logger import get_logger
from app.multi_agent.base import BaseSpecialistAgent
from app.multi_agent.models import AgentRole, SpecialistResult, SubTask, TaskPlan

logger = get_logger(__name__)

_PLANNER_SYSTEM_PROMPT = """\
You are the Planner Agent in the Aether Multi-Agent System.

Your job is to analyze the user's high-level goal and decompose it into a clean,
ordered series of subtasks assigned to the appropriate specialist agents:
- researcher: for gathering facts, web search, documentation, or reading files
- coder: for writing code, executing scripts, creating files, or running tests
- reviewer: for evaluating outputs, reviewing code, validating results, or QA

Output Format:
You MUST respond with a JSON object enclosed in ```json ... ``` with this structure:
{
  "goal": "Description of the overarching goal",
  "tasks": [
    {
      "id": "task_1",
      "title": "Short title",
      "description": "Clear instructions for what the specialist should accomplish",
      "assigned_to": "researcher" | "coder" | "reviewer",
      "dependencies": []
    },
    {
      "id": "task_2",
      "title": "Short title",
      "description": "Clear instructions",
      "assigned_to": "coder",
      "dependencies": ["task_1"]
    }
  ]
}

Keep plans focused, typically 2 to 5 subtasks. Every task must have a clear deliverable.
"""


class PlannerAgent(BaseSpecialistAgent):
    """Specialist responsible for decomposing goals into structured execution plans."""

    def __init__(self, llm: BaseLLM) -> None:
        super().__init__(
            role=AgentRole.PLANNER,
            name="Planner",
            system_prompt=_PLANNER_SYSTEM_PROMPT,
            llm=llm,
        )

    def plan(self, goal: str, context: str = "") -> TaskPlan:
        """Generate a structured TaskPlan for the given goal."""
        prompt = f"Create a step-by-step execution plan for this goal:\n{goal}"
        result = self._execute_direct(prompt=prompt, task_id="plan_0", goal=goal, context=context)

        return self._parse_plan(goal, result.output)

    def run(self, task: str, task_id: str = "plan_0", context: str = "") -> SpecialistResult:
        """Run the planner and return a SpecialistResult containing the Markdown plan."""
        plan = self.plan(task, context=context)
        return SpecialistResult(
            role=self.role,
            task_id=task_id,
            goal=task,
            output=plan.to_markdown(),
            success=True,
        )

    def _parse_plan(self, goal: str, text: str) -> TaskPlan:
        """Parse the JSON plan from the LLM response, with fallback."""
        # Try to find JSON inside markdown code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        raw_json = json_match.group(1) if json_match else text.strip()

        try:
            data = json.loads(raw_json)
            tasks_data = data.get("tasks", [])
            tasks: list[SubTask] = []
            for item in tasks_data:
                role_val = item.get("assigned_to", "coder").lower()
                role = (
                    AgentRole(role_val)
                    if role_val in AgentRole._value2member_map_
                    else AgentRole.CODER
                )
                tasks.append(
                    SubTask(
                        id=item.get("id", f"task_{len(tasks) + 1}"),
                        title=item.get("title", "Execute subtask"),
                        description=item.get("description", ""),
                        assigned_to=role,
                        dependencies=item.get("dependencies", []),
                    )
                )
            if tasks:
                return TaskPlan(goal=goal, tasks=tasks)
        except Exception as e:
            logger.warning("Could not parse planner JSON output: %s. Using fallback plan.", e)

        # Fallback default plan: Research -> Code -> Review
        return TaskPlan(
            goal=goal,
            tasks=[
                SubTask(
                    id="task_1",
                    title="Research and Requirements Analysis",
                    description=f"Gather necessary details and background for: {goal}",
                    assigned_to=AgentRole.RESEARCHER,
                    dependencies=[],
                ),
                SubTask(
                    id="task_2",
                    title="Implementation and Execution",
                    description=f"Implement the solution for: {goal}",
                    assigned_to=AgentRole.CODER,
                    dependencies=["task_1"],
                ),
                SubTask(
                    id="task_3",
                    title="Review and Verification",
                    description="Verify the implementation, review quality, and validate results.",
                    assigned_to=AgentRole.REVIEWER,
                    dependencies=["task_2"],
                ),
            ],
        )
