# import sys
#
# from app.service.chat import ChatService
# from core.connector.factory import create_llm, create_checkpointer
#
#
# def build_agent(name: str, persona: str, topic: str) -> ChatService:
#     system = (
#         f"You are {name}, in a conversation with another AI agent about this topic: {topic}. "
#         f"{persona} Keep each reply to 2-3 sentences and always move the discussion forward."
#     )
#     return ChatService(llm=create_llm(), checkpointer=create_checkpointer(), system=system)
#
#
# def main() -> None:
#     conversation_id = sys.argv[1] if len(sys.argv) > 1 else "default"
#     topic = input("Topic: ").strip()
#     if not topic:
#         print("A topic is required.")
#         return
#
#     agents = [
#         ("agent_1", build_agent("agent_1", "You explain ideas and share insights.", topic)),
#         ("agent_2", build_agent("agent_2", "You ask probing questions and respectfully challenge points.", topic)),
#         ("agent_3", build_agent("agent_3", "You provide counterarguments and alternative perspectives.", topic)),
#     ]
#
#     print(f"Conversation {conversation_id}. Press Ctrl+C to quit.")
#     try:
#         message = f"Let's discuss: {topic}"
#         print(f"user> {message}")
#         turn = 0
#         iteration = 0
#         while iteration < 1000:
#             name, agent = agents[turn % 3]
#             message = agent.send(f"{conversation_id}-{name}", "user", message)
#             print(f"{name}> {message}\n")
#             turn += 1
#             iteration += 1
#     except (KeyboardInterrupt, EOFError):
#         print("Exiting...")
#
#
# if __name__ == "__main__":
#     main()
