"""
Unit tests for the DelegateTaskTool.
"""

from __future__ import annotations

from app.llm.base import BaseLLM
from app.llm.models import LLMResponse
from app.multi_agent.team import AgentTeam
from app.multi_agent.tools.delegate_tool import DelegateTaskArgs, DelegateTaskTool


class SimpleMockLLM(BaseLLM):
    def generate(self, messages, tools=None) -> LLMResponse:
        return LLMResponse(content="Specialist execution finished.")


def test_delegate_tool_definition():
    llm = SimpleMockLLM()
    team = AgentTeam(llm=llm)
    tool = DelegateTaskTool(team=team)

    assert tool.name == "delegate_task"
    assert tool.args_schema == DelegateTaskArgs

    defn = tool.definition()
    assert defn.name == "delegate_task"
    assert "properties" in defn.input_schema


def test_delegate_tool_execute_valid():
    llm = SimpleMockLLM()
    team = AgentTeam(llm=llm)
    tool = DelegateTaskTool(team=team)

    args = DelegateTaskArgs(role="coder", task="Write quicksort function")
    result = tool.execute(args)

    assert result.success
    assert "Specialist execution finished." in result.output


def test_delegate_tool_execute_invalid_role():
    llm = SimpleMockLLM()
    team = AgentTeam(llm=llm)
    tool = DelegateTaskTool(team=team)

    args = DelegateTaskArgs(role="magician", task="Perform magic trick")
    result = tool.execute(args)

    assert not result.success
    assert "Invalid agent role 'magician'" in result.error
