from app.llm.base import BaseLLM
from app.llm.models import Message, Role
from app.memory.models import MemoryRecord


class MemorySummarizer:
    """
    Generates concise long-term memory summaries.
    """

    def __init__(
        self,
        llm: BaseLLM,
    ):
        self._llm = llm

    def summarize(
        self,
        memories: list[MemoryRecord],
    ) -> MemoryRecord:
        contents = "\n".join(
            f"- {memory.content}"
            for memory in memories
        )

        prompt = (
            "You are summarizing long-term user memories.\n\n"
            "Create one concise factual summary.\n"
            "Do not invent information.\n"
            "Do not omit important recurring facts.\n\n"
            f"Memories:\n{contents}\n\n"
            "Summary:"
        )

        response = self._llm.generate(
            [
                Message(
                    role=Role.SYSTEM,
                    content="You summarize long-term memories.",
                ),
                Message(
                    role=Role.USER,
                    content=prompt,
                ),
            ]
        )

        return MemoryRecord(
            content=response.content,
        )