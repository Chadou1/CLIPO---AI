@echo off
echo Starting ClipGenius Library Service...
echo.

cd /d "%~dp0backend"

REM Check if venv_310 exists
if not exist "venv_310\Scripts\python.exe" (
    echo ERROR: Virtual environment venv_310 not found!
    echo Please run setup.py first.
    pause
    exit /b 1
)

REM Activate venv_310 and start library service
echo Starting Library Service on port 32189 with venv_310...
venv_310\Scripts\python.exe -m uvicorn library_service:app --reload --host 0.0.0.0 --port 32189

pause
