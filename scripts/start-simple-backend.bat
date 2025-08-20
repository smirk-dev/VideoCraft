@echo off
REM Quick start script for the simple backend only

echo.
echo ╔══════════════════════════════════════════╗
echo ║           VideoCraft AI Editor           ║
echo ║          Simple Backend Startup          ║
echo ╚══════════════════════════════════════════╝
echo.

echo 🚀 Starting Simple Backend Server...
echo Backend will be available at: http://localhost:8001
echo API documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

echo.
echo 👋 Backend stopped
pause
