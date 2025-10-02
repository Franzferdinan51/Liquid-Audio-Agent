#!/usr/bin/env python3
"""
LFM2 (Local Frequency Matching 2) Integration Module
This module provides LFM2 functionality for the Liquid Audio Agent.
"""

import numpy as np
import warnings
from typing import Optional, Dict, Any

class LFM2Processor:
    """
    LFM2 Audio Processing Class
    Provides advanced local frequency matching capabilities for audio enhancement.
    """

    def __init__(self):
        self.lfm2_available = False
        self.liquid_audio = None
        self._init_lfm2()

    def _init_lfm2(self):
        """Initialize LFM2 processing capabilities."""
        try:
            import liquid_audio
            self.liquid_audio = liquid_audio
            self.lfm2_available = True
            print("[LFM2] Successfully loaded liquid-audio with LFM2 support")
        except ImportError as e:
            print(f"[LFM2] liquid-audio not available: {e}")
            print("[LFM2] Using fallback audio processing")
            self.lfm2_available = False

    def is_available(self) -> bool:
        """Check if LFM2 processing is available."""
        return self.lfm2_available

    def process_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Process audio data with LFM2 enhancement.

        Args:
            audio_data: Raw audio data as numpy array
            sample_rate: Audio sample rate (default: 16000)

        Returns:
            Dictionary containing processed audio and metadata
        """
        if self.lfm2_available:
            return self._process_with_lfm2(audio_data, sample_rate)
        else:
            return self._process_fallback(audio_data, sample_rate)

    def _process_with_lfm2(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Process audio using LFM2 from liquid-audio."""
        try:
            # LFM2 processing pipeline
            enhanced_audio = self.liquid_audio.lfm2_enhance(audio_data, sample_rate)

            # Frequency analysis
            frequencies = self.liquid_audio.lfm2_analyze(audio_data, sample_rate)

            # Noise reduction
            denoised = self.liquid_audio.lfm2_denoise(audio_data, sample_rate)

            return {
                "status": "success",
                "processed_audio": enhanced_audio,
                "denoised_audio": denoised,
                "frequency_analysis": frequencies,
                "sample_rate": sample_rate,
                "processing_method": "LFM2",
                "enhancement_applied": True
            }

        except Exception as e:
            print(f"[LFM2] Error processing audio: {e}")
            return self._process_fallback(audio_data, sample_rate)

    def _process_fallback(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Fallback audio processing when LFM2 is not available."""
        # Basic audio enhancement using numpy and scipy
        try:
            from scipy import signal
            from scipy.signal import butter, filtfilt

            # Normalize audio
            normalized = audio_data / np.max(np.abs(audio_data))

            # Apply basic noise reduction (high-pass filter)
            nyquist = sample_rate / 2
            low_cutoff = 80  # Remove frequencies below 80Hz
            b, a = butter(4, low_cutoff / nyquist, btype='high')
            filtered = filtfilt(b, a, normalized)

            # Basic frequency analysis using FFT
            frequencies = np.fft.fftfreq(len(filtered), 1/sample_rate)
            fft_values = np.fft.fft(filtered)

            return {
                "status": "success",
                "processed_audio": filtered,
                "denoised_audio": filtered,
                "frequency_analysis": {
                    "frequencies": frequencies[:len(frequencies)//2],
                    "magnitudes": np.abs(fft_values)[:len(fft_values)//2]
                },
                "sample_rate": sample_rate,
                "processing_method": "Fallback",
                "enhancement_applied": True,
                "lfm2_available": False
            }

        except ImportError:
            # Very basic processing if scipy is not available
            normalized = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data

            return {
                "status": "success",
                "processed_audio": normalized,
                "denoised_audio": normalized,
                "frequency_analysis": {"message": "Basic processing only"},
                "sample_rate": sample_rate,
                "processing_method": "Basic",
                "enhancement_applied": False,
                "lfm2_available": False
            }

    def get_audio_info(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Get detailed information about audio data."""
        return {
            "duration": len(audio_data) / 16000,  # Assuming 16kHz
            "sample_count": len(audio_data),
            "max_amplitude": np.max(np.abs(audio_data)),
            "rms": np.sqrt(np.mean(audio_data**2)),
            "dynamic_range": np.max(audio_data) - np.min(audio_data),
            "lfm2_available": self.lfm2_available
        }

# Global LFM2 processor instance
_lfm2_processor = None

def get_lfm2_processor() -> LFM2Processor:
    """Get the global LFM2 processor instance."""
    global _lfm2_processor
    if _lfm2_processor is None:
        _lfm2_processor = LFM2Processor()
    return _lfm2_processor

def process_voice_input(audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
    """
    Process voice input for AI interaction.

    Args:
        audio_data: Raw microphone input
        sample_rate: Audio sample rate

    Returns:
        Processed audio ready for AI model
    """
    processor = get_lfm2_processor()
    result = processor.process_audio(audio_data, sample_rate)

    # Add voice-specific processing metadata
    result.update({
        "voice_enhanced": True,
        "ready_for_ai": True,
        "timestamp": np.datetime64('now').astype(str)
    })

    return result

def test_lfm2_functionality():
    """Test LFM2 functionality and return status report."""
    processor = get_lfm2_processor()

    # Generate test audio (1 second of sine wave)
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_audio = np.sin(2 * np.pi * frequency * t)

    # Add some noise
    noise = np.random.normal(0, 0.1, len(test_audio))
    test_audio_noisy = test_audio + noise

    # Process the test audio
    result = processor.process_audio(test_audio_noisy, sample_rate)

    # Get audio info
    info = processor.get_audio_info(test_audio_noisy)

    return {
        "lfm2_available": processor.is_available(),
        "processing_method": result.get("processing_method"),
        "enhancement_applied": result.get("enhancement_applied", False),
        "audio_info": info,
        "test_result": "success" if result["status"] == "success" else "failed"
    }

if __name__ == "__main__":
    # Test LFM2 functionality when run directly
    print("=== LFM2 Integration Test ===")
    test_result = test_lfm2_functionality()

    print(f"LFM2 Available: {test_result['lfm2_available']}")
    print(f"Processing Method: {test_result['processing_method']}")
    print(f"Enhancement Applied: {test_result['enhancement_applied']}")
    print(f"Test Result: {test_result['test_result']}")
    print("\n=== Audio Info ===")
    for key, value in test_result['audio_info'].items():
        print(f"{key}: {value}")