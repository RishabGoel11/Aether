from app.core.session import Session
from app.session.stores.base import BaseSessionStore


class SessionManager:
    """
    Manages persistent conversation sessions.
    """

    def __init__(self, store: BaseSessionStore):
        self.store = store

    def load(self) -> Session:
        if self.store.exists():
            return self.store.load()

        return Session()

    def save(self, session: Session) -> None:
        self.store.save(session)

    def clear(self) -> Session:
        self.store.delete()
        return Session()