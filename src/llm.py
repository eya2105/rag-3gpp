import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from config import GROQ_MODEL, ROOT


load_dotenv(ROOT / ".env")


def get_groq_model(model: str | None = None) -> ChatGroq:
    api_key = (
        os.getenv("GROQ_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("AGENT_ROUTER_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "Set GROQ_API_KEY or API_KEY in .env or the environment."
        )
    return ChatGroq(
        groq_api_key=api_key,
        model=model or GROQ_MODEL,
        temperature=0,
        timeout=120,
    )
