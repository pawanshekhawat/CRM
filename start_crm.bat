@echo off
title Personal CRM - Institute Edition
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

echo ========================================================
echo Starting Personal CRM (Portable USB Edition)
echo Root Directory: %~dp0
echo ========================================================

set "PY_CMD="

:: 1. Try virtualenv python if it has working PySide6
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -c "import PySide6.QtCore" >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=%~dp0.venv\Scripts\python.exe"
    )
)

:: 2. Try Python Launcher (py -3)
if not defined PY_CMD (
    py -3 -c "import PySide6.QtCore" >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=py -3"
    )
)

:: 3. Try standard python command
if not defined PY_CMD (
    python -c "import PySide6.QtCore" >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=python"
    )
)

:: 4. Try known Python installation paths
if not defined PY_CMD (
    if exist "C:\Python314\python.exe" (
        "C:\Python314\python.exe" -c "import PySide6.QtCore" >nul 2>&1
        if not errorlevel 1 (
            set "PY_CMD=C:\Python314\python.exe"
        )
    )
)

if not defined PY_CMD (
    echo.
    echo [NOTICE] Required dependencies (PySide6) are not yet installed.
    echo Launching automated requirement installer...
    echo.
    call "%~dp0setup_requirements.bat"
    exit /b %errorlevel%
)

%PY_CMD% "%~dp0app\main.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error. Check logs in %~dp0logs\crm.log
    pause
)


