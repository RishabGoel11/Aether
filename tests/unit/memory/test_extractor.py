from app.llm.models import Message, Role
from app.memory.extractor import MemoryExtractor
from app.memory.models import MemoryCategory


def test_extract_preference():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="My favorite programming language is Python.",
            )
        ]
    )

    assert len(memories) == 1
    assert memories[0].category is MemoryCategory.PREFERENCE


def test_extract_project():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="I'm building Aether.",
            )
        ]
    )

    assert len(memories) == 1
    assert memories[0].category is MemoryCategory.PROJECT


def test_extract_returns_empty_for_non_memory():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="Hello, how are you?",
            )
        ]
    )

    assert memories == []


def test_extract_is_case_insensitive():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="MY FAVORITE language is Python.",
            )
        ]
    )

    assert len(memories) == 1
    assert memories[0].category is MemoryCategory.PREFERENCE


def test_extract_multiple_memories():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="I'm building Aether and I prefer Python.",
            )
        ]
    )

    assert len(memories) == 2

    categories = {memory.category for memory in memories}

    assert categories == {
        MemoryCategory.PROJECT,
        MemoryCategory.PREFERENCE,
    }


def test_extract_uses_latest_user_message():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.USER,
                content="Hello!",
            ),
            Message(
                role=Role.ASSISTANT,
                content="Hi there!",
            ),
            Message(
                role=Role.USER,
                content="I'm building Aether.",
            ),
        ]
    )

    assert len(memories) == 1
    assert memories[0].category is MemoryCategory.PROJECT


def test_extract_returns_empty_when_no_user_messages():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        [
            Message(
                role=Role.ASSISTANT,
                content="Hello!",
            ),
        ]
    )

    assert memories == []