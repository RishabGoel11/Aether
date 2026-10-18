from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.session import Session
from app.session.stores.base import BaseSessionStore
from app.session.stores.json_store import JsonSessionStore


class SessionManager:
    """
    Manages persistent conversation sessions with multi-session switching support.
    """

    def __init__(
        self,
        store: BaseSessionStore,
        sessions_dir: Path | str | None = None,
    ):
        self.store = store
        self.sessions_dir = Path(sessions_dir) if sessions_dir else Path("data") / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_session_id: str = "default"
        self._meta_file = self.sessions_dir / "sessions_index.json"
        self._ensure_default_session()

    def _load_meta(self) -> dict[str, dict]:
        """Load session metadata index."""
        if not self._meta_file.exists():
            return {}
        try:
            with self._meta_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_meta(self, meta: dict[str, dict]) -> None:
        """Save session metadata index."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        with self._meta_file.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def _ensure_default_session(self) -> None:
        """Ensure the default session is indexed."""
        meta = self._load_meta()
        if "default" not in meta:
            meta["default"] = {
                "id": "default",
                "title": "General Chat",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_meta(meta)

    def _get_store_for_session(self, session_id: str) -> BaseSessionStore:
        if session_id == "default":
            return self.store
        session_file = self.sessions_dir / f"{session_id}.json"
        return JsonSessionStore(session_file)

    def load(self, session_id: str | None = None) -> Session:
        sid = session_id or self.active_session_id
        store = self._get_store_for_session(sid)
        if store.exists():
            return store.load()
        return Session()

    def save(self, session: Session, session_id: str | None = None) -> None:
        sid = session_id or self.active_session_id
        store = self._get_store_for_session(sid)
        store.save(session)

        # Update metadata
        meta = self._load_meta()
        info = meta.get(
            sid,
            {
                "id": sid,
                "title": "New Chat",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        info["updated_at"] = datetime.now(timezone.utc).isoformat()

        msgs = session.get_messages()
        if msgs and info.get("title") in ("New Chat", "General Chat"):
            for m in msgs:
                if getattr(m.role, "value", str(m.role)) == "user" and m.content.strip():
                    first_line = m.content.strip().split("\n")[0][:36]
                    info["title"] = first_line
                    break

        meta[sid] = info
        self._save_meta(meta)

    def clear(self, session_id: str | None = None) -> Session:
        sid = session_id or self.active_session_id
        store = self._get_store_for_session(sid)
        store.delete()
        return Session()

    def create_session(self, title: str = "New Chat", session_id: str | None = None) -> str:
        """Create a new session, register it in metadata, and activate it."""
        sid = session_id or f"sess_{uuid4().hex[:8]}"
        meta = self._load_meta()
        now = datetime.now(timezone.utc).isoformat()
        meta[sid] = {
            "id": sid,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        self._save_meta(meta)
        self.active_session_id = sid
        store = self._get_store_for_session(sid)
        store.save(Session())
        return sid

    def switch_session(self, session_id: str) -> Session:
        """Activate and load a specific session."""
        self.active_session_id = session_id
        return self.load(session_id)

    def list_sessions(self) -> list[dict]:
        """Return list of all session summaries."""
        meta = self._load_meta()
        self._ensure_default_session()
        meta = self._load_meta()
        result = []
        for sid, info in meta.items():
            store = self._get_store_for_session(sid)
            msg_count = 0
            if store.exists():
                try:
                    s = store.load()
                    msg_count = len(s.get_messages())
                except Exception:
                    msg_count = 0

            result.append(
                {
                    "id": sid,
                    "title": info.get("title", sid),
                    "message_count": msg_count,
                    "created_at": info.get("created_at", ""),
                    "updated_at": info.get("updated_at", ""),
                    "active": sid == self.active_session_id,
                    "is_active": sid == self.active_session_id,
                }
            )

        result.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return result

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        meta = self._load_meta()
        if session_id in meta:
            del meta[session_id]
            self._save_meta(meta)

        store = self._get_store_for_session(session_id)
        if store.exists():
            store.delete()

        if self.active_session_id == session_id:
            self.active_session_id = "default"

        return True
