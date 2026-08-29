# rememb0

A conversational AI agent with persistent long-term memory, built using [mem0](https://mem0.ai) and [Qdrant](https://qdrant.tech). It remembers facts about the user across sessions and holds coherent multi-turn conversations. Powered entirely by free-tier APIs and local embeddings.

## What it does

- Chats with you like a normal LLM-powered assistant.
- Extracts and stores facts about you (name, preferences, location, etc.) as you talk, persisting across sessions, not just within one conversation.
- Retrieves relevant memories via semantic search and injects them into context, so it can answer relevant questions later.
- Maintains short-term conversation history within a session, so follow-up questions work correctly.
- Falls back gracefully if a rate limit is hit, instead of crashing.

## Architecture

| Component | Role | Provider |
|---|---|---|
| Chat responses | Generates the replies you see | Groq (`openai/gpt-oss-20b`) |
| Memory fact-extraction | Decides what's worth remembering from a conversation | Google Gemini (`gemini-3.6-flash`) |
| Embeddings | Converts text to vectors for storage/search | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (runs locally, no API key) |
| Vector storage | Stores and searches memory vectors | Qdrant (self-hosted via Docker) |
| Orchestration | Ties memory search/storage together | mem0 |

Two different LLMs are used deliberately: Groq for fast, low-latency chat replies where response speed matters most to the user, and Gemini for background memory extraction, where a much higher rate-limit ceiling matters more than raw speed.

## Setup

### Prerequisites
- Python 3.9+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Qdrant)
- A free [Groq API key](https://console.groq.com)
- A free [Gemini API key](https://aistudio.google.com/apikey)

### Steps

1. Clone the repo and set up a virtual environment:
   ```bash
   git clone <your-repo-url>
   cd mem0-chat-agent
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate  # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Start Qdrant (leave this running in its own terminal):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

5. Run the chatbot:
   ```bash
   python main.py
   ```

## Design notes

- **Why not use full transcript storage as memory?** mem0 extracts and distills facts rather than storing raw conversation history. This keeps stored memories concise and relevant to semantic search, rather than growing an unbounded, noisy transcript log.
- **Why the try/except fallback around `memory.add()`?** Free-tier LLM APIs impose rate limits (tokens-per-minute) that can be exceeded during fact-extraction on longer conversations. Rather than crashing the chat loop, the code falls back to storing the raw exchange without LLM-based extraction into organised facts when this happens.

## Known limitations

- Full verbatim conversation transcripts are not stored or retrievable, only distilled facts persist across sessions.
- Free-tier API rate limits may still be hit under heavy or rapid testing; the fallback described above handles this gracefully but does reduce extraction quality for that exchange.

## Built with

Python · mem0 · Qdrant · Groq · Google Gemini · sentence-transformers