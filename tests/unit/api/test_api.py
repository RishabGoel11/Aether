"""
Unit tests for the Aether FastAPI REST API and endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.multi_agent.models import AgentRole, SubTask, TaskPlan, TaskStatus, TeamResult


@pytest.fixture
def client():
    """Create a FastAPI test client with isolated dependencies."""
    application = create_app()
    return TestClient(application)


def test_index_serves_html(client):
    """Test that GET / returns the Web UI index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Aether" in response.text


def test_favicon_returns_204(client):
    """Test that GET /favicon.ico returns 204 No Content."""
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_health_check(client):
    """Test GET /api/health returns platform status and version."""
    with patch("app.api.routes.health.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_app.tools.list.return_value = ["tool_a", "tool_b"]
        mock_get_app.return_value = mock_app

        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.11.0"
        assert data["ollama_connected"] is True
        assert data["tools_registered"] == 2


def test_doctor_diagnostics(client):
    """Test GET /api/doctor executes diagnostics checks."""
    response = client.get("/api/doctor")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_api_key_auth(client, monkeypatch):
    """Test X-API-Key authorization when AETHER_API_KEY is configured."""
    monkeypatch.setenv("AETHER_API_KEY", "secret-token-123")

    # Missing header -> 401
    resp_unauth = client.post("/api/chat", json={"message": "hello"})
    assert resp_unauth.status_code == 401

    # Invalid header -> 401
    resp_bad = client.post(
        "/api/chat",
        json={"message": "hello"},
        headers={"X-API-Key": "wrong-token"},
    )
    assert resp_bad.status_code == 401

    # Valid header -> passes auth
    with patch("app.api.routes.chat.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_app.chat.return_value = "Authenticated reply"
        mock_get_app.return_value = mock_app

        resp_ok = client.post(
            "/api/chat",
            json={"message": "hello"},
            headers={"X-API-Key": "secret-token-123"},
        )
        assert resp_ok.status_code == 200
        assert resp_ok.json()["response"] == "Authenticated reply"


def test_chat_endpoint(client):
    """Test POST /api/chat and POST /api/chat/clear."""
    from app.llm.models import LLMResponse

    with patch("app.api.routes.chat.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_app.chat.return_value = LLMResponse(content="Hello from Aether", tool_calls=[])
        mock_get_app.return_value = mock_app

        res = client.post("/api/chat", json={"message": "Hi there"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["response"] == "Hello from Aether"

        clear_res = client.post("/api/chat/clear")
        assert clear_res.status_code == 200
        mock_app.clear_conversation.assert_called_once()


def test_run_agent_endpoint(client):
    """Test POST /api/run executes autonomous ReAct loop."""
    with patch("app.api.routes.agent.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.answer = "Computed 42"
        mock_result.success = True
        mock_step = MagicMock()
        mock_step.type.value = "thought"
        mock_step.content = "Thinking..."
        mock_step.tool_name = None
        mock_step.tool_args = None
        mock_result.trace.steps = [mock_step]
        mock_result.error = None
        mock_agent.run.return_value = mock_result
        mock_app.agent = mock_agent
        mock_get_app.return_value = mock_app

        res = client.post("/api/run", json={"goal": "Find the answer", "max_steps": 5})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["answer"] == "Computed 42"
        assert data["step_count"] == 1


def test_team_endpoint(client):
    """Test POST /api/team runs multi-agent team collaboration."""
    with patch("app.api.routes.team.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_team = MagicMock()

        plan = TaskPlan(
            goal="Test Team",
            tasks=[
                SubTask(
                    id="1",
                    title="Research",
                    description="Gather facts",
                    assigned_to=AgentRole.RESEARCHER,
                    status=TaskStatus.COMPLETED,
                    result="Found facts",
                )
            ],
        )
        team_result = TeamResult(
            goal="Test Team",
            plan=plan,
            final_answer="Comprehensive Deliverable",
            success=True,
        )
        mock_team.solve.return_value = team_result
        mock_app.team = mock_team
        mock_get_app.return_value = mock_app

        res = client.post("/api/team", json={"goal": "Test Team"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["final_answer"] == "Comprehensive Deliverable"
        assert len(data["subtasks"]) == 1
        assert data["subtasks"][0]["role"] == "researcher"


def test_rag_endpoints(client, tmp_path):
    """Test POST /api/rag/index and GET /api/rag/chunks."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("Aether architecture guidelines.")

    with patch("app.api.routes.rag.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_rag = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.id = "c1"
        mock_chunk.source = str(sample_file)
        mock_chunk.content = "Aether architecture guidelines."

        mock_rag.index.return_value = [mock_chunk]
        mock_rag.chunk_store.list.return_value = [mock_chunk]
        mock_rag.chunk_store.get_all.return_value = [mock_chunk]
        mock_app.rag = mock_rag
        mock_get_app.return_value = mock_app

        index_res = client.post(
            "/api/rag/index",
            json={"path": str(sample_file), "recursive": False},
        )
        assert index_res.status_code == 200
        assert index_res.json()["indexed_chunks"] == 1

        chunks_res = client.get("/api/rag/chunks")
        assert chunks_res.status_code == 200
        data = chunks_res.json()
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["id"] == "c1"


def test_memory_endpoints(client):
    """Test GET /api/memory and DELETE /api/memory/{id}."""
    with patch("app.api.routes.memory.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_mem = MagicMock()
        mock_mem.id = "mem-1"
        mock_mem.category.value = "fact"
        mock_mem.content = "User prefers dark mode"
        from datetime import datetime

        mock_mem.timestamp = datetime(2026, 1, 1, 12, 0, 0)

        mock_app.memory.get_all.return_value = [mock_mem]
        mock_app.memory.delete.return_value = True
        mock_get_app.return_value = mock_app

        get_res = client.get("/api/memory")
        assert get_res.status_code == 200
        records = get_res.json()
        assert len(records) == 1
        assert records[0]["id"] == "mem-1"
        assert records[0]["content"] == "User prefers dark mode"

        del_res = client.delete("/api/memory/mem-1")
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True


def test_voice_endpoints(client):
    """Test POST /api/voice/speak and GET /api/voice/devices."""
    with patch("app.api.routes.voice.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_voice = MagicMock()
        mock_voice.list_input_devices.return_value = [
            {"index": 0, "name": "Default Microphone", "max_input_channels": 2}
        ]
        mock_app.voice = mock_voice
        mock_get_app.return_value = mock_app

        speak_res = client.post("/api/voice/speak", json={"text": "Hello world"})
        assert speak_res.status_code == 200
        assert speak_res.json()["success"] is True
        mock_voice.speak.assert_called_once_with("Hello world")

        devices_res = client.get("/api/voice/devices")
        assert devices_res.status_code == 200
        devices = devices_res.json()
        assert len(devices) == 1
        assert devices[0]["name"] == "Default Microphone"


def test_sessions_endpoints(client):
    """Test sessions endpoints: listing, creating, retrieving, activating, and deleting."""
    with patch("app.api.routes.sessions.get_application") as mock_get_app:
        mock_app = MagicMock()
        mock_app.session.active_session_id = "default"
        mock_app.list_sessions.return_value = [
            {
                "id": "default",
                "title": "General Chat",
                "message_count": 2,
                "created_at": "2026-10-18T10:00:00Z",
                "updated_at": "2026-10-18T10:05:00Z",
                "active": True,
            }
        ]
        mock_session = MagicMock()
        mock_msg = MagicMock()
        mock_msg.role.value = "user"
        mock_msg.content = "Hello there"
        mock_session.get_messages.return_value = [mock_msg]

        mock_app.session.load.return_value = mock_session
        mock_app.switch_session.return_value = mock_session
        mock_app.create_session.return_value = "sess_123"
        mock_app.delete_session.return_value = True
        mock_get_app.return_value = mock_app

        # List
        res_list = client.get("/api/sessions")
        assert res_list.status_code == 200
        assert res_list.json()["active_session_id"] == "default"
        assert len(res_list.json()["sessions"]) == 1

        # Create
        res_create = client.post("/api/sessions", json={"title": "Work Project"})
        assert res_create.status_code == 200
        assert res_create.json()["id"] == "sess_123"

        # Get detail
        res_detail = client.get("/api/sessions/default")
        assert res_detail.status_code == 200
        assert res_detail.json()["messages"][0]["content"] == "Hello there"

        # Activate
        res_act = client.post("/api/sessions/sess_123/activate")
        assert res_act.status_code == 200
        assert res_act.json()["active"] is True

        # Delete
        res_del = client.delete("/api/sessions/sess_123")
        assert res_del.status_code == 200
        assert res_del.json()["deleted"] is True
