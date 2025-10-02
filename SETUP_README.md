# Liquid Audio Agent Setup Automation

This script automates the setup and verification of liquid-audio installation according to the official requirements from https://github.com/Liquid4All/liquid-audio.

## Official Installation Requirements

- **Python >=3.12** (REQUIRED - no fallback compatibility)
- `pip install liquid-audio` (standard installation)
- `pip install "liquid-audio[demo]"` (optional demo dependencies)
- `pip install flash-attn --no-build-isolation` (optional, requires CUDA)

## Usage

```bash
# Standard interactive mode
python setup_automation.py

# Non-interactive mode with automatic answers
python setup_automation.py --yes

# Force bypass Python version check (for testing only)
python setup_automation.py --force

# Skip demo dependencies
python setup_automation.py --no-demo

# Combined flags
python setup_automation.py --force --yes --no-demo
```

## Features

### Environment Validation
- **Python Version Check**: Strictly enforces Python >=3.12 requirement
- **CUDA Detection**: Checks for NVIDIA drivers and CUDA toolkit
- **PyTorch Verification**: Validates PyTorch installation and CUDA support
- **Package Status**: Detects currently installed liquid-audio and flash-attn

### Installation Automation
- **Official Commands**: Uses the exact official installation commands
- **Demo Support**: Handles both standard and demo dependency installation
- **Error Handling**: Provides helpful error messages for common issues
- **Multiple Fallbacks**: Tries alternative installation approaches

### Special Features
- **flash-attn Support**: Properly handles `--no-build-isolation` flag
- **CUDA Error Detection**: Identifies CUDA/Compiler issues with helpful hints
- **Demo Dependency Check**: Verifies fastrtc availability for demo features
- **Environment Configuration**: Generates `liquid_audio_env.txt` with all settings

## Command Line Options

- `--force`: Bypass Python version requirement (not recommended)
- `--no-demo`: Skip demo dependencies installation
- `--yes, -y`: Automatically answer yes to all prompts

## Generated Files

The script creates `liquid_audio_env.txt` with comprehensive configuration including:
- Python requirements and paths
- CUDA configuration settings
- Package version preferences
- Official installation command references

## Error Handling

The script provides detailed error messages for common issues:
- **Python Version**: Clear requirement enforcement with no fallback
- **CUDA Issues**: Detects missing nvcc, CUDA toolkit, or compiler issues
- **Compilation Errors**: Specific hints for flash-attn build failures
- **Import Failures**: Tests actual package functionality after installation

## Exit Status

- **Success (0)**: All components properly installed and verified
- **Failure (1)**: Critical requirements not met or installation failed

## Testing

The script includes comprehensive testing logic:
- Package import verification
- Demo component detection
- Version information display
- Integration validation

## Notes

- This script follows the official liquid-audio installation procedure exactly
- Python 3.12+ is a hard requirement - no compatibility mode available
- flash-attn requires CUDA toolkit and C++ compiler
- Demo dependencies include fastrtc for real-time communication features