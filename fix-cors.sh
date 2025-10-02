#!/bin/bash

echo "Fixing CORS configuration for n8n..."
echo ""

# Kill any existing n8n processes
echo "[1/3] Stopping any existing n8n processes..."
pkill -f "n8n start" > /dev/null 2>&1
sleep 2

# Set comprehensive CORS configuration
echo "[2/3] Setting CORS environment variables..."
export N8N_CORS_ORIGIN="*"
export N8N_CORS_ALLOW_ORIGIN="*"
export N8N_CORS_CREDENTIALS=true
export N8N_CORS_METHODS="GET,POST,PUT,DELETE,OPTIONS,PATCH"
export N8N_CORS_HEADERS="Content-Type,Authorization,X-Requested-With,Accept,Origin,User-Agent,DNT,Cache-Control,X-Mx-ReqToken,Keep-Alive,X-Requested-With,If-Modified-Since"

# Additional n8n settings
export N8N_HOST="0.0.0.0"
export N8N_PORT="5678"
export N8N_WEBHOOK_URL="http://localhost:5678"
export WEBHOOK_URL="http://localhost:5678"
export GENERIC_TIMEZONE="America/New_York"
export N8N_BASIC_AUTH_ACTIVE="false"
export N8N_EDITOR_BASE_URL="http://localhost:5678"

echo "[3/3] Starting n8n with fixed CORS configuration..."
echo ""
echo "CORS Configuration:"
echo "- Origin: $N8N_CORS_ORIGIN"
echo "- Allow Origin: $N8N_CORS_ALLOW_ORIGIN"
echo "- Credentials: $N8N_CORS_CREDENTIALS"
echo "- Methods: $N8N_CORS_METHODS"
echo "- Headers: $N8N_CORS_HEADERS"
echo ""

echo "Starting n8n..."
npx n8n start -o