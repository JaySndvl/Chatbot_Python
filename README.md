# Topic RAG Chatbot

A small Python web app for building a chatbot that stays focused on one topic by retrieving answers from a curated knowledge base before generating a reply.

## What it includes

- FastAPI backend
- Simple browser chat interface
- Topic-focused RAG pipeline using TF-IDF retrieval
- Optional OpenAI-compatible LLM endpoint
- Local fallback mode for offline development

## Project layout

- `app/main.py` starts the web server and exposes the chat API
- `app/rag.py` loads topic documents, chunks them, and retrieves relevant passages
- `app/llm.py` wraps the answer generator
- `app/chat.py` combines retrieval and generation
- `data/topic_docs/` stores the source documents for the topic
- `templates/index.html` and `static/app.js` provide the chat UI

## Getting started

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and adjust the topic name, documents path, and LLM settings.
3. Put topic-specific reference material into `data/topic_docs/`.
4. Run the app with Uvicorn.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## RAG configuration

The app is designed to focus on one topic by narrowing the document set and boosting matches against topic keywords. To tighten the scope further, keep only relevant files in `data/topic_docs/`, raise `TOP_K` to retrieve fewer passages, and edit `TOPIC_DESCRIPTION` so the system prompt stays specific.

If the automatic topic keywords are too broad, set `TOPIC_KEYWORDS` in `.env` with a comma-separated list of terms that define the target domain.

## Next steps

- Replace the sample topic docs with your own source material.
- Connect a real model by setting `LLM_PROVIDER`, `LLM_MODEL`, and API credentials.
- Add authentication and persistent chat history if you want multi-user sessions.
