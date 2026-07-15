from app.llm.models import Message, Role
from app.memory.models import MemoryRecord


class PromptBuilder:
    @staticmethod
    def build(
        messages: list[Message],
        memories: list[MemoryRecord] | None = None,
    ) -> list[Message]:
        system_prompt = (
            "You are Aether, a modular, local-first AI engineering assistant. "
            "Always introduce yourself as Aether. "
            "Never claim to be Qwen or any other model. "
            "Be helpful, accurate, and concise."
        )

        if memories:
            memory_text = "\n".join(f"- {memory.content}" for memory in memories)

            system_prompt += f"\n\nRelevant Memories:\n{memory_text}"

        system_message = Message(
            role=Role.SYSTEM,
            content=system_prompt,
        )

        return [system_message, *messages]
