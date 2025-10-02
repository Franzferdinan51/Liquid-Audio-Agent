#!/usr/bin/env python3
"""
Liquid Audio Agent Setup Automation Script
This script helps verify and set up the required dependencies for the Liquid Audio Agent.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=check,
                              capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        return None

def check_python_version():
    """Check Python version requirements for LFM2."""
    print("=== Python Version Check (LFM2 Support) ===")
    version = sys.version_info
    print(f"Current Python: {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 12):
        print("[OK] Python version meets LFM2/liquid-audio requirements (>=3.12)")
        return True
    else:
        print("[WARN] Python version may not support latest liquid-audio LFM2 (requires >=3.12)")
        print("      Attempting installation with fallback compatibility...")
        return "compatible"

def check_cuda():
    """Check CUDA installation and GPU availability."""
    print("\n=== CUDA and GPU Check ===")

    # Check nvidia-smi
    result = run_command("nvidia-smi")
    if result:
        print("✓ NVIDIA drivers installed")
        print(result.stdout.split('\n')[2:5])  # Show GPU info
    else:
        print("✗ NVIDIA drivers not found or not accessible")
        return False

    # Check nvcc
    result = run_command("nvcc --version")
    if result:
        print("✓ CUDA toolkit installed")
        return True
    else:
        print("✗ CUDA toolkit not installed (missing nvcc)")
        return False

def check_pytorch():
    """Check PyTorch installation and CUDA support."""
    print("\n=== PyTorch Check ===")
    try:
        import torch
        print(f"✓ PyTorch installed: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        return True
    except ImportError:
        print("✗ PyTorch not installed")
        return False

def check_packages():
    """Check if target packages are installed."""
    print("\n=== Package Installation Check ===")

    packages = ["liquid-audio", "flash-attn"]
    results = {}

    for package in packages:
        try:
            result = run_command(f"pip show {package}", check=False)
            if result and result.returncode == 0:
                print(f"✓ {package} is installed")
                results[package] = True
            else:
                print(f"✗ {package} is not installed")
                results[package] = False
        except Exception as e:
            print(f"✗ Error checking {package}: {e}")
            results[package] = False

    return results

def install_packages(packages_to_install):
    """Attempt to install specified packages."""
    print(f"\n=== Package Installation ===")

    for package in packages_to_install:
        print(f"\nAttempting to install {package}...")

        if package == "liquid-audio":
            # Try different approaches for liquid-audio
            commands = [
                f"pip install {package}",
                f"pip install {package} --pre",
                f"pip install {package} --no-deps",
                f"pip install git+https://github.com/liquid-audio/liquid-audio-python.git"
            ]
        elif package == "flash-attn":
            # Try different approaches for flash-attn
            commands = [
                f"pip install {package} --no-build-isolation",
                f"pip install {package} --pre",
                f"pip install {package} --find-links https://github.com/Dao-AILab/flash-attention/releases",
                f"pip install xformers"  # Alternative
            ]
        else:
            commands = [f"pip install {package}"]

        for cmd in commands:
            result = run_command(cmd, check=False)
            if result and result.returncode == 0:
                print(f"✓ Successfully installed {package} with: {cmd}")
                break
            else:
                print(f"✗ Failed to install {package} with: {cmd}")

        # Verify installation
        result = run_command(f"pip show {package}", check=False)
        if result and result.returncode == 0:
            print(f"✓ {package} installation verified")
        else:
            print(f"✗ {package} installation failed")

def suggest_alternatives():
    """Suggest alternative packages and solutions."""
    print("\n=== Alternative Solutions ===")

    alternatives = {
        "liquid-audio": [
            "Wait for stable release and Python 3.11 support",
            "Use Python 3.12+ in a separate virtual environment",
            "Install from source: git clone https://github.com/liquid-audio/liquid-audio-python.git",
            "Consider alternative audio processing libraries: librosa, soundfile, pydub"
        ],
        "flash-attn": [
            "Install CUDA toolkit development environment",
            "Use pre-built PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
            "Alternative attention libraries: xformers, efficient-attention",
            "Use Docker container with CUDA support",
            "Use CPU-only alternatives (slower but functional)"
        ]
    }

    for package, alts in alternatives.items():
        print(f"\n{package} alternatives:")
        for i, alt in enumerate(alts, 1):
            print(f"  {i}. {alt}")

def create_environment_file():
    """Create environment configuration file."""
    print("\n=== Creating Environment Configuration ===")

    env_content = """# Liquid Audio Agent Environment Configuration
# Copy this to .env or .env.local and update as needed

# Python Configuration
PYTHON_VERSION=3.12+

# CUDA Configuration
CUDA_HOME=C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.4
CUDA_VISIBLE_DEVICES=0

# PyTorch Configuration
TORCH_CUDA_ARCH_LIST="8.6"  # For RTX 3080

# Package Configuration
LIQUID_AUDIO_VERSION=latest
FLASH_ATTENTION_VERSION=latest

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
"""

    env_file = Path("liquid_audio_env.txt")
    with open(env_file, 'w') as f:
        f.write(env_content)

    print(f"✓ Environment configuration created: {env_file}")
    print("  Review and customize for your setup")

def test_lfm2_integration():
    """Test LFM2 integration functionality."""
    print("\n=== LFM2 Integration Test ===")

    try:
        # Import and test LFM2 integration
        import sys
        import os
        sys.path.append(os.getcwd())

        from lfm2_integration import test_lfm2_functionality
        result = test_lfm2_functionality()

        print(f"LFM2 Available: {'✓' if result['lfm2_available'] else '✗'}")
        print(f"Processing Method: {result['processing_method']}")
        print(f"Test Status: {result['test_result']}")

        if result['lfm2_available']:
            print("[OK] LFM2 is fully functional")
        else:
            print("[FALLBACK] Using basic audio processing")
            print("       Upgrade to Python 3.12+ for LFM2 support")

        return result['lfm2_available']

    except Exception as e:
        print(f"[ERROR] LFM2 test failed: {e}")
        return False

def main():
    """Main setup automation function."""
    print("Liquid Audio Agent Setup Automation (LFM2 Enhanced)")
    print("==================================================")

    # Check current environment
    python_ok = check_python_version()
    cuda_ok = check_cuda()
    pytorch_ok = check_pytorch()
    packages = check_packages()

    # Summary
    print("\n=== Setup Summary ===")
    if python_ok is True:
        print(f"Python 3.12+: {'✓'}")
    elif python_ok == "compatible":
        print(f"Python 3.12+: {'⚠' } (compatible fallback mode)")
    else:
        print(f"Python 3.12+: {'✗'}")

    print(f"CUDA Toolkit: {'✓' if cuda_ok else '✗'}")
    print(f"PyTorch CUDA: {'✓' if pytorch_ok else '✗'}")
    print(f"liquid-audio: {'✓' if packages.get('liquid-audio', False) else '✗'}")
    print(f"flash-attn: {'✓' if packages.get('flash-attn', False) else '✗'}")

    # Determine what needs to be installed
    to_install = []
    for package, installed in packages.items():
        if not installed:
            to_install.append(package)

    if to_install:
        print(f"\n=== Installation Required ===")
        print(f"Packages to install: {', '.join(to_install)}")

        response = input("Attempt automatic installation? (y/n): ").lower()
        if response == 'y':
            install_packages(to_install)
        else:
            suggest_alternatives()
    else:
        print("✓ All packages already installed")

    # Test LFM2 integration
    lfm2_ok = test_lfm2_integration()

    # Create configuration files
    create_environment_file()

    # Final recommendations
    print("\n=== Next Steps ===")
    if not python_ok or python_ok == "compatible":
        print("1. Upgrade to Python 3.12+ for full LFM2 support")
    if not cuda_ok:
        print("2. Install CUDA toolkit for flash-attn compilation")
    if not pytorch_ok:
        print("3. Install PyTorch with CUDA support")
    if not lfm2_ok:
        print("4. Install liquid-audio package: pip install liquid-audio")

    print("5. Review the generated documentation files:")
    print("   - python_upgrade_instructions.md")
    print("   - cuda_flash_attn_setup.md")
    print("   - liquid_audio_env.txt")
    print("6. Follow the setup guides and retry installation")

    print(f"\n=== LFM2 Status ===")
    if lfm2_ok:
        print("✓ LFM2 is ready for advanced audio processing")
    else:
        print("⚠ LFM2 not available - using fallback audio processing")
        print("  Upgrade to Python 3.12+ for LFM2 features")

if __name__ == "__main__":
    main()