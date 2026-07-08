from app.llm.models import Message, Role


class PromptBuilder:
    @staticmethod
    def build(messages: list[Message]) -> list[Message]:
        system_message = Message(
            role=Role.SYSTEM,
            content=(
                "You are Aether, a modular, local-first AI engineering assistant. "
                "Always introduce yourself as Aether. "
                "Never claim to be Qwen or any other model. "
                "Be helpful, accurate, and concise."
            ),
        )

        return [system_message, *messages]