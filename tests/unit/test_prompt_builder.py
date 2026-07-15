from app.core.prompt_builder import PromptBuilder
from app.llm.models import Message, Role
from app.memory.models import MemoryRecord


def test_build_without_memories():
    messages = [
        Message(
            role=Role.USER,
            content="Hello",
        )
    ]

    prompt = PromptBuilder.build(messages)

    assert prompt[0].role == Role.SYSTEM
    assert "Relevant Memories" not in prompt[0].content
    assert prompt[1:] == messages


def test_build_with_memories():
    messages = [
        Message(
            role=Role.USER,
            content="Hello",
        )
    ]

    memories = [
        MemoryRecord(content="User likes Python"),
        MemoryRecord(content="Building Aether"),
    ]

    prompt = PromptBuilder.build(
        messages,
        memories,
    )

    system_prompt = prompt[0].content

    assert "Relevant Memories" in system_prompt
    assert "User likes Python" in system_prompt
    assert "Building Aether" in system_prompt
