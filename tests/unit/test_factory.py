from app.config.config import LLMProvider, LLMSettings
from app.llm.factory import LLMFactory
from app.llm.ollama import OllamaLLM


def test_factory_returns_ollama_provider():
    settings = LLMSettings(
        provider=LLMProvider.OLLAMA,
        model="qwen3:8b",
        temperature=0.7,
    )

    llm = LLMFactory.create(settings)

    assert isinstance(llm, OllamaLLM)   