@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

:: 1. Try virtualenv pythonw if valid
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    "%~dp0.venv\Scripts\python.exe" -c "import PySide6.QtCore" >nul 2>&1
    if not errorlevel 1 (
        start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0app\main.py"
        exit /b 0
    )
)

:: 2. Try Python Launcher windowless (pyw -3)
py -3 -c "import PySide6.QtCore" >nul 2>&1
if not errorlevel 1 (
    where pyw.exe >nul 2>&1
    if not errorlevel 1 (
        start "" pyw -3 "%~dp0app\main.py"
        exit /b 0
    )
    start "" py -3 "%~dp0app\main.py"
    exit /b 0
)

:: 3. Try standard pythonw
python -c "import PySide6.QtCore" >nul 2>&1
if not errorlevel 1 (
    where pythonw.exe >nul 2>&1
    if not errorlevel 1 (
        start "" pythonw "%~dp0app\main.py"
        exit /b 0
    )
    start "" python "%~dp0app\main.py"
    exit /b 0
)

:: 4. Direct path fallback
if exist "C:\Python314\pythonw.exe" (
    "C:\Python314\python.exe" -c "import PySide6.QtCore" >nul 2>&1
    if not errorlevel 1 (
        start "" "C:\Python314\pythonw.exe" "%~dp0app\main.py"
        exit /b 0
    )
)

start "" python "%~dp0app\main.py"
exit /b 0

