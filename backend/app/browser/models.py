"""Browser models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class BrowserAction(Enum):
    """Browser action types."""

    # Navigation
    OPEN_URL = "open_url"
    BACK = "back"
    FORWARD = "forward"
    REFRESH = "refresh"
    STOP_LOADING = "stop_loading"

    # Tabs
    NEW_TAB = "new_tab"
    CLOSE_TAB = "close_tab"
    SWITCH_TAB = "switch_tab"
    LIST_TABS = "list_tabs"

    # Interaction
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SUBMIT_FORM = "submit_form"
    UPLOAD_FILE = "upload_file"

    # Extraction
    GET_TITLE = "get_title"
    GET_TEXT = "get_text"
    GET_LINKS = "get_links"
    GET_METADATA = "get_metadata"
    GET_STATUS = "get_status"

    # Downloads
    START_DOWNLOAD = "start_download"
    MONITOR_DOWNLOAD = "monitor_download"
    CANCEL_DOWNLOAD = "cancel_download"
    LIST_DOWNLOADS = "list_downloads"


class BrowserPermission(Enum):
    """Browser permission levels."""

    ALLOW = "allow"
    DENY = "deny"
    PROMPT = "prompt"


@dataclass
class BrowserActionResult:
    """Result of a browser action."""

    success: bool
    action: str
    message: str = ""
    data: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }