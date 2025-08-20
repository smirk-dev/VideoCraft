#!/bin/bash

# VideoCraft Production Startup Script

echo "🚀 Starting VideoCraft Production Deployment..."

# Check if required directories exist
mkdir -p backend/uploads backend/temp backend/processed

# Backend Setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install production requirements
pip install -r requirements.production.txt

# Start backend with gunicorn for production
echo "🔄 Starting backend server..."
gunicorn simple_main_backup:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --daemon

cd ..

# Frontend Setup
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies
npm ci --only=production

# Build for production
npm run build

# Install serve globally if not present
npm list -g serve || npm install -g serve

# Start frontend
echo "🌐 Starting frontend server..."
serve -s build -l 3000 &

cd ..

echo "✅ VideoCraft is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo ""
echo "To stop the services:"
echo "pkill -f gunicorn"
echo "pkill -f serve"
