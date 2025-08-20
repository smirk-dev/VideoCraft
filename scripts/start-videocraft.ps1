# VideoCraft AI Video Editor - Windows PowerShell Startup Script

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           VideoCraft AI Editor           ║" -ForegroundColor Cyan  
Write-Host "║         Professional Video Suite         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
        return $connection
    } catch {
        return $false
    }
}

# Default ports - FIXED as per user requirement
$BackendPort = 8001
$FrontendPort = 3001

Write-Host ""
Write-Host "🚀 Starting VideoCraft with FIXED ports:" -ForegroundColor Green
Write-Host "📡 Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "🌐 Frontend:   http://localhost:$FrontendPort" -ForegroundColor Cyan  
Write-Host "📚 API Docs:   http://localhost:$BackendPort/api/docs" -ForegroundColor Cyan
Write-Host ""

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    Write-Host "🖥️  Starting Backend Server..." -ForegroundColor Green
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            $pythonVersion = python3 --version 2>$null
            $pythonCmd = "python3"
        } else {
            $pythonCmd = "python"
        }
        Write-Host "✅ Using $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
        exit 1
    }
    
    # Start backend in new window
    $backendPath = Join-Path $ScriptDir "backend"
    $backendScript = Join-Path $backendPath "simple_main.py"
    
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; $pythonCmd simple_main.py --port $BackendPort" -PassThru -WindowStyle Normal
    
    Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
    Start-Sleep -Seconds 3
    
    Write-Host "🌐 Starting Frontend Server..." -ForegroundColor Green
    
    # Check if npm is available
    try {
        $npmVersion = npm --version 2>$null
        Write-Host "✅ Using npm $npmVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ npm not found. Please install Node.js" -ForegroundColor Red
        $backendProcess.Kill()
        exit 1
    }
    
    # Start frontend in new window
    $frontendPath = Join-Path $ScriptDir "frontend"
    
    $frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; `$env:PORT=$FrontendPort; `$env:REACT_APP_API_URL='http://localhost:$BackendPort'; npm start" -PassThru -WindowStyle Normal
    
    Write-Host "✅ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 VideoCraft is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Access your application at:" -ForegroundColor Cyan
    Write-Host "   🌐 Frontend: http://localhost:$FrontendPort" -ForegroundColor White
    Write-Host "   📡 Backend API: http://localhost:$BackendPort" -ForegroundColor White
    Write-Host "   📚 API Documentation: http://localhost:$BackendPort/api/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Both servers are running in separate windows" -ForegroundColor Yellow
    Write-Host "🛑 Close the terminal windows to stop the servers" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to open the application in your browser..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # Open browser
    Start-Process "http://localhost:$FrontendPort"
    
} catch {
    Write-Host "❌ Error starting servers: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the logs and try again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
