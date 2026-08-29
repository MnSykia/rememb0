import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 384,
        },
    },
    "llm": {
    "provider": "gemini",
    "config": {
        "api_key": os.getenv("GEMINI_API_KEY"),
        "model": "gemini-3.6-flash",
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
    },
    "version": "v1.1",
    "custom_instructions": (
    "Extract concise, factual statements about the user: name, location, "
    "occupation, preferences etc. Phrase each as a short, third-person "
    "statement (e.g., 'prefers tea over coffee'). If new information "
    "contradicts an existing fact, prioritize the newer one. Ignore "
    "small talk, greetings, and questions with no factual content."
    ),
}
