"""AI Framework Integrations for Aether.

Provides decoupled adapter layers for LangChain and LangGraph paradigms,
ensuring Aether remains framework-independent while supporting ecosystem interop.
"""

from app.integrations.langchain import (
    AetherChain,
    AetherLangChainLLM,
    AetherToolAdapter,
    LangChainPromptTemplate,
    LangChainToolAdapter,
)
from app.integrations.langgraph import (
    CompiledGraph,
    GraphReActAgent,
    GraphState,
    StateGraph,
)

__all__ = [
    "AetherChain",
    "AetherLangChainLLM",
    "AetherToolAdapter",
    "CompiledGraph",
    "GraphReActAgent",
    "GraphState",
    "LangChainPromptTemplate",
    "LangChainToolAdapter",
    "StateGraph",
]
