from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.core.exceptions import (
    LLMConnectionError,
    LLMResponseError,
)
from app.core.session import Session
from app.llm.factory import LLMFactory
from app.logger.config import configure_logging
from app.logger.logger import get_logger


def main():
    loader = ConfigLoader()
    settings = loader.load()

    configure_logging(settings.logging)

    logger = get_logger("aether.main")

    llm = LLMFactory.create(settings.llm)
    session = Session()

    engine = ConversationEngine(
        llm=llm,
        session=session,
    )

    logger.info("Aether started successfully.")

    print("Welcome to Aether!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            logger.info("Aether shutting down.")
            print("Goodbye!")
            break

        try:
            response = engine.chat(user_input)
            print(f"Aether: {response.content}")

        except LLMConnectionError as e:
            logger.error(str(e))
            print(f"❌ {e}")

        except LLMResponseError as e:
            logger.error(str(e))
            print(f"❌ {e}")


if __name__ == "__main__":
    main()