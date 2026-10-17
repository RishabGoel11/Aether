"""LangChain-compatible prompt template adapters for Aether."""

from __future__ import annotations

import re
from typing import Any

from app.llm.models import Message, Role


class PromptTemplateError(ValueError):
    """Raised when prompt template variable formatting fails."""


class LangChainPromptTemplate:
    """Prompt template adapter mimicking LangChain's PromptTemplate."""

    def __init__(self, template: str, input_variables: list[str] | None = None) -> None:
        self.template = template
        self.input_variables = (
            input_variables if input_variables is not None else self._extract_variables(template)
        )

    @staticmethod
    def _extract_variables(template: str) -> list[str]:
        """Extract variable names enclosed in single curly braces."""
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        found = re.findall(pattern, template)
        return sorted(list(set(found)))

    def format(self, **kwargs: Any) -> str:
        """Format the template with provided kwargs.

        Raises:
            PromptTemplateError: If any required variable is missing.
        """
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise PromptTemplateError(
                f"Missing prompt variables: {', '.join(missing)}. Expected: {self.input_variables}"
            )
        try:
            return self.template.format(**kwargs)
        except KeyError as exc:
            raise PromptTemplateError(f"Failed to format template: {exc}") from exc

    def to_message(self, role: Role = Role.USER, **kwargs: Any) -> Message:
        """Format the template and return as an Aether Message."""
        content = self.format(**kwargs)
        return Message(role=role, content=content)


class MessagePromptTemplate:
    """Template for a specific message role."""

    def __init__(self, role: Role, template: str) -> None:
        self.role = role
        self.prompt_template = LangChainPromptTemplate(template)

    @property
    def input_variables(self) -> list[str]:
        return self.prompt_template.input_variables

    def format(self, **kwargs: Any) -> Message:
        return self.prompt_template.to_message(role=self.role, **kwargs)


class ChatPromptTemplate:
    """Chat prompt template adapter combining multiple role-based templates."""

    def __init__(self, message_templates: list[MessagePromptTemplate]) -> None:
        self.message_templates = message_templates

    @classmethod
    def from_messages(cls, messages: list[tuple[str, str]]) -> ChatPromptTemplate:
        """Create a ChatPromptTemplate from tuples of (role_str, template_str).

        Example:
            [("system", "You are a helpful assistant."), ("user", "Hello {name}!")]
        """
        templates: list[MessagePromptTemplate] = []
        for role_str, tmpl in messages:
            norm_role = role_str.strip().lower()
            if norm_role in ("system", "sys"):
                role = Role.SYSTEM
            elif norm_role in ("user", "human"):
                role = Role.USER
            elif norm_role in ("assistant", "ai"):
                role = Role.ASSISTANT
            else:
                role = Role.USER
            templates.append(MessagePromptTemplate(role=role, template=tmpl))
        return cls(templates)

    @property
    def input_variables(self) -> list[str]:
        vars_set: set[str] = set()
        for mt in self.message_templates:
            vars_set.update(mt.input_variables)
        return sorted(list(vars_set))

    def format_messages(self, **kwargs: Any) -> list[Message]:
        """Format all message templates into Aether Message instances."""
        return [mt.format(**kwargs) for mt in self.message_templates]
