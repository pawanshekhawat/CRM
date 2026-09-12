import os
import sys
import tempfile
from pathlib import Path

# Base Directory: Resolves the root of the CRM directory on whatever drive it is mounted
if getattr(sys, "frozen", False):
    # If packaged as standalone executable (e.g. PyInstaller)
    ROOT_DIR = Path(sys.executable).resolve().parent
else:
    # Running from source (app/core/config.py -> app/core -> app -> CRM Root)
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Core Storage Directories (All relative to the USB root)
DATA_DIR = ROOT_DIR / "data"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
PHOTOS_DIR = ATTACHMENTS_DIR / "photos"
ADMISSION_FORMS_DIR = ATTACHMENTS_DIR / "admission_forms"
RECEIPTS_DIR = DATA_DIR / "receipts"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
TEMP_DIR = DATA_DIR / "temp"
LOGS_DIR = ROOT_DIR / "logs"
CONFIG_DIR = ROOT_DIR / "config"

# Database Configuration
DATABASE_PATH = DATA_DIR / "crm.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# App Information
APP_NAME = "Personal CRM - Institute Edition"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "CADDESK Centre"

def init_directories():
    """Ensure all required isolated local storage folders exist on the drive."""
    directories = [
        DATA_DIR,
        ATTACHMENTS_DIR,
        PHOTOS_DIR,
        ADMISSION_FORMS_DIR,
        RECEIPTS_DIR,
        EXPORTS_DIR,
        BACKUPS_DIR,
        TEMP_DIR,
        LOGS_DIR,
        CONFIG_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Redirect OS temporary file allocations into the USB temp folder
    tempfile.tempdir = str(TEMP_DIR)
    os.environ["TMPDIR"] = str(TEMP_DIR)
    os.environ["TEMP"] = str(TEMP_DIR)
    os.environ["TMP"] = str(TEMP_DIR)

# Initialize directories automatically upon config import
init_directories()
