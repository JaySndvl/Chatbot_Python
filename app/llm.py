from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings


@dataclass(frozen=True)
class GenerationResult:
    answer: str
    provider: str


class BaseGenerator:
    def generate(self, *, question: str, topic_name: str, topic_description: str, history: list[dict[str, str]]) -> GenerationResult:
        raise NotImplementedError


class LocalFallbackGenerator(BaseGenerator):
    def generate(
        self,
        *,
        question: str,
        topic_name: str,
        topic_description: str,
        history: list[dict[str, str]],
        message: str | None = None,
    ) -> GenerationResult:
        return GenerationResult(
            answer=message
            or "The AI provider is temporarily unavailable. Try again in a moment.",
            provider="local",
        )


class OpenAICompatibleGenerator(BaseGenerator):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, *, question: str, topic_name: str, topic_description: str, history: list[dict[str, str]]) -> GenerationResult:
        if not self.settings.llm_model or not self.settings.llm_api_key or not self.settings.llm_base_url:
            return LocalFallbackGenerator().generate(
                question=question,
                topic_name=topic_name,
                topic_description=topic_description,
                history=history,
                message="The AI provider is not configured. Add your Gemini API settings to .env and restart the server.",
            )

        system_prompt = (
            f"You are a helpful assistant focused on {topic_name}. "
            f"Stay within this scope: {topic_description}. "
            "Answer using your general knowledge, but only within this scope. "
            "If a request is outside this scope, reply exactly: "
            "'That topic is not covered by this chatbot.'"
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            *history,
            {
                "role": "user",
                "content": question,
            },
        ]

        payload = {
            "model": self.settings.llm_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        endpoint = self.settings.llm_base_url.rstrip("/") + "/chat/completions"

        try:
            with httpx.Client(timeout=45.0) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                answer = data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code in {401, 403}:
                message = "The AI provider rejected the API key. Check your Gemini credentials in .env."
            elif status_code == 404:
                message = "The AI provider endpoint or model could not be found. Check the Gemini model and base URL in .env."
            elif status_code == 503:
                message = "The Gemini provider is temporarily unavailable. Try again in a moment."
            else:
                message = "The AI provider returned an error. Check your Gemini settings and try again."
            return LocalFallbackGenerator().generate(
                question=question,
                topic_name=topic_name,
                topic_description=topic_description,
                history=history,
                message=message,
            )
        except Exception:
            return LocalFallbackGenerator().generate(
                question=question,
                topic_name=topic_name,
                topic_description=topic_description,
                history=history,
                message="The AI provider could not be reached. Check your Gemini settings and network connection.",
            )

        return GenerationResult(answer=answer, provider="openai-compatible")
