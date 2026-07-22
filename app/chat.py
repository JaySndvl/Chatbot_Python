from __future__ import annotations

from dataclasses import dataclass
import re

from app.config import Settings
from app.llm import BaseGenerator, LocalFallbackGenerator, OpenAICompatibleGenerator


@dataclass(frozen=True)
class ChatResponse:
    answer: str
    provider: str


class ChatService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.generator: BaseGenerator = self._build_generator(settings)

    def reply(self, question: str, history: list[dict[str, str]] | None = None) -> ChatResponse:
        conversation = history or []
        if not self._is_in_scope(question, conversation):
            return ChatResponse(
                answer=(
                    f"That topic is not covered by this chatbot. I can help with "
                    f"{self.settings.topic_name.lower()}."
                ),
                provider="scope-filter",
            )
        result = self.generator.generate(
            question=question,
            topic_name=self.settings.topic_name,
            topic_description=self.settings.topic_description,
            history=conversation[-6:],
        )
        return ChatResponse(answer=result.answer, provider=result.provider)

    def _build_generator(self, settings: Settings) -> BaseGenerator:
        if settings.llm_provider == "openai-compatible":
            return OpenAICompatibleGenerator(settings)
        return LocalFallbackGenerator()

    def _is_in_scope(self, question: str, history: list[dict[str, str]]) -> bool:
        """Allow questions containing configured topic terms or a recent in-scope turn."""
        keyword_terms = {
            term
            for keyword in self.settings.topic_keywords
            for term in re.findall(r"[a-zA-Z0-9']+", keyword.lower())
        }
        question_terms = set(re.findall(r"[a-zA-Z0-9']+", question.lower()))
        if keyword_terms.intersection(question_terms):
            return True

        # Permit natural follow-up questions when the immediately prior user turn
        # was explicitly within scope.
        previous_user_messages = [
            message.get("content", "")
            for message in history
            if message.get("role") == "user"
        ]
        if previous_user_messages:
            previous_terms = set(
                re.findall(r"[a-zA-Z0-9']+", previous_user_messages[-1].lower())
            )
            return bool(keyword_terms.intersection(previous_terms))
        return False
