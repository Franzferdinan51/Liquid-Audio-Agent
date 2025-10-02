# CORS Configuration Guide for Liquid Audio Agent + N8N

## Problem Overview

When connecting the Liquid Audio Agent (React app on localhost:3000) to N8N (localhost:5678), browsers enforce CORS (Cross-Origin Resource Sharing) policies that block requests between different origins. This results in "CORS Policy Error" messages.

## Quick Solutions

### Solution 1: Use the Automated Fix Scripts (Recommended)

The project includes pre-configured scripts to fix CORS issues automatically:

**Windows:**
```cmd
fix-cors.bat
```

**Linux/Mac:**
```bash
chmod +x fix-cors.sh
./fix-cors.sh
```

### Solution 2: Manual N8N Restart with CORS

Stop any existing N8N processes and restart with CORS variables:

**Windows:**
```cmd
taskkill /f /im node.exe
set N8N_CORS_ALLOW_ORIGIN=*
set N8N_CORS_CREDENTIALS=true
npx n8n start -o
```

**Linux/Mac:**
```bash
pkill -f "n8n start"
export N8N_CORS_ALLOW_ORIGIN="*"
export N8N_CORS_CREDENTIALS=true
npx n8n start -o
```

## Understanding CORS Configuration

### Required Environment Variables

```bash
# Core CORS settings
N8N_CORS_ORIGIN=*                    # Allows requests from any origin
N8N_CORS_ALLOW_ORIGIN=*              # Alternative CORS setting
N8N_CORS_CREDENTIALS=true            # Allow credentials in CORS requests
N8N_CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS,PATCH  # Allowed HTTP methods
N8N_CORS_HEADERS=Content-Type,Authorization,X-Requested-With,Accept,Origin,User-Agent,DNT,Cache-Control,X-Mx-ReqToken,Keep-Alive,X-Requested-With,If-Modified-Since  # Allowed headers

# N8N server settings
N8N_HOST=0.0.0.0                     # Bind to all interfaces
N8N_PORT=5678                        # N8N port (default)
N8N_WEBHOOK_URL=http://localhost:5678
N8N_EDITOR_BASE_URL=http://localhost:5678
N8N_BASIC_AUTH_ACTIVE=false          # Disable basic auth for local development
```

### Why These Settings Are Needed

1. **N8N_CORS_ALLOW_ORIGIN=\***: Allows the React app (localhost:3000) to make requests to N8N (localhost:5678)
2. **N8N_CORS_CREDENTIALS=true**: Enables sending authorization headers (API keys) in cross-origin requests
3. **N8N_HOST=0.0.0.0**: Ensures N8N is accessible from different interfaces

## Development Proxy Configuration

The Vite development server is configured with a proxy to handle CORS in development:

```typescript
// vite.config.ts
proxy: {
  '/api/n8n': {
    target: 'http://localhost:5678',
    changeOrigin: true,
    secure: false,
    rewrite: (path) => path.replace(/^\/api\/n8n/, ''),
  }
}
```

This means:
- Requests to `/api/n8n/api/v1/workflows` are proxied to `http://localhost:5678/api/v1/workflows`
- The proxy handles CORS headers automatically
- Only works in development mode

## Common Error Scenarios and Solutions

### 1. "CORS Policy Error. Your browser blocked the request"

**Cause:** N8N is running without CORS configuration
**Solution:** Run the fix-cors script or restart N8N with CORS variables

### 2. "Failed to fetch" Network Error

**Cause:** Either CORS issue or N8N is not running
**Solution:**
1. Verify N8N is running: Open http://localhost:5678 in browser
2. Check CORS configuration
3. Verify correct N8N URL in settings

### 3. "401 Unauthorized" Error

**Cause:** Invalid or missing N8N API key
**Solution:**
1. Open N8N web interface (http://localhost:5678)
2. Go to Settings > API
3. Copy the API key
4. Paste it in the Liquid Audio Agent settings

### 4. "404 Not Found" Error

**Cause:** Incorrect N8N URL or N8N not properly started
**Solution:**
1. Verify N8N is running on correct port (default: 5678)
2. Check that URL format is correct: `http://localhost:5678`
3. Ensure N8N is fully started (wait for "n8n ready" message)

## Production Considerations

For production deployments, consider using more secure CORS settings:

```bash
# Instead of *, specify your specific domain
N8N_CORS_ALLOW_ORIGIN=https://your-app-domain.com
N8N_CORS_ORIGIN=https://your-app-domain.com

# Keep credentials enabled for API authentication
N8N_CORS_CREDENTIALS=true
```

## Alternative Solutions

### Option 1: N8N Configuration File

Create a `.env` file in your N8N directory:

```bash
# .env
N8N_CORS_ALLOW_ORIGIN=*
N8N_CORS_CREDENTIALS=true
N8N_HOST=0.0.0.0
N8N_PORT=5678
```

Then start N8N with: `npx n8n start -o`

### Option 2: Docker with CORS

If using Docker, add CORS environment variables:

```yaml
# docker-compose.yml
services:
  n8n:
    image: n8nio/n8n
    environment:
      - N8N_CORS_ALLOW_ORIGIN=*
      - N8N_CORS_CREDENTIALS=true
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
    ports:
      - "5678:5678"
```

## Testing the Configuration

1. **Start N8N with CORS configuration**
2. **Start the Liquid Audio Agent**: `npm run dev`
3. **Open the app**: http://localhost:3000
4. **Test N8N connection**:
   - Click Settings button
   - Enter N8N URL: `http://localhost:5678`
   - Enter your N8N API key
   - Click "Test & Fetch Workflows"
5. **Expected result**: Success message with list of workflows

## Troubleshooting Checklist

- [ ] N8N is running and accessible at http://localhost:5678
- [ ] CORS environment variables are set before starting N8N
- [ ] N8N API key is valid and copied correctly
- [ ] No other applications are using port 5678
- [ ] Browser cache is cleared (Ctrl+Shift+R or Cmd+Shift+R)
- [ ] No firewall blocking localhost connections
- [ ] Node.js processes are properly restarted after CORS changes

## Security Notes

- The `*` origin allows requests from any domain, which is fine for local development
- For production, specify exact domains instead of `*`
- Keep your N8N API key secure and never commit it to version control
- Consider using HTTPS in production environments