from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.chat import ChatService
from app.config import BASE_DIR, get_settings

settings = get_settings()
chat_service = ChatService(settings)

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role such as user or assistant")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "topic_name": settings.topic_name,
            "topic_description": settings.topic_description,
        },
    )


@app.get("/api/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/api/chat")
def chat(payload: ChatRequest) -> JSONResponse:
    reply = chat_service.reply(
        payload.message,
        history=[message.model_dump() for message in payload.history],
    )
    return JSONResponse(
        {
            "answer": reply.answer,
            "provider": reply.provider,
        }
    )
