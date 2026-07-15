from app.memory.extractor import MemoryExtractor
from app.memory.models import MemoryCategory, MemorySource


def test_extract_preference():
    extractor = MemoryExtractor()

    memories = extractor.extract("My favorite programming language is Python.")

    assert len(memories) == 1
    assert memories[0].category == MemoryCategory.PREFERENCE
    assert memories[0].source == MemorySource.AUTOMATIC
    assert memories[0].content == ("My favorite programming language is Python.")


def test_extract_project():
    extractor = MemoryExtractor()

    memories = extractor.extract("I'm building Aether.")

    assert len(memories) == 1
    assert memories[0].category == MemoryCategory.PROJECT


def test_extract_returns_empty_for_non_memory():
    extractor = MemoryExtractor()

    memories = extractor.extract("Hello, how are you?")

    assert memories == []


def test_extract_is_case_insensitive():
    extractor = MemoryExtractor()

    memories = extractor.extract("MY FAVORITE language is Python.")

    assert len(memories) == 1
    assert memories[0].category == MemoryCategory.PREFERENCE


def test_extract_multiple_memories():
    extractor = MemoryExtractor()

    memories = extractor.extract("I'm building Aether and I prefer Python.")

    assert len(memories) == 2

    categories = {memory.category for memory in memories}

    assert MemoryCategory.PROJECT in categories
    assert MemoryCategory.PREFERENCE in categories
