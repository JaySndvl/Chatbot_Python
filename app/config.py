from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str
    topic_name: str
    topic_description: str
    topic_docs_dir: Path
    topic_keywords: tuple[str, ...]
    top_k: int
    chunk_size: int
    chunk_overlap: int
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str


def _split_keywords(raw_value: str) -> tuple[str, ...]:
    keywords = [part.strip().lower() for part in raw_value.split(",")]
    return tuple(keyword for keyword in keywords if keyword)


def get_settings() -> Settings:
    topic_name = os.getenv("TOPIC_NAME", "Your Topic")
    topic_description = os.getenv(
        "TOPIC_DESCRIPTION",
        "Describe the exact subject area the chatbot should focus on.",
    )
    topic_keywords = _split_keywords(os.getenv("TOPIC_KEYWORDS", ""))
    if not topic_keywords:
        topic_keywords = tuple(
            word.lower()
            for word in topic_name.split()
            if len(word) > 2
        )

    return Settings(
        app_name=os.getenv("APP_NAME", "Macro chatbot"),
        topic_name=topic_name,
        topic_description=topic_description,
        topic_docs_dir=_resolve_path(os.getenv("TOPIC_DOCS_DIR", "data/topic_docs")),
        topic_keywords=topic_keywords,
        top_k=max(1, int(os.getenv("TOP_K", "4"))),
        chunk_size=max(50, int(os.getenv("CHUNK_SIZE", "220"))),
        chunk_overlap=max(0, int(os.getenv("CHUNK_OVERLAP", "40"))),
        llm_provider=os.getenv("LLM_PROVIDER", "local").strip().lower(),
        llm_model=os.getenv("LLM_MODEL", "").strip(),
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        llm_base_url=os.getenv("LLM_BASE_URL", "").strip(),
    )


def _resolve_path(raw_value: str) -> Path:
    path = Path(raw_value)
    return path if path.is_absolute() else (BASE_DIR / path).resolve()
