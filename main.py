from app.bootstrap.builder import ApplicationBuilder
from app.core.exceptions import (
    LLMConnectionError,
    LLMResponseError,
)
from app.logger.logger import get_logger


def main():

    app = ApplicationBuilder()

    application = app.build()

    logger = get_logger("aether.main")

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
            response = application.chat(user_input)
            print(f"Aether: {response.content}")

        except LLMConnectionError as e:
            logger.error(str(e))
            print(f"❌ {e}")

        except LLMResponseError as e:
            logger.error(str(e))
            print(f"❌ {e}")


if __name__ == "__main__":
    main()
