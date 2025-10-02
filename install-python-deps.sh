#!/bin/bash
# Liquid Audio Agent Python Dependencies Installer
# This script installs the required Python packages for audio AI capabilities

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Liquid Audio Agent Python Dependencies Installer"
echo "========================================"
echo

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_status $RED "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.12+ from your system package manager or https://www.python.org/"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_status $BLUE "Current Python version: $PYTHON_VERSION"

# Extract major and minor version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Check Python version requirements
if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
    print_status $GREEN "[OK] Python version meets liquid-audio requirements"
elif [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -lt 12 ]; then
    print_status $YELLOW "[WARNING] Python version $PYTHON_VERSION is below recommended 3.12+"
    echo "liquid-audio may not work properly with this version"
    echo
    echo "Consider upgrading to Python 3.12+:"
    echo "  Ubuntu/Debian: sudo apt install python3.12 python3.12-venv python3.12-pip"
    echo "  macOS: brew install python@3.12"
    echo "  https://www.python.org/downloads/release/python-3120/"
    echo
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_status $RED "[ERROR] Python version $PYTHON_VERSION is too old"
    echo "Please install Python 3.12+"
    exit 1
fi

echo

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    print_status $RED "[ERROR] pip is not available"
    echo "Please install pip for Python 3"
    exit 1
fi

print_status $GREEN "[OK] pip is available"
echo

# Check for CUDA/NVIDIA GPU
echo "Checking GPU/CUDA capabilities..."
if command -v nvidia-smi &> /dev/null; then
    print_status $GREEN "[OK] NVIDIA GPU detected"
    nvidia-smi --query-gpu=name --format=csv,noheader,nounits

    # Check if CUDA toolkit is installed
    if command -v nvcc &> /dev/null; then
        print_status $GREEN "[OK] CUDA toolkit detected"
        CUDA_AVAILABLE=1
    else
        print_status $YELLOW "[WARNING] CUDA toolkit not found (nvcc missing)"
        echo "flash-attn may need to be compiled or may not work"
        echo "Consider installing CUDA toolkit: https://developer.nvidia.com/cuda-downloads"
        CUDA_AVAILABLE=0
    fi
else
    print_status $BLUE "[INFO] No NVIDIA GPU detected or nvidia-smi not available"
    echo "Will install CPU-only versions where possible"
    CUDA_AVAILABLE=0
fi

echo

# Create virtual environment (optional)
read -p "Create virtual environment? (recommended) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv audio-venv
    if [ $? -ne 0 ]; then
        print_status $RED "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "Activating virtual environment..."
    source audio-venv/bin/activate
    print_status $GREEN "[OK] Virtual environment created and activated"
fi

echo

# Upgrade pip first
echo "Upgrading pip..."
python3 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_status $YELLOW "[WARNING] Failed to upgrade pip, continuing anyway"
fi

echo

# Install core dependencies
echo "Installing core audio processing dependencies..."
echo

# Try liquid-audio first (may fail on older Python)
echo "Installing liquid-audio..."
pip3 install liquid-audio --no-build-isolation || {
    print_status $YELLOW "[WARNING] liquid-audio installation failed"
    echo "Trying alternative approaches..."

    pip3 install liquid-audio --pre --no-build-isolation || {
        print_status $YELLOW "[WARNING] liquid-audio --pre also failed"
        echo "Installing alternative audio libraries..."
        pip3 install librosa soundfile pydub
    }
} && print_status $GREEN "[OK] liquid-audio installed successfully"

echo

# Install flash-attn based on CUDA availability
if [ "$CUDA_AVAILABLE" -eq 1 ]; then
    echo "Installing flash-attn with CUDA support..."
    pip3 install flash-attn --no-build-isolation || {
        print_status $YELLOW "[WARNING] flash-attn installation failed"
        echo "Trying alternative approaches..."

        pip3 install flash-attn --find-links https://github.com/Dao-AILab/flash-attention/releases || {
            print_status $YELLOW "[WARNING] flash-attn from releases failed"
            echo "Installing xformers as alternative..."
            pip3 install xformers
        }
    } && print_status $GREEN "[OK] flash-attn installed successfully"
else
    print_status $BLUE "[INFO] Skipping flash-attn (CUDA not available)"
    echo "Installing CPU-only attention alternatives..."
    pip3 install xformers
fi

echo

# Install PyTorch with appropriate backend
echo "Installing PyTorch..."
if [ "$CUDA_AVAILABLE" -eq 1 ]; then
    echo "Installing PyTorch with CUDA support..."
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "Installing PyTorch CPU version..."
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

if [ $? -ne 0 ]; then
    print_status $YELLOW "[WARNING] PyTorch installation failed"
else
    print_status $GREEN "[OK] PyTorch installed successfully"
fi

echo

# Install additional dependencies from requirements.txt
echo "Installing additional dependencies from requirements.txt..."
pip3 install -r requirements.txt --no-deps || {
    print_status $YELLOW "[WARNING] Some dependencies from requirements.txt failed to install"
    echo "Installing critical packages individually..."

    # Install numpy and scipy (critical for audio processing)
    pip3 install numpy scipy
} && print_status $GREEN "[OK] All requirements.txt dependencies installed"

echo

# Verify installations
echo "Verifying installations..."
echo

# Check liquid-audio
python3 -c "import liquid_audio; print('liquid-audio version:', liquid_audio.__version__)" 2>/dev/null && \
    print_status $GREEN "[OK] liquid-audio is working" || \
    print_status $BLUE "[INFO] liquid-audio not available or not working"

# Check flash-attn
python3 -c "import flash_attn; print('flash-attn version:', flash_attn.__version__)" 2>/dev/null && \
    print_status $GREEN "[OK] flash-attn is working" || \
    print_status $BLUE "[INFO] flash-attn not available or not working"

# Check torch
python3 -c "import torch; print('PyTorch version:', torch.__version__, 'CUDA:', torch.cuda.is_available())" 2>/dev/null && {
    print_status $GREEN "[OK] PyTorch is working"
    python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"
} || \
    print_status $RED "[ERROR] PyTorch not working"

echo
echo "========================================"
echo "Installation completed!"
echo "========================================"
echo

if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    echo "Virtual environment created: audio-venv/"
    echo "To activate it manually: source audio-venv/bin/activate"
fi

echo
echo "Next steps:"
echo "1. Check the installation summary above"
echo "2. If any packages failed, review the error messages"
echo "3. Run the setup verification script: python3 setup_automation.py"
echo "4. Start the React application: npm run dev"
echo

# Make script executable if it's not already
chmod +x "$0" 2>/dev/null || true