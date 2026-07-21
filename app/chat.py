from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.llm import BaseGenerator, LocalFallbackGenerator, OpenAICompatibleGenerator
from app.rag import RetrievalResult, TopicRAG


@dataclass(frozen=True)
class ChatResponse:
    answer: str
    provider: str
    sources: list[RetrievalResult]


class ChatService:
    def __init__(self, settings: Settings, rag: TopicRAG) -> None:
        self.settings = settings
        self.rag = rag
        self.generator: BaseGenerator = self._build_generator(settings)

    def reply(self, question: str, history: list[dict[str, str]] | None = None) -> ChatResponse:
        conversation = history or []
        sources = self.rag.retrieve(question)
        result = self.generator.generate(
            question=question,
            topic_name=self.settings.topic_name,
            topic_description=self.settings.topic_description,
            context=sources,
            history=conversation[-6:],
        )
        return ChatResponse(answer=result.answer, provider=result.provider, sources=sources)

    def _build_generator(self, settings: Settings) -> BaseGenerator:
        if settings.llm_provider == "openai-compatible":
            return OpenAICompatibleGenerator(settings)
        return LocalFallbackGenerator()
