@echo off
setlocal enabledelayedexpansion

:: ========================================
:: Liquid Audio Agent - Unified Startup Script
:: ========================================
:: This script handles all startup scenarios:
:: - First-time setup and dependency installation
:: - Python environment and audio libraries setup
:: - N8N server with CORS configuration
:: - React application startup
:: - Service management and cleanup
:: ========================================

title Liquid Audio Agent - Unified Startup

:: Configuration
set APP_NAME=Liquid Audio Agent
set N8N_PORT=5678
set APP_PORT=3000
set N8N_HOST=0.0.0.0
set WEBHOOK_URL=http://localhost:%N8N_PORT%
set WAIT_TIME=8

:: Colors for output
set "INFO=[92m"    :: Green
set "WARN=[93m"    :: Yellow
set "ERROR=[91m"   :: Red
set "RESET=[0m"    :: Reset

:: Parse command line arguments
set SKIP_N8N=false
set SKIP_APP=false
set SKIP_PYTHON=false
set CLEAN_INSTALL=false
set HEADLESS=false
set HELP=false
set FIX_CORS=false

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--skip-n8n" set SKIP_N8N=true& shift & goto :parse_args
if /i "%~1"=="--skip-app" set SKIP_APP=true& shift & goto :parse_args
if /i "%~1"=="--skip-python" set SKIP_PYTHON=true& shift & goto :parse_args
if /i "%~1"=="--clean" set CLEAN_INSTALL=true& shift & goto :parse_args
if /i "%~1"=="--headless" set HEADLESS=true& shift & goto :parse_args
if /i "%~1"=="--fix-cors" set FIX_CORS=true& shift & goto :parse_args
if /i "%~1"=="--help" set HELP=true& shift & goto :parse_args
echo %WARN%Unknown option: %~1%RESET%
shift & goto :parse_args

:args_done

:: Display help
if "%HELP%"=="true" (
    echo.
    echo %APP_NAME% - Unified Startup Script
    echo.
    echo Usage: %~nx0 [options]
    echo.
    echo Options:
    echo   --skip-n8n      Skip N8N server startup
    echo   --skip-app      Skip React application startup
    echo   --skip-python   Skip Python dependencies setup
    echo   --clean         Clean install all dependencies
    echo   --headless      Don't auto-open browsers
    echo   --fix-cors      Fix CORS issues only, then exit
    echo   --help          Show this help message
    echo.
    echo Default behavior: Start all services with full setup
    echo.
    goto :end
)

:: Clear screen for clean start
cls
echo %INFO%========================================%RESET%
echo %INFO%Liquid Audio Agent - Unified Startup%RESET%
echo %INFO%========================================%RESET%
echo.

:: Check prerequisites
call :check_prerequisites
if errorlevel 1 goto :error

:: Handle CORS fix mode
if "%FIX_CORS%"=="true" (
    call :fix_cors_only
    goto :end
)

:: Clean install if requested
if "%CLEAN_INSTALL%"=="true" (
    call :clean_install
)

:: Install Node.js dependencies
call :install_node_dependencies
if errorlevel 1 goto :error

:: Setup Python environment and dependencies
if "%SKIP_PYTHON%"=="false" (
    goto :setup_python_environment
) else (
    goto :main_continue
)

:main_continue
:: Start N8N server
if "%SKIP_N8N%"=="false" (
    call :start_n8n_server
    if errorlevel 1 goto :error
)

:: Start React application
if "%SKIP_APP%"=="false" (
    call :start_react_app
    if errorlevel 1 goto :error
)

:: Show final status
call :show_startup_status

:: Wait for user input to stop services
if not "%HEADLESS%"=="true" (
    echo.
    echo %INFO%Press any key to stop all services...%RESET%
    pause >nul
    call :stop_services
) else (
    echo.
    echo %INFO%Services started in headless mode. Press Ctrl+C to stop.%RESET%
    if not "%SKIP_N8N%"=="false" if not "%SKIP_APP%"=="false" (
        pause
    )
)

goto :end

:: ========================================
:: Function Definitions
:: ========================================

:check_prerequisites
echo %INFO%Checking prerequisites...%RESET%

:: Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR%Node.js is not installed or not in PATH%RESET%
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)
echo - Node.js: OK

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %WARN%Python is not installed or not in PATH%RESET%
    echo Python is required for audio processing features.
    echo Please install Python 3.12+ from https://python.org/
    set SKIP_PYTHON=true
) else (
    echo - Python: OK
)

:: Check for .env.local file
if not exist ".env.local" (
    echo %WARN%Warning: .env.local file not found!%RESET%
    echo Please create .env.local with your API keys:
    echo   GEMINI_API_KEY=your_gemini_api_key_here
    echo.
    echo Press any key to continue anyway...
    pause >nul
) else (
    echo - Environment file: OK
)

:: Check if ports are available
netstat -an | findstr ":%N8N_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo %WARN%Port %N8N_PORT% is already in use%RESET%
    echo Will attempt to stop existing N8N processes...
    call :stop_n8n_processes
)

netstat -an | findstr ":%APP_PORT%" >nul 2>&1
if not errorlevel 1 (
    echo %WARN%Port %APP_PORT% is already in use%RESET%
    echo Please stop the process using port %APP_PORT%
)

echo %INFO%Prerequisites check completed.%RESET%
echo.
exit /b 0

:install_node_dependencies
echo %INFO%Installing Node.js dependencies...%RESET%

if not exist "node_modules" (
    echo Installing fresh dependencies...
    npm install
    if errorlevel 1 (
        echo %ERROR%Failed to install Node.js dependencies%RESET%
        exit /b 1
    )
) else (
    echo Node.js dependencies already installed.
)
echo.
exit /b 0

:setup_python_environment
echo %INFO%Setting up Python environment...%RESET%

:: Check if setup_automation.py exists
if not exist "setup_automation.py" (
    echo %WARN%setup_automation.py not found. Skipping Python setup.%RESET%
    goto :continue_after_python
)

:: Run Python setup
python setup_automation.py
if errorlevel 1 (
    echo %WARN%Python setup encountered issues, but continuing...%RESET%
    echo Audio features may not work without proper Python environment.
)
echo.

:continue_after_python
goto :main_continue

:start_n8n_server
echo %INFO%Starting N8N server with CORS configuration...%RESET%

:: Set CORS environment variables
set N8N_CORS_ALLOW_ORIGIN=*
set N8N_CORS_CREDENTIALS=true
set N8N_CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS,PATCH
set N8N_CORS_HEADERS=Content-Type,Authorization,X-Requested-With,n8n-api-key
set N8N_HOST=%N8N_HOST%
set N8N_PORT=%N8N_PORT%
set N8N_WEBHOOK_URL=%WEBHOOK_URL%
set GENERIC_TIMEZONE=America/New_York

:: Start N8N in background
if "%HEADLESS%"=="true" (
    start "N8N Server" /min cmd /c "npx n8n start"
) else (
    start "N8N Server" cmd /c "npx n8n start"
)

:: Wait for N8N to start
echo Waiting for N8N to initialize...
timeout /t %WAIT_TIME% /nobreak >nul

:: Check if N8N is running
curl -s http://localhost:%N8N_PORT% >nul 2>&1
if errorlevel 1 (
    echo %WARN%N8N may not be responding. Check for errors.%RESET%
) else (
    echo %INFO%N8N server started successfully%RESET%
)
echo.
exit /b 0

:start_react_app
echo %INFO%Starting React application...%RESET%

:: Start React app
if "%HEADLESS%"=="true" (
    start "Liquid Audio Agent" /min cmd /c "npm run dev"
) else (
    start "Liquid Audio Agent" cmd /c "npm run dev"
)

:: Wait a moment for React to start
timeout /t 3 /nobreak >nul

echo %INFO%React application started%RESET%
echo.
exit /b 0

:show_startup_status
echo %INFO%========================================%RESET%
echo %INFO%Startup Complete!%RESET%
echo %INFO%========================================%RESET%
echo.

if not "%SKIP_N8N%"=="true" (
    echo %INFO%Services Running:%RESET%
    echo • N8N Interface: http://localhost:%N8N_PORT%
    echo • N8N Webhooks: http://localhost:%N8N_PORT%/webhook
)

if not "%SKIP_APP%"=="true" (
    echo • Liquid Audio Agent: http://localhost:%APP_PORT%
)

echo.
echo %INFO%Features Available:%RESET%
if "%SKIP_PYTHON%"=="false" (
    echo • Voice processing with liquid-audio
    echo • Flash attention optimization
) else (
    echo • Basic voice simulation ^(Python disabled^)
)

echo • N8N workflow automation
echo • AI model integration
echo • Real-time chat interface

echo.
exit /b 0

:clean_install
echo %INFO%Performing clean install...%RESET%

:: Stop existing services
call :stop_services

:: Remove node_modules
if exist "node_modules" (
    echo Removing existing Node.js dependencies...
    rmdir /s /q node_modules
)

:: Remove package-lock.json
if exist "package-lock.json" (
    echo Removing package lock file...
    del package-lock.json
)

echo.
exit /b 0

:stop_services
echo %INFO%Stopping services...%RESET%

:: Stop Node.js processes
taskkill /f /im node.exe >nul 2>&1

:: Additional cleanup
timeout /t 2 /nobreak >nul
echo %INFO%Services stopped.%RESET%
echo.
exit /b 0

:stop_n8n_processes
echo Stopping existing N8N processes...
taskkill /f /im node.exe /fi "WINDOWTITLE eq N8N*" >nul 2>&1
timeout /t 2 /nobreak >nul
exit /b 0

:fix_cors_only
echo %INFO%Fixing CORS configuration...%RESET%

:: Stop existing N8N
call :stop_n8n_processes

:: Set comprehensive CORS variables
set N8N_CORS_ALLOW_ORIGIN=*
set N8N_CORS_CREDENTIALS=true
set N8N_CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS,PATCH
set N8N_CORS_HEADERS=Content-Type,Authorization,X-Requested-With,n8n-api-key,Accept,Origin,Cache-Control
set N8N_HOST=0.0.0.0
set N8N_PORT=%N8N_PORT%
set N8N_WEBHOOK_URL=%WEBHOOK_URL%

echo Starting N8N with comprehensive CORS settings...
start "N8N Server (CORS Fixed)" cmd /c "npx n8n start"

timeout /t %WAIT_TIME% /nobreak >nul

echo %INFO%CORS configuration applied!%RESET%
echo N8N Interface: http://localhost:%N8N_PORT%
echo.
echo %INFO%Test your connection in the browser.%RESET%
exit /b 0

:error
echo %ERROR%Startup encountered errors. Please check the messages above.%RESET%
echo.
pause
exit /b 1

:end
echo %INFO%Unified startup script completed.%RESET%
if not "%HEADLESS%"=="true" pause
exit /b 0