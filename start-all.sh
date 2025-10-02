#!/bin/bash

echo "========================================"
echo "Starting Liquid Audio Agent + n8n with CORS"
echo "========================================"
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "[WARNING] .env.local file not found!"
    echo "Please create .env.local with your GEMINI_API_KEY"
    echo "Example: GEMINI_API_KEY=your_api_key_here"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

echo "[1/3] Starting n8n with CORS enabled..."
echo ""

# Start n8n in background
./start-n8n-cors.sh &
N8N_PID=$!

echo "[2/3] Waiting for n8n to start..."
sleep 8

echo "[3/3] Starting Liquid Audio Agent..."
echo ""

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

# Start the React app in background
npm run dev &
APP_PID=$!

echo ""
echo "========================================"
echo "Both services are starting up:"
echo "- n8n: http://localhost:5678"
echo "- Liquid Audio Agent: http://localhost:3000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services..."

# Function to clean up background processes
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $N8N_PID $APP_PID 2>/dev/null
    # Also kill any remaining node processes
    pkill -f "n8n start" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo "Done."
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait