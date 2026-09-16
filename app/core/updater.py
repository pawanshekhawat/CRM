import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PySide6.QtCore import QObject, QThread, Signal

from app.core.config import (
    APP_VERSION,
    BACKUPS_DIR,
    CONFIG_DIR,
    DATABASE_PATH,
    DATA_DIR,
    ROOT_DIR,
    TEMP_DIR,
)

logger = logging.getLogger("CRM.Updater")

GITHUB_REPO = "pawanshekhawat/CRM"
MANIFEST_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/config/version.json"
GITHUB_RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


@dataclass
class UpdateInfo:
    """Encapsulates release and version information."""
    current_version: str = APP_VERSION
    latest_version: str = APP_VERSION
    title: str = ""
    changelog: List[str] = field(default_factory=list)
    download_url: str = ""
    release_date: str = ""
    is_update_available: bool = False
    file_name: str = ""
    file_size_bytes: int = 0
    github_repo: str = GITHUB_REPO


def parse_version_tuple(v_str: str) -> Tuple[int, ...]:
    """Parses a version string like 'v1.2.3' into a numeric tuple (1, 2, 3)."""
    clean_str = re.sub(r"^[vV]", "", (v_str or "").strip())
    parts = []
    for segment in clean_str.split("."):
        num_match = re.match(r"^(\d+)", segment)
        if num_match:
            parts.append(int(num_match.group(1)))
        else:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def compare_versions(current_v: str, latest_v: str) -> int:
    """
    Compares two version strings.
    Returns:
       1 if latest_v > current_v (update available)
       0 if latest_v == current_v
      -1 if latest_v < current_v
    """
    cur_tuple = parse_version_tuple(current_v)
    lat_tuple = parse_version_tuple(latest_v)
    if lat_tuple > cur_tuple:
        return 1
    elif lat_tuple < cur_tuple:
        return -1
    return 0


def create_pre_update_backup() -> Optional[Path]:
    """
    Creates a timestamped backup copy of crm.db in data/backups/
    before applying any code or application updates.
    """
    if not DATABASE_PATH.exists():
        return None

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"crm_backup_pre_update_{timestamp}.db"
    backup_path = BACKUPS_DIR / backup_filename

    try:
        shutil.copy2(DATABASE_PATH, backup_path)
        logger.info(f"Created pre-update database backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create pre-update database backup: {e}")
        return None


def fetch_update_info(timeout: int = 6) -> UpdateInfo:
    """
    Fetches the latest release info from GitHub version manifest or Releases API.
    Does NOT throw unhandled network exceptions; returns UpdateInfo with is_update_available=False on error.
    """
    update_info = UpdateInfo(current_version=APP_VERSION)
    is_frozen = getattr(sys, "frozen", False)

    headers = {
        "User-Agent": f"PersonalCRM-Updater/{APP_VERSION}",
        "Accept": "application/json",
    }

    # 1. First attempt: Raw GitHub version.json manifest (lightweight & no rate limit)
    try:
        manifest_url = f"{MANIFEST_RAW_URL}?t={int(time.time())}"
        req = urllib.request.Request(manifest_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                raw_data = response.read().decode("utf-8")
                manifest = json.loads(raw_data)
                latest_v = manifest.get("version", APP_VERSION)
                update_info.latest_version = latest_v
                update_info.title = manifest.get("title", f"Version {latest_v}")
                update_info.changelog = manifest.get("changelog", [])
                update_info.release_date = manifest.get("release_date", "")
                update_info.github_repo = manifest.get("github_repo", GITHUB_REPO)

                if is_frozen:
                    exe_url = manifest.get("exe_download_url") or f"https://github.com/{GITHUB_REPO}/releases/download/v{latest_v}/PersonalCRM.exe"
                    update_info.download_url = exe_url
                    update_info.file_name = "PersonalCRM.exe"
                else:
                    update_info.download_url = manifest.get("download_url", f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip")
                    update_info.file_name = f"PersonalCRM_v{latest_v}.zip"

                update_info.is_update_available = compare_versions(APP_VERSION, latest_v) > 0
                logger.info(f"Update check (manifest): Current={APP_VERSION}, Latest={latest_v}, Available={update_info.is_update_available}")
                return update_info
    except Exception as e:
        logger.debug(f"Raw manifest fetch failed: {e}. Falling back to GitHub Releases API...")

    # 2. Second attempt: GitHub Releases API
    try:
        req = urllib.request.Request(GITHUB_RELEASES_API_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                raw_data = response.read().decode("utf-8")
                rel = json.loads(raw_data)
                tag_name = rel.get("tag_name", "")
                latest_v = re.sub(r"^[vV]", "", tag_name) or APP_VERSION
                update_info.latest_version = latest_v
                update_info.title = rel.get("name") or f"Version {latest_v}"
                update_info.release_date = (rel.get("published_at") or "")[:10]
                update_info.download_url = rel.get("html_url", "")

                # Parse changelog lines from release body
                body_text = rel.get("body", "")
                lines = [line.strip().lstrip("-*# ").strip() for line in body_text.splitlines() if line.strip()]
                update_info.changelog = lines if lines else ["Performance optimizations and bug fixes."]

                # Check for downloadable binary assets
                assets = rel.get("assets", [])
                if assets:
                    if is_frozen:
                        # Prioritize .exe or portable zip assets
                        exe_assets = [
                            a for a in assets
                            if a.get("name", "").lower().endswith(".exe") or "portable" in a.get("name", "").lower()
                        ]
                        if exe_assets:
                            update_info.download_url = exe_assets[0].get("browser_download_url", "")
                            update_info.file_name = exe_assets[0].get("name", "")
                            update_info.file_size_bytes = exe_assets[0].get("size", 0)
                    if not update_info.download_url or update_info.download_url.endswith("/releases"):
                        update_info.download_url = assets[0].get("browser_download_url", "")
                        update_info.file_name = assets[0].get("name", "")
                        update_info.file_size_bytes = assets[0].get("size", 0)
                
                if not update_info.download_url or not update_info.download_url.endswith((".zip", ".exe")):
                    if is_frozen:
                        update_info.download_url = f"https://github.com/{GITHUB_REPO}/releases/download/v{latest_v}/PersonalCRM.exe"
                        update_info.file_name = "PersonalCRM.exe"
                    else:
                        update_info.download_url = f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag_name}.zip" if tag_name else f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
                        update_info.file_name = f"PersonalCRM_v{latest_v}.zip"

                update_info.is_update_available = compare_versions(APP_VERSION, latest_v) > 0
                logger.info(f"Update check (Releases API): Current={APP_VERSION}, Latest={latest_v}, Available={update_info.is_update_available}")
                return update_info
    except Exception as e:
        logger.info(f"GitHub Releases API fetch failed or offline: {e}")

    # Fallback to local config version if offline
    local_manifest = CONFIG_DIR / "version.json"
    if local_manifest.exists():
        try:
            with open(local_manifest, "r", encoding="utf-8") as f:
                data = json.load(f)
                update_info.title = data.get("title", f"Version {APP_VERSION}")
                update_info.changelog = data.get("changelog", [])
        except Exception:
            pass

    # Ensure download_url has fallback
    if not update_info.download_url:
        if is_frozen:
            update_info.download_url = f"https://github.com/{GITHUB_REPO}/releases/latest"
            update_info.file_name = "PersonalCRM.exe"
        else:
            update_info.download_url = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
            update_info.file_name = f"PersonalCRM_v{update_info.latest_version}.zip"

    return update_info


class UpdateCheckWorker(QThread):
    """Asynchronous background worker to check for software updates without blocking UI."""
    update_found = Signal(object)    # UpdateInfo
    up_to_date = Signal(object)      # UpdateInfo
    check_failed = Signal(str)       # Error message

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def run(self):
        try:
            info = fetch_update_info()
            if info.is_update_available:
                self.update_found.emit(info)
            else:
                self.up_to_date.emit(info)
        except Exception as e:
            logger.error(f"Error during update check worker: {e}")
            self.check_failed.emit(str(e))


class UpdateDownloadWorker(QThread):
    """Streams the update file to data/temp/ and reports download progress."""
    progress = Signal(int, int, float)   # bytes_downloaded, total_bytes, percentage
    download_finished = Signal(str)      # target_file_path
    download_failed = Signal(str)        # error message

    def __init__(self, download_url: str, file_name: Optional[str] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.download_url = download_url
        self.file_name = file_name or "PersonalCRM_Update.zip"

    def run(self):
        try:
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            target_path = TEMP_DIR / self.file_name

            headers = {
                "User-Agent": f"PersonalCRM-Updater/{APP_VERSION}",
            }
            req = urllib.request.Request(self.download_url, headers=headers)

            with urllib.request.urlopen(req, timeout=45) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 1024 * 64  # 64 KB chunks

                with open(target_path, "wb") as f_out:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        downloaded += len(chunk)
                        pct = (downloaded / total_size * 100.0) if total_size > 0 else 0.0
                        self.progress.emit(downloaded, total_size, pct)

            logger.info(f"Update package downloaded successfully to: {target_path}")
            self.download_finished.emit(str(target_path))
        except Exception as e:
            logger.error(f"Failed to download update package: {e}")
            self.download_failed.emit(str(e))


def apply_update_and_restart(update_file_path: str):
    """
    Safely installs downloaded update files and restarts the application in-place.
    STRICT RULE: The data/ folder (crm.db, photos) is 100% PRESERVED and NEVER overwritten.
    """
    create_pre_update_backup()

    update_path = Path(update_file_path)
    if not update_path.exists():
        raise FileNotFoundError(f"Update file not found: {update_file_path}")

    is_frozen = getattr(sys, "frozen", False)

    if is_frozen:
        # Standalone Executable update: Replace PersonalCRM.exe via a detached helper script
        target_exe = Path(sys.executable).resolve()
        helper_bat = TEMP_DIR / "apply_update.bat"

        extracted_exe: Optional[Path] = None

        if update_path.suffix.lower() == ".exe":
            extracted_exe = update_path.resolve()
        elif update_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(update_path, "r") as zip_ref:
                for name in zip_ref.namelist():
                    if name.endswith("PersonalCRM.exe") or name.lower() == "personalcrm.exe":
                        temp_exe = (TEMP_DIR / "PersonalCRM_New.exe").resolve()
                        with zip_ref.open(name) as src, open(temp_exe, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        extracted_exe = temp_exe
                        break

                # Also extract updated config/version.json if present
                for name in zip_ref.namelist():
                    norm = name.replace("\\", "/").strip("/")
                    if norm.endswith("version.json"):
                        dest_cfg = CONFIG_DIR / "version.json"
                        with zip_ref.open(name) as src, open(dest_cfg, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        break

        # STRICT VERIFICATION: Ensure the candidate is an actual valid Windows executable
        if not extracted_exe or not extracted_exe.exists():
            raise ValueError(
                "The downloaded update package does not contain a compiled 'PersonalCRM.exe'.\n\n"
                "To update the standalone portable app, please ensure the GitHub release "
                "contains the compiled 'PersonalCRM.exe' or 'PersonalCRM_Portable.zip' asset.\n\n"
                "Your local database and files have not been modified."
            )

        try:
            with open(extracted_exe, "rb") as f:
                header = f.read(2)
            if header != b"MZ":
                raise ValueError(
                    f"Downloaded file is not a valid 64-bit Windows executable.\n\n"
                    "Aborting update to prevent file corruption. Your database and student data are 100% safe."
                )
        except Exception as e:
            raise ValueError(f"Executable validation failed: {e}")

        new_exe_to_copy = extracted_exe.resolve()
        current_pid = os.getpid()

        bat_content = f"""@echo off
title Personal CRM Updater
echo ===================================================
echo Updating Personal CRM to latest version...
echo ===================================================

:: Ensure the previous process terminates and releases handles
taskkill /F /PID {current_pid} > nul 2>&1

:: Retry loop to safely replace PersonalCRM.exe
set RETRY_COUNT=0
:RETRY_LOOP
timeout /t 1 /nobreak > nul

:: Attempt rename first (Windows allows renaming running/terminating executables)
if exist "{target_exe}.old" del /f /q "{target_exe}.old" > nul 2>&1
move /y "{target_exe}" "{target_exe}.old" > nul 2>&1

copy /y "{new_exe_to_copy}" "{target_exe}" > nul 2>&1
if not errorlevel 1 goto COPY_SUCCESS

set /a RETRY_COUNT+=1
if %RETRY_COUNT% LSS 12 (
    echo Waiting for application process to release file lock (Attempt %RETRY_COUNT%/12)...
    goto RETRY_LOOP
)

echo [ERROR] Update copy failed after multiple attempts.
echo Please close any open instances of Personal CRM and try again.
pause
exit /b 1

:COPY_SUCCESS
echo [SUCCESS] Personal CRM updated successfully!
del /f /q "{target_exe}.old" > nul 2>&1
del /f /q "{new_exe_to_copy}" > nul 2>&1
del /f /q "{update_path.resolve()}" > nul 2>&1

echo Restarting Personal CRM...
start "" "{target_exe}"
del "%~f0"
exit
"""
        helper_bat.write_text(bat_content, encoding="utf-8")
        logger.info(f"Generated standalone updater script at: {helper_bat}")

        # Cleanly quit Qt application before invoking updater script
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.quit()
        except Exception:
            pass

        # Launch detached updater script
        subprocess.Popen(
            ["cmd.exe", "/c", str(helper_bat)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            close_fds=True,
        )
        os._exit(0)


    else:
        # Source/Script mode: Extract updated code files excluding data/
        if update_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(update_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    norm_name = member.replace("\\", "/").strip("/")
                    parts = norm_name.split("/")

                    # If files are wrapped in a top-level directory like 'CRM-main/' or 'Isolated-CRM-main/'
                    if len(parts) > 1 and ("CRM" in parts[0] or parts[0].endswith("-main") or parts[0].startswith("v")):
                        rel_parts = parts[1:]
                    else:
                        rel_parts = parts

                    if not rel_parts or not rel_parts[0]:
                        continue

                    rel_path_str = "/".join(rel_parts)

                    # Strictly protect data/, logs/, backups/, and .git/
                    if (
                        rel_path_str.startswith("data/")
                        or rel_path_str.startswith("logs/")
                        or rel_path_str.startswith("backups/")
                        or rel_path_str.startswith(".git/")
                        or rel_path_str in ("data", "logs", "backups", ".git")
                    ):
                        continue

                    target_dest = ROOT_DIR / Path(*rel_parts)
                    if member.endswith("/"):
                        target_dest.mkdir(parents=True, exist_ok=True)
                    else:
                        target_dest.parent.mkdir(parents=True, exist_ok=True)
                        with zip_ref.open(member) as source, open(target_dest, "wb") as target:
                            shutil.copyfileobj(source, target)

            logger.info("Extracted update files over source directory successfully.")
            update_path.unlink(missing_ok=True)

        # Relaunch via start_crm.bat or python
        start_bat = ROOT_DIR / "start_crm.bat"
        if start_bat.exists():
            subprocess.Popen(["cmd.exe", "/c", str(start_bat)], cwd=str(ROOT_DIR))
        else:
            subprocess.Popen([sys.executable, str(ROOT_DIR / "app" / "main.py")], cwd=str(ROOT_DIR))
        sys.exit(0)

