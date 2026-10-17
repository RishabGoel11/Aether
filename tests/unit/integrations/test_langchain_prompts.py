import pytest

from app.integrations.langchain.prompts import (
    ChatPromptTemplate,
    LangChainPromptTemplate,
    PromptTemplateError,
)
from app.llm.models import Role


def test_prompt_template_variable_extraction():
    tmpl = LangChainPromptTemplate("Hello {name}, welcome to {place}!")
    assert tmpl.input_variables == ["name", "place"]


def test_prompt_template_format_success():
    tmpl = LangChainPromptTemplate("Answer question: {question}")
    result = tmpl.format(question="What is gravity?")
    assert result == "Answer question: What is gravity?"


def test_prompt_template_missing_variable_raises():
    tmpl = LangChainPromptTemplate("Hello {first} {last}")
    with pytest.raises(PromptTemplateError) as exc_info:
        tmpl.format(first="Albert")
    assert "Missing prompt variables: last" in str(exc_info.value)


def test_prompt_template_to_message():
    tmpl = LangChainPromptTemplate("System alert: {msg}")
    msg = tmpl.to_message(role=Role.SYSTEM, msg="Low disk space")
    assert msg.role == Role.SYSTEM
    assert msg.content == "System alert: Low disk space"


def test_chat_prompt_template():
    chat_tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert in {domain}."),
            ("user", "Explain {topic} in simple terms."),
        ]
    )

    assert chat_tmpl.input_variables == ["domain", "topic"]

    messages = chat_tmpl.format_messages(domain="physics", topic="quantum entanglement")
    assert len(messages) == 2
    assert messages[0].role == Role.SYSTEM
    assert messages[0].content == "You are an expert in physics."
    assert messages[1].role == Role.USER
    assert messages[1].content == "Explain quantum entanglement in simple terms."
