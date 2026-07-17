import pytest
from unittest.mock import MagicMock
from app.brain.dispatcher import CommandDispatcher
from app.brain.matcher import CommandMatcher


def test_dispatcher_routes_keyword_match():
    mock_matcher = MagicMock(spec=CommandMatcher)
    mock_matcher.match.return_value = {"intent": "system_status", "params": {}}

    mock_cmd = MagicMock()
    mock_cmd.execute.return_value = "System is operational."

    registry = MagicMock()
    registry.get_command_details.return_value = {
        "system_status": {"description": "Get status.", "parameters": {}}
    }
    registry.get_command.return_value = mock_cmd

    dispatcher = MagicMock(spec=CommandDispatcher)
    dispatcher._matcher = mock_matcher
    dispatcher._registry = registry

    # We need to call the real dispatch method, so let's import and call directly
    from app.brain import dispatcher as dispatcher_module
    dispatcher_module.registry = registry
    real_dispatcher = dispatcher_module.CommandDispatcher(mock_matcher)

    response = real_dispatcher.dispatch("system status")
    assert response == "System is operational."
    mock_matcher.match.assert_called_once_with("system status", registry.get_command_details.return_value)
    registry.get_command.assert_called_once_with("system_status")
    mock_cmd.execute.assert_called_once_with({})


def test_dispatcher_returns_none_on_no_match():
    mock_matcher = MagicMock(spec=CommandMatcher)
    mock_matcher.match.return_value = None

    registry = MagicMock()
    registry.get_command_details.return_value = {}

    from app.brain import dispatcher as dispatcher_module
    dispatcher_module.registry = registry
    real_dispatcher = dispatcher_module.CommandDispatcher(mock_matcher)

    response = real_dispatcher.dispatch("hello")
    assert response is None


def test_dispatcher_handles_command_exception():
    mock_matcher = MagicMock(spec=CommandMatcher)
    mock_matcher.match.return_value = {"intent": "system_status", "params": {}}

    mock_cmd = MagicMock()
    mock_cmd.execute.side_effect = Exception("Boom")

    registry = MagicMock()
    registry.get_command_details.return_value = {
        "system_status": {"description": "Get status.", "parameters": {}}
    }
    registry.get_command.return_value = mock_cmd

    from app.brain import dispatcher as dispatcher_module
    dispatcher_module.registry = registry
    real_dispatcher = dispatcher_module.CommandDispatcher(mock_matcher)

    response = real_dispatcher.dispatch("system status")
    assert "error" in response.lower()