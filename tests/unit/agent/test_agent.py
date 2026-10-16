"""
Unit tests for the Aether Agentic ReAct loop.

Covers:
- AgentStep / AgentTrace / AgentResult models
- AgentRunner: direct answer (no tools)
- AgentRunner: single tool call + observation → final answer
- AgentRunner: multiple sequential tool calls
- AgentRunner: max_steps exhausted → fallback answer
- AgentRunner: tool not found
- AgentRunner: tool policy denial
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from app.agent.models import AgentResult, AgentStep, AgentTrace, StepType
from app.agent.runner import AgentRunner
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, ToolCall
from app.tools.base import BaseTool
from app.tools.executor import ToolExecutor
from app.tools.models import ToolResult
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

# ──────────────────────────────────────────────────────────────────────────────
# Helpers / stubs
# ──────────────────────────────────────────────────────────────────────────────


class FakeLLM(BaseLLM):
    """LLM that returns pre-programmed responses in sequence."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = list(responses)
        self._index = 0

    def generate(self, messages, tools=None) -> LLMResponse:
        if self._index < len(self._responses):
            resp = self._responses[self._index]
            self._index += 1
            return resp
        # Fallback: plain text answer so the loop always terminates
        return LLMResponse(content="Done.")


class EchoArgs(BaseModel):
    message: str


class EchoTool(BaseTool[EchoArgs]):
    """Returns the message it is given — useful for deterministic tests."""

    name = "echo"
    description = "Echoes back the message."
    args_schema = EchoArgs

    def execute(self, args: EchoArgs) -> ToolResult:
        return ToolResult(success=True, output=f"ECHO: {args.message}")


def make_tool_call(name: str, **kwargs: Any) -> ToolCall:
    return ToolCall(id="tc-1", name=name, arguments=kwargs)


def make_runner(
    responses: list[LLMResponse],
    tools: list | None = None,
    max_steps: int = 10,
) -> AgentRunner:
    registry = ToolRegistry()
    for tool in tools or []:
        registry.register(tool)

    return AgentRunner(
        llm=FakeLLM(responses),
        tools=registry,
        tool_executor=ToolExecutor(),
        tool_policy=ToolPolicy(),
        max_steps=max_steps,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Model tests
# ──────────────────────────────────────────────────────────────────────────────


class TestAgentStep:
    def test_step_fields(self):
        step = AgentStep(type=StepType.THOUGHT, content="Thinking...")
        assert step.type == StepType.THOUGHT
        assert step.content == "Thinking..."
        assert step.tool_name is None
        assert step.tool_args is None

    def test_action_step_with_tool_info(self):
        step = AgentStep(
            type=StepType.ACTION,
            content="Calling echo",
            tool_name="echo",
            tool_args={"message": "hi"},
        )
        assert step.tool_name == "echo"
        assert step.tool_args == {"message": "hi"}


class TestAgentTrace:
    def test_add_and_filter(self):
        trace = AgentTrace(goal="test goal")
        trace.add(AgentStep(type=StepType.THOUGHT, content="T1"))
        trace.add(AgentStep(type=StepType.ACTION, content="A1"))
        trace.add(AgentStep(type=StepType.OBSERVATION, content="O1"))
        trace.add(AgentStep(type=StepType.ANSWER, content="Final"))

        assert len(trace.steps) == 4
        assert len(trace.thoughts()) == 1
        assert len(trace.actions()) == 1
        assert len(trace.observations()) == 1

    def test_last_answer_none_when_empty(self):
        trace = AgentTrace(goal="goal")
        assert trace.last_answer() is None

    def test_last_answer_returns_most_recent(self):
        trace = AgentTrace(goal="goal")
        trace.add(AgentStep(type=StepType.ANSWER, content="First"))
        trace.add(AgentStep(type=StepType.ANSWER, content="Last"))
        assert trace.last_answer().content == "Last"

    def test_summary_includes_all_steps(self):
        trace = AgentTrace(goal="goal")
        trace.add(AgentStep(type=StepType.THOUGHT, content="thinking"))
        trace.add(AgentStep(type=StepType.ANSWER, content="done"))
        summary = trace.summary()
        assert "THOUGHT" in summary
        assert "ANSWER" in summary


class TestAgentResult:
    def test_success_result(self):
        trace = AgentTrace(goal="g")
        result = AgentResult(success=True, answer="OK", trace=trace)
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        trace = AgentTrace(goal="g")
        result = AgentResult(
            success=False,
            answer="Partial",
            trace=trace,
            error="Max steps reached",
        )
        assert result.success is False
        assert result.error is not None


# ──────────────────────────────────────────────────────────────────────────────
# AgentRunner tests
# ──────────────────────────────────────────────────────────────────────────────


class TestAgentRunnerInit:
    def test_invalid_max_steps_raises(self):
        with pytest.raises(ValueError, match="max_steps"):
            AgentRunner(
                llm=FakeLLM([]),
                tools=ToolRegistry(),
                tool_executor=ToolExecutor(),
                tool_policy=ToolPolicy(),
                max_steps=0,
            )

    def test_valid_construction(self):
        runner = make_runner([], max_steps=5)
        assert runner.max_steps == 5


class TestAgentRunnerDirectAnswer:
    """LLM responds immediately with text — no tool calls."""

    def test_returns_success(self):
        runner = make_runner(
            [LLMResponse(content="Paris is the capital of France.")]
        )
        result = runner.run("What is the capital of France?")

        assert result.success is True
        assert "Paris" in result.answer

    def test_trace_contains_answer_step(self):
        runner = make_runner([LLMResponse(content="42")])
        result = runner.run("What is 6 * 7?")

        assert result.trace.last_answer() is not None
        assert result.trace.last_answer().type == StepType.ANSWER

    def test_empty_llm_response_gets_fallback_text(self):
        runner = make_runner([LLMResponse(content="")])
        result = runner.run("Something")

        assert result.success is True
        assert result.answer  # non-empty fallback


class TestAgentRunnerWithToolCall:
    """LLM calls a tool, then provides a final answer."""

    def test_single_tool_call_then_answer(self):
        tc = make_tool_call("echo", message="hello")
        responses = [
            LLMResponse(content="Let me echo.", tool_calls=[tc]),
            LLMResponse(content="The echo returned: ECHO: hello"),
        ]
        runner = make_runner(responses, tools=[EchoTool()])
        result = runner.run("Echo hello")

        assert result.success is True
        # Trace should contain thought + action + observation + answer
        types = [s.type for s in result.trace.steps]
        assert StepType.ACTION in types
        assert StepType.OBSERVATION in types
        assert StepType.ANSWER in types

    def test_observation_contains_tool_output(self):
        tc = make_tool_call("echo", message="world")
        responses = [
            LLMResponse(tool_calls=[tc]),
            LLMResponse(content="Done"),
        ]
        runner = make_runner(responses, tools=[EchoTool()])
        result = runner.run("Echo world")

        observations = result.trace.observations()
        assert len(observations) == 1
        assert "ECHO: world" in observations[0].content

    def test_multiple_sequential_tool_calls(self):
        tc1 = make_tool_call("echo", message="first")
        tc2 = make_tool_call("echo", message="second")
        responses = [
            LLMResponse(tool_calls=[tc1]),
            LLMResponse(tool_calls=[tc2]),
            LLMResponse(content="Both done."),
        ]
        runner = make_runner(responses, tools=[EchoTool()])
        result = runner.run("Echo twice")

        assert result.success is True
        actions = result.trace.actions()
        assert len(actions) == 2

    def test_thought_captured_alongside_tool_call(self):
        tc = make_tool_call("echo", message="test")
        responses = [
            LLMResponse(content="I should call echo.", tool_calls=[tc]),
            LLMResponse(content="Final answer."),
        ]
        runner = make_runner(responses, tools=[EchoTool()])
        result = runner.run("test")

        thoughts = result.trace.thoughts()
        assert len(thoughts) == 1
        assert "echo" in thoughts[0].content.lower()


class TestAgentRunnerMaxSteps:
    """Agent hits max_steps and must return a fallback answer."""

    def test_max_steps_returns_failure(self):
        # Each call returns a tool call — loop never terminates on its own.
        tc = make_tool_call("echo", message="loop")
        looping_response = LLMResponse(tool_calls=[tc])
        # Final fallback synthesis
        fallback = LLMResponse(content="Here is what I found so far.")

        # We need max_steps tool-call responses + 1 fallback synthesis.
        runner = make_runner(
            [looping_response] * 4 + [fallback],
            tools=[EchoTool()],
            max_steps=3,
        )
        result = runner.run("Loop forever")

        assert result.success is False
        assert result.error is not None
        assert result.answer  # still has a best-effort answer

    def test_max_steps_trace_has_fallback_answer(self):
        tc = make_tool_call("echo", message="x")
        fallback = LLMResponse(content="Best effort.")
        runner = make_runner(
            [LLMResponse(tool_calls=[tc])] * 3 + [fallback],
            tools=[EchoTool()],
            max_steps=2,
        )
        result = runner.run("Goal")

        last = result.trace.last_answer()
        assert last is not None
        assert last.type == StepType.ANSWER


class TestAgentRunnerToolErrors:
    """Tool not found and policy denial scenarios."""

    def test_unknown_tool_produces_observation_with_error(self):
        tc = make_tool_call("nonexistent_tool")
        responses = [
            LLMResponse(tool_calls=[tc]),
            LLMResponse(content="OK"),
        ]
        runner = make_runner(responses, tools=[])
        result = runner.run("Use a missing tool")

        observations = result.trace.observations()
        assert any("not found" in obs.content for obs in observations)

    def test_policy_denial_produces_observation(self):
        tc = make_tool_call("echo", message="hi")
        responses = [
            LLMResponse(tool_calls=[tc]),
            LLMResponse(content="OK"),
        ]

        # Build a policy that denies everything.
        deny_policy = Mock(spec=ToolPolicy)
        deny_policy.is_allowed.return_value = False

        registry = ToolRegistry()
        registry.register(EchoTool())

        runner = AgentRunner(
            llm=FakeLLM(responses),
            tools=registry,
            tool_executor=ToolExecutor(),
            tool_policy=deny_policy,
            max_steps=10,
        )
        result = runner.run("Echo hi")

        observations = result.trace.observations()
        assert any("denied" in obs.content.lower() for obs in observations)
