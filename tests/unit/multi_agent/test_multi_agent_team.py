"""
Unit tests for the AgentTeam orchestrator.
"""

from __future__ import annotations

import pytest

from app.llm.base import BaseLLM
from app.llm.models import LLMResponse
from app.multi_agent.models import AgentRole
from app.multi_agent.team import AgentTeam


class SequenceMockLLM(BaseLLM):
    """Returns responses in sequence for multi-step agent interaction."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.index = 0

    def generate(self, messages, tools=None) -> LLMResponse:
        if self.index < len(self.responses):
            resp = self.responses[self.index]
            self.index += 1
            return LLMResponse(content=resp)
        return LLMResponse(content="Step completed.")


def test_agent_team_initialization():
    llm = SequenceMockLLM(["done"])
    team = AgentTeam(llm=llm)

    assert team.planner is not None
    assert team.researcher is not None
    assert team.coder is not None
    assert team.reviewer is not None
    assert team.coordinator is not None

    assert team.get_specialist(AgentRole.CODER) is team.coder
    assert team.get_specialist("reviewer") is team.reviewer

    with pytest.raises(ValueError):
        team.get_specialist("invalid_role")


def test_agent_team_delegate():
    llm = SequenceMockLLM(["Research on FastAPI vs Litestar complete."])
    team = AgentTeam(llm=llm)

    result = team.delegate(role="researcher", task="Compare web frameworks")
    assert result.success
    assert result.role == AgentRole.RESEARCHER
    assert "FastAPI" in result.output
    assert team.blackboard.get_task_result("adhoc_0") == result.output


def test_agent_team_solve_full_workflow():
    # 1. Plan response (JSON plan with 2 subtasks: researcher, coder)
    plan_json = """\
```json
{
  "goal": "Build simple API",
  "tasks": [
    {
      "id": "task_1",
      "title": "API Specification",
      "description": "Define endpoints",
      "assigned_to": "researcher",
      "dependencies": []
    },
    {
      "id": "task_2",
      "title": "API Code",
      "description": "Write FastAPI code",
      "assigned_to": "coder",
      "dependencies": ["task_1"]
    }
  ]
}
```\
"""
    # 2. Researcher response for task_1
    researcher_resp = "Endpoints: GET /health, POST /items"
    # 3. Coder response for task_2
    coder_resp = "from fastapi import FastAPI\napp = FastAPI()"
    # 4. Coordinator final synthesis response
    coordinator_resp = "### Simple API Deliverable\nWe defined endpoints and wrote the code."

    llm = SequenceMockLLM([plan_json, researcher_resp, coder_resp, coordinator_resp])
    team = AgentTeam(llm=llm)

    result = team.solve("Build simple API")
    assert result.success
    assert result.goal == "Build simple API"
    assert result.plan is not None
    assert len(result.specialist_results) == 2
    assert result.specialist_results[0].role == AgentRole.RESEARCHER
    assert result.specialist_results[1].role == AgentRole.CODER
    assert "Simple API Deliverable" in result.final_answer
