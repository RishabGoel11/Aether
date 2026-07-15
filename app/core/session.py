from app.llm.models import Message


class Session:
    """
    Stores the conversation history for a single chat session.
    """

    def __init__(self):
        self._messages: list[Message] = []

    def add_message(self, message: Message) -> None:
        self._messages.append(message)

    def get_messages(self) -> list[Message]:
        return self._messages

    def clear(self) -> None:
        self._messages.clear()
