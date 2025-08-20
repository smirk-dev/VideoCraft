@echo off
REM VideoCraft AI Video Editor - Windows Setup Script
REM Run this script to quickly set up and start VideoCraft

echo.
echo ╔══════════════════════════════════════════╗
echo ║           VideoCraft AI Editor           ║
echo ║     AI-Powered Video Editing Platform    ║
echo ╚══════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo ❌ Please run this script from the VideoCraft project root directory
    pause
    exit /b 1
)

echo ✅ Project structure verified
echo.

REM Create necessary directories
echo 📁 Creating directories...
mkdir uploads 2>nul
mkdir processed 2>nul
mkdir temp 2>nul
mkdir logs 2>nul
mkdir static 2>nul
mkdir models_cache 2>nul
echo ✅ Directories created

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating environment file...
    copy ".env.example" ".env" >nul
    echo ✅ Created .env file - you can modify settings there
) else (
    echo ✅ Found existing .env file
)

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Python dependencies installed
echo.

REM Check if Node.js is available for frontend
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found - frontend will not be available
    echo Install Node.js from: https://nodejs.org/
    goto :start_backend
) else (
    echo ✅ Node.js detected
    echo.
    echo 🌐 Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        cd ..
        goto :start_backend
    )
    cd ..
    echo ✅ Frontend dependencies installed
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo Choose an option:
echo 1. Start Backend Only (API Server)
echo 2. Start Frontend Only (Web Interface)
echo 3. Start Both (Recommended)
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :start_backend
if "%choice%"=="2" goto :start_frontend
if "%choice%"=="3" goto :start_both
if "%choice%"=="4" goto :end

:start_backend
echo.
echo 🚀 Starting VideoCraft AI backend...
echo Backend will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server
echo.
cd backend
python -m uvicorn simple_backend:app --host 0.0.0.0 --port 8000 --reload
cd ..
goto :end

:start_frontend
echo.
echo 🌐 Starting VideoCraft frontend...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
cd frontend
npm start
cd ..
goto :end

:start_both
echo.
echo 🚀 Starting both backend and frontend...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs
echo.
echo Starting backend in background...
start "VideoCraft Backend" cmd /c "cd backend && python -m uvicorn simple_backend:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend...
cd frontend
npm start
cd ..

:end
echo.
echo 👋 Thank you for using VideoCraft AI Video Editor!
pause
