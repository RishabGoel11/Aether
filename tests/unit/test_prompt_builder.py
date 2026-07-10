from app.core.prompt_builder import PromptBuilder
from app.llm.models import Message, Role


def test_build_adds_system_message():
    user_message = Message(
        role=Role.USER,
        content="Hello",
    )

    result = PromptBuilder.build([user_message])

    assert result[0].role == Role.SYSTEM

def test_build_preserves_original_messages():
    user_message = Message(
        role=Role.USER,
        content="Hello",
    )

    result = PromptBuilder.build([user_message])

    assert result[1:] == [user_message]

def test_build_returns_one_extra_message():
    messages = [
        Message(
            role=Role.USER,
            content="Hello",
        )
    ]

    result = PromptBuilder.build(messages)

    assert len(result) == len(messages) + 1