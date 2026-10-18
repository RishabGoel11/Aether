from __future__ import annotations

from typing import TYPE_CHECKING

from app.agent.runner import AgentRunner
from app.config.config import Settings
from app.core.engine import ConversationEngine
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.rag.pipeline import RAGPipeline
from app.session.manager import SessionManager
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry

if TYPE_CHECKING:
    from app.multi_agent.team import AgentTeam
    from app.voice.pipeline import VoicePipeline
    from app.web.pipeline import WebPipeline


class Application:
    """
    Represents a running Aether application.

    This class owns the application's core components and
    provides the primary interface for interacting with them.
    """

    def __init__(
        self,
        settings: Settings,
        engine: ConversationEngine,
        session: SessionManager,
        memory: MemoryManager,
        extractor: MemoryExtractor,
        tools: ToolRegistry,
        tool_executor: ToolExecutor,
        agent: AgentRunner,
        rag: RAGPipeline | None = None,
        web: WebPipeline | None = None,
        voice: VoicePipeline | None = None,
        team: AgentTeam | None = None,
    ):
        self.settings = settings
        self.engine = engine
        self.session = session
        self.memory = memory
        self.extractor = extractor
        self.tools = tools
        self.tool_executor = tool_executor
        self.agent = agent
        self.rag = rag
        self.web = web
        self.voice = voice
        self.team = team

    def chat(self, user_input: str, session_id: str | None = None):
        """
        Send a message to Aether within the active or specified session.
        """
        if session_id and session_id != self.session.active_session_id:
            self.switch_session(session_id)

        response = self.engine.chat(user_input)

        self.session.save(self.engine.session)

        return response

    def switch_session(self, session_id: str):
        """
        Switch active session in both the session manager and engine.
        """
        session = self.session.switch_session(session_id)
        self.engine.session = session
        return session

    def create_session(self, title: str = "New Chat") -> str:
        """
        Create a new session, activate it, and update engine.
        """
        session_id = self.session.create_session(title=title)
        self.engine.session = self.session.load(session_id)
        return session_id

    def list_sessions(self) -> list[dict]:
        """
        List all available conversation sessions.
        """
        return self.session.list_sessions()

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and reset engine active session.
        """
        success = self.session.delete_session(session_id)
        self.engine.session = self.session.load()
        return success

    def clear_conversation(self) -> None:
        """
        Clear the current conversation and start a new session.
        """
        self.engine.session = self.session.clear()

    def get_langchain_model(self):
        """Return a LangChain-compatible chat model wrapping Aether's configured LLM."""
        from app.integrations.langchain.llm import AetherLangChainLLM

        return AetherLangChainLLM(self.engine.llm, tools=self.tools.list())

    def create_graph_agent(self):
        """Create a stateful LangGraph ReAct agent using Aether's LLM and registered tools."""
        from app.integrations.langgraph.agent import GraphReActAgent

        return GraphReActAgent(
            llm=self.engine.llm,
            tools=self.tools.list(),
            executor=self.tool_executor,
        )
