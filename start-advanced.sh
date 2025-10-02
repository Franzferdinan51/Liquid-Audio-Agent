#!/bin/bash

echo "========================================"
echo "Advanced Liquid Audio Agent + n8n Launcher"
echo "========================================"
echo ""

# Configuration options
SKIP_N8N=false
SKIP_APP=false
HEADLESS=false
CLEAN_START=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-n8n)
            SKIP_N8N=true
            shift
            ;;
        --skip-app)
            SKIP_APP=true
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --clean)
            CLEAN_START=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-n8n    Skip starting n8n server"
            echo "  --skip-app    Skip starting Liquid Audio Agent"
            echo "  --headless    Don't auto-open browser windows"
            echo "  --clean       Clean node_modules and reinstall"
            echo "  --help        Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for available options"
            exit 1
            ;;
    esac
done

# Clean start if requested
if [ "$CLEAN_START" = "true" ]; then
    echo "[CLEAN] Removing node_modules..."
    rm -rf node_modules
    rm -f package-lock.json
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "[WARNING] .env.local file not found!"
    echo "Please create .env.local with your GEMINI_API_KEY"
    echo "Example: GEMINI_API_KEY=your_api_key_here"
    echo ""
    if [ "$CLEAN_START" = "false" ]; then
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

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

# Start n8n if not skipped
if [ "$SKIP_N8N" = "false" ]; then
    echo "[1/2] Starting n8n with CORS enabled..."
    echo ""

    if [ "$HEADLESS" = "false" ]; then
        ./start-n8n-cors.sh &
    else
        ./start-n8n-cors.sh > /dev/null 2>&1 &
    fi
    N8N_PID=$!

    echo "[WAIT] Waiting for n8n to start..."
    sleep 8
else
    echo "[SKIP] Skipping n8n startup"
fi

# Start Liquid Audio Agent if not skipped
if [ "$SKIP_APP" = "false" ]; then
    echo "[2/2] Starting Liquid Audio Agent..."
    echo ""

    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
        echo ""
    fi

    if [ "$HEADLESS" = "false" ]; then
        npm run dev &
    else
        npm run dev > /dev/null 2>&1 &
    fi
    APP_PID=$!
else
    echo "[SKIP] Skipping Liquid Audio Agent startup"
fi

echo ""
echo "========================================"
echo "Services started:"
if [ "$SKIP_N8N" = "false" ]; then echo "- n8n: http://localhost:5678"; fi
if [ "$SKIP_APP" = "false" ]; then echo "- Liquid Audio Agent: http://localhost:3000"; fi
echo "========================================"
echo ""

if [ "$HEADLESS" = "false" ]; then
    echo "Press Ctrl+C to stop all services..."
    wait
else
    echo "Running in headless mode. Services will continue running."
    echo "Use Ctrl+C to stop."
    wait
fi