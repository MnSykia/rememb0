import os
from groq import Groq
from mem0 import Memory
from dotenv import load_dotenv
from config import config
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
memory = Memory.from_config(config)

# Short term-memory below is separate from mem0's long-term memory, which remains across sessions.
chat_history = []

def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant long-term memories (collected from across sessions)
    relevant_memories = memory.search(query=message, filters={"user_id": user_id}, limit=3)
    memories_str = "\n".join(
        f"- {entry['memory']}" for entry in relevant_memories["results"]
    )
    print(memories_str)

    # Prompt includes system instructions + recent session history + current message
    system_prompt = f"You are a helpful AI. Answer the question based on query and memories.\nUser Memories:\n{memories_str}"
    messages = (
        [{"role": "system", "content": system_prompt}]
        + chat_history
        + [{"role": "user", "content": message}]
    )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b", messages=messages
    )
    assistant_response = response.choices[0].message.content

    # Update running session history i.e. short-term memory
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": assistant_response})

    # New long-term memories (from current exchange)
    new_exchange = [
        {"role": "user", "content": message},
        {"role": "assistant", "content": assistant_response},
    ]
    # Failsafe if TPM gets exceeded, although not observed when using Google GenAI api
    try:
        memory.add(new_exchange, user_id=user_id, metadata={"source": "demo"}, infer=True)
    except Exception as e:
        if "rate_limit_exceeded" in str(e) or "413" in str(e):
            print("(Note: falling back to raw storage due to rate limit)")
            memory.add(new_exchange, user_id=user_id, metadata={"source": "demo"}, infer=False)
        else:
            raise

    return assistant_response


def main():
    print("Chat with AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print(f"AI: {chat_with_memories(user_input)}")


if __name__ == "__main__":
    main()