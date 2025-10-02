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

## 📦 Installation

### liquid-audio Official Installation

**Requirements:**
- Python 3.12+ (strict requirement)
- PyTorch and Torchaudio (automatically installed)

**Standard Installation:**
```bash
pip install liquid-audio
```

**Demo Installation (with additional dependencies):**
```bash
pip install "liquid-audio[demo]"
```

**GPU Acceleration (Optional):**
```bash
pip install flash-attn --no-build-isolation
```

**Verification:**
```bash
python -c "from liquid_audio import LFM2AudioProcessor; print('liquid-audio installed successfully')"
```

### Frontend Installation
```bash
# Clone and setup the React application
git clone <repository-url>
cd liquid-audio-agent
npm install
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.12+ (required for liquid-audio)
- **PyTorch** and **Torchaudio** (automatically installed with liquid-audio)
- **NVIDIA GPU** with CUDA Toolkit (recommended for flash-attn 2)

### One-Command Setup

```bash
# Windows (Recommended)
./startup.bat

# Linux/macOS
./startup.sh
```

This unified script handles:
- ✅ Dependency installation (Node.js + Python)
- ✅ liquid-audio and LFM2 setup
- ✅ N8N server with CORS configuration
- ✅ React application startup

### Manual Setup

```bash
# Install Node.js dependencies
npm install

# Install liquid-audio (official installation)
pip install liquid-audio

# Optional: Install demo dependencies for liquid-audio
pip install "liquid-audio[demo]"

# Optional: Install flash attention 2 for GPU acceleration
pip install flash-attn --no-build-isolation

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

### liquid-audio Setup

liquid-audio provides LFM2 (Local Frequency Matching 2) technology for advanced audio processing:

#### Standard Installation
```bash
# Basic installation
pip install liquid-audio

# Verify installation
python -c "import liquid_audio; print('liquid-audio loaded successfully')"
```

#### Demo Installation
```bash
# Installation with demo dependencies
pip install "liquid-audio[demo]"
```

#### GPU Acceleration (Optional)
```bash
# Install flash attention 2 for improved performance
pip install flash-attn --no-build-isolation
```

**liquid-audio Requirements:**
- Python 3.12+ (strict requirement)
- PyTorch 2.8.0+ (automatically installed)
- Torchaudio 2.8.0+ (automatically installed)
- CUDA-compatible GPU (optional but recommended for flash-attn 2)
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
├── requirements.txt           # Additional Python dependencies
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
# Create virtual environment (Python 3.12+ required)
python -m venv audio-env
source audio-env/bin/activate  # Linux/macOS
# or
audio-env\Scripts\activate     # Windows

# Install liquid-audio with official commands
pip install liquid-audio

# Optional: Install demo dependencies
pip install "liquid-audio[demo]"

# Optional: Install additional project dependencies
pip install -r requirements.txt

# Optional: Install flash attention 2 for GPU acceleration
pip install flash-attn --no-build-isolation
```

## 🧪 Testing

### Audio Features
```bash
# Test liquid-audio installation
python -c "
from liquid_audio import LFM2AudioProcessor
import numpy as np
print('liquid-audio loaded successfully')

# Test basic functionality (requires model download)
# processor = LFM2AudioProcessor.from_pretrained('LiquidAI/LFM2-Audio-1.5B')
# print('LFM2 processor initialized successfully')
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

#### liquid-audio Installation
```bash
# Python version issue
python --version  # Must be 3.12+

# If Python < 3.12, upgrade Python first:
# Windows: Download from python.org
# macOS: brew install python@3.12
# Ubuntu: sudo apt update && sudo apt install python3.12 python3.12-venv

# Clean installation
pip uninstall liquid-audio -y
pip install liquid-audio

# Install with demo dependencies
pip install "liquid-audio[demo]"

# Flash attention 2 issues
pip install flash-attn --no-build-isolation

# PyTorch compatibility (liquid-audio handles this automatically)
pip install torch>=2.8.0 torchaudio>=2.8.0
```

#### Python Version Compatibility
```bash
# Check Python version
python --version  # Must be 3.12+
python3 --version  # Alternative command

# On systems with multiple Python versions:
python3.12 --version
python3.12 -m pip install liquid-audio

# Create virtual environment with specific Python version
python3.12 -m venv audio-env
source audio-env/bin/activate  # Linux/macOS
audio-env\Scripts\activate     # Windows
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

## 🤖 MCP Server Integration

The Liquid Audio MCP Server provides comprehensive Model Context Protocol (MCP) integration, allowing AI models to directly access advanced LFM2 audio processing capabilities.

### MCP Server Features

#### 🔧 Audio Processing Tools
- **Process Audio Files**: Apply LFM2 enhancement with configurable parameters
- **Frequency Analysis**: Deep spectral and temporal analysis
- **Format Conversion**: Support for WAV, MP3, FLAC, OGG formats
- **Noise Reduction**: Advanced noise filtering and voice enhancement

#### 🎤 Real-time Audio Capabilities
- **Microphone Recording**: Live audio capture with configurable settings
- **Audio Level Monitoring**: Real-time level detection and voice activity
- **Streaming Processing**: Low-latency audio processing pipeline
- **Voice Activity Detection**: Intelligent speech detection

#### 🧬 LFM2 Specific Features
- **Local Frequency Matching**: Advanced frequency domain processing
- **Voice Characteristic Analysis**: Detailed voice profile extraction
- **Speech-to-Speech Conversion**: Voice transformation while preserving content
- **Quality Enhancement**: Multi-layered audio improvement

### 📦 MCP Server Installation

#### Prerequisites
- Python 3.8+ (recommended 3.12+ for liquid-audio)
- liquid-audio library installed
- MCP client compatible with Claude, GPT, or other AI models

#### Installation Steps

1. **Install Python Dependencies**
```bash
# Install required packages
pip install liquid-audio numpy soundfile sounddevice scipy mcp

# Optional: Install GPU acceleration
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Optional: Install flash attention for better performance
pip install flash-attn --no-build-isolation
```

2. **Verify Installation**
```bash
python -c "
import liquid_audio
import numpy as np
print('✅ liquid-audio installed successfully')

# Test MCP server imports
try:
    from mcp.server import Server
    print('✅ MCP server components available')
except ImportError:
    print('❌ MCP server components missing')
"
```

3. **Configure Environment Variables**
```bash
# Create .env file for MCP server
echo "LIQUID_AUDIO_MODEL_PATH=./models" >> .env
echo "LIQUID_AUDIO_CACHE_DIR=./cache" >> .env
echo "LIQUID_AUDIO_LOG_LEVEL=INFO" >> .env
```

### 🚀 Starting the MCP Server

#### Method 1: Direct Execution
```bash
# Start the MCP server
python mcp-server.py

# Or with specific configuration
LIQUID_AUDIO_LOG_LEVEL=DEBUG python mcp-server.py
```

#### Method 2: Using MCP Client Configuration
Add to your MCP client configuration (typically `~/.config/claude/mcp_settings.json` or similar):

```json
{
  "mcpServers": {
    "liquid-audio": {
      "command": "python",
      "args": ["mcp-server.py"],
      "env": {
        "LIQUID_AUDIO_MODEL_PATH": "./models",
        "LIQUID_AUDIO_CACHE_DIR": "./cache",
        "LIQUID_AUDIO_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Method 3: Docker Deployment
```bash
# Build Docker image
docker build -t liquid-audio-mcp .

# Run container
docker run -p 8080:8080 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/cache:/app/cache \
  liquid-audio-mcp
```

### 🛠 MCP Tools Usage

#### Audio Processing Tools

**Process Audio File**
```python
# AI model can call this tool
{
  "tool": "process_audio_file",
  "arguments": {
    "input_path": "./input/speech.wav",
    "output_path": "./output/enhanced_speech.wav",
    "enhancement_level": 1.2,
    "noise_reduction": True,
    "voice_enhancement": True
  }
}
```

**Analyze Audio Frequencies**
```python
{
  "tool": "analyze_audio_frequencies",
  "arguments": {
    "audio_path": "./input/audio.wav",
    "analysis_type": "all",  # spectral, temporal, mfcc, all
    "output_format": "json"
  }
}
```

**Convert Audio Format**
```python
{
  "tool": "convert_audio_format",
  "arguments": {
    "input_path": "./input/audio.wav",
    "output_path": "./output/audio.mp3",
    "target_format": "mp3",
    "sample_rate": 44100
  }
}
```

#### Real-time Audio Tools

**Start Microphone Recording**
```python
{
  "tool": "start_microphone_recording",
  "arguments": {
    "duration": 5.0,  # seconds, optional
    "sample_rate": 44100,
    "channels": 1
  }
}
```

**Stop Recording and Process**
```python
{
  "tool": "stop_microphone_recording",
  "arguments": {
    "output_path": "./output/recorded_audio.wav",
    "apply_lfm2": True
  }
}
```

**Monitor Audio Levels**
```python
{
  "tool": "monitor_audio_levels",
  "arguments": {
    "duration": 10.0,
    "threshold": 0.01
  }
}
```

#### LFM2 Advanced Tools

**Apply LFM2 Enhancement**
```python
{
  "tool": "apply_lfm2_enhancement",
  "arguments": {
    "audio_path": "./input/speech.wav",
    "output_path": "./output/lfm2_enhanced.wav",
    "model_name": "LiquidAI/LFM2-Audio-1.5B",
    "enhancement_strength": 1.0
  }
}
```

**Voice Characteristic Analysis**
```python
{
  "tool": "voice_characteristic_analysis",
  "arguments": {
    "audio_path": "./input/speech.wav",
    "analysis_depth": "comprehensive"  # basic, detailed, comprehensive
  }
}
```

**Speech-to-Speech Conversion**
```python
{
  "tool": "speech_to_speech_conversion",
  "arguments": {
    "input_path": "./input/source_voice.wav",
    "output_path": "./output/converted_voice.wav",
    "target_voice": "neutral",
    "preserve_content": True
  }
}
```

#### Model Management Tools

**Load LFM2 Model**
```python
{
  "tool": "load_lfm2_model",
  "arguments": {
    "model_name": "LiquidAI/LFM2-Audio-1.5B",
    "device": "auto",  # cpu, cuda, auto
    "precision": "float32"  # float32, float16, bfloat16
  }
}
```

**Batch Processing**
```python
{
  "tool": "batch_process_audio",
  "arguments": {
    "input_directory": "./input/",
    "output_directory": "./output/",
    "file_pattern": "*.wav",
    "processing_type": "lfm2"  # lfm2, enhancement, conversion, analysis
  }
}
```

### 🎯 Use Case Examples

#### Use Case 1: Voice Assistant Enhancement
```python
# AI Assistant workflow for voice enhancement
tools_used = [
    "start_microphone_recording",  # Capture user voice
    "stop_microphone_recording",   # Stop and save recording
    "process_audio_file",          # Apply noise reduction
    "voice_characteristic_analysis" # Analyze voice patterns
]

# Result: Enhanced audio with detailed analysis
```

#### Use Case 2: Audio Content Processing
```python
# Batch processing workflow for audio content
tools_used = [
    "load_lfm2_model",             # Initialize processing models
    "batch_process_audio",         # Process multiple files
    "analyze_audio_frequencies",   # Analyze processed audio
    "convert_audio_format"         # Convert to target format
]

# Result: Processed audio files with analysis reports
```

#### Use Case 3: Real-time Audio Monitoring
```python
# Real-time monitoring workflow
tools_used = [
    "monitor_audio_levels",        # Monitor audio levels
    "start_microphone_recording",  # Start recording on activity
    "apply_lfm2_enhancement",      # Enhance recorded audio
    "get_audio_info"              # Get detailed audio information
]

# Result: Real-time audio monitoring and enhancement
```

### 🔧 Configuration Options

#### Environment Variables
```bash
# Model Configuration
LIQUID_AUDIO_MODEL_PATH=./models          # Model storage directory
LIQUID_AUDIO_CACHE_DIR=./cache            # Processing cache directory
LIQUID_AUDIO_LOG_LEVEL=INFO               # Logging level

# Audio Processing
LIQUID_AUDIO_DEVICE=auto                  # Processing device (auto/cpu/cuda)
LIQUID_AUDIO_MAX_FILE_SIZE=100MB          # Maximum file size
LIQUID_AUDIO_SAMPLE_RATE=44100            # Default sample rate
```

#### Model Configuration
```json
{
  "model": {
    "default_model": "LiquidAI/LFM2-Audio-1.5B",
    "auto_load": true,
    "cache_models": true,
    "preferred_device": "auto"
  }
}
```

#### Audio Processing Settings
```json
{
  "audio": {
    "default_sample_rate": 44100,
    "default_channels": 1,
    "supported_formats": ["wav", "mp3", "flac", "ogg"],
    "max_file_size": "100MB"
  },
  "processing": {
    "default_enhancement_level": 1.0,
    "default_noise_reduction": true,
    "batch_size": 1
  }
}
```

### 🐛 Troubleshooting

#### Common Issues

**1. Model Loading Fails**
```bash
# Check internet connection and disk space
ping google.com
df -h ./models/

# Verify liquid-audio installation
python -c "import liquid_audio; print('OK')"

# Reinstall if necessary
pip uninstall liquid-audio -y
pip install liquid-audio
```

**2. Audio Device Access Issues**
```bash
# Check available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone access
python -c "
import sounddevice as sd
import numpy as np
def callback(indata, frames, time, status):
    print('Audio working:', status is None)
with sd.InputStream(callback=callback):
    sd.sleep(1000)
"
```

**3. Memory Issues**
```bash
# Check system resources
python -c "
import psutil
print(f'Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB')
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

#### Debug Mode
```bash
# Enable detailed logging
LIQUID_AUDIO_LOG_LEVEL=DEBUG python mcp-server.py

# Check log file
tail -f mcp-liquid-audio.log
```

### 📚 API Documentation

#### liquid-audio LFM2 Processing
```python
from liquid_audio import LFM2AudioProcessor, LFM2AudioModel
import numpy as np

# Initialize LFM2 processor and model
processor = LFM2AudioProcessor.from_pretrained("LiquidAI/LFM2-Audio-1.5B").eval()
model = LFM2AudioModel.from_pretrained("LiquidAI/LFM2-Audio-1.5B").eval()

# Process audio with LFM2
audio_data = np.random.randn(16000)  # 1 second audio at 16kHz
processed_audio = processor(audio_data)

# Generate audio response
audio_response = model.generate(audio_data)
```

#### MCP Server API
```javascript
// Example MCP tool call from AI model
const mcpResponse = await callMCPTool({
  server: "liquid-audio",
  tool: "process_audio_file",
  arguments: {
    input_path: "speech.wav",
    output_path: "enhanced_speech.wav",
    enhancement_level: 1.2
  }
});

console.log(mcpResponse.content);
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

- **liquid-audio**: LFM2 (Local Frequency Matching 2) technology for advanced audio processing
- **N8N**: Workflow automation platform
- **Google Gemini**: AI model integration
- **React**: Frontend framework
- **PyTorch**: Deep learning framework
- **Flash Attention**: Optimized attention mechanism for GPU acceleration

## 📞 Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/Franzferdinan51/Liquid-Audio-Agent/issues)
- **Documentation**: Check the `/docs` folder for detailed guides
- **liquid-audio Support**: Refer to official [liquid-audio documentation](https://github.com/Liquid4All/liquid-audio)
- **Liquid4All**: Visit [Liquid4All GitHub](https://github.com/Liquid4All) for liquid-audio updates

---

**Built with ❤️ and liquid-audio LFM2 technology**
