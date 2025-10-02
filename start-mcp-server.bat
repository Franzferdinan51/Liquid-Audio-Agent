@echo off
REM Liquid Audio MCP Server Startup Script (Windows)
REM Automated startup with configuration and monitoring

echo ================================
echo Liquid Audio MCP Server
echo ================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "mcp-server.py" (
    echo ❌ mcp-server.py not found. Please run from project root.
    pause
    exit /b 1
)

REM Check dependencies
echo 🔍 Checking dependencies...
python -c "import liquid_audio, mcp, sounddevice, numpy" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencies missing. Installing...
    python setup-mcp.py
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "models" mkdir models
if not exist "cache" mkdir cache
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "input" mkdir input
if not exist "output" mkdir output

REM Set environment variables
if not exist ".env" (
    echo ⚙️  Creating environment configuration...
    (
        echo # Liquid Audio MCP Server Configuration
        echo LIQUID_AUDIO_MODEL_PATH=./models
        echo LIQUID_AUDIO_CACHE_DIR=./cache
        echo LIQUID_AUDIO_LOG_LEVEL=INFO
        echo LIQUID_AUDIO_DEVICE=auto
    ) > .env
)

REM Start the MCP server
echo.
echo 🚀 Starting Liquid Audio MCP Server...
echo    Logs will be saved to: mcp-liquid-audio.log
echo    Press Ctrl+C to stop the server
echo.

REM Run with environment variables
set LIQUID_AUDIO_MODEL_PATH=./models
set LIQUID_AUDIO_CACHE_DIR=./cache
set LIQUID_AUDIO_LOG_LEVEL=INFO

python mcp-server.py

echo.
echo Server stopped. Press any key to exit.
pause >nul