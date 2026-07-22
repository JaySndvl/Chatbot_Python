# Topic RAG Chatbot

A small Python web app for building a chatbot that stays focused on one topic while using an LLM's general knowledge to generate replies.

## What it includes

- FastAPI backend
- Simple browser chat interface
- Keyword-based topic filter with an additional LLM scope instruction
- Optional OpenAI-compatible LLM endpoint, including Gemini
- Local fallback mode for offline development

## Project layout

- `app/main.py` starts the web server and exposes the chat API
- `app/llm.py` wraps the answer generator
- `app/chat.py` applies topic filtering and coordinates response generation
- `templates/index.html` and `static/app.js` provide the chat UI

## Getting started

1. Create a virtual environment and install dependencies.
2. Adjust `.env` with the topic name, keywords, and LLM settings.
3. Run the app with Uvicorn.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Topic configuration

Set `TOPIC_DESCRIPTION` to define what the assistant may answer and set `TOPIC_KEYWORDS` to a comma-separated list of words that identify in-scope user questions. The app rejects questions without one of those terms before calling the LLM. Gemini receives the same scope instruction as a second safeguard.

## Next steps

- Connect a real model by setting `LLM_PROVIDER`, `LLM_MODEL`, and API credentials.
- Add authentication and persistent chat history if you want multi-user sessions.
