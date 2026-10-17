"""
Unit tests for the multi-agent Blackboard state and communication bus.
"""

from __future__ import annotations

from app.multi_agent.blackboard import Blackboard
from app.multi_agent.models import AgentMessage, AgentRole, SubTask


def test_blackboard_artifacts():
    bb = Blackboard()
    bb.set_artifact("schema", {"user": "str"})
    assert bb.get_artifact("schema") == {"user": "str"}
    assert bb.get_artifact("missing", default=42) == 42


def test_blackboard_task_results():
    bb = Blackboard()
    bb.post_task_result("task_1", "Result of task 1")
    assert bb.get_task_result("task_1") == "Result of task 1"
    assert bb.get_task_result("task_2") is None


def test_blackboard_messages():
    bb = Blackboard()
    msg1 = AgentMessage(
        sender="coordinator",
        recipient="researcher",
        content="Investigate topic A",
        role=AgentRole.COORDINATOR,
    )
    msg2 = AgentMessage(
        sender="researcher",
        recipient="coder",
        content="Found schema",
        role=AgentRole.RESEARCHER,
    )
    bb.record_message(msg1)
    bb.record_message(msg2)

    assert len(bb.get_messages()) == 2
    assert len(bb.get_messages(recipient="researcher")) == 1
    assert len(bb.get_messages(role=AgentRole.RESEARCHER)) == 1


def test_blackboard_context_summary():
    bb = Blackboard()
    empty_summary = bb.build_context_summary()
    assert "No previous task outputs" in empty_summary

    bb.post_task_result("t1", "Output of task 1")
    bb.set_artifact("api_key", "secret123")

    current_task = SubTask(
        id="t2",
        title="Task 2",
        description="Do task 2",
        assigned_to=AgentRole.CODER,
        dependencies=["t1"],
    )

    summary = bb.build_context_summary(current_task=current_task)
    assert "Output of task 1" in summary
    assert "api_key" in summary
    assert "Prerequisites for current task `t2`:" in summary

    bb.clear()
    assert "No previous task outputs" in bb.build_context_summary()
