@echo off
REM VideoCraft AI Video Editor - Custom Port Startup Script
REM This script starts VideoCraft on alternative ports to avoid conflicts

echo.
echo ╔══════════════════════════════════════════╗
echo ║           VideoCraft AI Editor           ║
echo ║        Custom Port Configuration         ║
echo ╚══════════════════════════════════════════╝
echo.

echo 🔧 Starting VideoCraft on alternative ports...
echo.

echo Choose your port configuration:
echo 1. Backend: 8001, Frontend: 3001 (Recommended)
echo 2. Backend: 8002, Frontend: 3002
echo 3. Backend: 8080, Frontend: 3080
echo 4. Custom ports
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    set BACKEND_PORT=8001
    set FRONTEND_PORT=3001
    goto :start_servers
)

if "%choice%"=="2" (
    set BACKEND_PORT=8002
    set FRONTEND_PORT=3002
    goto :start_servers
)

if "%choice%"=="3" (
    set BACKEND_PORT=8080
    set FRONTEND_PORT=3080
    goto :start_servers
)

if "%choice%"=="4" (
    set /p BACKEND_PORT="Enter backend port (default 8001): "
    if "%BACKEND_PORT%"=="" set BACKEND_PORT=8001
    set /p FRONTEND_PORT="Enter frontend port (default 3001): "
    if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3001
    goto :start_servers
)

echo Invalid choice. Using default ports 8001 and 3001.
set BACKEND_PORT=8001
set FRONTEND_PORT=3001

:start_servers
echo.
echo 🚀 Starting VideoCraft with custom ports:
echo 📡 Backend API: http://localhost:%BACKEND_PORT%
echo 🌐 Frontend:   http://localhost:%FRONTEND_PORT%
echo 📚 API Docs:   http://localhost:%BACKEND_PORT%/api/docs
echo.

echo Choose startup method:
echo 1. Start Backend Only
echo 2. Start Frontend Only  
echo 3. Start Both (in separate windows)
echo.
set /p method="Enter your choice (1-3): "

if "%method%"=="1" goto :start_backend
if "%method%"=="2" goto :start_frontend
if "%method%"=="3" goto :start_both

:start_backend
echo 🖥️ Starting Backend on port %BACKEND_PORT%...
cd backend
set PORT=%BACKEND_PORT%
python -m uvicorn simple_backend:app --host 0.0.0.0 --port %BACKEND_PORT% --reload
goto :end

:start_frontend
echo 🌐 Starting Frontend on port %FRONTEND_PORT%...
cd frontend
set PORT=%FRONTEND_PORT%
set REACT_APP_API_URL=http://localhost:%BACKEND_PORT%
npm start
goto :end

:start_both
echo 🚀 Starting both servers...
echo.
echo Starting Backend in new window...
start "VideoCraft Backend (Port %BACKEND_PORT%)" cmd /c "cd backend && set PORT=%BACKEND_PORT% && python -m uvicorn simple_backend:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend in new window...
start "VideoCraft Frontend (Port %FRONTEND_PORT%)" cmd /c "cd frontend && set PORT=%FRONTEND_PORT% && set REACT_APP_API_URL=http://localhost:%BACKEND_PORT% && npm start"

echo.
echo ✅ Both servers starting in separate windows!
echo.
echo 📡 Backend: http://localhost:%BACKEND_PORT%
echo 🌐 Frontend: http://localhost:%FRONTEND_PORT%
echo 📚 API Docs: http://localhost:%BACKEND_PORT%/api/docs
echo.

:end
echo.
echo Press any key to exit...
pause >nul
