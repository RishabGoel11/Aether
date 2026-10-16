from __future__ import annotations

from app.llm.models import Message, Role


class Session:
    """
    Stores the conversation history for a single chat session.
    """

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def add_message(self, message: Message) -> None:
        self._messages.append(message)

    def get_messages(
        self,
        window: int | None = None,
    ) -> list[Message]:
        """
        Return the conversation history.

        When *window* is set, only the most recent *window* messages
        are returned.  The slice is snapped back to the nearest USER
        message so that assistant / tool-result pairs are never split
        mid-context, which prevents LLM confusion with long histories.
        """
        messages = self._messages

        if window is None or len(messages) <= window:
            return list(messages)

        sliced = messages[-window:]

        # Walk forward until we land on a USER turn so the context
        # always starts cleanly at a human message.
        start = next(
            (i for i, m in enumerate(sliced) if m.role == Role.USER),
            0,
        )

        return sliced[start:]

    def clear(self) -> None:
        self._messages.clear()
