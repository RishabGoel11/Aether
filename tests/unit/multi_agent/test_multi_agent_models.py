"""
Unit tests for Multi-Agent data models.
"""

from __future__ import annotations

from app.multi_agent.models import (
    AgentMessage,
    AgentRole,
    SpecialistResult,
    SubTask,
    TaskPlan,
    TaskStatus,
    TeamResult,
)


def test_agent_role_enum():
    assert AgentRole.PLANNER == "planner"
    assert AgentRole.RESEARCHER == "researcher"
    assert AgentRole.CODER == "coder"
    assert AgentRole.REVIEWER == "reviewer"
    assert AgentRole.COORDINATOR == "coordinator"


def test_subtask_is_ready():
    task = SubTask(
        id="task_2",
        title="Code implementation",
        description="Write code",
        assigned_to=AgentRole.CODER,
        dependencies=["task_1"],
    )
    assert not task.is_ready(set())
    assert not task.is_ready({"other_task"})
    assert task.is_ready({"task_1"})
    assert task.is_ready({"task_1", "task_0"})


def test_task_plan_lifecycle():
    t1 = SubTask(
        id="t1",
        title="Research",
        description="Find docs",
        assigned_to=AgentRole.RESEARCHER,
        dependencies=[],
    )
    t2 = SubTask(
        id="t2",
        title="Implement",
        description="Code it",
        assigned_to=AgentRole.CODER,
        dependencies=["t1"],
    )
    t3 = SubTask(
        id="t3",
        title="Review",
        description="Verify",
        assigned_to=AgentRole.REVIEWER,
        dependencies=["t2"],
    )

    plan = TaskPlan(goal="Build uptime checker", tasks=[t1, t2, t3])

    assert plan.get_task("t1") is t1
    assert plan.get_task("unknown") is None
    assert plan.completed_task_ids() == set()
    assert not plan.is_complete()

    # Initially only t1 has satisfied dependencies
    ready = plan.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == "t1"

    # Complete t1
    assert plan.mark_completed("t1", "Research complete.")
    assert "t1" in plan.completed_task_ids()

    # Now t2 should be ready
    ready2 = plan.get_ready_tasks()
    assert len(ready2) == 1
    assert ready2[0].id == "t2"

    # Fail t2
    assert plan.mark_failed("t2", "Syntax error.")
    assert plan.get_task("t2").status == TaskStatus.FAILED

    # Plan is not complete until t3 is resolved or marked
    plan.get_task("t3").status = TaskStatus.SKIPPED
    assert plan.is_complete()

    md = plan.to_markdown()
    assert "Build uptime checker" in md
    assert "[x] **t1**" in md
    assert "[!] **t2**" in md
    assert "[s] **t3**" in md


def test_agent_message_and_results():
    msg = AgentMessage(
        sender="planner",
        recipient="coder",
        content="Please build feature X",
        role=AgentRole.PLANNER,
    )
    assert msg.sender == "planner"
    assert msg.role == AgentRole.PLANNER

    spec_res = SpecialistResult(
        role=AgentRole.CODER,
        task_id="t2",
        goal="Build feature X",
        output="Feature X completed",
        success=True,
    )
    assert spec_res.success
    assert spec_res.role == AgentRole.CODER

    team_res = TeamResult(
        goal="Overall goal",
        specialist_results=[spec_res],
        final_answer="Final solution",
        success=True,
    )
    assert team_res.success
    assert len(team_res.specialist_results) == 1
