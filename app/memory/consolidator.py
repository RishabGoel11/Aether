from app.memory.manager import MemoryManager
from app.memory.summarizer import MemorySummarizer


class MemoryConsolidator:
    """
    Consolidates many memories into a summarized memory.
    """

    def __init__(
        self,
        manager: MemoryManager,
        summarizer: MemorySummarizer,
        threshold: int = 20,
    ):
        self._manager = manager
        self._summarizer = summarizer
        self._threshold = threshold

    def consolidate(self) -> None:
        memories = self._manager.list()

        if len(memories) < self._threshold:
            return

        summary = self._summarizer.summarize(memories)

        self._manager.remember(summary)

        for memory in memories:
            self._manager.forget(memory.id)