@echo off
setlocal enabledelayedexpansion
title Personal CRM - Institute Edition Setup & Dependency Installer
cd /d "%~dp0"

echo ========================================================================
echo   PERSONAL CRM - INSTITUTE EDITION
echo   Automated Environment & Requirement Installer
echo ========================================================================
echo.

:: 1. Check for Python
echo [1/4] Checking Python installation...
set "PYTHON_EXE="

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_EXE=py -3"
    goto :PYTHON_FOUND
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto :PYTHON_FOUND
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python3"
    goto :PYTHON_FOUND
)

echo.
echo [ERROR] Python was not found on this computer.
echo Please install Python 3.10+ from https://www.python.org/downloads/
echo (Make sure to check "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:PYTHON_FOUND
echo Python executable found: %PYTHON_EXE%
%PYTHON_EXE% --version

:: 2. Setup Virtual Environment
echo.
echo [2/4] Setting up isolated local virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment in .venv...
    %PYTHON_EXE% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Existing virtual environment detected.
)

:: 3. Install and Upgrade Requirements
echo.
echo [3/4] Installing / Upgrading required packages from requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install one or more requirements.
    pause
    exit /b 1
)

:: 4. Ensure Data and Attachments Directories Exist
echo.
echo [4/4] Initializing isolated data directories...
if not exist "data\attachments\photos" mkdir "data\attachments\photos"
if not exist "data\attachments\admission_forms" mkdir "data\attachments\admission_forms"
if not exist "data\receipts" mkdir "data\receipts"
if not exist "data\exports" mkdir "data\exports"
if not exist "data\backups" mkdir "data\backups"
if not exist "data\temp" mkdir "data\temp"
if not exist "logs" mkdir "logs"
if not exist "config" mkdir "config"

echo.
echo ========================================================================
echo   [SUCCESS] All dependencies and directories are installed and ready!
echo ========================================================================
echo.
echo You can now run the CRM anytime using 'start_crm.bat' or 'launcher.bat'.
echo.
set /p RUN_NOW="Would you like to start Personal CRM right now? (Y/N): "
if /i "%RUN_NOW%"=="Y" (
    echo Launching Personal CRM...
    start "" ".venv\Scripts\pythonw.exe" app\main.py
)
exit /b 0
