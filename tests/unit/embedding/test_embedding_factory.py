from app.embedding.factory import EmbeddingFactory
from app.embedding.ollama import OllamaEmbedder


def test_factory_returns_ollama_embedder():
    embedder = EmbeddingFactory.create()

    assert isinstance(embedder, OllamaEmbedder)

