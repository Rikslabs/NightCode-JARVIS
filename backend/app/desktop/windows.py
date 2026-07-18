"""Window controller for desktop automation."""

from typing import Optional, Dict, Any


class WindowController:
    """Controls window actions on the desktop."""

    def __init__(self):
        self._mock_windows: Dict[str, Dict[str, Any]] = {
            "notepad": {"state": "normal", "focused": False},
            "chrome": {"state": "normal", "focused": False},
            "terminal": {"state": "normal", "focused": False},
        }

    def open(self, app_name: str) -> bool:
        """Open an application (metadata only)."""
        if app_name in self._mock_windows:
            return True
        self._mock_windows[app_name] = {"state": "normal", "focused": False}
        return True

    def focus(self, window_name: str) -> bool:
        """Focus a window (metadata only)."""
        if window_name in self._mock_windows:
            for win in self._mock_windows:
                self._mock_windows[win]["focused"] = False
            self._mock_windows[window_name]["focused"] = True
            return True
        return False

    def minimize(self, window_name: str) -> bool:
        """Minimize a window (metadata only)."""
        if window_name in self._mock_windows:
            self._mock_windows[window_name]["state"] = "minimized"
            return True
        return False

    def maximize(self, window_name: str) -> bool:
        """Maximize a window (metadata only)."""
        if window_name in self._mock_windows:
            self._mock_windows[window_name]["state"] = "maximized"
            return True
        return False

    def close(self, window_name: str) -> bool:
        """Close a window (metadata only)."""
        if window_name in self._mock_windows:
            del self._mock_windows[window_name]
            return True
        return False

    def get_window_info(self, window_name: str) -> Optional[Dict[str, Any]]:
        """Get window information."""
        return self._mock_windows.get(window_name)

    def list_windows(self) -> list:
        """List all windows."""
        return list(self._mock_windows.keys())

    def screenshot(self, window_name: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot metadata (no actual screenshot)."""
        return {
            "success": True,
            "window": window_name,
            "format": "metadata_only",
            "dimensions": [1920, 1080],
        }