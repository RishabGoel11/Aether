from __future__ import annotations

import json
from pathlib import Path

from app.core.session import Session
from app.llm.models import Message
from app.session.stores.base import BaseSessionStore


class JsonSessionStore(BaseSessionStore):
    """
    Stores a conversation session as JSON.
    """

    def __init__(self, filepath: Path):
        self.filepath = filepath

    def load(self) -> Session:
        with self.filepath.open("r", encoding="utf-8") as file:
            data = json.load(file)

        session = Session()

        for message_data in data["messages"]:
            session.add_message(Message.model_validate(message_data))

        return session

    def save(self, session: Session) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": 1,
            "messages": [
                message.model_dump()
                for message in session.get_messages()
            ],
        }

        with self.filepath.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def delete(self) -> None:
        if self.exists():
            self.filepath.unlink()

    def exists(self) -> bool:
        return self.filepath.exists()