@echo off
REM NourishNest Development Server Starter (Windows)
REM This script starts both Django backend and Vite frontend servers

echo.
echo ======================================
echo   NourishNest - Local Development
echo ======================================
echo.

REM Get the project root directory
set PROJECT_ROOT=%~dp0

REM Start backend in a new window
echo Starting Backend (Django on port 8000)...
start "Backend - Django" cmd /k "cd /d %PROJECT_ROOT%Backend && python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in a new window
echo Starting Frontend (Vite on port 5173)...
start "Frontend - Vite" cmd /k "cd /d %PROJECT_ROOT%Frontend && npm run dev"

echo.
echo ======================================
echo   Servers Starting...
echo ======================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/api/docs/
echo.
echo Both windows are now open in separate terminals
echo.
pause
