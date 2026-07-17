from fastapi import FastAPI
from pydantic import BaseModel

from app.brain.jarvis import JarvisBrain

# Import commands to ensure they are registered
from app.commands import system_status
from app.commands import memory_commands

app = FastAPI(
    title="NightCode Labs - JARVIS Core",
    version="0.2.0"
)

brain = JarvisBrain()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "status": "ONLINE",
        "system": brain.name,
        "version": brain.version,
        "company": "NightCode Labs"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    reply = brain.process(request.message)

    return {
        "reply": reply
    }