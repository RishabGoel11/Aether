"""State management abstractions for LangGraph workflows in Aether."""

from __future__ import annotations

import copy
from typing import Any, Callable


def append_reducer(existing: list[Any] | None, new_item: Any) -> list[Any]:
    """Reducer that appends items to an existing list."""
    res = list(existing) if existing is not None else []
    if isinstance(new_item, list):
        res.extend(new_item)
    else:
        res.append(new_item)
    return res


class GraphState:
    """State container managing typed or dictionary-based state and checkpoints."""

    def __init__(
        self,
        initial_data: dict[str, Any] | None = None,
        reducers: dict[str, Callable[[Any, Any], Any]] | None = None,
    ) -> None:
        self._data: dict[str, Any] = copy.deepcopy(initial_data) if initial_data else {}
        self._reducers: dict[str, Callable[[Any, Any], Any]] = reducers or {}
        self._checkpoints: list[dict[str, Any]] = [copy.deepcopy(self._data)]

    @property
    def data(self) -> dict[str, Any]:
        """Current state dictionary snapshot."""
        return copy.deepcopy(self._data)

    @property
    def checkpoints(self) -> list[dict[str, Any]]:
        """History of all state snapshots after each transition."""
        return [copy.deepcopy(c) for c in self._checkpoints]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def update(self, patch: dict[str, Any]) -> None:
        """Apply state updates, respecting any registered field-level reducers."""
        for key, new_val in patch.items():
            if key in self._reducers:
                reducer = self._reducers[key]
                existing_val = self._data.get(key)
                self._data[key] = reducer(existing_val, new_val)
            else:
                self._data[key] = copy.deepcopy(new_val)

        self._checkpoints.append(copy.deepcopy(self._data))
