@echo off
REM VideoCraft Production Startup Script for Windows

echo 🚀 Starting VideoCraft Production Deployment...

REM Check if required directories exist
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\temp" mkdir backend\temp
if not exist "backend\processed" mkdir backend\processed

REM Backend Setup
echo 📦 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install production requirements
pip install -r requirements.production.txt

REM Start backend
echo 🔄 Starting backend server...
start /B uvicorn simple_main_backup:app --host 0.0.0.0 --port 8000 --workers 4

cd ..

REM Frontend Setup
echo 🎨 Setting up frontend...
cd frontend

REM Install dependencies
call npm ci --only=production

REM Build for production
call npm run build

REM Install serve globally if not present
call npm list -g serve >nul 2>&1 || npm install -g serve

REM Start frontend
echo 🌐 Starting frontend server...
start /B serve -s build -l 3000

cd ..

echo ✅ VideoCraft is now running!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo To stop the services, close this window or use Task Manager
pause
