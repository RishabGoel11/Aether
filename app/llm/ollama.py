import ollama
from ollama import ResponseError

from app.config.config import LLMSettings
from app.core.exceptions import (
    LLMConnectionError,
    LLMResponseError,
)
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, ToolCall
from app.logger.logger import get_logger
from app.tools.models import ToolDefinition

logger = get_logger(__name__)


class OllamaLLM(BaseLLM):
    def __init__(self, settings: LLMSettings):
        self.model = settings.model
        self.temperature = settings.temperature

        logger.info(f"Initialized Ollama provider with model '{self.model}'.")

    @staticmethod
    def _build_tools(
        tools: list[ToolDefinition],
    ) -> list[dict]:
        """Convert Aether tool definitions to Ollama's tool format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
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
            request_kwargs = {
                "model": self.model,
                "messages": ollama_messages,
            }

            if tools:
                request_kwargs["tools"] = self._build_tools(tools)

            response = ollama.chat(**request_kwargs)

            logger.info("Received response from Ollama.")

            tool_calls = []

            for index, tool_call in enumerate(
                response["message"].get("tool_calls", []),
            ):
                function = tool_call["function"]

                tool_calls.append(
                    ToolCall(
                        id=f"call_{index}",
                        name=function["name"],
                        arguments=function.get("arguments", {}),
                    )
                )

            return LLMResponse(
                content=response["message"].get("content", ""),
                tool_calls=tool_calls,
            )

        except ConnectionError as exc:
            logger.error("Failed to connect to Ollama.")

            raise LLMConnectionError(
                "Unable to connect to the Ollama server.",
            ) from exc

        except ResponseError as exc:
            logger.error("Ollama returned an invalid response.")

            raise LLMResponseError(
                f"Ollama error: {exc}",
            ) from exc
