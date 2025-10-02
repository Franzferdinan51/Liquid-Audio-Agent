# Liquid Audio Agent

A sophisticated React-based AI assistant application with advanced voice processing capabilities, integrating LFM2 (Local Frequency Matching 2) technology for enhanced audio analysis and processing.

## 🎵 Features

### Core Capabilities
- **🤖 AI-Powered Chat**: Multi-LLM support with Google Gemini integration
- **🎤 Voice Processing**: Real-time audio input with LFM2 enhancement
- **🔄 Workflow Automation**: N8N integration for complex workflows
- **🧠 Memory System**: Context persistence and intelligent responses
- **⚡ GPU Acceleration**: Flash attention optimization for performance

### LFM2 Integration
- **🎵 Advanced Audio Analysis**: Local Frequency Matching 2 for superior audio processing
- **🔊 Enhanced Voice Recognition**: Improved audio quality and accuracy
- **⚙️ Local Processing**: On-device audio processing with privacy focus
- **🎛️ Audio Enhancement**: Noise reduction and voice optimization

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.12+ (required for LFM2)
- **NVIDIA GPU** with CUDA Toolkit (recommended for flash-attn)

### One-Command Setup

```bash
# Windows (Recommended)
./startup.bat

# Linux/macOS
./startup.sh
```

This unified script handles:
- ✅ Dependency installation (Node.js + Python)
- ✅ LFM2 and liquid-audio setup
- ✅ N8N server with CORS configuration
- ✅ React application startup

### Manual Setup

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies with LFM2
npm run install-python-deps

# Start development server
npm run dev
```

## 🔧 Configuration

### Environment Variables
Create `.env.local` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
N8N_API_KEY=your_n8n_api_key_here
```

### LFM2 Setup

LFM2 (Local Frequency Matching 2) provides advanced audio processing capabilities:

```bash
# Install liquid-audio with LFM2 support
pip install liquid-audio

# Verify LFM2 installation
python -c "import liquid_audio; print('LFM2 loaded successfully')"
```

**LFM2 Requirements:**
- Python 3.12+
- CUDA-compatible GPU (optional but recommended)
- Compatible audio drivers

## 📁 Project Structure

```
liquid-audio-agent/
├── startup.bat                 # 🚀 Unified startup script
├── App.tsx                     # Main React application
├── components/                 # React components
│   ├── ChatWindow.tsx         # Chat interface with voice support
│   ├── SettingsModal.tsx      # Configuration and settings
│   └── ...                    # Other UI components
├── services/                   # Backend services
│   ├── geminiService.ts       # AI model integration
│   └── n8nService.ts          # Workflow automation
├── setup_automation.py        # Python environment setup
├── requirements.txt           # Python dependencies (LFM2)
└── scripts/                   # Utility scripts
    └── install-python-deps.js # Cross-platform installer
```

## 🎛️ Startup Options

The unified `startup.bat` script supports multiple options:

```bash
# Default: Start all services
./startup.bat

# Development options
./startup.bat --skip-n8n       # Skip N8N server
./startup.bat --skip-python    # Skip Python setup
./startup.bat --headless       # No auto-open browsers
./startup.bat --clean          # Clean install dependencies

# Troubleshooting
./startup.bat --fix-cors       # Fix N8N CORS issues only
./startup.bat --help           # Show all options
```

## 🔊 Audio Processing with LFM2

### LFM2 Features
- **Frequency Analysis**: Advanced local frequency matching
- **Voice Enhancement**: Noise reduction and clarity improvement
- **Real-time Processing**: Low-latency audio processing
- **GPU Acceleration**: CUDA-compatible processing

### Audio Pipeline
1. **Input Capture**: Microphone access via browser
2. **LFM2 Processing**: Local frequency analysis and enhancement
3. **AI Integration**: Enhanced audio sent to AI models
4. **Response Generation**: Context-aware responses
5. **Audio Output**: Optional voice synthesis

## 🔄 N8N Integration

### Workflow Automation
- **Real-time Execution**: Direct N8N workflow calls from the app
- **CORS Configuration**: Pre-configured for seamless integration
- **Function Calling**: AI-driven workflow execution
- **Webhook Support**: Real-time event processing

### N8N Setup
```bash
# Start N8N with CORS (handled by startup script)
export N8N_CORS_ALLOW_ORIGIN=*
npx n8n start
```

Access N8N at: http://localhost:5678

## 🛠 Development

### Scripts
```bash
npm run dev                    # Start development server
npm run build                  # Build for production
npm run install-python-deps   # Install Python dependencies
npm run verify-python-setup   # Verify Python environment
npm run setup-all              # Install all dependencies
npm run dev-full              # Full setup and start
```

### Python Environment
```bash
# Create virtual environment
python -m venv audio-env
source audio-env/bin/activate  # Linux/macOS
# or
audio-env\Scripts\activate     # Windows

# Install LFM2 dependencies
pip install -r requirements.txt
pip install liquid-audio       # LFM2 support
```

## 🧪 Testing

### Audio Features
```bash
# Test LFM2 installation
python -c "
import liquid_audio
import numpy as np
audio = np.random.randn(16000)  # 1 second at 16kHz
processed = liquid_audio.lfm2_process(audio)
print('LFM2 processing successful')
"

# Test microphone access
npm run test-audio
```

### N8N Integration
```bash
# Test CORS configuration
node test-cors-connection.js

# Validate setup
node validate-setup.js
```

## 🌐 Service URLs

When running locally:
- **Liquid Audio Agent**: http://localhost:3000
- **N8N Interface**: http://localhost:5678
- **N8N Webhooks**: http://localhost:5678/webhook

## 🔧 Troubleshooting

### Common Issues

#### LFM2 Installation
```bash
# Python version issue
python --version  # Must be 3.12+

# Install with specific version
pip install liquid-audio==1.0.0

# GPU support
pip install liquid-audio[cuda]
```

#### CORS Issues
```bash
# Fix N8N CORS
./startup.bat --fix-cors

# Manual CORS setup
export N8N_CORS_ALLOW_ORIGIN=*
export N8N_CORS_CREDENTIALS=true
```

#### Audio Problems
```bash
# Check microphone permissions
# Ensure browser has microphone access

# Test audio hardware
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## 📚 API Documentation

### LFM2 Audio Processing
```python
import liquid_audio
import numpy as np

# Process audio with LFM2
audio_data = np.random.randn(16000)  # 1 second audio
enhanced = liquid_audio.lfm2_enhance(audio_data)

# Frequency analysis
frequencies = liquid_audio.lfm2_analyze(audio_data)
```

### N8N Workflow Execution
```javascript
// Execute N8N workflow
const response = await fetch('http://localhost:5678/api/v1/workflows/execute', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${N8N_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    workflowData: { /* workflow data */ }
  })
});
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LFM2 Technology**: Advanced local frequency matching for audio processing
- **Liquid Audio**: Core audio processing library
- **N8N**: Workflow automation platform
- **Google Gemini**: AI model integration
- **React**: Frontend framework

## 📞 Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/Franzferdinan51/Liquid-Audio-Agent/issues)
- **Documentation**: Check the `/docs` folder for detailed guides
- **LFM2 Support**: Refer to liquid-audio documentation

---

**Built with ❤️ and LFM2 technology**
