"""Browser Controller - Deterministic browser automation layer."""

from .models import (
    BrowserAction,
    BrowserActionResult,
    BrowserPermission,
)
from .controller import BrowserController
from .tabs import TabController
from .navigation import NavigationController
from .interaction import InteractionController
from .extraction import ExtractionController
from .downloads import DownloadController
from .permissions import BrowserPermissionManager
from .registry import BrowserRegistry
from .validator import BrowserValidator

__all__ = [
    "BrowserAction",
    "BrowserActionResult",
    "BrowserPermission",
    "BrowserController",
    "TabController",
    "NavigationController",
    "InteractionController",
    "ExtractionController",
    "DownloadController",
    "BrowserPermissionManager",
    "BrowserRegistry",
    "BrowserValidator",
]
