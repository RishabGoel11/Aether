"""Chain execution abstractions following the LangChain pipe and execution style."""

from __future__ import annotations

from typing import Any, Callable

from app.integrations.langchain.llm import AetherLangChainLLM, LangChainAIMessage
from app.integrations.langchain.prompts import ChatPromptTemplate, LangChainPromptTemplate
from app.llm.base import BaseLLM


class AetherChain:
    """Composable execution chain connecting prompt templates to models and parsers.

    Supports the modern pipe operator (|) syntax:
        chain = prompt | llm | (lambda x: x.upper())
    """

    def __init__(
        self,
        prompt: LangChainPromptTemplate | ChatPromptTemplate,
        llm: AetherLangChainLLM | BaseLLM,
        output_parser: Callable[[str], Any] | None = None,
    ) -> None:
        self.prompt = prompt
        self.llm = llm if isinstance(llm, AetherLangChainLLM) else AetherLangChainLLM(llm)
        self.output_parser = output_parser

    def invoke(self, inputs: dict[str, Any]) -> Any:
        """Execute the chain: format prompt -> invoke LLM -> parse output."""
        if isinstance(self.prompt, ChatPromptTemplate):
            messages = self.prompt.format_messages(**inputs)
            response: LangChainAIMessage = self.llm.invoke(messages)
        else:
            prompt_str = self.prompt.format(**inputs)
            response = self.llm.invoke(prompt_str)

        text = response.content
        if self.output_parser is not None:
            return self.output_parser(text)
        return text

    def __call__(self, inputs: dict[str, Any]) -> Any:
        return self.invoke(inputs)

    def __or__(self, other: Callable[[Any], Any]) -> AetherChain:
        """Chain with another callable (output parser / transform)."""
        if self.output_parser is not None:
            existing_parser = self.output_parser
            new_parser = lambda text: other(existing_parser(text))  # noqa: E731
        else:
            new_parser = other

        return AetherChain(
            prompt=self.prompt,
            llm=self.llm,
            output_parser=new_parser,
        )


class RouterChain:
    """Routes an input to one of multiple candidate chains based on a routing condition."""

    def __init__(
        self,
        router: Callable[[dict[str, Any]], str],
        destinations: dict[str, AetherChain | Callable[[dict[str, Any]], Any]],
        default_destination: AetherChain | Callable[[dict[str, Any]], Any] | None = None,
    ) -> None:
        self.router = router
        self.destinations = destinations
        self.default_destination = default_destination

    def invoke(self, inputs: dict[str, Any]) -> Any:
        route_key = self.router(inputs)
        selected = self.destinations.get(route_key, self.default_destination)
        if selected is None:
            raise KeyError(
                f"Router selected key '{route_key}', but no destination or default was found."
            )
        if hasattr(selected, "invoke"):
            return selected.invoke(inputs)
        return selected(inputs)
