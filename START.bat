@echo off
echo Starting Clipo AI...
echo.

REM Start Auth Service
echo Starting Auth Service (Port 32190)...
start "Clipo Auth Service" cmd /k "cd backend && venv\Scripts\activate && uvicorn auth_service:app --reload --host 0.0.0.0 --port 32190"

timeout /t 2 /nobreak >nul

REM Start Video Service
echo Starting Video Service (Port 32191)...
start "Clipo Video Service" cmd /k "cd backend && venv\Scripts\activate && uvicorn video_service:app --reload --host 0.0.0.0 --port 32191"

timeout /t 2 /nobreak >nul

REM Start Library Service
echo Starting Library Service (Port 32189)...
start "Clipo Library Service" cmd /k "cd backend && venv\Scripts\activate && uvicorn library_service:app --reload --host 0.0.0.0 --port 32189"

timeout /t 2 /nobreak >nul

REM Start frontend
echo Starting Frontend (Port 32192)...
start "Clipo Frontend" cmd /k "cd frontend && npx next dev -H 0.0.0.0 -p 32192"

echo.
echo ========================================
echo Clipo AI lancé avec succès!
echo ========================================
echo Site Web: http://88.191.169.79:32192
echo Auth API: http://88.191.169.79:32190
echo Video API: http://88.191.169.79:32191
echo Library API: http://88.191.169.79:32189
echo ========================================
echo PORTS A OUVRIR: 32189, 32190, 32191, 32192
echo ========================================
echo.
echo Appuyez sur une touche pour quitter...
pause >nul
