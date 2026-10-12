from config import DbProvider
from core.connector.llm.lmstudio import LmStudioConnector
from core.connector.db.sqlite import SqliteConversationStore
from core.protocols import Conversational
from core.connector.factory import create_store

def greet(llm: Conversational) -> str:
    return llm.ask("Say hello in five words.", system="Be brief.")

if __name__ == "__main__":
    # llm = LmStudioConnector()
    # print(greet(llm))

    store = create_store(DbProvider.POSTGRESQL)
    store.save("demo", "user", "Hello, how are you?")
    store.save("demo", "assistant", "A structural interface")

    for message in store.history("demo"):
        print(message)