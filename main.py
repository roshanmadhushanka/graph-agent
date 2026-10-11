from core.connector.llm import LmStudioConnector
from core.protocols import Conversational

def greet(llm: Conversational) -> str:
    return llm.ask("Say hello in five words.", system="Be brief.")

if __name__ == "__main__":
    llm = LmStudioConnector()
    print(greet(llm))
