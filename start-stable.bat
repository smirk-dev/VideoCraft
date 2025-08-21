@echo off
echo Starting VideoCraft with Stable Backend...

echo.
echo Stopping any existing processes...
taskkill /f /im node.exe 2>nul
taskkill /f /im python.exe 2>nul

echo.
echo Starting backend on http://127.0.0.1:8002...
start "VideoCraft Backend" cmd /k "cd /d %~dp0backend && python stable_backend.py"

echo.
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting frontend on http://localhost:3001...
start "VideoCraft Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo Both servers starting...
echo Frontend: http://localhost:3001
echo Backend: http://127.0.0.1:8002
echo.
echo Press any key to exit...
pause >nul
