import ollama
from ollama import ResponseError

from app.config.config import LLMSettings
from app.core.exceptions import (
    LLMConnectionError,
    LLMResponseError,
)
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message
from app.logger.logger import get_logger

logger = get_logger(__name__)


class OllamaLLM(BaseLLM):
    def __init__(self, settings: LLMSettings):
        self.model = settings.model
        self.temperature = settings.temperature

        logger.info(f"Initialized Ollama provider with model '{self.model}'.")

    def generate(self, messages: list[Message]) -> LLMResponse:
        ollama_messages = []

        for message in messages:
            ollama_messages.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        logger.info("Sending request to Ollama.")

        try:
            response = ollama.chat(
                model=self.model,
                messages=ollama_messages,
            )

            logger.info("Received response from Ollama.")

            return LLMResponse(content=response["message"]["content"])

        except ConnectionError as e:
            logger.error("Failed to connect to Ollama.")

            raise LLMConnectionError("Unable to connect to the Ollama server.") from e

        except ResponseError as e:
            logger.error("Ollama returned an invalid response.")

            raise LLMResponseError(f"Ollama error: {e}") from e
