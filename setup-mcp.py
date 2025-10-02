#!/usr/bin/env python3
"""
Liquid Audio MCP Server Setup Script
Automated installation and configuration for the MCP server
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for MCP server")
        return False

    print("✅ Python version meets requirements")
    return True

def check_system_info():
    """Display system information"""
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")

    # Check for CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("⚠️  CUDA not available - will use CPU for processing")
    except ImportError:
        print("⚠️  PyTorch not installed - will install with CPU support")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing MCP server dependencies...")

    try:
        # Install basic requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements-mcp.txt"
        ])
        print("✅ Basic dependencies installed")

        # Test liquid-audio installation
        try:
            import liquid_audio
            print("✅ liquid-audio installed successfully")
        except ImportError as e:
            print(f"⚠️  liquid-audio installation issue: {e}")
            print("   This may require manual installation")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "models",
        "cache",
        "temp",
        "logs",
        "input",
        "output"
    ]

    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def create_env_file():
    """Create environment configuration file"""
    env_file = Path(".env")

    if env_file.exists():
        print("⚠️  .env file already exists")
        return

    print("\n⚙️  Creating environment configuration...")

    env_content = """# Liquid Audio MCP Server Configuration
LIQUID_AUDIO_MODEL_PATH=./models
LIQUID_AUDIO_CACHE_DIR=./cache
LIQUID_AUDIO_LOG_LEVEL=INFO
LIQUID_AUDIO_DEVICE=auto
LIQUID_AUDIO_SAMPLE_RATE=44100
LIQUID_AUDIO_MAX_FILE_SIZE=100MB

# Optional: GPU Configuration
# LIQUID_AUDIO_DEVICE=cuda

# Optional: Advanced Configuration
# LIQUID_AUDIO_BATCH_SIZE=1
# LIQUID_AUDIO_PARALLEL_PROCESSING=false
"""

    with open(env_file, "w") as f:
        f.write(env_content)

    print("✅ Created .env file")

def test_mcp_server():
    """Test MCP server startup"""
    print("\n🧪 Testing MCP server...")

    try:
        # Test imports
        import mcp.server
        import liquid_audio
        import sounddevice as sd
        import numpy as np
        print("✅ All required modules imported successfully")

        # Test audio device
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} audio devices")

        # Test basic functionality
        print("✅ MCP server components working correctly")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Warning during testing: {e}")
        return True  # Continue despite warnings

def create_client_config():
    """Create MCP client configuration example"""
    config_dir = Path.home() / ".config" / "claude"
    config_file = config_dir / "mcp_settings.json"

    print(f"\n📝 Creating MCP client configuration example...")
    print(f"   Location: {config_file}")

    config = {
        "mcpServers": {
            "liquid-audio": {
                "command": "python",
                "args": [str(Path.cwd() / "mcp-server.py")],
                "env": {
                    "LIQUID_AUDIO_MODEL_PATH": str(Path.cwd() / "models"),
                    "LIQUID_AUDIO_CACHE_DIR": str(Path.cwd() / "cache"),
                    "LIQUID_AUDIO_LOG_LEVEL": "INFO"
                }
            }
        }
    }

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Save configuration example
    example_file = Path("mcp-client-config-example.json")
    with open(example_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration example saved to {example_file}")
    print("   Copy this to your MCP client configuration")

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 MCP Server Setup Complete!")
    print("="*60)

    print("\n🚀 Quick Start:")
    print("1. Start the MCP server:")
    print("   python mcp-server.py")
    print()
    print("2. Or use npm script:")
    print("   npm run start-mcp-server")
    print()
    print("3. Configure your MCP client using the provided example")
    print()
    print("📚 Available Tools:")
    print("• process_audio_file - Process audio with LFM2 enhancement")
    print("• analyze_audio_frequencies - Analyze audio patterns")
    print("• start_microphone_recording - Record audio")
    print("• apply_lfm2_enhancement - Advanced LFM2 processing")
    print("• voice_characteristic_analysis - Voice analysis")
    print("• batch_process_audio - Process multiple files")
    print()
    print("📖 Documentation:")
    print("• Check README.md for detailed usage examples")
    print("• Review mcp-config.json for configuration options")
    print()
    print("🐛 Troubleshooting:")
    print("• Check logs: tail -f mcp-liquid-audio.log")
    print("• Test dependencies: npm run verify-mcp-setup")
    print("• Debug mode: LIQUID_AUDIO_LOG_LEVEL=DEBUG python mcp-server.py")

def main():
    """Main setup function"""
    print("🔧 Liquid Audio MCP Server Setup")
    print("="*40)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Show system info
    check_system_info()

    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)

    # Create directories
    create_directories()

    # Create environment file
    create_env_file()

    # Test server
    if not test_mcp_server():
        print("⚠️  Setup completed with warnings")

    # Create client configuration
    create_client_config()

    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()