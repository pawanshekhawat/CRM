@echo off
title Personal CRM - Institute Edition
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

echo ========================================================
echo Starting Personal CRM (Portable USB Edition)
echo Root Directory: %~dp0
echo ========================================================

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0app\main.py"
) else (
    python "%~dp0app\main.py"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error. Check logs in %~dp0logs\crm.log
    pause
)

