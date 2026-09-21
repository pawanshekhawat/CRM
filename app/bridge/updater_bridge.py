import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from app.core.config import APP_VERSION
from app.core.updater import (
    UpdateInfo,
    fetch_update_info,
    UpdateCheckWorker,
    UpdateDownloadWorker,
    apply_update_and_restart,
)

logger = logging.getLogger("CRM.UpdaterBridge")


class UpdaterBridge(QObject):
    """Bridge for checking software releases, download progress, and self-updating."""

    checkStarted = Signal()
    checkFinished = Signal(bool, str, str, "QVariantList")  # available, latest_v, title, changelog
    downloadProgress = Signal(int, int, float)             # downloaded, total, percentage
    downloadFinished = Signal(str)                        # local_file_path
    updateFailed = Signal(str)                            # error message

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_info: Optional[UpdateInfo] = None
        self._check_worker: Optional[UpdateCheckWorker] = None
        self._download_worker: Optional[UpdateDownloadWorker] = None

    @Slot(result=str)
    def getCurrentVersion(self) -> str:
        return APP_VERSION

    @Slot()
    def checkForUpdates(self):
        """Starts background update check."""
        self.checkStarted.emit()
        self._check_worker = UpdateCheckWorker()
        self._check_worker.update_found.connect(self._on_update_found)
        self._check_worker.up_to_date.connect(self._on_up_to_date)
        self._check_worker.check_failed.connect(self._on_check_failed)
        self._check_worker.start()

    def _on_update_found(self, info: UpdateInfo):
        self._current_info = info
        self.checkFinished.emit(True, info.latest_version, info.title, info.changelog)

    def _on_up_to_date(self, info: UpdateInfo):
        self._current_info = info
        self.checkFinished.emit(False, info.latest_version, info.title, info.changelog)

    def _on_check_failed(self, error_msg: str):
        self.updateFailed.emit(error_msg)

    @Slot()
    def downloadAndInstall(self):
        """Downloads the update package and applies it."""
        if not self._current_info or not self._current_info.download_url:
            # Re-fetch info synchronously if needed
            self._current_info = fetch_update_info()

        if not self._current_info.download_url:
            self.updateFailed.emit("No valid download URL found.")
            return

        self._download_worker = UpdateDownloadWorker(
            download_url=self._current_info.download_url,
            file_name=self._current_info.file_name,
        )
        self._download_worker.progress.connect(self._on_progress)
        self._download_worker.download_finished.connect(self._on_download_finished)
        self._download_worker.download_failed.connect(self._on_download_failed)
        self._download_worker.start()

    def _on_progress(self, downloaded: int, total: int, pct: float):
        self.downloadProgress.emit(downloaded, total, pct)

    def _on_download_finished(self, file_path: str):
        self.downloadFinished.emit(file_path)
        try:
            apply_update_and_restart(file_path)
        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            self.updateFailed.emit(str(e))

    def _on_download_failed(self, err_msg: str):
        self.updateFailed.emit(err_msg)
