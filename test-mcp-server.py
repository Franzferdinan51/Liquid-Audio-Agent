#!/usr/bin/env python3
"""
MCP Server Test Script
Test all MCP tools and functionality
"""

import asyncio
import json
import sys
import numpy as np
import soundfile as sf
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, '.')

try:
    from mcp_tools import MCPAudioTools, LFM2AdvancedTools
    from mcp_server import LiquidAudioMCPServer
    LIQUID_AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    LIQUID_AUDIO_AVAILABLE = False

class MCPTester:
    """Test suite for MCP server functionality"""

    def __init__(self):
        self.audio_tools = MCPAudioTools()
        self.lfm2_tools = LFM2AdvancedTools()
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"     {message}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })

    async def test_basic_functionality(self):
        """Test basic MCP functionality"""
        print("\n🧪 Testing Basic Functionality")
        print("-" * 40)

        # Test tool initialization
        try:
            tools = MCPAudioTools()
            self.log_test("Tool Initialization", True, "MCP tools initialized successfully")
        except Exception as e:
            self.log_test("Tool Initialization", False, str(e))

        # Test LFM2 tools (if available)
        if LIQUID_AUDIO_AVAILABLE:
            try:
                lfm2_tools = LFM2AdvancedTools()
                self.log_test("LFM2 Tools Initialization", True, "LFM2 tools available")
            except Exception as e:
                self.log_test("LFM2 Tools Initialization", False, str(e))
        else:
            self.log_test("LFM2 Availability", False, "liquid-audio not installed")

    async def test_audio_processing(self):
        """Test audio processing capabilities"""
        print("\n🎵 Testing Audio Processing")
        print("-" * 40)

        # Create test audio
        try:
            sample_rate = 44100
            duration = 1.0
            frequency = 440  # A4 note
            t = np.linspace(0, duration, int(sample_rate * duration))
            test_audio = 0.3 * np.sin(2 * np.pi * frequency * t)

            # Save test audio
            test_file = "test_audio.wav"
            sf.write(test_file, test_audio, sample_rate)

            self.log_test("Test Audio Creation", True, f"Created {test_file}")

            # Test audio validation
            is_valid, message, metadata = await self.audio_tools.validate_audio_file(test_file)
            self.log_test("Audio Validation", is_valid, message)

            # Test feature extraction
            features = await self.audio_tools.extract_audio_features(test_audio, sample_rate)
            self.log_test("Feature Extraction", len(features) > 0, f"Extracted {len(features)} feature types")

            # Test noise reduction
            noisy_audio = test_audio + 0.1 * np.random.randn(len(test_audio))
            enhanced_audio = await self.audio_tools.apply_noise_reduction(noisy_audio, sample_rate)
            self.log_test("Noise Reduction", len(enhanced_audio) > 0, "Noise reduction applied")

            # Test voice enhancement
            voice_enhanced = await self.audio_tools.apply_voice_enhancement(test_audio, sample_rate)
            self.log_test("Voice Enhancement", len(voice_enhanced) > 0, "Voice enhancement applied")

            # Cleanup
            Path(test_file).unlink(missing_ok=True)

        except Exception as e:
            self.log_test("Audio Processing Tests", False, str(e))

    async def test_lfm2_functionality(self):
        """Test LFM2-specific functionality"""
        if not LIQUID_AUDIO_AVAILABLE:
            print("\n🧬 Skipping LFM2 Tests (not available)")
            return

        print("\n🧬 Testing LFM2 Functionality")
        print("-" * 40)

        try:
            # Test LFM2 initialization
            success = await self.lfm2_tools.initialize_lfm2()
            self.log_test("LFM2 Model Loading", success, "LFM2 models loaded successfully" if success else "Failed to load models")

            if success:
                # Create test audio for LFM2
                sample_rate = 16000
                duration = 2.0
                test_audio = 0.3 * np.random.randn(int(sample_rate * duration))

                # Test voice characteristic extraction
                characteristics = await self.lfm2_tools.extract_voice_characteristics(test_audio, sample_rate)
                self.log_test("Voice Characteristic Extraction", len(characteristics) > 0, f"Extracted {len(characteristics)} characteristics")

                # Test speech enhancement
                enhanced = await self.lfm2_tools.enhance_speech_quality(test_audio, sample_rate)
                self.log_test("Speech Enhancement", len(enhanced) > 0, "Speech enhanced successfully")

                # Test audio embedding
                embedding = await self.lfm2_tools.generate_audio_embedding(test_audio, sample_rate)
                self.log_test("Audio Embedding", len(embedding) > 0, f"Generated {len(embedding)}-dimensional embedding")

        except Exception as e:
            self.log_test("LFM2 Tests", False, str(e))

    async def test_audio_utilities(self):
        """Test audio utility functions"""
        print("\n🔧 Testing Audio Utilities")
        print("-" * 40)

        try:
            # Test audio mixing
            audio1 = 0.3 * np.random.randn(1000)
            audio2 = 0.2 * np.random.randn(1200)
            mixed = await self.audio_tools.mix_audio(audio1, audio2)
            self.log_test("Audio Mixing", len(mixed) > 0, f"Mixed audio length: {len(mixed)}")

            # Test audio fading
            faded = await self.audio_tools.fade_audio(audio1, 0.1, 0.1)
            self.log_test("Audio Fading", len(faded) > 0, "Audio fade applied")

            # Test audio normalization
            normalized = await self.audio_tools.normalize_audio(audio1)
            self.log_test("Audio Normalization", len(normalized) > 0, "Audio normalized")

            # Test silence generation
            silence = await self.audio_tools.generate_silence(1.0)
            self.log_test("Silence Generation", len(silence) > 0, f"Generated {len(silence)} samples of silence")

            # Test resampling
            resampled = await self.audio_tools.resample_audio(audio1, 44100, 22050)
            self.log_test("Audio Resampling", len(resampled) > 0, f"Resampled from 44100 to 22050 Hz")

            # Test SNR calculation
            snr = await self.audio_tools.calculate_snr(audio1, 0.01 * np.random.randn(len(audio1)))
            self.log_test("SNR Calculation", True, f"SNR: {snr:.2f} dB")

            # Test voice activity detection
            vad_results = await self.audio_tools.detect_voice_activity(audio1, 44100)
            self.log_test("Voice Activity Detection", len(vad_results) > 0, f"Detected {len(vad_results)} frames")

        except Exception as e:
            self.log_test("Audio Utility Tests", False, str(e))

    async def test_server_initialization(self):
        """Test MCP server initialization"""
        print("\n🖥️  Testing Server Initialization")
        print("-" * 40)

        try:
            # Test server class instantiation
            server = LiquidAudioMCPServer()
            self.log_test("Server Class Instantiation", True, "MCP server class created")

            # Test tool registration (would require actual MCP client to fully test)
            if hasattr(server, 'server') and hasattr(server.server, 'list_tools'):
                self.log_test("Tool Registration", True, "Tools registered with MCP server")
            else:
                self.log_test("Tool Registration", False, "Tool registration method not found")

        except Exception as e:
            self.log_test("Server Initialization Tests", False, str(e))

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting MCP Server Test Suite")
        print("=" * 50)

        await self.test_basic_functionality()
        await self.test_audio_processing()
        await self.test_lfm2_functionality()
        await self.test_audio_utilities()
        await self.test_server_initialization()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)

        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['message']}")

        print(f"\n{'🎉 All tests passed!' if failed == 0 else '⚠️  Some tests failed - check installation'}")

async def main():
    """Main test function"""
    tester = MCPTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())