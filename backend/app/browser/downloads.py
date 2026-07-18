"""Download controller for Browser."""

from typing import Optional, Dict, Any, List

from .models import BrowserAction, BrowserActionResult


class DownloadController:
    """Controls browser download operations."""

    def __init__(self):
        self._downloads: Dict[str, Dict[str, Any]] = {
            "example.pdf": {"status": "completed", "progress": 100},
            "data.zip": {"status": "downloading", "progress": 50},
        }

    def start_download(self, url: str, file_name: Optional[str] = None) -> BrowserActionResult:
        """Start a download (metadata only - requires approval)."""
        name = file_name or url.split("/")[-1]
        self._downloads[name] = {"status": "started", "progress": 0, "url": url}
        return BrowserActionResult(
            success=True,
            action=BrowserAction.START_DOWNLOAD.value,
            message=f"Download started: {name}",
            data={"url": url, "file_name": name},
        )

    def monitor_download(self, file_name: str) -> BrowserActionResult:
        """Monitor a download (metadata only)."""
        download = self._downloads.get(file_name)
        if download:
            return BrowserActionResult(
                success=True,
                action=BrowserAction.MONITOR_DOWNLOAD.value,
                message=f"Download status for: {file_name}",
                data=download,
            )
        return BrowserActionResult(
            success=False,
            action=BrowserAction.MONITOR_DOWNLOAD.value,
            message=f"Download not found: {file_name}",
        )

    def cancel_download(self, file_name: str) -> BrowserActionResult:
        """Cancel a download (metadata only)."""
        if file_name in self._downloads:
            self._downloads[file_name]["status"] = "cancelled"
        return BrowserActionResult(
            success=True,
            action=BrowserAction.CANCEL_DOWNLOAD.value,
            message=f"Download cancelled: {file_name}",
        )

    def list_downloads(self) -> BrowserActionResult:
        """List all downloads."""
        return BrowserActionResult(
            success=True,
            action=BrowserAction.LIST_DOWNLOADS.value,
            message="Downloads listed",
            data={"downloads": list(self._downloads.keys())},
        )