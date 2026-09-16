import os
import sys
from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication

from app.core.config import APP_VERSION, DATABASE_PATH, BACKUPS_DIR
from app.core.database import init_db
from app.core.updater import (
    UpdateInfo,
    compare_versions,
    create_pre_update_backup,
    parse_version_tuple,
    fetch_update_info,
)
from app.ui.widgets.update_dialog import UpdateDialog


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()


def test_parse_version_tuple():
    assert parse_version_tuple("1.0.0") == (1, 0, 0)
    assert parse_version_tuple("v1.0.1") == (1, 0, 1)
    assert parse_version_tuple("V2.15.8") == (2, 15, 8)
    assert parse_version_tuple("1.0") == (1, 0, 0)
    assert parse_version_tuple("1.0.0-beta") == (1, 0, 0)


def test_compare_versions():
    # Newer versions (should return 1)
    assert compare_versions("1.0.0", "1.0.1") == 1
    assert compare_versions("1.0.0", "1.1.0") == 1
    assert compare_versions("1.0.0", "2.0.0") == 1
    assert compare_versions("v1.0.0", "v1.0.1") == 1

    # Same versions (should return 0)
    assert compare_versions("1.0.0", "1.0.0") == 0
    assert compare_versions("v1.0.0", "1.0.0") == 0
    assert compare_versions("1.2.3", "v1.2.3") == 0

    # Older versions (should return -1)
    assert compare_versions("1.0.1", "1.0.0") == -1
    assert compare_versions("2.0.0", "1.9.9") == -1


def test_pre_update_backup():
    # Ensure DB file exists
    assert DATABASE_PATH.exists()

    backup_path = create_pre_update_backup()
    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.parent == BACKUPS_DIR
    assert "crm_backup_pre_update_" in backup_path.name
    assert backup_path.stat().st_size > 0

    # Cleanup test backup file
    try:
        backup_path.unlink()
    except Exception:
        pass


def test_update_info_dataclass():
    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.0.1",
        title="Bugfix Release",
        changelog=["Fixed UI alignment", "Updated fees calculations"],
        is_update_available=True,
    )
    assert info.is_update_available is True
    assert len(info.changelog) == 2
    assert info.latest_version == "1.0.1"


def test_update_dialog_instantiation():
    app = QApplication.instance() or QApplication(sys.argv)

    sample_info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        title="Major Feature Update",
        changelog=["Added In-App Updater", "WhatsApp chat simulator improvements"],
        is_update_available=True,
        download_url="https://github.com/pawanshekhawat/Isolated-CRM/releases",
    )

    dlg = UpdateDialog(update_info=sample_info)
    assert dlg is not None
    assert dlg.update_info.latest_version == "1.1.0"
    assert dlg.update_btn.isEnabled() is True
    assert "v1.1.0" in dlg.update_btn.text()

    dlg.close()
