from unittest.mock import Mock

from app.memory.consolidator import MemoryConsolidator
from app.memory.models import MemoryRecord


def test_does_nothing_below_threshold():
    manager = Mock()
    summarizer = Mock()

    manager.list.return_value = [
        MemoryRecord(content="Memory 1"),
        MemoryRecord(content="Memory 2"),
    ]

    consolidator = MemoryConsolidator(
        manager,
        summarizer,
        threshold=3,
    )

    try:
        consolidator.consolidate()
    except NotImplementedError:
        pass

    summarizer.summarize.assert_not_called()


def test_calls_summarizer():
    manager = Mock()
    summarizer = Mock()

    memories = [MemoryRecord(content=f"Memory {i}") for i in range(5)]

    manager.list.return_value = memories

    consolidator = MemoryConsolidator(
        manager,
        summarizer,
        threshold=5,
    )

    try:
        consolidator.consolidate()
    except NotImplementedError:
        pass

    summarizer.summarize.assert_called_once_with(memories)


def test_stores_summary():
    manager = Mock()
    summarizer = Mock()

    memories = [MemoryRecord(content=f"Memory {i}") for i in range(5)]

    summary = MemoryRecord(content="Summary")

    manager.list.return_value = memories
    summarizer.summarize.return_value = summary

    consolidator = MemoryConsolidator(
        manager,
        summarizer,
        threshold=5,
    )

    consolidator.consolidate()

    manager.remember.assert_called_once_with(summary)


def test_deletes_old_memories():
    manager = Mock()
    summarizer = Mock()

    memories = [MemoryRecord(content=f"Memory {i}") for i in range(5)]

    manager.list.return_value = memories
    summarizer.summarize.return_value = MemoryRecord(content="Summary")

    consolidator = MemoryConsolidator(
        manager,
        summarizer,
        threshold=5,
    )

    consolidator.consolidate()

    assert manager.forget.call_count == len(memories)

    for memory in memories:
        manager.forget.assert_any_call(memory.id)
