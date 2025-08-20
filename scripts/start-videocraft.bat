@echo off
echo.
echo ╔══════════════════════════════════════════╗
echo ║           VideoCraft AI Editor           ║
echo ║         Professional Video Suite         ║
echo ╚══════════════════════════════════════════╝
echo.

echo 🚀 Starting VideoCraft with FIXED ports...
echo.

echo 🖥️  Starting Backend Server on port 8001...
cd /d "%~dp0backend"
start "VideoCraft Backend" cmd /k "python simple_main.py --port 8001"

echo ✅ Backend starting on port 8001...
timeout /t 3 >nul

echo 🌐 Starting Frontend Server on port 3001...
cd /d "%~dp0frontend"
set PORT=3001
set REACT_APP_API_URL=http://localhost:8001
start "VideoCraft Frontend" cmd /k "npm start"

echo ✅ Frontend starting on port 3001...
echo.
echo 🎉 VideoCraft is now starting!
echo.
echo 📱 Your application will be available at:
echo    🌐 Frontend: http://localhost:3001
echo    📡 Backend API: http://localhost:8001
echo    📚 API Documentation: http://localhost:8001/api/docs
echo.
echo 💡 Both servers are running in separate windows
echo 🛑 Close the command windows to stop the servers
echo.

timeout /t 5 >nul
start http://localhost:3001

echo Press any key to exit this launcher...
pause >nul
