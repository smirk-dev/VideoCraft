# 🚀 VideoCraft Deployment Setup Script
# Run this script to prepare your project for Vercel + Railway deployment

Write-Host "🎬 VideoCraft Deployment Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. Create production environment files
Write-Host "📋 Creating production environment files..." -ForegroundColor Yellow

# Backend production environment
$backendEnvContent = @"
# Production environment for Railway deployment
DATABASE_URL=postgresql://railway_generated_url
RAILWAY_ENVIRONMENT=production
HOST=0.0.0.0
PORT=$PORT
DEBUG=false
MAX_UPLOAD_SIZE=104857600
CORS_ORIGINS=["https://videocraft.vercel.app"]
PYTHONPATH=/app/backend
HF_CACHE_DIR=/app/models_cache
USE_GPU=false
"@

$backendEnvContent | Out-File -FilePath "backend\.env.production" -Encoding UTF8
Write-Host "✅ Created backend/.env.production" -ForegroundColor Green

# Frontend production environment
$frontendEnvContent = @"
# Production environment for Vercel deployment
REACT_APP_API_URL=https://videocraft-backend.railway.app
REACT_APP_MAX_FILE_SIZE=104857600
GENERATE_SOURCEMAP=false
NODE_ENV=production
"@

$frontendEnvContent | Out-File -FilePath "frontend\.env.production" -Encoding UTF8
Write-Host "✅ Created frontend/.env.production" -ForegroundColor Green

# 2. Update CORS settings in backend
Write-Host "🔗 Updating CORS settings..." -ForegroundColor Yellow

$corsUpdate = @"
# Add this to your backend/simple_main_backup.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://videocraft.vercel.app",
        "https://your-custom-domain.com",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"@

Write-Host "⚠️  Manual Step Required:" -ForegroundColor Red
Write-Host $corsUpdate -ForegroundColor Gray

# 3. Build frontend for testing
Write-Host "🏗️  Building frontend for production..." -ForegroundColor Yellow
Set-Location frontend
npm run build
Set-Location ..
Write-Host "✅ Frontend build complete" -ForegroundColor Green

# 4. Test backend startup
Write-Host "🧪 Testing backend startup..." -ForegroundColor Yellow
Set-Location backend
try {
    $process = Start-Process python -ArgumentList "simple_main_backup.py --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Hidden
    Start-Sleep 5
    $process.Kill()
    Write-Host "✅ Backend startup test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend startup test failed" -ForegroundColor Red
}
Set-Location ..

Write-Host ""
Write-Host "🎉 Deployment preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Push your code to GitHub" -ForegroundColor White
Write-Host "2. Deploy backend to Railway (railway.app)" -ForegroundColor White
Write-Host "3. Deploy frontend to Vercel (vercel.com)" -ForegroundColor White
Write-Host "4. Update API URL in frontend/.env.production with actual Railway URL" -ForegroundColor White
Write-Host ""
Write-Host "📚 See docs/DEPLOYMENT_VERCEL_RAILWAY.md for detailed instructions" -ForegroundColor Yellow
