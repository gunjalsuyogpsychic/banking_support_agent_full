import os
from dataclasses import dataclass

@dataclass
class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")   # groq or ollama
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    DB_PATH: str = os.getenv("DB_PATH", "storage/support_tickets.db")

settings = Settings()
