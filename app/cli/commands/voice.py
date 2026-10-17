"""
CLI command: aether voice

Interactive voice assistant listening to your microphone and speaking responses aloud.

Usage
-----
    aether voice
    aether voice --seconds 6
    aether voice --until-silence
"""

from __future__ import annotations

from app.bootstrap.builder import ApplicationBuilder


def voice(seconds: float = 5.0, until_silence: bool = False, speak_response: bool = True) -> None:
    """
    Launch interactive microphone voice assistant session.
    """
    app = ApplicationBuilder().build()

    if not app.voice:
        print("❌ Error: Voice pipeline is not initialized.")
        return

    print("\n🎙️  Aether Voice Assistant")
    print("─" * 60)
    devices = app.voice.list_input_devices()
    if devices:
        default_dev = devices[0]["name"]
        print(f"Default Microphone: {default_dev}")
    else:
        print("⚠️ No microphone input devices detected.")

    mode = "automatic silence detection" if until_silence else f"{seconds}s fixed window"
    print(f"Listening Mode: {mode}")
    print("Speak naturally. Aether will listen, transcribe, process, and speak back.")
    print("─" * 60)
    print("Commands: Press [Enter] to start speaking, or type 'exit' to quit.\n")

    while True:
        try:
            cmd = input("Press [Enter] to speak (or 'exit'): ").strip().lower()
            if cmd in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            print("\n🔴 Listening... Speak into your microphone now.")
            turn = app.voice.listen_and_process(
                duration=seconds,
                until_silence=until_silence,
                speak_response=speak_response,
            )

            user_text = turn.get("user_text", "").strip()
            response_text = turn.get("response_text", "").strip()

            if user_text:
                print(f"🗣️  You said: {user_text}")
                print(f"🤖 Aether:   {response_text}\n")
            else:
                print("⚠️  No speech detected. Please speak closer to your microphone.\n")

        except KeyboardInterrupt:
            print("\nVoice session ended.")
            break
        except Exception as exc:
            print(f"❌ Voice error: {exc}\n")
