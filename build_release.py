import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = ROOT_DIR / "release"
APP_MAIN = ROOT_DIR / "app" / "main.py"

print("========================================================")
print("Building Standalone Single-File Personal CRM (.exe)")
print(f"Root Directory: {ROOT_DIR}")
print("========================================================")

# Hidden imports required for dynamic/modular loading
HIDDEN_IMPORTS = [
    # Core
    "app.core.base",
    "app.core.config",
    "app.core.database",
    "app.core.signals",
    "app.core.updater",
    # Models
    "app.models.course",
    "app.models.custom_fields",
    "app.models.message_template",
    "app.models.staff",
    "app.models.student",
    # Controllers & Services
    "app.modules.courses.controllers",
    "app.modules.staff.controllers",
    "app.modules.students.controllers",
    "app.modules.students.reports",
    "app.modules.messaging.controllers",
    # Bridge Layer
    "app.bridge",
    "app.bridge.crm_bridge",
    "app.bridge.students_bridge",
    "app.bridge.courses_bridge",
    "app.bridge.staff_bridge",
    "app.bridge.finance_bridge",
    "app.bridge.messaging_bridge",
    "app.bridge.reports_bridge",
    "app.bridge.updater_bridge",
    # PySide6 Qt Quick / QML
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",
    "PySide6.QtQuickLayouts",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtPrintSupport",
    # Third-party
    "sqlalchemy.dialects.sqlite",
    "reportlab",
    "reportlab.lib.pagesizes",
    "reportlab.platypus",
    "reportlab.lib.styles",
    "reportlab.lib.colors",
    "openpyxl",
    "PIL",
    "PIL.Image",
]

# Build PyInstaller command with --onefile
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name",
    "PersonalCRM",
    "--paths",
    str(ROOT_DIR),
]

# Add UI design system and QML assets
ui_assets = ROOT_DIR / "ui"
if ui_assets.exists():
    cmd.extend(["--add-data", f"{ui_assets};ui"])

# Add assets directory if it exists
messaging_assets = ROOT_DIR / "app" / "modules" / "messaging" / "assets"
if messaging_assets.exists():
    cmd.extend(["--add-data", f"{messaging_assets};app/modules/messaging/assets"])

# Bundle all essential runtime DLLs (vcruntime140, vcruntime140_1, python3xx, sqlite3, ssl)
py_base = Path(sys.base_prefix)
for dll in py_base.glob("*.dll"):
    cmd.extend(["--add-binary", f"{dll};."])

dlls_folder = py_base / "DLLs"
if dlls_folder.exists():
    for dll in dlls_folder.glob("*.dll"):
        cmd.extend(["--add-binary", f"{dll};."])

for imp in HIDDEN_IMPORTS:
    cmd.extend(["--hidden-import", imp])

cmd.append(str(APP_MAIN))

print("\nRunning PyInstaller (--onefile)...")
result = subprocess.run(cmd, cwd=str(ROOT_DIR))

if result.returncode != 0:
    print(f"\n[ERROR] PyInstaller build failed with exit code {result.returncode}")
    sys.exit(result.returncode)

ONEFILE_EXE = DIST_DIR / "PersonalCRM.exe"
print(f"\n[SUCCESS] Single-file executable built: {ONEFILE_EXE}")

# Clean up temporary build artifacts to avoid confusion
if BUILD_DIR.exists():
    print(f"Cleaning up temporary build folder: {BUILD_DIR}...")
    try:
        shutil.rmtree(BUILD_DIR)
    except Exception as e:
        print(f"Note: Could not completely remove build dir: {e}")

# Prepare Standalone Portable Release Folder
RELEASE_FOLDER = RELEASE_DIR / "PersonalCRM_Portable"
print(f"\nCreating portable release package in: {RELEASE_FOLDER}...")

if RELEASE_FOLDER.exists():
    shutil.rmtree(RELEASE_FOLDER)
RELEASE_FOLDER.mkdir(parents=True, exist_ok=True)

# 1. Copy the single .exe into the release folder
shutil.copy2(ONEFILE_EXE, RELEASE_FOLDER / "PersonalCRM.exe")

# 2. Copy data directory
dest_data = RELEASE_FOLDER / "data"
src_data = ROOT_DIR / "data"
if src_data.exists():
    print(f"Copying database and attachments from {src_data} to {dest_data}...")
    shutil.copytree(src_data, dest_data, ignore=shutil.ignore_patterns("*.tmp", "temp", "backups"))

# Ensure essential data subdirectories exist
(dest_data / "attachments" / "photos").mkdir(parents=True, exist_ok=True)
(dest_data / "attachments" / "admission_forms").mkdir(parents=True, exist_ok=True)
(dest_data / "receipts").mkdir(parents=True, exist_ok=True)
(dest_data / "exports").mkdir(parents=True, exist_ok=True)
(dest_data / "backups").mkdir(parents=True, exist_ok=True)
(dest_data / "temp").mkdir(parents=True, exist_ok=True)

# 3. Ensure logs and config directories exist
(RELEASE_FOLDER / "logs").mkdir(parents=True, exist_ok=True)
dest_config = RELEASE_FOLDER / "config"
dest_config.mkdir(parents=True, exist_ok=True)
src_version = ROOT_DIR / "config" / "version.json"
if src_version.exists():
    shutil.copy2(src_version, dest_config / "version.json")

# 4. Create README for end users
readme_content = """========================================================================
PERSONAL CRM (PORTABLE DESKTOP EDITION - QT QUICK ARCHITECTURE)
========================================================================

HOW TO RUN:
1. Double-click 'PersonalCRM.exe'.
2. The application will launch instantly with NO Python or setup needed!

PORTABILITY & DATA PRIVACY:
- All database records, student details, course catalogs, fee records,
  and image attachments stay strictly inside the 'data/' folder on this drive.
- No database data is stored in the cloud.
- Built-in In-App Updates: When updates are published, click 'Check for Updates'
  inside the app to automatically update in-place without losing your data!

FOLDER CONTENTS:
- PersonalCRM.exe       : Standalone application executable (Single-file)
- data/                 : Local SQLite database & attachment photos
- logs/                 : Application operation logs
- config/               : Institute settings & version metadata
========================================================================
"""
(RELEASE_FOLDER / "README_PORTABLE.txt").write_text(readme_content, encoding="utf-8")

# 5. Create a clean ZIP archive for sharing
app_version = "1.0.0"
if src_version.exists():
    try:
        import json
        with open(src_version, "r", encoding="utf-8") as f:
            app_version = json.load(f).get("version", "1.0.0")
    except Exception:
        pass

zip_path = RELEASE_DIR / f"PersonalCRM_Portable_v{app_version}.zip"
print(f"\nCompressing release bundle into {zip_path}...")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(RELEASE_FOLDER):
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(RELEASE_DIR)
            zipf.write(full_path, rel_path)

zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"[SUCCESS] Standalone package ready: {zip_path} ({zip_size_mb:.1f} MB)")
print("========================================================")
