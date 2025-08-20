#!/bin/bash

# 🚀 VideoCraft Deployment Setup Script (Linux/Mac)
# Run this script to prepare your project for Vercel + Railway deployment

echo "🎬 VideoCraft Deployment Setup"
echo "================================"

# 1. Create production environment files
echo "📋 Creating production environment files..."

# Backend production environment
cat > backend/.env.production << EOF
# Production environment for Railway deployment
DATABASE_URL=postgresql://railway_generated_url
RAILWAY_ENVIRONMENT=production
HOST=0.0.0.0
PORT=\$PORT
DEBUG=false
MAX_UPLOAD_SIZE=104857600
CORS_ORIGINS=["https://videocraft.vercel.app"]
PYTHONPATH=/app/backend
HF_CACHE_DIR=/app/models_cache
USE_GPU=false
EOF

echo "✅ Created backend/.env.production"

# Frontend production environment
cat > frontend/.env.production << EOF
# Production environment for Vercel deployment
REACT_APP_API_URL=https://videocraft-backend.railway.app
REACT_APP_MAX_FILE_SIZE=104857600
GENERATE_SOURCEMAP=false
NODE_ENV=production
EOF

echo "✅ Created frontend/.env.production"

# 2. Build frontend for testing
echo "🏗️ Building frontend for production..."
cd frontend
npm run build
cd ..
echo "✅ Frontend build complete"

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Deploy backend to Railway (railway.app)"
echo "3. Deploy frontend to Vercel (vercel.com)"
echo "4. Update API URL in frontend/.env.production with actual Railway URL"
echo ""
echo "📚 See docs/DEPLOYMENT_VERCEL_RAILWAY.md for detailed instructions"
