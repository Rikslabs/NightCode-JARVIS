"""Tests for Desktop Action Framework."""

import pytest

from app.desktop.models import (
    MouseAction,
    KeyboardAction,
    WindowAction,
    ClipboardAction,
    DesktopAction,
    ActionResult,
    ActionPermission,
)
from app.desktop.controller import DesktopController
from app.desktop.actions import DesktopActions
from app.desktop.permissions import DesktopPermissionManager
from app.desktop.registry import DesktopRegistry
from app.desktop.validator import DesktopValidator
from app.desktop.mouse import MouseController
from app.desktop.keyboard import KeyboardController
from app.desktop.clipboard import ClipboardController
from app.desktop.windows import WindowController


class TestMouseAction:
    def test_all_actions(self):
        assert MouseAction.MOVE.value == "move"
        assert MouseAction.CLICK.value == "click"
        assert MouseAction.DOUBLE_CLICK.value == "double_click"
        assert MouseAction.RIGHT_CLICK.value == "right_click"
        assert MouseAction.SCROLL.value == "scroll"
        assert MouseAction.DRAG.value == "drag"


class TestKeyboardAction:
    def test_all_actions(self):
        assert KeyboardAction.TYPE.value == "type"
        assert KeyboardAction.PRESS.value == "press"
        assert KeyboardAction.HOTKEY.value == "hotkey"


class TestWindowAction:
    def test_all_actions(self):
        assert WindowAction.OPEN.value == "open"
        assert WindowAction.FOCUS.value == "focus"
        assert WindowAction.MINIMIZE.value == "minimize"
        assert WindowAction.MAXIMIZE.value == "maximize"
        assert WindowAction.CLOSE.value == "close"


class TestClipboardAction:
    def test_all_actions(self):
        assert ClipboardAction.COPY.value == "copy"
        assert ClipboardAction.PASTE.value == "paste"


class TestActionPermission:
    def test_all_permissions(self):
        assert ActionPermission.DENY.value == "deny"
        assert ActionPermission.ALLOW.value == "allow"
        assert ActionPermission.PROMPT.value == "prompt"


class TestDesktopAction:
    def test_create_action(self):
        action = DesktopAction(action_type="move_mouse", parameters={"x": 100, "y": 200})
        assert action.action_type == "move_mouse"
        assert action.parameters["x"] == 100

    def test_to_dict(self):
        action = DesktopAction(action_type="click")
        d = action.to_dict()
        assert d["action_type"] == "click"


class TestActionResult:
    def test_success_result(self):
        action = DesktopAction(action_type="click")
        result = ActionResult(success=True, action=action)
        assert result.success is True

    def test_failure_result(self):
        action = DesktopAction(action_type="click")
        result = ActionResult(success=False, action=action, message="Failed")
        assert result.success is False


# ============================================
# MouseController Tests
# ============================================

class TestMouseController:
    def test_move(self):
        mouse = MouseController()
        assert mouse.move(100, 200) is True

    def test_click(self):
        mouse = MouseController()
        assert mouse.click() is True

    def test_double_click(self):
        mouse = MouseController()
        assert mouse.double_click() is True

    def test_right_click(self):
        mouse = MouseController()
        assert mouse.right_click() is True

    def test_scroll(self):
        mouse = MouseController()
        assert mouse.scroll("down", 3) is True

    def test_drag(self):
        mouse = MouseController()
        assert mouse.drag(0, 0, 100, 100) is True

    def test_get_position(self):
        mouse = MouseController()
        pos = mouse.get_position()
        assert pos == (0, 0)


# ============================================
# KeyboardController Tests
# ============================================

class TestKeyboardController:
    def test_type_text(self):
        kb = KeyboardController()
        assert kb.type_text("hello") is True

    def test_press(self):
        kb = KeyboardController()
        assert kb.press("enter") is True

    def test_hotkey(self):
        kb = KeyboardController()
        assert kb.hotkey("ctrl", "c") is True

    def test_get_supported_keys(self):
        kb = KeyboardController()
        keys = kb.get_supported_keys()
        assert "ctrl" in keys


# ============================================
# ClipboardController Tests
# ============================================

class TestClipboardController:
    def test_copy(self):
        cb = ClipboardController()
        assert cb.copy("test") is True

    def test_paste(self):
        cb = ClipboardController()
        cb.copy("test")
        assert cb.paste() == "test"

    def test_clear(self):
        cb = ClipboardController()
        cb.copy("test")
        assert cb.clear() is True
        assert cb.paste() is None


# ============================================
# WindowController Tests
# ============================================

class TestWindowController:
    def test_open(self):
        win = WindowController()
        assert win.open("notepad") is True

    def test_focus(self):
        win = WindowController()
        assert win.focus("notepad") is True

    def test_minimize(self):
        win = WindowController()
        assert win.minimize("notepad") is True

    def test_maximize(self):
        win = WindowController()
        assert win.maximize("notepad") is True

    def test_get_window_info(self):
        win = WindowController()
        info = win.get_window_info("notepad")
        assert info is not None

    def test_list_windows(self):
        win = WindowController()
        windows = win.list_windows()
        assert len(windows) >= 3

    def test_screenshot(self):
        win = WindowController()
        result = win.screenshot("notepad")
        assert result["success"] is True


# ============================================
# DesktopPermissionManager Tests
# ============================================

class TestDesktopPermissionManager:
    def test_check_permission_default(self):
        pm = DesktopPermissionManager()
        action = DesktopAction(action_type="click")
        perm = pm.check_permission(action)
        assert perm == ActionPermission.PROMPT

    def test_dangerous_action_denied(self):
        pm = DesktopPermissionManager()
        action = DesktopAction(action_type="open_app")
        perm = pm.check_permission(action)
        assert perm == ActionPermission.DENY

    def test_allow_action(self):
        pm = DesktopPermissionManager()
        pm.allow_action("click")
        action = DesktopAction(action_type="click")
        perm = pm.check_permission(action)
        assert perm == ActionPermission.ALLOW

    def test_log_action(self):
        pm = DesktopPermissionManager()
        action = DesktopAction(action_type="click")
        pm.log_action(action, True)
        log = pm.get_audit_log()
        assert len(log) == 1


# ============================================
# DesktopValidator Tests
# ============================================

class TestDesktopValidator:
    def test_validate_valid_action(self):
        validator = DesktopValidator()
        action = DesktopAction(action_type="click")
        result = validator.validate(action)
        assert result.success is True

    def test_validate_missing_action_type(self):
        validator = DesktopValidator()
        action = DesktopAction(action_type="")
        result = validator.validate(action)
        assert result.success is False

    def test_validate_coordinates_valid(self):
        validator = DesktopValidator()
        assert validator.validate_coordinates(100, 200) is True

    def test_validate_coordinates_negative(self):
        validator = DesktopValidator()
        assert validator.validate_coordinates(-1, 0) is False


# ============================================
# DesktopController Tests
# ============================================

class TestDesktopController:
    def test_execute_click(self):
        controller = DesktopController()
        action = DesktopAction(action_type="click")
        result = controller.execute(action)
        assert result.success is True

    def test_execute_denied_action(self):
        pm = DesktopPermissionManager()
        pm.deny_action("open_app")
        controller = DesktopController(pm)
        action = DesktopAction(action_type="open_app")
        result = controller.execute(action)
        assert result.success is False

    def test_get_audit_log(self):
        controller = DesktopController()
        action = DesktopAction(action_type="click")
        controller.execute(action)
        log = controller.get_audit_log()
        assert len(log) == 1


# ============================================
# DesktopActions Tests
# ============================================

class TestDesktopActions:
    def test_move_mouse(self):
        actions = DesktopActions()
        result = actions.move_mouse(100, 200)
        assert result.success is True

    def test_click(self):
        actions = DesktopActions()
        result = actions.click()
        assert result.success is True

    def test_type_text(self):
        actions = DesktopActions()
        result = actions.type_text("hello")
        assert result.success is True

    def test_press_hotkey(self):
        actions = DesktopActions()
        result = actions.press_hotkey("ctrl", "c")
        assert result.success is True

    def test_copy(self):
        actions = DesktopActions()
        result = actions.copy("test")
        assert result.success is True

    def test_open_application(self):
        actions = DesktopActions()
        result = actions.open_application("notepad")
        assert result.success is True


# ============================================
# DesktopRegistry Tests
# ============================================

class TestDesktopRegistry:
    def test_get_instance(self):
        registry = DesktopRegistry.get_instance()
        assert isinstance(registry, DesktopRegistry)

    def test_register_and_get_controller(self):
        registry = DesktopRegistry()
        controller = DesktopController()
        registry.register_controller("test", controller)
        assert registry.get_controller("test") is controller

    def test_clear(self):
        registry = DesktopRegistry()
        controller = DesktopController()
        registry.register_controller("test", controller)
        registry.clear()
        assert registry.get_controller("test") is None