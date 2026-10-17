from app.integrations.langgraph.state import GraphState, append_reducer


def test_graph_state_basic_and_checkpoints():
    state = GraphState({"count": 0, "status": "idle"})
    assert state["count"] == 0
    assert state.get("status") == "idle"
    assert len(state.checkpoints) == 1

    state.update({"count": 1})
    assert state["count"] == 1
    assert len(state.checkpoints) == 2


def test_graph_state_with_append_reducer():
    state = GraphState(
        initial_data={"messages": ["init"]},
        reducers={"messages": append_reducer},
    )

    state.update({"messages": "hello"})
    assert state["messages"] == ["init", "hello"]

    state.update({"messages": ["world", "foo"]})
    assert state["messages"] == ["init", "hello", "world", "foo"]
    assert len(state.checkpoints) == 3
