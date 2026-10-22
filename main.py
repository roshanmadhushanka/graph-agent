import sys

from app.service.chat import ChatService
from core.connector.factory import create_llm, create_checkpointer
from app.tools import TOOLS

def main() -> None:
    conversation_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    chat = ChatService(
        llm=create_llm(),
        checkpointer=create_checkpointer(),
        system="You are a concise assistant. Use tools for time and math.",
        tools=TOOLS,
    )

    print(f"Conversation {conversation_id}. Type 'exit' to quit.")
    try:

        while True:
            prompt = input("user> ").strip()
            if prompt.lower() == "exit":
                return
            if prompt:
                print(f"assistant> {chat.send(conversation_id, "user", prompt)}")
    except (KeyboardInterrupt, EOFError):
        print("Exiting...")

if __name__ == "__main__":
    main()