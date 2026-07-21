# Workspace Instructions

This workspace contains a Python chatbot web application built around a topic-focused RAG pipeline.

- Keep the app scoped to one topic by curating documents in `data/topic_docs/`.
- Prefer small, focused changes that preserve the FastAPI + browser UI structure.
- When adding new knowledge sources, update the retrieval settings in `app/rag.py` and document the change in `README.md`.
- Use the local fallback response mode for development unless a real LLM provider is configured.
