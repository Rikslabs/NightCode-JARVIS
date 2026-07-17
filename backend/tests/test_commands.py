import pytest
from unittest.mock import MagicMock
from app.commands.memory_commands import RememberNameCommand, GetNameCommand
from app.commands.system_status import SystemStatusCommand


def test_remember_name_command_stores_name(monkeypatch):
    captured = {}

    def fake_execute(operation, key, value):
        if operation == "set":
            captured[key] = value
            return type("Result", (), {"success": True, "data": value})()
        return type("Result", (), {"success": True, "data": None})()

    mock_tool = MagicMock()
    mock_tool.execute = fake_execute
    monkeypatch.setattr("app.commands.memory_commands.get_tool", lambda name: mock_tool)

    cmd = RememberNameCommand()
    response = cmd.execute({"name": "Vikash"})
    assert response == "I'll remember that. Hello, Vikash."
    assert captured["name"] == "Vikash"


def test_remember_name_command_missing_name():
    cmd = RememberNameCommand()
    response = cmd.execute({})
    assert "couldn't determine your name" in response.lower()


def test_get_name_command_returns_name(monkeypatch):
    mock_tool = MagicMock()
    mock_tool.execute.return_value = type("Result", (), {"success": True, "data": "Vikash"})()
    monkeypatch.setattr("app.commands.memory_commands.get_tool", lambda name: mock_tool)

    cmd = GetNameCommand()
    response = cmd.execute({})
    assert response == "Your name is Vikash."


def test_get_name_command_missing_name(monkeypatch):
    mock_tool = MagicMock()
    mock_tool.execute.return_value = type("Result", (), {"success": True, "data": None})()
    monkeypatch.setattr("app.commands.memory_commands.get_tool", lambda name: mock_tool)

    cmd = GetNameCommand()
    response = cmd.execute({})
    assert response == "I don't know your name yet."


def test_system_status_command_returns_report():
    cmd = SystemStatusCommand()
    response = cmd.execute({})
    assert "JARVIS Status: Operational" in response
    assert "Version: 1.0.0" in response
    assert "Available Modules:" in response