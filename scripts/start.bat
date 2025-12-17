@echo off
REM ClipGenius AI - Quick Start Script for Windows

echo Starting ClipGenius AI...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Create environment files if they don't exist
if not exist backend\.env (
    echo Creating backend\.env from example...
    copy backend\.env.example backend\.env
    echo Please edit backend\.env with your API keys before continuing.
    pause
)

if not exist frontend\.env.local (
    echo Creating frontend\.env.local from example...
    copy frontend\.env.local.example frontend\.env.local
)

REM Start services
echo Starting Docker containers...
docker-compose -f infrastructure\docker-compose.yml up --build -d

echo.
echo Services started successfully!
echo.
echo Access points:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Celery Flower: http://localhost:5555
echo.
echo View logs:
echo    docker-compose -f infrastructure\docker-compose.yml logs -f
echo.
echo Stop services:
echo    docker-compose -f infrastructure\docker-compose.yml down
echo.
pause
