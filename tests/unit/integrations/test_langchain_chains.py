from unittest.mock import MagicMock

from app.integrations.langchain.chains import AetherChain, RouterChain
from app.integrations.langchain.llm import AetherLangChainLLM
from app.integrations.langchain.prompts import ChatPromptTemplate, LangChainPromptTemplate
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse


def test_aether_chain_pipe_and_invoke():
    mock_llm = MagicMock(spec=BaseLLM)
    mock_llm.generate.return_value = LLMResponse(
        content="Antigravity is an IDE.",
        tool_calls=[],
    )

    prompt = LangChainPromptTemplate("Tell me about {product}")
    lc_model = AetherLangChainLLM(mock_llm)

    # Chain using pipe syntax
    chain = AetherChain(prompt, lc_model) | (lambda text: text.upper())

    result = chain.invoke({"product": "Antigravity"})
    assert result == "ANTIGRAVITY IS AN IDE."


def test_aether_chain_with_chat_prompt():
    mock_llm = MagicMock(spec=BaseLLM)
    mock_llm.generate.return_value = LLMResponse(
        content="42",
        tool_calls=[],
    )

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a math tutor."),
            ("user", "What is the answer to {question}?"),
        ]
    )

    chain = AetherChain(chat_prompt, mock_llm)
    result = chain.invoke({"question": "life, the universe, and everything"})
    assert result == "42"


def test_router_chain():
    chain_math = MagicMock()
    chain_math.invoke.return_value = "Math Answer"

    chain_general = MagicMock()
    chain_general.invoke.return_value = "General Answer"

    def simple_router(inputs: dict) -> str:
        if "calc" in inputs.get("query", "").lower():
            return "math"
        return "general"

    router = RouterChain(
        router=simple_router,
        destinations={
            "math": chain_math,
            "general": chain_general,
        },
    )

    assert router.invoke({"query": "calculate 2 + 2"}) == "Math Answer"
    assert router.invoke({"query": "tell a story"}) == "General Answer"
