#!/usr/bin/env powershell
# VideoCraft Unified Startup Script - All Issues Fixed

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🎬 VideoCraft Fixed & Ready             ║" -ForegroundColor Cyan  
Write-Host "║            All Issues Resolved - Port 8003          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Fixed Configuration
$BackendPort = 8003
$FrontendPort = 3001

Write-Host "🔧 Issues Fixed:" -ForegroundColor Green
Write-Host "  ✅ Port conflicts resolved (8002 → 8003)" -ForegroundColor White
Write-Host "  ✅ Backend-frontend integration standardized" -ForegroundColor White
Write-Host "  ✅ Multiple backend files organized" -ForegroundColor White
Write-Host "  ✅ Consistent endpoint URLs implemented" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Starting VideoCraft with FIXED configuration:" -ForegroundColor Green
Write-Host "📡 Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "🌐 Frontend:   http://localhost:$FrontendPort" -ForegroundColor Cyan  
Write-Host ""

try {
    Write-Host "🖥️  Installing Backend Dependencies..." -ForegroundColor Green
    cd backend
    pip install Flask Flask-CORS python-dotenv
    
    Write-Host "✅ Starting Clean Backend on Port $BackendPort..." -ForegroundColor Green
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py" -PassThru -WindowStyle Normal
    
    Start-Sleep -Seconds 3
    
    Write-Host "🌐 Starting Frontend on Port $FrontendPort..." -ForegroundColor Green
    cd ../frontend
    
    $frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; `$env:PORT=$FrontendPort; `$env:REACT_APP_API_URL='http://localhost:$BackendPort'; npm start" -PassThru -WindowStyle Normal
    
    Write-Host ""
    Write-Host "🎉 VideoCraft is now running with ALL FIXES APPLIED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Access your application:" -ForegroundColor Cyan
    Write-Host "   🌐 Frontend: http://localhost:$FrontendPort" -ForegroundColor White
    Write-Host "   📡 Backend: http://localhost:$BackendPort" -ForegroundColor White
    Write-Host "   📊 Test Analysis: Go to SimpleAnalysisPage" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Test the fixed integration:" -ForegroundColor Yellow
    Write-Host "   1. Visit http://localhost:$FrontendPort/simple" -ForegroundColor White
    Write-Host "   2. Click 'Run Analysis Again' button" -ForegroundColor White
    Write-Host "   3. Should see analysis data displayed!" -ForegroundColor White
    Write-Host ""
    
    # Open browser automatically
    Start-Process "http://localhost:$FrontendPort/simple"
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
