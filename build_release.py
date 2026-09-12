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
print("Building Standalone Portable Personal CRM (.exe)")
print(f"Root Directory: {ROOT_DIR}")
print("========================================================")

# Hidden imports required for dynamic/modular loading
HIDDEN_IMPORTS = [
    # Core
    "app.core.base",
    "app.core.config",
    "app.core.database",
    "app.core.signals",
    # Models
    "app.models.course",
    "app.models.custom_fields",
    "app.models.staff",
    "app.models.student",
    # Modules
    "app.modules.base_module",
    "app.modules.registry",
    # Courses
    "app.modules.courses.controllers",
    "app.modules.courses.course_module",
    "app.modules.courses.views.course_form_dialog",
    "app.modules.courses.views.course_list_view",
    # Staff
    "app.modules.staff.controllers",
    "app.modules.staff.staff_module",
    "app.modules.staff.views.batch_form_dialog",
    "app.modules.staff.views.batch_roster_dialog",
    "app.modules.staff.views.staff_detail_dialog",
    "app.modules.staff.views.staff_form_dialog",
    "app.modules.staff.views.staff_list_view",
    # Students
    "app.modules.students.controllers",
    "app.modules.students.reports",
    "app.modules.students.student_module",
    "app.modules.students.views.custom_fields_dialog",
    "app.modules.students.views.student_detail_view",
    "app.modules.students.views.student_form_dialog",
    "app.modules.students.views.student_list_view",
    # UI
    "app.ui.theme",
    "app.ui.widgets.dynamic_fields",
    "app.ui.widgets.form_image_viewer",
    "app.ui.widgets.search_bar",
    "app.ui.widgets.stat_card",
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
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtPrintSupport",
]

# Build PyInstaller command
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onedir",
    "--windowed",
    "--name",
    "PersonalCRM",
    "--paths",
    str(ROOT_DIR),
]

for imp in HIDDEN_IMPORTS:
    cmd.extend(["--hidden-import", imp])

cmd.append(str(APP_MAIN))

print("\nRunning PyInstaller...")
result = subprocess.run(cmd, cwd=str(ROOT_DIR))

if result.returncode != 0:
    print(f"\n[ERROR] PyInstaller build failed with exit code {result.returncode}")
    sys.exit(result.returncode)

TARGET_DIST = DIST_DIR / "PersonalCRM"
print(f"\n[SUCCESS] PyInstaller build completed at {TARGET_DIST}")

# Prepare the portable release package
print("\nPackaging portable standalone release (with data isolation)...")

# 1. Copy data directory
dest_data = TARGET_DIST / "data"
src_data = ROOT_DIR / "data"
if src_data.exists():
    print(f"Copying database and attachments from {src_data} to {dest_data}...")
    if dest_data.exists():
        shutil.rmtree(dest_data)
    shutil.copytree(src_data, dest_data, ignore=shutil.ignore_patterns("*.tmp", "temp", "backups"))

# Ensure essential data subdirectories exist
(dest_data / "attachments" / "photos").mkdir(parents=True, exist_ok=True)
(dest_data / "attachments" / "admission_forms").mkdir(parents=True, exist_ok=True)
(dest_data / "receipts").mkdir(parents=True, exist_ok=True)
(dest_data / "exports").mkdir(parents=True, exist_ok=True)
(dest_data / "backups").mkdir(parents=True, exist_ok=True)
(dest_data / "temp").mkdir(parents=True, exist_ok=True)

# 2. Ensure logs and config directories exist
(TARGET_DIST / "logs").mkdir(parents=True, exist_ok=True)
(TARGET_DIST / "config").mkdir(parents=True, exist_ok=True)

# 3. Create a Launcher batch script inside the distribution folder
launcher_content = """@echo off
title Personal CRM - Institute Edition (Portable)
cd /d "%~dp0"
start "" "%~dp0PersonalCRM.exe"
exit
"""
(TARGET_DIST / "Start_Personal_CRM.bat").write_text(launcher_content, encoding="utf-8")

# 4. Create README for end users
readme_content = """========================================================================
PERSONAL CRM - INSTITUTE EDITION (PORTABLE STANDALONE RELEASE)
========================================================================

HOW TO RUN:
1. Double-click 'PersonalCRM.exe' or 'Start_Personal_CRM.bat'.
2. The application will launch instantly in isolated portable mode.

PORTABILITY & DATA PRIVACY:
- All database records, student details, course catalogs, fee records,
  and image attachments stay strictly inside the 'data/' folder.
- You can copy this entire folder to any USB flash drive or Windows PC.
- No Python installation or runtime setup is required on the target PC.

FOLDER STRUCTURE:
- PersonalCRM.exe       : Main application executable (Compiled binary)
- data/                 : Local SQLite database & attachment photos
- logs/                 : Application operation logs
- config/               : Institute settings & custom configurations
========================================================================
"""
(TARGET_DIST / "README_PORTABLE.txt").write_text(readme_content, encoding="utf-8")

# 5. Create a clean ZIP archive for sharing
RELEASE_DIR.mkdir(parents=True, exist_ok=True)
zip_path = RELEASE_DIR / "PersonalCRM_Portable_Standalone.zip"
print(f"\nCompressing release bundle into {zip_path}...")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(TARGET_DIST):
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(DIST_DIR)
            zipf.write(full_path, rel_path)

zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"[SUCCESS] Standalone package ready: {zip_path} ({zip_size_mb:.1f} MB)")
print("========================================================")
