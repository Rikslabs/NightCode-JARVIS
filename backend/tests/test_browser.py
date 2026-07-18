"""Tests for Browser Controller."""

import pytest

from app.browser.models import (
    BrowserAction,
    BrowserPermission,
    BrowserActionResult,
)
from app.browser.controller import BrowserController
from app.browser.navigation import NavigationController
from app.browser.tabs import TabController
from app.browser.interaction import InteractionController
from app.browser.extraction import ExtractionController
from app.browser.downloads import DownloadController
from app.browser.permissions import BrowserPermissionManager
from app.browser.registry import BrowserRegistry
from app.browser.validator import BrowserValidator


# ============================================
# Model Tests
# ============================================

class TestBrowserAction:
    def test_all_actions(self):
        assert BrowserAction.OPEN_URL.value == "open_url"
        assert BrowserAction.BACK.value == "back"
        assert BrowserAction.FORWARD.value == "forward"
        assert BrowserAction.REFRESH.value == "refresh"
        assert BrowserAction.STOP_LOADING.value == "stop_loading"
        assert BrowserAction.NEW_TAB.value == "new_tab"
        assert BrowserAction.CLOSE_TAB.value == "close_tab"
        assert BrowserAction.SWITCH_TAB.value == "switch_tab"
        assert BrowserAction.LIST_TABS.value == "list_tabs"
        assert BrowserAction.CLICK.value == "click"
        assert BrowserAction.TYPE.value == "type"
        assert BrowserAction.SCROLL.value == "scroll"
        assert BrowserAction.SUBMIT_FORM.value == "submit_form"
        assert BrowserAction.UPLOAD_FILE.value == "upload_file"
        assert BrowserAction.GET_TITLE.value == "get_title"
        assert BrowserAction.GET_TEXT.value == "get_text"
        assert BrowserAction.GET_LINKS.value == "get_links"
        assert BrowserAction.GET_METADATA.value == "get_metadata"
        assert BrowserAction.GET_STATUS.value == "get_status"
        assert BrowserAction.START_DOWNLOAD.value == "start_download"
        assert BrowserAction.MONITOR_DOWNLOAD.value == "monitor_download"
        assert BrowserAction.CANCEL_DOWNLOAD.value == "cancel_download"
        assert BrowserAction.LIST_DOWNLOADS.value == "list_downloads"


class TestBrowserPermission:
    def test_all_permissions(self):
        assert BrowserPermission.ALLOW.value == "allow"
        assert BrowserPermission.DENY.value == "deny"
        assert BrowserPermission.PROMPT.value == "prompt"


class TestBrowserActionResult:
    def test_create_result(self):
        result = BrowserActionResult(success=True, action="click")
        assert result.success is True
        assert result.action == "click"

    def test_result_with_data(self):
        result = BrowserActionResult(
            success=True,
            action="open_url",
            message="Navigated",
            data={"url": "https://example.com"},
        )
        assert result.data["url"] == "https://example.com"

    def test_result_to_dict(self):
        result = BrowserActionResult(success=True, action="refresh")
        d = result.to_dict()
        assert d["success"] is True
        assert d["action"] == "refresh"
        assert "timestamp" in d


# ============================================
# NavigationController Tests
# ============================================

class TestNavigationController:
    def test_open_url(self):
        nav = NavigationController()
        result = nav.open_url("https://example.com")
        assert result.success is True
        assert result.data["url"] == "https://example.com"

    def test_back(self):
        nav = NavigationController()
        result = nav.back()
        assert result.success is True

    def test_forward(self):
        nav = NavigationController()
        result = nav.forward()
        assert result.success is True

    def test_refresh(self):
        nav = NavigationController()
        result = nav.refresh()
        assert result.success is True

    def test_stop_loading(self):
        nav = NavigationController()
        result = nav.stop_loading()
        assert result.success is True

    def test_get_current_url(self):
        nav = NavigationController()
        assert nav.get_current_url() is None
        nav.open_url("https://test.com")
        assert nav.get_current_url() == "https://test.com"


# ============================================
# TabController Tests
# ============================================

class TestTabController:
    def test_initial_tab(self):
        tabs = TabController()
        result = tabs.list_tabs()
        assert result.success is True
        assert len(result.data["tabs"]) == 1

    def test_new_tab(self):
        tabs = TabController()
        result = tabs.new_tab("https://example.com")
        assert result.success is True
        assert result.data["tab_id"] == 2

    def test_close_tab(self):
        tabs = TabController()
        result = tabs.close_tab(1)
        assert result.success is True
        assert len(tabs._tabs) == 0

    def test_switch_tab(self):
        tabs = TabController()
        tabs.new_tab("https://example.com")
        result = tabs.switch_tab(2)
        assert result.success is True
        assert result.data["tab_id"] == 2

    def test_get_active_tab(self):
        tabs = TabController()
        active = tabs.get_active_tab()
        assert active is not None
        assert active["id"] == 1


# ============================================
# InteractionController Tests
# ============================================

class TestInteractionController:
    def test_click(self):
        interaction = InteractionController()
        result = interaction.click("#button")
        assert result.success is True
        assert result.data["selector"] == "#button"

    def test_type(self):
        interaction = InteractionController()
        result = interaction.type("#input", "hello")
        assert result.success is True
        assert result.data["text"] == "hello"

    def test_scroll(self):
        interaction = InteractionController()
        result = interaction.scroll("down", 100)
        assert result.success is True
        assert result.data["direction"] == "down"

    def test_submit_form(self):
        interaction = InteractionController()
        result = interaction.submit_form("#form")
        assert result.success is True

    def test_upload_file(self):
        interaction = InteractionController()
        result = interaction.upload_file("#file", "/path/to/file.pdf")
        assert result.success is True
        assert result.data["file_path"] == "/path/to/file.pdf"


# ============================================
# ExtractionController Tests
# ============================================

class TestExtractionController:
    def test_get_title(self):
        extraction = ExtractionController()
        result = extraction.get_title()
        assert result.success is True
        assert "title" in result.data

    def test_get_text(self):
        extraction = ExtractionController()
        result = extraction.get_text("#content")
        assert result.success is True
        assert "text" in result.data

    def test_get_links(self):
        extraction = ExtractionController()
        result = extraction.get_links()
        assert result.success is True
        assert "links" in result.data
        assert len(result.data["links"]) > 0

    def test_get_metadata(self):
        extraction = ExtractionController()
        result = extraction.get_metadata()
        assert result.success is True
        assert "metadata" in result.data

    def test_get_status(self):
        extraction = ExtractionController()
        result = extraction.get_status()
        assert result.success is True
        assert "status" in result.data


# ============================================
# DownloadController Tests
# ============================================

class TestDownloadController:
    def test_start_download(self):
        downloads = DownloadController()
        result = downloads.start_download("https://example.com/file.pdf")
        assert result.success is True
        assert result.data["file_name"] == "file.pdf"

    def test_monitor_download(self):
        downloads = DownloadController()
        result = downloads.monitor_download("example.pdf")
        assert result.success is True
        assert "status" in result.data

    def test_cancel_download(self):
        downloads = DownloadController()
        result = downloads.cancel_download("example.pdf")
        assert result.success is True

    def test_list_downloads(self):
        downloads = DownloadController()
        result = downloads.list_downloads()
        assert result.success is True
        assert "downloads" in result.data


# ============================================
# BrowserPermissionManager Tests
# ============================================

class TestBrowserPermissionManager:
    def test_check_permission_default(self):
        pm = BrowserPermissionManager()
        perm = pm.check_permission(BrowserAction.OPEN_URL.value)
        assert perm == BrowserPermission.ALLOW

    def test_requires_approval(self):
        pm = BrowserPermissionManager()
        assert pm.requires_approval(BrowserAction.UPLOAD_FILE.value) is True
        assert pm.requires_approval(BrowserAction.SUBMIT_FORM.value) is True
        assert pm.requires_approval(BrowserAction.OPEN_URL.value) is False

    def test_is_safe(self):
        pm = BrowserPermissionManager()
        assert pm.is_safe(BrowserAction.GET_TITLE.value) is True
        assert pm.is_safe(BrowserAction.UPLOAD_FILE.value) is False

    def test_set_permission(self):
        pm = BrowserPermissionManager()
        pm.set_permission(BrowserAction.OPEN_URL.value, BrowserPermission.DENY)
        assert pm.check_permission(BrowserAction.OPEN_URL.value) == BrowserPermission.DENY


# ============================================
# BrowserValidator Tests
# ============================================

class TestBrowserValidator:
    def test_validate_valid_action(self):
        validator = BrowserValidator()
        result = validator.validate(BrowserAction.OPEN_URL.value)
        assert result.success is True

    def test_validate_unknown_action(self):
        validator = BrowserValidator()
        result = validator.validate("unknown_action")
        assert result.success is False

    def test_is_valid_action(self):
        validator = BrowserValidator()
        assert validator.is_valid_action(BrowserAction.CLICK.value) is True
        assert validator.is_valid_action("unknown") is False


# ============================================
# BrowserController Tests
# ============================================

class TestBrowserController:
    def test_execute_open_url(self):
        controller = BrowserController()
        result = controller.execute(BrowserAction.OPEN_URL.value, url="https://example.com")
        assert result.success is True

    def test_execute_click(self):
        controller = BrowserController()
        result = controller.execute(BrowserAction.CLICK.value, selector="#button")
        assert result.success is True

    def test_execute_unknown_action(self):
        controller = BrowserController()
        result = controller.execute("unknown_action")
        assert result.success is False

    def test_get_audit_log(self):
        controller = BrowserController()
        controller.execute(BrowserAction.OPEN_URL.value, url="https://example.com")
        log = controller.get_audit_log()
        assert len(log) == 1


# ============================================
# BrowserRegistry Tests
# ============================================

class TestBrowserRegistry:
    def test_get_instance(self):
        registry = BrowserRegistry.get_instance()
        assert isinstance(registry, BrowserRegistry)

    def test_register_and_get_controller(self):
        registry = BrowserRegistry()
        controller = BrowserController()
        registry.register_controller("test", controller)
        assert registry.get_controller("test") is controller

    def test_clear(self):
        registry = BrowserRegistry()
        controller = BrowserController()
        registry.register_controller("test", controller)
        registry.clear()
        assert registry.get_controller("test") is None


# ============================================
# Integration Tests
# ============================================

class TestBrowserIntegration:
    def test_full_navigation_flow(self):
        controller = BrowserController()
        controller.execute(BrowserAction.OPEN_URL.value, url="https://example.com")
        controller.execute(BrowserAction.GET_TITLE.value)
        log = controller.get_audit_log()
        assert len(log) == 2

    def test_tab_management_flow(self):
        controller = BrowserController()
        controller.execute(BrowserAction.NEW_TAB.value)
        controller.execute(BrowserAction.SWITCH_TAB.value, tab_id=2)
        controller.execute(BrowserAction.LIST_TABS.value)
        log = controller.get_audit_log()
        assert len(log) == 3

    def test_form_interaction_flow(self):
        controller = BrowserController()
        controller.execute(BrowserAction.OPEN_URL.value, url="https://example.com/form")
        controller.execute(BrowserAction.TYPE.value, selector="#username", text="admin")
        controller.execute(BrowserAction.SUBMIT_FORM.value, selector="#form")
        log = controller.get_audit_log()
        assert len(log) == 3

    def test_download_flow(self):
        controller = BrowserController()
        controller.execute(BrowserAction.START_DOWNLOAD.value, url="https://example.com/file.pdf")
        controller.execute(BrowserAction.MONITOR_DOWNLOAD.value, file_name="file.pdf")
        log = controller.get_audit_log()
        assert len(log) == 2

    def test_permission_enforcement(self):
        pm = BrowserPermissionManager()
        pm.set_permission(BrowserAction.OPEN_URL.value, BrowserPermission.DENY)
        assert pm.check_permission(BrowserAction.OPEN_URL.value) == BrowserPermission.DENY
        assert pm.requires_approval(BrowserAction.UPLOAD_FILE.value) is True