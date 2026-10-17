"""
Unit tests for the five specialist agents: Planner, Researcher, Coder, Reviewer, Coordinator.
"""

from __future__ import annotations

from app.llm.base import BaseLLM
from app.llm.models import LLMResponse
from app.multi_agent.agents.coder import CoderAgent
from app.multi_agent.agents.coordinator import CoordinatorAgent
from app.multi_agent.agents.planner import PlannerAgent
from app.multi_agent.agents.researcher import ResearchAgent
from app.multi_agent.agents.reviewer import ReviewerAgent
from app.multi_agent.models import AgentRole


class MockLLM(BaseLLM):
    """Deterministic LLM for testing specialists."""

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[str] = []

    def generate(self, messages, tools=None) -> LLMResponse:
        self.calls.append(messages[-1].content)
        return LLMResponse(content=self.response_text)


def test_planner_agent_json_parsing():
    json_plan = """\
```json
{
  "goal": "Build CLI tool",
  "tasks": [
    {
      "id": "task_1",
      "title": "Analyze CLI options",
      "description": "Examine argparse vs click",
      "assigned_to": "researcher",
      "dependencies": []
    },
    {
      "id": "task_2",
      "title": "Write CLI script",
      "description": "Implement main.py",
      "assigned_to": "coder",
      "dependencies": ["task_1"]
    }
  ]
}
```\
"""
    llm = MockLLM(json_plan)
    planner = PlannerAgent(llm=llm)

    plan = planner.plan("Build CLI tool")
    assert plan.goal == "Build CLI tool"
    assert len(plan.tasks) == 2
    assert plan.tasks[0].assigned_to == AgentRole.RESEARCHER
    assert plan.tasks[1].dependencies == ["task_1"]

    res = planner.run("Build CLI tool")
    assert res.success
    assert "Analyze CLI options" in res.output


def test_planner_agent_fallback_on_invalid_json():
    llm = MockLLM("Here is my unstructured thought on the plan.")
    planner = PlannerAgent(llm=llm)

    plan = planner.plan("Complex task")
    assert len(plan.tasks) == 3
    assert plan.tasks[0].assigned_to == AgentRole.RESEARCHER
    assert plan.tasks[1].assigned_to == AgentRole.CODER
    assert plan.tasks[2].assigned_to == AgentRole.REVIEWER


def test_researcher_agent_direct():
    llm = MockLLM("Here are the research findings on web scraping.")
    researcher = ResearchAgent(llm=llm)

    res = researcher.run(task="Research web scraping libraries", task_id="t1")
    assert res.success
    assert res.role == AgentRole.RESEARCHER
    assert "research findings" in res.output


def test_coder_agent_direct():
    llm = MockLLM("def solve(): return 42")
    coder = CoderAgent(llm=llm)

    res = coder.run(task="Write a solve function", task_id="t2")
    assert res.success
    assert res.role == AgentRole.CODER
    assert "def solve():" in res.output


def test_reviewer_agent_direct():
    llm = MockLLM("Verdict: APPROVED\nThe code is well written and has test coverage.")
    reviewer = ReviewerAgent(llm=llm)

    res = reviewer.run(task="Review the solve function", task_id="t3")
    assert res.success
    assert res.role == AgentRole.REVIEWER
    assert "APPROVED" in res.output


def test_coordinator_agent_synthesis():
    llm = MockLLM("Final Deliverable:\nWe implemented and reviewed the feature successfully.")
    coordinator = CoordinatorAgent(llm=llm)

    output = coordinator.synthesize(
        goal="Deliver feature",
        plan_summary="Plan:\n- task_1",
        results_summary="Results:\n- completed",
        review_summary="Verdict: APPROVED",
    )
    assert "Final Deliverable" in output
    assert len(llm.calls) == 1
