from app.memory.models import (
    MemoryCategory,
    MemoryRecord,
    MemorySource,
)


def test_memory_record_defaults():
    record = MemoryRecord(content="User likes Python")

    assert record.content == "User likes Python"
    assert record.category == MemoryCategory.OTHER
    assert record.source == MemorySource.AUTOMATIC
    assert record.metadata == {}
    assert record.id is not None
    assert record.created_at is not None
    assert record.updated_at is not None


def test_memory_record_custom_values():
    record = MemoryRecord(
        content="Building Aether",
        category=MemoryCategory.PROJECT,
        source=MemorySource.EXPLICIT,
        metadata={"language": "python"},
    )

    assert record.category == MemoryCategory.PROJECT
    assert record.source == MemorySource.EXPLICIT
    assert record.metadata["language"] == "python"