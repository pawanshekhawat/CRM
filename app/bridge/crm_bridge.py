import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from app.core.config import (
    APP_NAME,
    APP_VERSION,
    ORGANIZATION_NAME,
    DATABASE_PATH,
    DATA_DIR,
    RECEIPTS_DIR,
    EXPORTS_DIR,
    BACKUPS_DIR,
    PHOTOS_DIR,
)
from app.core.updater import create_pre_update_backup
from app.modules.students.controllers import StudentController
from app.modules.courses.controllers import CourseController
from app.modules.staff.controllers import StaffController

logger = logging.getLogger("CRM.Bridge")


class CRMBridge(QObject):
    """
    Main Application Bridge: Manages global navigation, system status,
    toast notifications, institute metadata, and high-level actions.
    """

    pageChanged = Signal(str)
    toastMessage = Signal(str, str, str)  # message, type (success|error|warning|info), title
    themeChanged = Signal(str)            # "dark" | "light"
    statsUpdated = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_page = "Dashboard"
        self._theme_mode = "dark"

    @Slot(result=str)
    def getAppName(self) -> str:
        return APP_NAME

    @Slot(result=str)
    def getAppVersion(self) -> str:
        return APP_VERSION

    @Slot(result=str)
    def getOrganizationName(self) -> str:
        return ORGANIZATION_NAME

    @Slot(result=str)
    def getCurrentPage(self) -> str:
        return self._current_page

    @Slot(str)
    def navigateTo(self, page_name: str):
        if self._current_page != page_name:
            self._current_page = page_name
            self.pageChanged.emit(page_name)

    @Slot(str, str, str)
    def showToast(self, message: str, msg_type: str = "info", title: str = ""):
        self.toastMessage.emit(message, msg_type, title)

    @Slot(result=str)
    def getThemeMode(self) -> str:
        return self._theme_mode

    @Slot(str)
    def setThemeMode(self, mode: str):
        if mode in ("dark", "light") and self._theme_mode != mode:
            self._theme_mode = mode
            self.themeChanged.emit(mode)

    @Slot(result="QVariantMap")
    def getGlobalStats(self) -> Dict[str, Any]:
        """Aggregates high-level metrics for top bar and system health."""
        try:
            student_metrics = StudentController.get_dashboard_metrics()
            course_metrics = CourseController.get_courses_dashboard_metrics()
            staff_metrics = StaffController.get_staff_dashboard_metrics()

            return {
                "total_students": student_metrics.get("total_students", 0),
                "active_students": student_metrics.get("active_students", 0),
                "total_fees_collected": student_metrics.get("total_paid", 0.0),
                "total_pending_dues": student_metrics.get("balance_due", 0.0),
                "total_courses": course_metrics.get("total_courses", 0),
                "total_batches": staff_metrics.get("total_batches", 0),
                "active_batches": staff_metrics.get("active_batches", 0),
                "total_staff": staff_metrics.get("total_staff", 0),
                "db_size_kb": (DATABASE_PATH.stat().st_size // 1024) if DATABASE_PATH.exists() else 0,
            }
        except Exception as e:
            logger.error(f"Error fetching global stats: {e}")
            return {
                "total_students": 0,
                "active_students": 0,
                "total_fees_collected": 0.0,
                "total_pending_dues": 0.0,
                "total_courses": 0,
                "total_batches": 0,
                "active_batches": 0,
                "total_staff": 0,
                "db_size_kb": 0,
            }

    @Slot(result=bool)
    def createManualBackup(self) -> bool:
        try:
            backup_path = create_pre_update_backup()
            if backup_path and backup_path.exists():
                self.showToast(f"Database backed up to {backup_path.name}", "success", "Backup Successful")
                return True
            else:
                self.showToast("Could not create database backup.", "error", "Backup Failed")
                return False
        except Exception as e:
            logger.error(f"Error during manual backup: {e}")
            self.showToast(str(e), "error", "Backup Error")
            return False

    @Slot(str)
    def openPathInExplorer(self, path_str: str):
        try:
            target = Path(path_str)
            if not target.is_absolute():
                target = DATA_DIR / path_str
            if target.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(target.resolve())))
            else:
                self.showToast(f"Path does not exist: {path_str}", "warning", "File Not Found")
        except Exception as e:
            logger.error(f"Failed to open path: {e}")

    @Slot(str)
    def openExternalUrl(self, url_str: str):
        try:
            QDesktopServices.openUrl(QUrl(url_str))
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
