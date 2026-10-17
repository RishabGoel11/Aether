import pytest

from app.integrations.langgraph.graph import END, GraphExecutionError, StateGraph


def test_state_graph_linear_workflow():
    workflow = StateGraph()

    def step_a(state: dict) -> dict:
        return {"val": state.get("val", 0) + 1}

    def step_b(state: dict) -> dict:
        return {"val": state["val"] * 2}

    workflow.add_node("step_a", step_a)
    workflow.add_node("step_b", step_b)
    workflow.set_entry_point("step_a")
    workflow.add_edge("step_a", "step_b")
    workflow.add_edge("step_b", END)

    app = workflow.compile()
    final = app.invoke({"val": 5})
    assert final["val"] == 12  # (5 + 1) * 2 = 12


def test_state_graph_conditional_edges():
    workflow = StateGraph()

    def worker(state: dict) -> dict:
        return {"counter": state["counter"] + 1}

    def router(state: dict) -> str:
        if state["counter"] < 3:
            return "loop"
        return "done"

    workflow.add_node("worker", worker)
    workflow.set_entry_point("worker")
    workflow.add_conditional_edges(
        "worker",
        router,
        path_map={"loop": "worker", "done": END},
    )

    app = workflow.compile()
    final = app.invoke({"counter": 0})
    assert final["counter"] == 3


def test_state_graph_streaming():
    workflow = StateGraph()

    workflow.add_node("node1", lambda s: {"step1": True})
    workflow.add_node("node2", lambda s: {"step2": True})
    workflow.set_entry_point("node1")
    workflow.add_edge("node1", "node2")
    workflow.add_edge("node2", END)

    app = workflow.compile()
    events = list(app.stream({}))

    assert len(events) == 2
    assert events[0][0] == "node1"
    assert events[0][1]["step1"] is True
    assert events[1][0] == "node2"
    assert events[1][1]["step2"] is True


def test_state_graph_budget_exhaustion():
    workflow = StateGraph()
    workflow.add_node("loop", lambda s: {"x": s.get("x", 0) + 1})
    workflow.set_entry_point("loop")
    workflow.add_edge("loop", "loop")  # infinite loop

    app = workflow.compile()
    with pytest.raises(GraphExecutionError) as exc_info:
        app.invoke({}, max_steps=5)
    assert "exceeded maximum execution steps budget" in str(exc_info.value)


def test_state_graph_missing_entry_point():
    workflow = StateGraph()
    workflow.add_node("a", lambda s: {})
    with pytest.raises(ValueError):
        workflow.compile()
