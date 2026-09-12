@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

:: Use relative python executable from the isolated virtual environment
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0app\main.py"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    start "" "%~dp0.venv\Scripts\python.exe" "%~dp0app\main.py"
) else (
    echo Python runtime not found in .venv. Attempting system python...
    python "%~dp0app\main.py"
)
exit

