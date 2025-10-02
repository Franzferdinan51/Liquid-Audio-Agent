#!/bin/bash

echo "Starting n8n with CORS enabled..."
echo ""

# Set CORS environment variables
export N8N_WEBHOOK_URL=http://localhost:5678
export N8N_HOST=0.0.0.0
export N8N_PORT=5678
export N8N_METRICS=true
export GENERIC_TIMEZONE=America/New_York
export WEBHOOK_URL=http://localhost:5678
export N8N_BASIC_AUTH_ACTIVE=false
export N8N_BASIC_AUTH_USER=""
export N8N_BASIC_AUTH_PASSWORD=""
export N8N_EDITOR_BASE_URL=http://localhost:5678

# Enable CORS settings
export N8N_CORS_ORIGIN="*"
export N8N_CORS_ALLOW_ORIGIN="*"
export N8N_CORS_CREDENTIALS=true
export N8N_CORS_METHODS="GET,POST,PUT,DELETE,OPTIONS,PATCH"
export N8N_CORS_HEADERS="Content-Type,Authorization,X-Requested-With"

echo "Configuration:"
echo "- Host: $N8N_HOST"
echo "- Port: $N8N_PORT"
echo "- CORS Origins: $N8N_CORS_ORIGIN"
echo "- CORS Credentials: $N8N_CORS_CREDENTIALS"
echo "- CORS Methods: $N8N_CORS_METHODS"
echo "- CORS Headers: $N8N_CORS_HEADERS"
echo ""

echo "Starting n8n..."
npx n8n start -o