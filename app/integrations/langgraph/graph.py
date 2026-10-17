"""StateGraph workflow engine implementing LangGraph cyclic and stateful graph execution."""

from __future__ import annotations

from typing import Any, Callable, Iterator

from app.integrations.langgraph.state import GraphState

START = "__start__"
END = "__end__"


class GraphExecutionError(RuntimeError):
    """Raised when graph execution encounters an invalid state or cycle error."""


class CompiledGraph:
    """Executable state machine compiled from a StateGraph."""

    def __init__(
        self,
        nodes: dict[str, Callable[[dict[str, Any]], dict[str, Any]]],
        edges: dict[str, str],
        conditional_edges: dict[str, tuple[Callable[[dict[str, Any]], str], dict[str, str] | None]],
        entry_point: str,
        reducers: dict[str, Callable[[Any, Any], Any]] | None = None,
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges
        self.entry_point = entry_point
        self.reducers = reducers or {}

    def _get_next_node(self, current_node: str, state_data: dict[str, Any]) -> str:
        """Determine next node using conditional or direct edges."""
        if current_node in self.conditional_edges:
            router_fn, path_map = self.conditional_edges[current_node]
            route_result = router_fn(state_data)
            if path_map is not None:
                if route_result not in path_map:
                    keys = list(path_map.keys())
                    raise GraphExecutionError(
                        f"Conditional router returned '{route_result}', "
                        f"not found in path_map: {keys}"
                    )
                return path_map[route_result]
            return route_result

        if current_node in self.edges:
            return self.edges[current_node]

        # If no edge from current node, default to END
        return END

    def stream(
        self,
        initial_state: dict[str, Any],
        max_steps: int = 50,
    ) -> Iterator[tuple[str, dict[str, Any]]]:
        """Stream execution step-by-step, yielding (node_name, state_snapshot)."""
        state = GraphState(initial_state, reducers=self.reducers)
        current_node = self.entry_point
        steps_executed = 0

        while current_node != END:
            if steps_executed >= max_steps:
                raise GraphExecutionError(
                    f"Graph exceeded maximum execution steps budget ({max_steps})."
                )

            if current_node not in self.nodes:
                raise GraphExecutionError(f"Node '{current_node}' is not registered in graph.")

            node_fn = self.nodes[current_node]
            output = node_fn(state.data)

            if output and isinstance(output, dict):
                state.update(output)

            yield (current_node, state.data)
            steps_executed += 1

            current_node = self._get_next_node(current_node, state.data)

    def invoke(
        self,
        initial_state: dict[str, Any],
        max_steps: int = 50,
    ) -> dict[str, Any]:
        """Run graph to completion from initial state and return final state dict."""
        final_state = initial_state
        for _node_name, state_snapshot in self.stream(initial_state, max_steps=max_steps):
            final_state = state_snapshot
        return final_state


class StateGraph:
    """Builder for constructing stateful, multi-node cyclic or acyclic workflows."""

    def __init__(self, reducers: dict[str, Callable[[Any, Any], Any]] | None = None) -> None:
        self.nodes: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self.edges: dict[str, str] = {}
        self.conditional_edges: dict[
            str, tuple[Callable[[dict[str, Any]], str], dict[str, str] | None]
        ] = {}
        self.entry_point: str | None = None
        self.reducers = reducers or {}

    def add_node(self, name: str, action: Callable[[dict[str, Any]], dict[str, Any]]) -> StateGraph:
        """Register a node in the graph."""
        if name in (START, END):
            raise ValueError(f"Cannot use reserved node name '{name}'.")
        self.nodes[name] = action
        return self

    def add_edge(self, start_node: str, end_node: str) -> StateGraph:
        """Register a direct edge between two nodes."""
        if start_node == START:
            self.entry_point = end_node
        else:
            self.edges[start_node] = end_node
        return self

    def set_entry_point(self, node: str) -> StateGraph:
        """Set the initial node to execute when the graph runs."""
        return self.add_edge(START, node)

    def add_conditional_edges(
        self,
        source: str,
        router: Callable[[dict[str, Any]], str],
        path_map: dict[str, str] | None = None,
    ) -> StateGraph:
        """Register a dynamic routing edge out of a node."""
        self.conditional_edges[source] = (router, path_map)
        return self

    def compile(self) -> CompiledGraph:
        """Validate and compile into an executable CompiledGraph instance."""
        if not self.entry_point:
            raise ValueError("Graph entry point has not been set. Use set_entry_point().")
        if self.entry_point not in self.nodes:
            raise ValueError(f"Entry point node '{self.entry_point}' does not exist.")

        return CompiledGraph(
            nodes=self.nodes,
            edges=self.edges,
            conditional_edges=self.conditional_edges,
            entry_point=self.entry_point,
            reducers=self.reducers,
        )
