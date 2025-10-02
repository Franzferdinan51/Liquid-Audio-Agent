#!/usr/bin/env python3
"""
Liquid Audio Agent Setup Automation Script
This script helps verify and set up the required dependencies for liquid-audio.

Official liquid-audio installation requirements:
- Python >=3.12 (required)
- pip install liquid-audio
- pip install "liquid-audio[demo]" (optional demo dependencies)
- pip install flash-attn --no-build-isolation (optional, requires CUDA)

The script follows the official installation procedure from:
https://github.com/Liquid4All/liquid-audio
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
    """Check Python version requirements for liquid-audio."""
    print("=== Python Version Check (liquid-audio Requirement) ===")
    version = sys.version_info
    print(f"Current Python: {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 12):
        print("[OK] Python version meets liquid-audio requirements (>=3.12)")
        return True
    else:
        print("[FAIL] Python version does not meet liquid-audio requirements (requires >=3.12)")
        print(f"       Current: {version.major}.{version.minor}")
        print("       Required: 3.12 or higher")
        print("       liquid-audio requires Python >=3.12 - no fallback compatibility available")
        return False

def check_cuda():
    """Check CUDA installation and GPU availability."""
    print("\n=== CUDA and GPU Check ===")

    # Check nvidia-smi
    result = run_command("nvidia-smi")
    if result:
        print("[OK] NVIDIA drivers installed")
        print(result.stdout.split('\n')[2:5])  # Show GPU info
    else:
        print("[FAIL] NVIDIA drivers not found or not accessible")
        return False

    # Check nvcc
    result = run_command("nvcc --version")
    if result:
        print("[OK] CUDA toolkit installed")
        return True
    else:
        print("[FAIL] CUDA toolkit not installed (missing nvcc)")
        return False

def check_pytorch():
    """Check PyTorch installation and CUDA support."""
    print("\n=== PyTorch Check ===")
    try:
        import torch
        print(f"[OK] PyTorch installed: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        return True
    except ImportError:
        print("[FAIL] PyTorch not installed")
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
                print(f"[OK] {package} is installed")
                results[package] = True
            else:
                print(f"[FAIL] {package} is not installed")
                results[package] = False
        except Exception as e:
            print(f"[ERROR] Error checking {package}: {e}")
            results[package] = False

    return results

def install_packages(packages_to_install, install_demo=False):
    """Attempt to install specified packages."""
    print(f"\n=== Package Installation ===")

    for package in packages_to_install:
        print(f"\nAttempting to install {package}...")

        if package == "liquid-audio":
            # Use official liquid-audio installation commands
            if install_demo:
                commands = [
                    f'pip install "{package}[demo]"',
                    f"pip install {package}",
                    f'pip install "{package}[demo]" --user'
                ]
            else:
                commands = [
                    f"pip install {package}",
                    f"pip install {package} --user",
                    f"pip install {package} --upgrade"
                ]
        elif package == "flash-attn":
            # Use official flash-attn installation command
            commands = [
                f"pip install {package} --no-build-isolation",
                f"pip install {package} --no-build-isolation --user",
                f"pip install {package} --no-build-isolation --verbose"
            ]
        else:
            commands = [f"pip install {package}"]

        for cmd in commands:
            print(f"  Trying: {cmd}")
            result = run_command(cmd, check=False)
            if result and result.returncode == 0:
                print(f"[OK] Successfully installed {package} with: {cmd}")
                break
            else:
                print(f"[FAIL] Failed to install {package} with: {cmd}")
                if "--no-build-isolation" in cmd and result and result.stderr:
                    # Provide more helpful error messages for flash-attn
                    if "CUDA" in result.stderr or "nvcc" in result.stderr:
                        print("  Hint: Make sure CUDA toolkit is installed and nvcc is in PATH")
                    elif "gcc" in result.stderr or "g++" in result.stderr:
                        print("  Hint: Make sure you have a C++ compiler installed")
                elif package == "liquid-audio" and result and result.stderr:
                    if "Python" in result.stderr and "3.12" in result.stderr:
                        print("  Hint: liquid-audio requires Python >=3.12")

        # Verify installation
        result = run_command(f"pip show {package}", check=False)
        if result and result.returncode == 0:
            print(f"[OK] {package} installation verified")
            # Show version info
            version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
            if version_line:
                print(f"  Version: {version_line[0].split(':')[1].strip()}")
        else:
            print(f"[FAIL] {package} installation failed")

def suggest_alternatives():
    """Suggest alternative packages and solutions."""
    print("\n=== Alternative Solutions ===")

    alternatives = {
        "liquid-audio": [
            "Upgrade to Python 3.12+ (required - no alternatives available)",
            "Create a virtual environment with Python 3.12+: python -m venv venv --python=python3.12",
            "Use conda with Python 3.12+: conda create -n liquid-audio python=3.12",
            "Install from source (requires Python 3.12+): pip install git+https://github.com/Liquid4All/liquid-audio.git",
            "Alternative audio processing libraries: librosa, soundfile, pydub (different API)"
        ],
        "flash-attn": [
            "Install CUDA toolkit development environment (required for compilation)",
            "Ensure nvcc is in your PATH environment variable",
            "Install C++ compiler (gcc/g++ on Linux, MSVC on Windows)",
            "Use pre-built PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
            "Alternative attention libraries: xformers, efficient-attention",
            "Use Docker container with CUDA support: docker run --gpus all pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
            "Use CPU-only processing (slower but functional)"
        ]
    }

    for package, alts in alternatives.items():
        print(f"\n{package} alternatives:")
        for i, alt in enumerate(alts, 1):
            print(f"  {i}. {alt}")

    print(f"\n=== Official Installation Commands ===")
    print("liquid-audio (official):")
    print("  pip install liquid-audio")
    print("  pip install \"liquid-audio[demo]\"  # optional demo dependencies")
    print("flash-attn (official):")
    print("  pip install flash-attn --no-build-isolation  # optional")

def create_environment_file():
    """Create environment configuration file."""
    print("\n=== Creating Environment Configuration ===")

    env_content = """# Liquid Audio Agent Environment Configuration
# Copy this to .env or .env.local and update as needed

# Python Configuration (REQUIRED: >=3.12)
PYTHON_VERSION=3.12+
PYTHON_PATH=python3.12

# CUDA Configuration (for flash-attn compilation)
CUDA_HOME=C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.4
CUDA_VISIBLE_DEVICES=0
CUDA_VERSION=12.4

# PyTorch Configuration
TORCH_CUDA_ARCH_LIST="8.6"  # For RTX 3080, adjust for your GPU
PYTORCH_VERSION=2.8.0+

# liquid-audio Configuration
LIQUID_AUDIO_VERSION=latest
LIQUID_AUDIO_DEMO=false  # Set to true to install demo dependencies

# flash-attn Configuration (optional)
FLASH_ATTENTION_VERSION=latest
FLASH_ATTENTION_ENABLED=false  # Set to true to install flash-attn

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
VIRTUAL_ENV=false

# Official Installation Commands Reference:
# pip install liquid-audio
# pip install "liquid-audio[demo]"  # optional demo dependencies
# pip install flash-attn --no-build-isolation  # optional, requires CUDA
"""

    env_file = Path("liquid_audio_env.txt")
    with open(env_file, 'w') as f:
        f.write(env_content)

    print(f"[OK] Environment configuration created: {env_file}")
    print("  Review and customize for your setup")
    print("  Note: liquid-audio requires Python >=3.12")

def test_liquid_audio_integration():
    """Test liquid-audio integration functionality."""
    print("\n=== liquid-audio Integration Test ===")

    # Test liquid-audio import
    try:
        import liquid_audio
        print("[OK] liquid-audio package imported successfully")

        # Test basic functionality
        if hasattr(liquid_audio, 'version'):
            print(f"  Version: {liquid_audio.version}")

        # Check for demo components if available
        try:
            import fastrtc
            print("[OK] Demo dependencies (fastrtc) available")
            demo_available = True
        except ImportError:
            print("[INFO] Demo dependencies (fastrtc) not installed")
            demo_available = False

        return True, demo_available

    except ImportError as e:
        print(f"[FAIL] liquid-audio import failed: {e}")
        return False, False
    except Exception as e:
        print(f"[ERROR] liquid-audio test failed: {e}")
        return False, False

def main():
    """Main setup automation function."""
    import argparse

    parser = argparse.ArgumentParser(description='Liquid Audio Agent Setup Automation')
    parser.add_argument('--force', action='store_true',
                       help='Force installation check (bypass Python version requirement)')
    parser.add_argument('--no-demo', action='store_true',
                       help='Skip demo dependencies installation')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Automatically answer yes to all prompts')
    args = parser.parse_args()

    print("Liquid Audio Agent Setup Automation")
    print("===================================")

    # Check current environment
    python_ok = check_python_version()
    if not python_ok and not args.force:
        print("\n=== CRITICAL: Python Version Requirement ===")
        print("liquid-audio requires Python >=3.12")
        print("Please upgrade Python before continuing.")
        print("Use --force to bypass this check (not recommended)")
        return
    elif not python_ok and args.force:
        print("\n=== WARNING: Bypassing Python Version Requirement ===")
        print("Proceeding despite Python version mismatch...")
        print("liquid-audio installation will likely fail!")
        python_ok = True  # Allow script to continue for testing

    cuda_ok = check_cuda()
    pytorch_ok = check_pytorch()
    packages = check_packages()

    # Summary
    print("\n=== Setup Summary ===")
    print(f"Python 3.12+: {'[OK]' if python_ok else '[FAIL]'}")
    print(f"CUDA Toolkit: {'[OK]' if cuda_ok else '[FAIL]'}")
    print(f"PyTorch CUDA: {'[OK]' if pytorch_ok else '[FAIL]'}")
    print(f"liquid-audio: {'[OK]' if packages.get('liquid-audio', False) else '[FAIL]'}")
    print(f"flash-attn: {'[OK]' if packages.get('flash-attn', False) else '[FAIL]'}")

    # Determine what needs to be installed
    to_install = []
    for package, installed in packages.items():
        if not installed:
            to_install.append(package)

    if to_install:
        print(f"\n=== Installation Required ===")
        print(f"Packages to install: {', '.join(to_install)}")

        # Ask about demo installation if liquid-audio is needed
        install_demo = False
        if "liquid-audio" in to_install and not args.no_demo:
            if args.yes:
                install_demo = True
                print("[AUTO] Installing liquid-audio with demo dependencies")
            else:
                demo_response = input("Install liquid-audio with demo dependencies? (y/n): ").lower()
                install_demo = demo_response == 'y'

        if args.yes:
            print("[AUTO] Attempting automatic installation")
            install_packages(to_install, install_demo=install_demo)
        else:
            response = input("Attempt automatic installation? (y/n): ").lower()
            if response == 'y':
                install_packages(to_install, install_demo=install_demo)
            else:
                suggest_alternatives()
    else:
        print("[OK] All packages already installed")

    # Test liquid-audio integration
    liquid_audio_ok, demo_ok = test_liquid_audio_integration()

    # Create configuration files
    create_environment_file()

    # Final recommendations
    print("\n=== Next Steps ===")
    if not cuda_ok:
        print("1. Install CUDA toolkit for flash-attn compilation")
    if not pytorch_ok:
        print("2. Install PyTorch with CUDA support")
    if not liquid_audio_ok:
        print("3. Install liquid-audio package: pip install liquid-audio")
    if not demo_ok and liquid_audio_ok:
        print("4. For demo features: pip install 'liquid-audio[demo]'")

    print("5. Review the generated environment file: liquid_audio_env.txt")
    print("6. Test the installation with your liquid-audio application")

    print(f"\n=== liquid-audio Status ===")
    if liquid_audio_ok:
        print("[OK] liquid-audio is ready for use")
        if demo_ok:
            print("[OK] Demo dependencies are available")
        else:
            print("[INFO] Install demo dependencies for demo features: pip install 'liquid-audio[demo]'")
    else:
        print("[FAIL] liquid-audio not available - installation failed or incomplete")

if __name__ == "__main__":
    main()