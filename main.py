from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.core.session import Session
from app.llm.factory import LLMFactory


def main():
    loader = ConfigLoader()
    settings = loader.load()

    llm = LLMFactory.create(settings.llm)
    session = Session()

    engine = ConversationEngine(llm, session=session)

    print("Welcome to Aether!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            print("Goodbye!")
            break

        response = engine.chat(user_input)

        print(f"Aether: {response.content}")


if __name__ == "__main__":
    main()
