#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Fix CORS configuration for N8N to work with Liquid Audio Agent

.DESCRIPTION
    This script stops any existing N8N processes and restarts N8N with
    comprehensive CORS configuration to allow requests from the Liquid Audio Agent.

.PARAMETER SkipStop
    Skip stopping existing N8N processes

.PARAMETER Port
    N8N port to use (default: 5678)

.EXAMPLE
    .\fix-cors.ps1
    Restart N8N with CORS configuration on default port

.EXAMPLE
    .\fix-cors.ps1 -Port 5679
    Restart N8N with CORS configuration on port 5679

.EXAMPLE
    .\fix-cors.ps1 -SkipStop
    Start N8N with CORS configuration without stopping existing processes
#>

param(
    [switch]$SkipStop,
    [int]$Port = 5678
)

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🔧 Fixing CORS configuration for N8N..." -ForegroundColor Cyan
Write-Host ""

# Function to stop N8N processes
function Stop-N8NProcesses {
    Write-Host "[1/3] Stopping any existing N8N processes..." -ForegroundColor Yellow

    try {
        # Stop Node.js processes that might be running N8N
        $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
        $n8nStopped = $false

        foreach ($process in $nodeProcesses) {
            try {
                # Check if this node process is running n8n
                $processInfo = Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)" -ErrorAction SilentlyContinue
                if ($processInfo.CommandLine -and $processInfo.CommandLine -match "n8n") {
                    Write-Host "   Stopping N8N process (PID: $($process.Id))..." -ForegroundColor Gray
                    $process.Kill()
                    $n8nStopped = $true
                }
            } catch {
                # Continue if we can't check process details
            }
        }

        if ($n8nStopped) {
            Write-Host "   N8N processes stopped" -ForegroundColor Green
        } else {
            Write-Host "   No running N8N processes found" -ForegroundColor Gray
        }

        # Give processes time to stop
        Start-Sleep -Seconds 2
    }
    catch {
        Write-Warning "   Could not stop N8N processes: $($_.Exception.Message)"
    }
}

# Function to set CORS environment variables
function Set-CORSEnvironment {
    Write-Host "[2/3] Setting CORS environment variables..." -ForegroundColor Yellow

    $env:N8N_CORS_ORIGIN = "*"
    $env:N8N_CORS_ALLOW_ORIGIN = "*"
    $env:N8N_CORS_CREDENTIALS = "true"
    $env:N8N_CORS_METHODS = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    $env:N8N_CORS_HEADERS = "Content-Type,Authorization,X-Requested-With,Accept,Origin,User-Agent,DNT,Cache-Control,X-Mx-ReqToken,Keep-Alive,X-Requested-With,If-Modified-Since"

    # Additional N8N settings
    $env:N8N_HOST = "0.0.0.0"
    $env:N8N_PORT = $Port
    $env:N8N_WEBHOOK_URL = "http://localhost:$Port"
    $env:WEBHOOK_URL = "http://localhost:$Port"
    $env:GENERIC_TIMEZONE = "America/New_York"
    $env:N8N_BASIC_AUTH_ACTIVE = "false"
    $env:N8N_EDITOR_BASE_URL = "http://localhost:$Port"

    Write-Host "   Environment variables set:" -ForegroundColor Gray
    Write-Host "     N8N_CORS_ORIGIN=$env:N8N_CORS_ORIGIN" -ForegroundColor Gray
    Write-Host "     N8N_CORS_ALLOW_ORIGIN=$env:N8N_CORS_ALLOW_ORIGIN" -ForegroundColor Gray
    Write-Host "     N8N_CORS_CREDENTIALS=$env:N8N_CORS_CREDENTIALS" -ForegroundColor Gray
    Write-Host "     N8N_PORT=$env:N8N_PORT" -ForegroundColor Gray
}

# Function to start N8N
function Start-N8N {
    Write-Host "[3/3] Starting N8N with fixed CORS configuration..." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "🔒 CORS Configuration Summary:" -ForegroundColor Cyan
    Write-Host "   Origin: $env:N8N_CORS_ORIGIN" -ForegroundColor White
    Write-Host "   Allow Origin: $env:N8N_CORS_ALLOW_ORIGIN" -ForegroundColor White
    Write-Host "   Credentials: $env:N8N_CORS_CREDENTIALS" -ForegroundColor White
    Write-Host "   Methods: $env:N8N_CORS_METHODS" -ForegroundColor White
    Write-Host "   Headers: $env:N8N_CORS_HEADERS" -ForegroundColor White
    Write-Host ""

    Write-Host "🚀 Starting N8N..." -ForegroundColor Green
    Write-Host "   Web Interface: http://localhost:$Port" -ForegroundColor White
    Write-Host "   API Endpoint: http://localhost:$Port/api/v1" -ForegroundColor White
    Write-Host ""

    try {
        # Start N8N
        npx n8n start -o
    }
    catch {
        Write-Error "Failed to start N8N: $($_.Exception.Message)"
        Write-Host ""
        Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
        Write-Host "   1. Make sure Node.js and npm are installed" -ForegroundColor White
        Write-Host "   2. Make sure n8n is installed: npm install -g n8n" -ForegroundColor White
        Write-Host "   3. Check if port $Port is available" -ForegroundColor White
        Write-Host "   4. Run this script as Administrator if needed" -ForegroundColor White
        exit 1
    }
}

# Main execution
try {
    if (-not $SkipStop) {
        Stop-N8NProcesses
    }

    Set-CORSEnvironment
    Start-N8N
}
catch {
    Write-Error "Script failed: $($_.Exception.Message)"
    exit 1
}