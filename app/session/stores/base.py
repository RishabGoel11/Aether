from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.session import Session


class BaseSessionStore(ABC):
    """
    Abstract interface for persistent session storage.
    """
    
    @abstractmethod
    def load(self) -> Session: ...

    @abstractmethod
    def save(self, session: Session) -> None: ...

    @abstractmethod
    def delete(self) -> None: ...

    @abstractmethod
    def exists(self) -> bool: ...
