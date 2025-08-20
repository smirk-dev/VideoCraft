#!/bin/bash
# VideoCraft AI Video Editor - Startup Script
# Cross-platform startup script

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           VideoCraft AI Editor           ║"
echo "║         Professional Video Suite         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v netstat >/dev/null 2>&1; then
        netstat -an | grep -q ":$port "
        return $?
    elif command -v ss >/dev/null 2>&1; then
        ss -an | grep -q ":$port "
        return $?
    else
        return 1
    fi
}

# Default ports
BACKEND_PORT=8001
FRONTEND_PORT=3001

echo "🔍 Checking port availability..."

# Check if default ports are available
if check_port $BACKEND_PORT; then
    echo "⚠️  Port $BACKEND_PORT is in use, trying alternative..."
    BACKEND_PORT=8002
    if check_port $BACKEND_PORT; then
        BACKEND_PORT=8080
    fi
fi

if check_port $FRONTEND_PORT; then
    echo "⚠️  Port $FRONTEND_PORT is in use, trying alternative..."
    FRONTEND_PORT=3002
    if check_port $FRONTEND_PORT; then
        FRONTEND_PORT=3080
    fi
fi

echo ""
echo "🚀 Starting VideoCraft with ports:"
echo "📡 Backend API: http://localhost:$BACKEND_PORT"
echo "🌐 Frontend:   http://localhost:$FRONTEND_PORT"
echo "📚 API Docs:   http://localhost:$BACKEND_PORT/api/docs"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🖥️  Starting Backend Server..."
cd "$SCRIPT_DIR/backend"

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

# Start backend in background
$PYTHON_CMD simple_main.py --port $BACKEND_PORT &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
sleep 3

echo "🌐 Starting Frontend Server..."
cd "$SCRIPT_DIR/frontend"

# Check if npm is available
if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm not found. Please install Node.js"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Set environment variables and start frontend
export PORT=$FRONTEND_PORT
export REACT_APP_API_URL="http://localhost:$BACKEND_PORT"

npm start &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "🎉 VideoCraft is now running!"
echo ""
echo "📱 Access your application at:"
echo "   🌐 Frontend: http://localhost:$FRONTEND_PORT"
echo "   📡 Backend API: http://localhost:$BACKEND_PORT"
echo "   📚 API Documentation: http://localhost:$BACKEND_PORT/api/docs"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"

# Trap Ctrl+C and cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

trap cleanup INT

# Wait for processes
wait
