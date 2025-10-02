#!/bin/bash
# Liquid Audio MCP Server Startup Script (Linux/macOS)
# Automated startup with configuration and monitoring

set -e

echo "================================"
echo "Liquid Audio MCP Server"
echo "================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check if in correct directory
if [ ! -f "mcp-server.py" ]; then
    echo "❌ mcp-server.py not found. Please run from project root."
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
if ! python3 -c "import liquid_audio, mcp, sounddevice, numpy" 2>/dev/null; then
    echo "⚠️  Dependencies missing. Installing..."
    python3 setup-mcp.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Create necessary directories
mkdir -p models cache temp logs input output

# Set environment variables
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cat > .env << EOF
# Liquid Audio MCP Server Configuration
LIQUID_AUDIO_MODEL_PATH=./models
LIQUID_AUDIO_CACHE_DIR=./cache
LIQUID_AUDIO_LOG_LEVEL=INFO
LIQUID_AUDIO_DEVICE=auto
EOF
fi

# Start the MCP server
echo
echo "🚀 Starting Liquid Audio MCP Server..."
echo "   Logs will be saved to: mcp-liquid-audio.log"
echo "   Press Ctrl+C to stop the server"
echo

# Export environment variables
export LIQUID_AUDIO_MODEL_PATH="./models"
export LIQUID_AUDIO_CACHE_DIR="./cache"
export LIQUID_AUDIO_LOG_LEVEL="INFO"

# Run the server
python3 mcp-server.py

echo
echo "Server stopped."