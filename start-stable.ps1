# VideoCraft Stable Startup Script
Write-Host "Starting VideoCraft with Stable Backend..." -ForegroundColor Green

Write-Host "`nStopping any existing processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "`nStarting stable backend on http://127.0.0.1:8002..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn stable_backend:app --host 127.0.0.1 --port 8002"

Write-Host "`nWaiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`nStarting frontend on http://localhost:3001..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm start"

Write-Host "`nBoth servers are starting..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "Backend: http://127.0.0.1:8002" -ForegroundColor White
Write-Host "API Test: file:///$PSScriptRoot/api-test.html" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
