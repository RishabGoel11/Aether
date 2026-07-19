from app.llm.models import Message, Role
from app.memory.models import MemoryRecord


class PromptBuilder:
    @staticmethod
    def _format_memories(
        memories: list[MemoryRecord],
    ) -> str:
        """
        Format memories for inclusion in the system prompt.
        """

        if not memories:
            return ""

        memory_text = "\n".join(
            f"- {memory.content}"
            for memory in memories
        )

        return (
            "\n\nKnown information about the user:\n"
            f"{memory_text}"
        )

    @staticmethod
    def build(
        messages: list[Message],
        memories: list[MemoryRecord] | None = None,
    ) -> list[Message]:
        """
        Build the prompt sent to the language model.
        """

        system_prompt = (
            "You are Aether, a modular, local-first AI engineering assistant. "
            "Always introduce yourself as Aether. "
            "Never claim to be Qwen or any other model. "
            "Be helpful, accurate, and concise."
        )

        system_prompt += PromptBuilder._format_memories(
            memories or [],
        )

        system_message = Message(
            role=Role.SYSTEM,
            content=system_prompt,
        )

        return [system_message, *messages]