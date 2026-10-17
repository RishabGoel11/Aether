"""LangChain adapter module for Aether."""

from app.integrations.langchain.chains import AetherChain, RouterChain
from app.integrations.langchain.llm import AetherLangChainLLM, LangChainAIMessage
from app.integrations.langchain.prompts import (
    ChatPromptTemplate,
    LangChainPromptTemplate,
    MessagePromptTemplate,
    PromptTemplateError,
)
from app.integrations.langchain.tools import AetherToolAdapter, LangChainToolAdapter

__all__ = [
    "AetherChain",
    "AetherLangChainLLM",
    "AetherToolAdapter",
    "ChatPromptTemplate",
    "LangChainAIMessage",
    "LangChainPromptTemplate",
    "LangChainToolAdapter",
    "MessagePromptTemplate",
    "PromptTemplateError",
    "RouterChain",
]
