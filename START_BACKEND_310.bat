@echo off
echo ============================================================
echo 🚀 Starting ClipGenius Backend (Python 3.10)
echo ============================================================

cd backend
if not exist "venv_310" (
    echo ❌ Virtual environment venv_310 not found!
    echo Please run setup first.
    pause
    exit /b
)

echo 🐍 Using Python: venv_310
start "ClipGenius Auth Service" cmd /k "venv_310\Scripts\python.exe -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 8000"
start "ClipGenius Video Service" cmd /k "venv_310\Scripts\python.exe -m uvicorn video_service:app --reload --host 0.0.0.0 --port 8001"

pause
