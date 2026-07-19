import sys
import pytest
from unittest.mock import MagicMock, patch

# Mock ollama before importing app modules that depend on it
sys.modules.setdefault("ollama", MagicMock())

from app.brain.jarvis import JarvisBrain


def test_brain_dispatches_command():
    brain = JarvisBrain()
    brain.dispatcher = MagicMock()
    brain.dispatcher.dispatch.return_value = "Command response."

    response = brain.process("system status")
    assert response == "Command response."
    brain.dispatcher.dispatch.assert_called_once_with("system status")


def test_brain_falls_back_to_ai_when_no_command():
    brain = JarvisBrain()
    brain.dispatcher = MagicMock()
    brain.dispatcher.dispatch.return_value = None
    brain.provider_manager = MagicMock()
    brain.provider_manager.generate.return_value = "AI response."

    response = brain.process("hello")
    assert response == "AI response."
    brain.dispatcher.dispatch.assert_called_once_with("hello")
    brain.provider_manager.generate.assert_called_once_with("hello")


def test_brain_name_and_version():
    brain = JarvisBrain()
    assert brain.name == "JARVIS Core"
    assert brain.version == "1.0.0"
