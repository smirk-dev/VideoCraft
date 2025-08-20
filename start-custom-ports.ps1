# VideoCraft AI Video Editor - Custom Port Startup Script
# PowerShell version for better cross-platform support

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           VideoCraft AI Editor           ║" -ForegroundColor Cyan  
Write-Host "║        Custom Port Configuration         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 Port Configuration Options:" -ForegroundColor Yellow
Write-Host "1. Backend: 8001, Frontend: 3001 (DEFAULT - Recommended)" -ForegroundColor Green
Write-Host "2. Backend: 8002, Frontend: 3002" -ForegroundColor Yellow  
Write-Host "3. Backend: 8080, Frontend: 3080" -ForegroundColor Yellow
Write-Host "4. Custom ports" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Enter your choice (1-4, default is 1)"

# Default to option 1 if no choice or invalid choice
if ([string]::IsNullOrEmpty($choice) -or $choice -eq "1") {
    $BackendPort = 8001
    $FrontendPort = 3001
    Write-Host "Using DEFAULT ports: Backend 8001, Frontend 3001" -ForegroundColor Green
}
    "2" { 
        $BackendPort = 8002
        $FrontendPort = 3002
    }
    "3" { 
        $BackendPort = 8080
        $FrontendPort = 3080
    }
    "4" {
        $BackendPort = Read-Host "Enter backend port (default 8001)"
        if ([string]::IsNullOrEmpty($BackendPort)) { $BackendPort = 8001 }
        $FrontendPort = Read-Host "Enter frontend port (default 3001)"
        if ([string]::IsNullOrEmpty($FrontendPort)) { $FrontendPort = 3001 }
    }
    default {
        Write-Host "Invalid choice. Using default ports." -ForegroundColor Yellow
        $BackendPort = 8001
        $FrontendPort = 3001
    }
}

Write-Host ""
Write-Host "🚀 Starting VideoCraft with ports:" -ForegroundColor Green
Write-Host "📡 Backend API: http://localhost:$BackendPort" -ForegroundColor Cyan
Write-Host "🌐 Frontend:   http://localhost:$FrontendPort" -ForegroundColor Cyan  
Write-Host "📚 API Docs:   http://localhost:$BackendPort/api/docs" -ForegroundColor Cyan
Write-Host ""

Write-Host "Startup Options:" -ForegroundColor Yellow
Write-Host "1. Start Backend Only" -ForegroundColor Green
Write-Host "2. Start Frontend Only" -ForegroundColor Green
Write-Host "3. Start Both (separate windows)" -ForegroundColor Green
Write-Host ""

$method = Read-Host "Enter your choice (1-3)"

switch ($method) {
    "1" {
        Write-Host "🖥️ Starting Backend on port $BackendPort..." -ForegroundColor Green
        Set-Location backend
        $env:PORT = $BackendPort
        python -m uvicorn simple_backend:app --host 0.0.0.0 --port $BackendPort --reload
    }
    "2" {
        Write-Host "🌐 Starting Frontend on port $FrontendPort..." -ForegroundColor Green
        Set-Location frontend  
        $env:PORT = $FrontendPort
        $env:REACT_APP_API_URL = "http://localhost:$BackendPort"
        npm start
    }
    "3" {
        Write-Host "🚀 Starting both servers in separate windows..." -ForegroundColor Green
        
        # Start Backend
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; `$env:PORT=$BackendPort; python -m uvicorn simple_backend:app --host 0.0.0.0 --port $BackendPort --reload" -WindowStyle Normal
        
        Start-Sleep -Seconds 3
        
        # Start Frontend  
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; `$env:PORT=$FrontendPort; `$env:REACT_APP_API_URL='http://localhost:$BackendPort'; npm start" -WindowStyle Normal
        
        Write-Host ""
        Write-Host "✅ Both servers are starting in separate windows!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📡 Backend: http://localhost:$BackendPort" -ForegroundColor Cyan
        Write-Host "🌐 Frontend: http://localhost:$FrontendPort" -ForegroundColor Cyan
        Write-Host "📚 API Docs: http://localhost:$BackendPort/api/docs" -ForegroundColor Cyan
    }
    default {
        Write-Host "Invalid choice." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
