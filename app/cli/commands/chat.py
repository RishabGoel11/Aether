from app.bootstrap.builder import ApplicationBuilder


def run() -> None:
    """
    Start an interactive chat session.
    """
    app = ApplicationBuilder().build()

    print("Welcome to Aether!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        response = app.chat(user_input)

        print(f"Aether: {response.content}\n")