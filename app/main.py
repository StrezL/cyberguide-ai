import json
import os
from pathlib import Path
from typing import AsyncIterator, Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

app = FastAPI(
    title="CyberGuide AI",
    description="An AI-powered security awareness and defensive learning platform.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1200)
    domain: str = Field(default="General Security", max_length=80)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    mode: Literal["explain", "measures", "quiz"] = "explain"


SYSTEM_PROMPT = """You are CyberGuide AI, an educational security-awareness assistant.
Give accurate, clear, practical guidance for defensive and academic learning only.
Prioritize prevention, detection, safe configuration, incident reporting, and recovery.
Do not provide instructions that enable credential theft, malware creation, unauthorized
access, evasion, destructive activity, or exploitation of real targets. If a request is
unsafe, refuse briefly and redirect it toward defensive concepts or a safe lab exercise.
Adapt vocabulary to the stated learner level. Never claim to replace a qualified security
professional. Use clear headings, numbered sections, and concise bullet points when they
make the answer easier to study. For broad questions such as types of network security,
give a short overview followed by well-organized categories, named controls, what each
control does, and a practical example. Avoid vague generic answers."""


def build_user_prompt(payload: AskRequest) -> str:
    instructions = {
        "explain": "Explain the concept with a simple example and finish with three key takeaways.",
        "measures": "Focus on practical prevention, detection, response, and recovery measures.",
        "quiz": "Create five questions. Give the answer key after a clear divider.",
    }
    return (
        f"Learning domain: {payload.domain}\n"
        f"Learner level: {payload.level}\n"
        f"Response mode: {payload.mode}\n"
        f"Instruction: {instructions[payload.mode]}\n\n"
        f"User question: {payload.question}"
    )


async def groq_stream(payload: AskRequest) -> AsyncIterator[str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        yield "The AI service is not configured yet. Add GROQ_API_KEY to the server environment and restart the application."
        return

    request_body = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(payload)},
        ],
        "temperature": 0.35,
        "max_tokens": 900,
        "stream": True,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", GROQ_URL, json=request_body, headers=headers) as response:
                if response.status_code != 200:
                    yield "The AI service could not complete this request. Please check the server configuration and try again."
                    return
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0]["delta"].get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                        continue
    except httpx.HTTPError:
        yield "The AI service is temporarily unavailable. Please try again in a moment."


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/ask")
async def ask(payload: AskRequest) -> StreamingResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be blank")
    return StreamingResponse(
        groq_stream(payload),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"},
    )
