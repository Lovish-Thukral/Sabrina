@echo off

:: Change to the directory where this .bat file lives
cd /d "%~dp0"

:: Check if venv Python exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python not found at .venv\Scripts\python.exe
    echo Please run setup first.
    pause
    exit /b 1
)

:: Launch Sabrina AI
.venv\Scripts\python.exe main.py