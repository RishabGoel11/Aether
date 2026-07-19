from unittest.mock import MagicMock, patch

from app.embedding.ollama import OllamaEmbedder


def test_embed():
    response = MagicMock()
    response.embeddings = [[0.1, 0.2, 0.3]]

    with patch("app.embedding.ollama.Client") as mock_client:
        mock_client.return_value.embed.return_value = response

        embedder = OllamaEmbedder()

        embedding = embedder.embed("Hello")

        assert embedding == [0.1, 0.2, 0.3]

        mock_client.return_value.embed.assert_called_once_with(
            model="nomic-embed-text",
            input="Hello",
        )


def test_embed_batch():
    response = MagicMock()
    response.embeddings = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    with patch("app.embedding.ollama.Client") as mock_client:
        mock_client.return_value.embed.return_value = response

        embedder = OllamaEmbedder()

        embeddings = embedder.embed_batch(
            [
                "Hello",
                "World",
            ]
        )

        assert embeddings == [
            [0.1, 0.2],
            [0.3, 0.4],
        ]

        mock_client.return_value.embed.assert_called_once_with(
            model="nomic-embed-text",
            input=[
                "Hello",
                "World",
            ],
        )
    
def test_custom_model():
    response = MagicMock()
    response.embeddings = [[0.1]]

    with patch("app.embedding.ollama.Client") as mock_client:
        mock_client.return_value.embed.return_value = response

        embedder = OllamaEmbedder(model="bge-m3")

        embedder.embed("Hello")

        mock_client.return_value.embed.assert_called_once_with(
            model="bge-m3",
            input="Hello",
        )


def test_custom_host():
    with patch("app.embedding.ollama.Client") as mock_client:
        OllamaEmbedder(host="http://test:11434")

        mock_client.assert_called_once_with(
            host="http://test:11434",
        )