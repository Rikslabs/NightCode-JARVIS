import pytest
from app.memory.base import Command
from app.memory.registry import register_command, get_command, get_command_details


class DummyCommand(Command):
    description = "A dummy command for testing."
    parameters = {"param1": "First parameter."}

    def execute(self, params: dict) -> str:
        return "dummy"


class AnotherDummyCommand(Command):
    description = "Another dummy command."

    def execute(self, params: dict) -> str:
        return "another"


def test_register_command_stores_instance():
    register_command("dummy")(DummyCommand)
    cmd = get_command("dummy")
    assert cmd is not None
    assert isinstance(cmd, DummyCommand)


def test_register_command_returns_details():
    register_command("dummy")(DummyCommand)
    details = get_command_details()
    assert "dummy" in details
    assert details["dummy"]["description"] == "A dummy command for testing."
    assert details["dummy"]["parameters"] == {"param1": "First parameter."}


def test_register_duplicate_intent_warns():
    # Register once, then register again with a different class to trigger warning
    register_command("dummy")(DummyCommand)
    with pytest.warns(UserWarning, match="Duplicate intent registration"):
        register_command("dummy")(AnotherDummyCommand)


def test_get_command_missing_intent_returns_none():
    assert get_command("nonexistent") is None


def test_get_command_details_omits_commands_without_description():
    class NoDescCommand(Command):
        def execute(self, params: dict) -> str:
            return "no desc"

    register_command("no_desc")(NoDescCommand)
    details = get_command_details()
    assert "no_desc" not in details