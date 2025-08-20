# Quick start script for the simple backend only (PowerShell version)

Write-Host ""
Write-Host "VideoCraft AI Editor - Simple Backend Startup" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Simple Backend Server..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:8001" -ForegroundColor Cyan
Write-Host "API documentation: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

Write-Host ""
Write-Host "Backend stopped" -ForegroundColor Yellow
Write-Host "Press any key to exit..." -ForegroundColor Yellow
Read-Host
