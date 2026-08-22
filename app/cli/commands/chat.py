from app.bootstrap.builder import ApplicationBuilder


def run() -> None:
    """
    Start an interactive chat session.
    """
    app = ApplicationBuilder().build()

    print("Welcome to Aether!")
    print("Type 'exit' to quit or '/clear' to start a new conversation.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.lower() == "/clear":
            app.clear_conversation()
            print("Conversation cleared.\n")
            continue

        if not user_input:
            continue

        response = app.chat(user_input)

        print(f"Aether: {response.content}\n")