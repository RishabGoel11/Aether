"""
AgentTeam — Orchestrator managing collaborative multi-agent problem solving.
"""

from __future__ import annotations

from app.llm.base import BaseLLM
from app.logger.logger import get_logger
from app.multi_agent.agents.coder import CoderAgent
from app.multi_agent.agents.coordinator import CoordinatorAgent
from app.multi_agent.agents.planner import PlannerAgent
from app.multi_agent.agents.researcher import ResearchAgent
from app.multi_agent.agents.reviewer import ReviewerAgent
from app.multi_agent.base import BaseSpecialistAgent
from app.multi_agent.blackboard import Blackboard
from app.multi_agent.models import (
    AgentRole,
    SpecialistResult,
    TaskStatus,
    TeamResult,
)
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)


class AgentTeam:
    """
    Coordinates a team of specialized AI agents to solve complex goals.

    Parameters
    ----------
    llm:
        BaseLLM model instance shared or assigned to agents.
    tools:
        Optional ToolRegistry for agents that execute tools.
    executor:
        Optional ToolExecutor for running tool calls.
    policy:
        Optional ToolPolicy for tool access control.
    """

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
        policy: ToolPolicy | None = None,
        max_agent_steps: int = 10,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.executor = executor
        self.policy = policy
        self.blackboard = Blackboard()

        # Instantiate specialist team members
        self.planner = PlannerAgent(llm=self.llm)
        self.researcher = ResearchAgent(
            llm=self.llm,
            tools=self.tools,
            executor=self.executor,
            policy=self.policy,
            max_steps=max_agent_steps,
        )
        self.coder = CoderAgent(
            llm=self.llm,
            tools=self.tools,
            executor=self.executor,
            policy=self.policy,
            max_steps=max_agent_steps,
        )
        self.reviewer = ReviewerAgent(
            llm=self.llm,
            tools=self.tools,
            executor=self.executor,
            policy=self.policy,
            max_steps=max_agent_steps,
        )
        self.coordinator = CoordinatorAgent(llm=self.llm)

        self._specialists: dict[AgentRole, BaseSpecialistAgent] = {
            AgentRole.PLANNER: self.planner,
            AgentRole.RESEARCHER: self.researcher,
            AgentRole.CODER: self.coder,
            AgentRole.REVIEWER: self.reviewer,
            AgentRole.COORDINATOR: self.coordinator,
        }

    def get_specialist(self, role: AgentRole | str) -> BaseSpecialistAgent:
        """Retrieve a specialist agent by role."""
        if isinstance(role, str):
            role = AgentRole(role.lower())
        if role not in self._specialists:
            raise ValueError(f"Unknown agent role: {role}")
        return self._specialists[role]

    def delegate(
        self, role: AgentRole | str, task: str, task_id: str = "adhoc_0"
    ) -> SpecialistResult:
        """Directly delegate a single task to a specific specialist."""
        specialist = self.get_specialist(role)
        context = self.blackboard.build_context_summary()
        result = specialist.run(task=task, task_id=task_id, context=context)
        if result.success and result.output:
            self.blackboard.post_task_result(task_id, result.output)
        return result

    def solve(self, goal: str) -> TeamResult:
        """
        Execute the full multi-agent collaborative workflow for a goal.

        Workflow:
        1. Planner decomposes the goal into a structured TaskPlan.
        2. Specialists execute ready tasks according to dependencies.
        3. Blackboard tracks outputs and context across all tasks.
        4. Coordinator synthesizes the cohesive final deliverable.
        """
        self.blackboard.clear()
        logger.info("AgentTeam initiating collaboration for goal: %s", goal)

        # 1. Planning phase
        plan = self.planner.plan(goal)
        specialist_results: list[SpecialistResult] = []

        # 2. Execution phase
        while not plan.is_complete():
            ready_tasks = plan.get_ready_tasks()
            if not ready_tasks:
                # If no tasks are ready and not complete, break deadlock
                logger.warning("No ready tasks available; terminating execution loop.")
                break

            for task in ready_tasks:
                task.status = TaskStatus.IN_PROGRESS
                specialist = self.get_specialist(task.assigned_to)

                context = self.blackboard.build_context_summary(current_task=task)
                logger.info(
                    "Executing subtask [%s] via %s: %s",
                    task.id,
                    task.assigned_to.value,
                    task.title,
                )

                subtask_prompt = f"Task: {task.title}\nInstructions: {task.description}"
                res = specialist.run(task=subtask_prompt, task_id=task.id, context=context)
                specialist_results.append(res)

                if res.success:
                    plan.mark_completed(task.id, res.output)
                    self.blackboard.post_task_result(task.id, res.output)
                else:
                    plan.mark_failed(task.id, res.error or "Task failed")
                    logger.error("Subtask [%s] failed: %s", task.id, res.error)

        # 3. Synthesis phase
        results_summary = self.blackboard.build_context_summary()
        review_tasks = [r for r in specialist_results if r.role == AgentRole.REVIEWER]
        review_text = review_tasks[-1].output if review_tasks else ""

        final_answer = self.coordinator.synthesize(
            goal=goal,
            plan_summary=plan.to_markdown(),
            results_summary=results_summary,
            review_summary=review_text,
        )

        all_success = all(t.status == TaskStatus.COMPLETED for t in plan.tasks)
        return TeamResult(
            goal=goal,
            plan=plan,
            specialist_results=specialist_results,
            final_answer=final_answer,
            success=all_success,
        )
