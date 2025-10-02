# Python Dependencies Installation Guide

This guide covers the installation of Python dependencies required for the Liquid Audio Agent's audio processing capabilities.

## Overview

The Liquid Audio Agent requires the following Python packages:
- **liquid-audio**: Core audio processing library
- **flash-attn**: GPU-accelerated attention mechanism for faster processing
- **PyTorch**: Machine learning framework with CUDA support
- **Additional utilities**: Audio processing and development tools

## Prerequisites

### System Requirements
- **Python**: 3.12+ (required for liquid-audio)
- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **GPU**: NVIDIA GPU with CUDA support (recommended for flash-attn)
- **RAM**: 8GB+ minimum, 16GB+ recommended
- **Storage**: 10GB+ free space for dependencies

### Required Software
1. **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/)
2. **CUDA Toolkit**: For GPU acceleration (optional but recommended)
   - Download from [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
   - CUDA 12.x recommended for compatibility

### Platform-Specific Setup

#### Windows
1. Install Python 3.12+ from python.org
2. During installation, check "Add Python to PATH"
3. Install Visual Studio Build Tools (for compiling packages)
4. Install CUDA Toolkit if you have an NVIDIA GPU

#### macOS
1. Install Python 3.12+ with Homebrew:
   ```bash
   brew install python@3.12
   ```
2. Install Xcode Command Line Tools:
   ```bash
   xcode-select --install
   ```

#### Linux
1. Install Python 3.12+ using your package manager:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.12 python3.12-venv python3.12-pip

   # Fedora
   sudo dnf install python3.12 python3.12-pip
   ```
2. Install build tools:
   ```bash
   sudo apt install build-essential
   ```

## Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install all dependencies is using the automated installer:

#### Option A: Using npm scripts
```bash
# Install Node.js dependencies and Python dependencies
npm run setup-all

# Or install Python dependencies only
npm run install-python-deps

# Verify installation
npm run verify-python-setup

# Start development with full setup
npm run dev-full
```

#### Option B: Direct script execution
```bash
# On Windows
install-python-deps.bat

# On macOS/Linux
./install-python-deps.sh
```

#### Option C: Node.js wrapper (cross-platform)
```bash
node scripts/install-python-deps.js
```

### Method 2: Manual Installation

#### Step 1: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv audio-venv

# Activate virtual environment
# Windows
audio-venv\Scripts\activate.bat
# macOS/Linux
source audio-venv/bin/activate
```

#### Step 2: Upgrade pip
```bash
python -m pip install --upgrade pip
```

#### Step 3: Install Core Dependencies
```bash
# Install liquid-audio (may require Python 3.12+)
pip install liquid-audio --no-build-isolation

# Install PyTorch with CUDA support (if available)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install flash-attn (requires CUDA toolkit)
pip install flash-attn --no-build-isolation
```

#### Step 4: Install Additional Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt
```

### Method 3: Alternative Installations

If the main packages fail to install, try these alternatives:

#### liquid-audio Alternatives
```bash
# Try pre-release version
pip install liquid-audio --pre --no-build-isolation

# Install from source
pip install git+https://github.com/liquid-audio/liquid-audio-python.git

# Use alternative audio libraries
pip install librosa soundfile pydub
```

#### flash-attn Alternatives
```bash
# Try from releases
pip install flash-attn --find-links https://github.com/Dao-AILab/flash-attention/releases

# Use xformers as alternative
pip install xformers

# Use CPU-only PyTorch if CUDA issues
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
**Problem**: `liquid-audio requires Python >=3.12`
**Solution**:
- Install Python 3.12+ from python.org
- Use pyenv to manage multiple Python versions
- Create a separate virtual environment with Python 3.12+

#### 2. CUDA/GPU Issues
**Problem**: `flash-attn installation fails` or `nvcc not found`
**Solution**:
- Install CUDA Toolkit from NVIDIA website
- Set CUDA_HOME environment variable
- Use CPU-only alternatives if GPU not available

#### 3. Build Errors
**Problem**: `Microsoft Visual C++ 14.0 is required` (Windows)
**Solution**:
- Install Visual Studio Build Tools
- Or use pre-compiled wheels when available

#### 4. Permission Issues
**Problem**: `Permission denied` during installation
**Solution**:
- Use virtual environment instead of system Python
- Run Command Prompt as Administrator (Windows)
- Use `--user` flag with pip install

### Verification Steps

1. **Check Python version**:
   ```bash
   python --version
   ```

2. **Verify package installation**:
   ```bash
   pip list | grep -E "(liquid-audio|flash-attn|torch)"
   ```

3. **Test import**:
   ```python
   import torch
   print(f"PyTorch: {torch.__version__}")
   print(f"CUDA available: {torch.cuda.is_available()}")

   try:
       import liquid_audio
       print(f"liquid-audio: {liquid_audio.__version__}")
   except ImportError:
       print("liquid-audio not available")

   try:
       import flash_attn
       print(f"flash-attn: {flash_attn.__version__}")
   except ImportError:
       print("flash-attn not available")
   ```

4. **Run automated verification**:
   ```bash
   python setup_automation.py
   ```

## Environment Configuration

### Environment Variables
Create a `.env.local` file in the project root:

```bash
# Python Configuration
PYTHON_VERSION=3.12+

# CUDA Configuration (if applicable)
CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4
CUDA_VISIBLE_DEVICES=0

# PyTorch Configuration
TORCH_CUDA_ARCH_LIST="8.6"  # Adjust based on your GPU

# Package Configuration
LIQUID_AUDIO_VERSION=latest
FLASH_ATTENTION_VERSION=latest
```

### Virtual Environment
For consistent development, always use a virtual environment:

```bash
# Create
python -m venv audio-venv

# Activate
# Windows
audio-venv\Scripts\activate.bat
# macOS/Linux
source audio-venv/bin/activate

# Deactivate when done
deactivate
```

## Performance Optimization

### GPU Acceleration
1. Ensure NVIDIA drivers are up to date
2. Install matching CUDA toolkit version
3. Use GPU-optimized PyTorch builds
4. Configure `TORCH_CUDA_ARCH_LIST` for your GPU architecture

### Memory Management
1. Use virtual environments to isolate dependencies
2. Monitor GPU memory usage during training
3. Adjust batch sizes based on available GPU memory
4. Use mixed precision training when possible

## Next Steps

After successful installation:

1. **Verify setup**: Run `npm run verify-python-setup`
2. **Start development**: Run `npm run dev`
3. **Test audio features**: Check the chat interface for voice capabilities
4. **Monitor performance**: Use the application's built-in monitoring tools

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the setup automation output
3. Examine the specific error messages
4. Consider using alternative packages if main ones fail
5. Check the project's GitHub repository for known issues

## File Structure

After installation, you'll have these new files:
- `requirements.txt` - Python dependencies list
- `install-python-deps.bat` - Windows installer
- `install-python-deps.sh` - Unix/Linux installer
- `scripts/install-python-deps.js` - Node.js wrapper
- `audio-venv/` - Virtual environment (if created)
- `.env.local` - Environment configuration (if created)