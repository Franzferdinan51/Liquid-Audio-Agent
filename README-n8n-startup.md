# Startup Scripts for Liquid Audio Agent + n8n

This directory contains startup scripts for running both the Liquid Audio Agent application and n8n with CORS configuration enabled. The CORS setup allows the Liquid Audio Agent to make API requests to n8n from different origins.

## Available Scripts

### Simple Startup Scripts
**Basic startup for both services:**
- **`start-all.bat`** - Windows batch script (simple startup)
- **`start-all.sh`** - Unix shell script (simple startup)

**n8n only (with CORS):**
- **`start-n8n-cors.bat`** - Windows batch script for n8n only
- **`start-n8n-cors.sh`** - Unix shell script for n8n only

### Advanced Startup Scripts
**Flexible startup with options:**
- **`start-advanced.bat`** - Windows advanced script with command-line options
- **`start-advanced.sh`** - Unix advanced script with command-line options

## Usage

### Simple Startup
#### Windows
```bash
./start-all.bat
```

#### Linux/macOS
```bash
./start-all.sh
```

### Advanced Startup with Options
#### Windows
```bash
# Start both services
./start-advanced.bat

# Start only n8n
./start-advanced.bat --skip-app

# Start only the app
./start-advanced.bat --skip-n8n

# Clean install and start both
./start-advanced.bat --clean

# Start without opening browsers
./start-advanced.bat --headless

# Show all options
./start-advanced.bat --help
```

#### Linux/macOS
```bash
# Start both services
./start-advanced.sh

# Start only n8n
./start-advanced.sh --skip-app

# Start only the app
./start-advanced.sh --skip-n8n

# Clean install and start both
./start-advanced.sh --clean

# Start without opening browsers
./start-advanced.sh --headless

# Show all options
./start-advanced.sh --help
```

### n8n Only (with CORS)
#### Windows
```bash
./start-n8n-cors.bat
```

#### Linux/macOS
```bash
./start-n8n-cors.sh
```

### CORS Fix Scripts (Recommended for Connection Issues)
#### Windows
```bash
./fix-cors.bat
```

#### Linux/macOS
```bash
./fix-cors.sh
```

*Use these scripts if you encounter CORS connection errors. They stop existing processes and restart n8n with comprehensive CORS settings.*

## Configuration

The scripts configure n8n with the following CORS settings:

- **Allowed Origins**: http://localhost:3000, http://localhost:3001, http://127.0.0.1:3000, http://127.0.0.1:3001
- **Credentials**: Enabled (allows cookies and authentication headers)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS, PATCH
- **Headers**: Content-Type, Authorization, X-Requested-With

## Additional Settings

- **Host**: 0.0.0.0 (listens on all network interfaces)
- **Port**: 5678 (default n8n port)
- **Auto-open**: Automatically opens the n8n UI in browser
- **Webhook URL**: http://localhost:5678
- **Basic Auth**: Disabled (for development)

## Command-Line Options (Advanced Scripts)

| Option | Description |
|--------|-------------|
| `--skip-n8n` | Skip starting n8n server |
| `--skip-app` | Skip starting Liquid Audio Agent |
| `--headless` | Don't auto-open browser windows |
| `--clean` | Clean node_modules and reinstall dependencies |
| `--help` | Show help message and available options |

## Service URLs

When both services are running:
- **Liquid Audio Agent**: http://localhost:3000
- **n8n Web Interface**: http://localhost:5678
- **n8n Webhooks**: http://localhost:5678/webhook

## Integration with Liquid Audio Agent

The CORS configuration allows the Liquid Audio Agent (running on http://localhost:3000) to make API requests to n8n (running on http://localhost:5678) without being blocked by browser security policies. This enables:
- Workflow execution via the app's N8N integration
- Real-time webhook communication
- API calls between services

## Prerequisites

1. **Environment Variables**: Create `.env.local` with your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Required Software**:
   - Node.js (v16 or higher)
   - npm or yarn
   - n8n (installed globally or locally)

3. **Install Dependencies**:
   ```bash
   npm install
   ```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change the `N8N_PORT` environment variable in the scripts
   - Or kill existing processes: `taskkill /f /im node.exe` (Windows) or `pkill node` (Unix)

2. **CORS issues**:
   - Add your specific origin to the `N8N_CORS_ORIGIN` environment variable
   - Check browser console for specific CORS errors

3. **Permission denied** (Unix/macOS):
   ```bash
   chmod +x start-all.sh
   chmod +x start-advanced.sh
   chmod +x start-n8n-cors.sh
   ```

4. **Missing .env.local**:
   - Scripts will warn if `.env.local` is missing
   - Create the file with your `GEMINI_API_KEY`

5. **Dependency issues**:
   - Use `--clean` option to reinstall all dependencies
   - Or manually run: `rm -rf node_modules && npm install`

### Development Tips

- Use `--headless` mode for automated testing or CI/CD
- Use `--skip-n8n` when working only on the React app
- Use `--skip-app` when configuring n8n workflows
- Check the console output for service startup status