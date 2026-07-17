from ollama import chat

from app.ai.provider import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self):
        self.model = "qwen2.5-coder:7b"

    def generate(self, prompt: str) -> str:
        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, the AI assistant of NightCode Labs. "
                        "Be concise, helpful, and professional."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response["message"]["content"]