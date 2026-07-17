from app.ai.ollama import OllamaProvider
from app.ai.provider_manager import ProviderManager
from app.brain.dispatcher import CommandDispatcher
from app.brain.matcher import CommandMatcher


class JarvisBrain:
    def __init__(self):
        self.name = "JARVIS Core"
        self.version = "0.5"

        self.provider_manager = ProviderManager()
        self.provider_manager.register_provider(
            name="ollama",
            provider_cls=OllamaProvider,
            capabilities=["chat", "intent-classification"],
            priority=10,
        )

        self.ai = self.provider_manager.get_provider("ollama")
        self.matcher = CommandMatcher(ai_provider=self.ai)
        self.dispatcher = CommandDispatcher(self.matcher)

    def process(self, message: str) -> str:
        # 1. Attempt to dispatch a command
        command_response = self.dispatcher.dispatch(message)
        if command_response is not None:
            return command_response

        # 2. If no command was dispatched, fall back to AI
        return self.provider_manager.generate(message)