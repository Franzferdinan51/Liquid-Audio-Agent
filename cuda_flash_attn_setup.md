# CUDA Toolkit and flash-attn Installation Guide

## Current Situation
- GPU: NVIDIA RTX 3080 (CUDA 13.0 capable)
- CUDA Drivers: Installed (581.29)
- CUDA Toolkit: NOT installed (missing nvcc)
- PyTorch: 2.2.0 CPU version

## Solution Options

### Option 1: Install CUDA Toolkit 12.x (Recommended for compatibility)
1. Download CUDA Toolkit 12.4 from NVIDIA: https://developer.nvidia.com/cuda-12-4-0-download-archive
2. Select Windows, x86_64, Version 12.4, exe (local)
3. Install with default settings (typically installs to C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4)
4. After installation, add to PATH:
   - C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin
   - C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\libnvvp

### Option 2: Install precompiled PyTorch with CUDA support
```bash
# Uninstall current PyTorch
pip uninstall torch torchvision torchaudio

# Install PyTorch with CUDA 12.1 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### After CUDA Setup
```bash
# Verify CUDA installation
nvcc --version

# Install flash-attn
pip install flash-attn --no-build-isolation

# Alternative: Try precompiled wheels if available
pip install flash-attn --find-links https://github.com/Dao-AILab/flash-attention/releases
```

### Option 3: Use Docker with CUDA support
1. Install Docker Desktop with WSL2 backend
2. Pull PyTorch CUDA image:
   ```bash
   docker pull pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel
   ```
3. Run container and install flash-attn inside

### Option 4: Use alternative attention libraries
If flash-attn installation fails:
```bash
# Try alternatives
pip install xformers
pip install efficient-attention
```

## Troubleshooting
- If nvcc not found, check CUDA_HOME environment variable
- Ensure CUDA toolkit version matches PyTorch CUDA version
- May need to install Visual Studio Build Tools for compilation
- Check torch.cuda.is_available() after CUDA PyTorch installation