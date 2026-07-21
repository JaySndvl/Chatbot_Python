from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import Settings

DOCUMENT_SUFFIXES = {".md", ".txt", ".rst"}
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9']+")


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    source: str
    snippet: str
    score: float


class TopicRAG:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._chunks: list[Chunk] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self.refresh()

    def refresh(self) -> None:
        self._chunks = self._load_chunks(self.settings.topic_docs_dir)
        if not self._chunks:
            self._vectorizer = None
            self._matrix = None
            return

        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(chunk.text for chunk in self._chunks)

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievalResult]:
        if not query.strip() or self._vectorizer is None or self._matrix is None:
            return []

        query_vector = self._vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vector, self._matrix).ravel()
        query_terms = set(self._tokenize(query))
        topic_terms = set(self.settings.topic_keywords)

        ranked: list[RetrievalResult] = []
        for index, base_score in enumerate(similarity_scores):
            chunk = self._chunks[index]
            chunk_terms = set(self._tokenize(chunk.text))
            overlap_boost = 0.0
            if query_terms:
                overlap_boost += 0.04 * len(query_terms.intersection(chunk_terms))
            if topic_terms:
                overlap_boost += 0.06 * len(topic_terms.intersection(chunk_terms))
            final_score = float(base_score + overlap_boost)
            ranked.append(
                RetrievalResult(
                    source=chunk.source,
                    snippet=self._trim_snippet(chunk.text),
                    score=final_score,
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        limit = top_k or self.settings.top_k
        return [item for item in ranked[:limit] if item.score > 0.0]

    def document_count(self) -> int:
        return len(self._chunks)

    def _load_chunks(self, docs_dir: Path) -> list[Chunk]:
        if not docs_dir.exists():
            return []

        chunks: list[Chunk] = []
        for path in sorted(docs_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in DOCUMENT_SUFFIXES:
                text = path.read_text(encoding="utf-8", errors="ignore").strip()
                if text:
                    relative_name = path.relative_to(docs_dir).as_posix()
                    for index, chunk_text in enumerate(
                        self._chunk_text(text, self.settings.chunk_size, self.settings.chunk_overlap)
                    ):
                        chunks.append(Chunk(source=relative_name, index=index, text=chunk_text))
        return chunks

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> Iterable[str]:
        words = text.split()
        if len(words) <= chunk_size:
            yield text.strip()
            return

        step = max(1, chunk_size - chunk_overlap)
        for start in range(0, len(words), step):
            chunk_words = words[start : start + chunk_size]
            if not chunk_words:
                break
            yield " ".join(chunk_words).strip()

    def _tokenize(self, text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())

    def _trim_snippet(self, text: str, limit: int = 260) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= limit:
            return cleaned
        return cleaned[: limit - 1].rstrip() + "…"
