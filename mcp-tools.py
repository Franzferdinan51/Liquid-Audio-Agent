#!/usr/bin/env python3
"""
MCP Tools for Liquid Audio Integration
Advanced tool definitions and implementations for audio processing
"""

import asyncio
import json
import logging
import os
import tempfile
import wave
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import soundfile as sf
import sounddevice as sd

try:
    from liquid_audio import LFM2AudioProcessor, LFM2AudioModel
    LIQUID_AUDIO_AVAILABLE = True
except ImportError:
    LIQUID_AUDIO_AVAILABLE = False

logger = logging.getLogger("mcp-liquid-audio-tools")

class AudioProcessingError(Exception):
    """Custom exception for audio processing errors"""
    pass

class MCPAudioTools:
    """Collection of MCP tools for liquid-audio integration"""

    def __init__(self):
        self.processor = None
        self.model = None
        self._temp_files = []

    def __del__(self):
        """Cleanup temporary files"""
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")
        self._temp_files.clear()

    def create_temp_file(self, suffix: str = ".wav") -> str:
        """Create a temporary file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        self._temp_files.append(temp_file.name)
        return temp_file.name

    async def validate_audio_file(self, audio_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate audio file and return metadata"""
        try:
            path = Path(audio_path)
            if not path.exists():
                return False, f"File does not exist: {audio_path}", {}

            if not path.is_file():
                return False, f"Path is not a file: {audio_path}", {}

            # Try to load audio file
            audio_data, sample_rate = sf.read(audio_path)

            metadata = {
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "channels": audio_data.shape[1] if len(audio_data.shape) > 1 else 1,
                "samples": len(audio_data),
                "data_type": str(audio_data.dtype),
                "file_size": path.stat().st_size
            }

            return True, "Valid audio file", metadata

        except Exception as e:
            return False, f"Invalid audio file: {str(e)}", {}

    async def apply_noise_reduction(self, audio_data: np.ndarray,
                                  sample_rate: int,
                                  noise_reduction_level: float = 0.5) -> np.ndarray:
        """Apply noise reduction to audio data"""
        try:
            # Simple spectral subtraction for noise reduction
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Estimate noise from first few frames
            noise_frames = audio_data[:, :int(0.1 * sample_rate)]
            noise_spectrum = np.mean(np.abs(np.fft.fft(noise_frames)), axis=1, keepdims=True)

            # Apply spectral subtraction
            audio_spectrum = np.fft.fft(audio_data)
            magnitude = np.abs(audio_spectrum)
            phase = np.angle(audio_spectrum)

            # Subtract noise spectrum
            enhanced_magnitude = magnitude - noise_reduction_level * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)

            # Reconstruct audio
            enhanced_spectrum = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = np.real(np.fft.ifft(enhanced_spectrum))

            return enhanced_audio[0] if enhanced_audio.shape[0] == 1 else enhanced_audio

        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            return audio_data

    async def apply_voice_enhancement(self, audio_data: np.ndarray,
                                    sample_rate: int,
                                    enhancement_level: float = 1.2) -> np.ndarray:
        """Apply voice enhancement to audio data"""
        try:
            # Apply spectral emphasis for voice enhancement
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Create emphasis filter (high-pass to enhance speech)
            pre_emphasis = 0.97
            emphasized_audio = np.append(audio_data[0, 0], audio_data[0, 1:] - pre_emphasis * audio_data[0, :-1])

            # Apply gain
            enhanced_audio = emphasized_audio * enhancement_level

            # Normalize to prevent clipping
            enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio)) * 0.95

            return enhanced_audio

        except Exception as e:
            logger.error(f"Voice enhancement failed: {str(e)}")
            return audio_data

    async def extract_audio_features(self, audio_data: np.ndarray,
                                   sample_rate: int,
                                   feature_types: List[str] = None) -> Dict[str, Any]:
        """Extract various audio features"""
        try:
            if feature_types is None:
                feature_types = ["spectral", "temporal", "prosodic"]

            features = {}

            # Normalize audio
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)
            audio_data = audio_data / np.max(np.abs(audio_data))

            if "spectral" in feature_types:
                # Spectral features
                fft = np.fft.fft(audio_data[0])
                frequencies = np.fft.fftfreq(len(fft), 1/sample_rate)
                magnitude = np.abs(fft[:len(fft)//2])

                # Spectral centroid
                spectral_centroid = np.sum(frequencies[:len(frequencies)//2] * magnitude) / np.sum(magnitude)

                # Spectral bandwidth
                spectral_bandwidth = np.sqrt(np.sum(((frequencies[:len(frequencies)//2] - spectral_centroid)**2) * magnitude) / np.sum(magnitude))

                # Spectral rolloff
                cumsum = np.cumsum(magnitude)
                rolloff_point = 0.85 * cumsum[-1]
                rolloff_idx = np.where(cumsum >= rolloff_point)[0]
                spectral_rolloff = frequencies[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0

                features["spectral"] = {
                    "centroid": float(spectral_centroid),
                    "bandwidth": float(spectral_bandwidth),
                    "rolloff": float(spectral_rolloff),
                    "flux": float(np.sum(np.diff(magnitude)**2))
                }

            if "temporal" in feature_types:
                # Temporal features
                rms_energy = np.sqrt(np.mean(audio_data**2))
                zero_crossing_rate = np.sum(np.diff(np.sign(audio_data[0])) != 0) / len(audio_data[0])

                features["temporal"] = {
                    "rms_energy": float(rms_energy),
                    "zero_crossing_rate": float(zero_crossing_rate),
                    "peak_amplitude": float(np.max(np.abs(audio_data[0]))),
                    "dynamic_range": float(np.max(audio_data[0]) - np.min(audio_data[0]))
                }

            if "prosodic" in feature_types:
                # Prosodic features (pitch-related)
                fundamental_freq = self._estimate_pitch(audio_data[0], sample_rate)

                features["prosodic"] = {
                    "fundamental_frequency": float(fundamental_freq),
                    "pitch_range": float(0.0)  # Would need more sophisticated analysis
                }

            return features

        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return {}

    def _estimate_pitch(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Estimate fundamental frequency using autocorrelation"""
        try:
            # Autocorrelation
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[len(autocorr)//2:]

            # Find first peak after zero lag
            min_period = int(sample_rate / 800)  # 800 Hz max
            max_period = int(sample_rate / 80)   # 80 Hz min

            if len(autocorr) > max_period:
                # Find peak in valid range
                peak_idx = np.argmax(autocorr[min_period:max_period]) + min_period

                if peak_idx > 0:
                    return sample_rate / peak_idx

            return 0.0

        except Exception as e:
            logger.error(f"Pitch estimation failed: {str(e)}")
            return 0.0

    async def resample_audio(self, audio_data: np.ndarray,
                           original_sample_rate: int,
                           target_sample_rate: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        try:
            if original_sample_rate == target_sample_rate:
                return audio_data

            # Simple linear interpolation resampling
            duration = len(audio_data) / original_sample_rate
            target_length = int(duration * target_sample_rate)

            # Use numpy's interpolation
            original_indices = np.arange(len(audio_data))
            target_indices = np.linspace(0, len(audio_data) - 1, target_length)

            if audio_data.ndim == 1:
                resampled_audio = np.interp(target_indices, original_indices, audio_data)
            else:
                resampled_audio = np.zeros((audio_data.shape[0], target_length))
                for ch in range(audio_data.shape[0]):
                    resampled_audio[ch] = np.interp(target_indices, original_indices, audio_data[ch])

            return resampled_audio

        except Exception as e:
            logger.error(f"Resampling failed: {str(e)}")
            return audio_data

    async def calculate_snr(self, signal: np.ndarray, noise: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio"""
        try:
            signal_power = np.mean(signal**2)
            noise_power = np.mean(noise**2)

            if noise_power == 0:
                return float('inf')

            snr_db = 10 * np.log10(signal_power / noise_power)
            return float(snr_db)

        except Exception as e:
            logger.error(f"SNR calculation failed: {str(e)}")
            return 0.0

    async def detect_voice_activity(self, audio_data: np.ndarray,
                                  sample_rate: int,
                                  threshold: float = 0.01) -> List[Dict[str, Any]]:
        """Detect voice activity in audio"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Frame-based voice activity detection
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            frame_overlap = int(0.010 * sample_rate)  # 10ms overlap

            voice_activity = []
            frame_start = 0

            while frame_start + frame_length <= len(audio_data[0]):
                frame = audio_data[0, frame_start:frame_start + frame_length]

                # Calculate frame energy
                frame_energy = np.sqrt(np.mean(frame**2))
                is_speech = frame_energy > threshold

                voice_activity.append({
                    "start_time": frame_start / sample_rate,
                    "end_time": (frame_start + frame_length) / sample_rate,
                    "energy": float(frame_energy),
                    "is_speech": is_speech
                })

                frame_start += (frame_length - frame_overlap)

            return voice_activity

        except Exception as e:
            logger.error(f"Voice activity detection failed: {str(e)}")
            return []

    async def apply_equalizer(self, audio_data: np.ndarray,
                            sample_rate: int,
                            bands: Dict[str, Tuple[float, float, float]]) -> np.ndarray:
        """Apply equalizer with specified frequency bands"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Apply FFT
            fft_data = np.fft.fft(audio_data[0])
            frequencies = np.fft.fftfreq(len(fft_data), 1/sample_rate)

            # Create frequency response
            freq_response = np.ones_like(frequencies)

            for band_name, (freq_min, freq_max, gain_db) in bands.items():
                gain_linear = 10**(gain_db / 20)

                # Find frequency indices
                band_indices = np.where((np.abs(frequencies) >= freq_min) &
                                      (np.abs(frequencies) <= freq_max))[0]

                # Apply gain
                freq_response[band_indices] *= gain_linear

            # Apply frequency response
            processed_fft = fft_data * freq_response
            processed_audio = np.real(np.fft.ifft(processed_fft))

            return processed_audio.reshape(1, -1)

        except Exception as e:
            logger.error(f"Equalizer application failed: {str(e)}")
            return audio_data

    async def compress_dynamic_range(self, audio_data: np.ndarray,
                                   threshold: float = 0.7,
                                   ratio: float = 4.0,
                                   attack_time: float = 0.003,
                                   release_time: float = 0.1) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Simple compression implementation
            compressed_audio = audio_data.copy()

            # Calculate envelope
            envelope = np.abs(audio_data[0])

            # Apply compression
            for i in range(1, len(envelope)):
                if envelope[i] > threshold:
                    # Apply compression ratio
                    excess = envelope[i] - threshold
                    compressed_excess = excess / ratio
                    envelope[i] = threshold + compressed_excess

            # Apply envelope to audio
            gain = envelope / (np.abs(audio_data[0]) + 1e-8)
            compressed_audio[0] = audio_data[0] * gain

            return compressed_audio

        except Exception as e:
            logger.error(f"Dynamic range compression failed: {str(e)}")
            return audio_data

    async def generate_silence(self, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Generate silence of specified duration"""
        try:
            num_samples = int(duration * sample_rate)
            silence = np.zeros(num_samples, dtype=np.float32)
            return silence

        except Exception as e:
            logger.error(f"Silence generation failed: {str(e)}")
            return np.array([])

    async def mix_audio(self, audio1: np.ndarray, audio2: np.ndarray,
                       gain1: float = 1.0, gain2: float = 1.0) -> np.ndarray:
        """Mix two audio signals with specified gains"""
        try:
            # Ensure same length
            max_length = max(len(audio1), len(audio2))

            if len(audio1) < max_length:
                audio1 = np.pad(audio1, (0, max_length - len(audio1)), 'constant')
            if len(audio2) < max_length:
                audio2 = np.pad(audio2, (0, max_length - len(audio2)), 'constant')

            # Apply gains and mix
            mixed_audio = gain1 * audio1 + gain2 * audio2

            # Normalize to prevent clipping
            max_amplitude = np.max(np.abs(mixed_audio))
            if max_amplitude > 1.0:
                mixed_audio = mixed_audio / max_amplitude * 0.95

            return mixed_audio

        except Exception as e:
            logger.error(f"Audio mixing failed: {str(e)}")
            return audio1

    async def fade_audio(self, audio_data: np.ndarray,
                        fade_in_duration: float = 0.1,
                        fade_out_duration: float = 0.1,
                        sample_rate: int = 44100) -> np.ndarray:
        """Apply fade in and fade out to audio"""
        try:
            faded_audio = audio_data.copy()

            # Fade in
            if fade_in_duration > 0:
                fade_in_samples = int(fade_in_duration * sample_rate)
                fade_in_curve = np.linspace(0, 1, fade_in_samples)
                faded_audio[:fade_in_samples] *= fade_in_curve

            # Fade out
            if fade_out_duration > 0:
                fade_out_samples = int(fade_out_duration * sample_rate)
                fade_out_curve = np.linspace(1, 0, fade_out_samples)
                faded_audio[-fade_out_samples:] *= fade_out_curve

            return faded_audio

        except Exception as e:
            logger.error(f"Audio fading failed: {str(e)}")
            return audio_data

    async def calculate_audio_similarity(self, audio1: np.ndarray, audio2: np.ndarray) -> Dict[str, float]:
        """Calculate similarity metrics between two audio signals"""
        try:
            # Ensure same length
            min_length = min(len(audio1), len(audio2))
            audio1 = audio1[:min_length]
            audio2 = audio2[:min_length]

            # Normalize
            audio1 = audio1 / (np.max(np.abs(audio1)) + 1e-8)
            audio2 = audio2 / (np.max(np.abs(audio2)) + 1e-8)

            # Calculate metrics
            correlation = np.corrcoef(audio1, audio2)[0, 1]

            # Mean squared error
            mse = np.mean((audio1 - audio2)**2)

            # Spectral similarity
            fft1 = np.fft.fft(audio1)
            fft2 = np.fft.fft(audio2)
            spectral_similarity = np.corrcoef(np.abs(fft1), np.abs(fft2))[0, 1]

            return {
                "correlation": float(correlation),
                "mse": float(mse),
                "spectral_similarity": float(spectral_similarity)
            }

        except Exception as e:
            logger.error(f"Audio similarity calculation failed: {str(e)}")
            return {"correlation": 0.0, "mse": 1.0, "spectral_similarity": 0.0}

    async def apply_reverb(self, audio_data: np.ndarray,
                         sample_rate: int,
                         room_size: float = 0.5,
                         damping: float = 0.5,
                         wet_level: float = 0.3) -> np.ndarray:
        """Apply simple reverb effect"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Simple convolution reverb using exponentially decaying impulse response
            reverb_length = int(room_size * sample_rate)
            impulse_response = np.exp(-damping * np.arange(reverb_length))
            impulse_response = impulse_response / np.sum(np.abs(impulse_response))

            # Apply convolution
            reverb_signal = np.convolve(audio_data[0], impulse_response, mode='same')

            # Mix dry and wet signals
            wet_audio = wet_level * reverb_signal
            dry_audio = (1 - wet_level) * audio_data[0]
            processed_audio = dry_audio + wet_audio

            return processed_audio.reshape(1, -1)

        except Exception as e:
            logger.error(f"Reverb application failed: {str(e)}")
            return audio_data

    async def detect_clipping(self, audio_data: np.ndarray, threshold: float = 0.99) -> Dict[str, Any]:
        """Detect clipping in audio signal"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Find clipping samples
            positive_clipping = np.where(audio_data[0] > threshold)[0]
            negative_clipping = np.where(audio_data[0] < -threshold)[0]

            total_clipping = len(positive_clipping) + len(negative_clipping)
            clipping_percentage = (total_clipping / len(audio_data[0])) * 100

            return {
                "has_clipping": total_clipping > 0,
                "clipping_samples": int(total_clipping),
                "clipping_percentage": float(clipping_percentage),
                "positive_clips": int(len(positive_clipping)),
                "negative_clips": int(len(negative_clipping)),
                "max_amplitude": float(np.max(np.abs(audio_data[0])))
            }

        except Exception as e:
            logger.error(f"Clipping detection failed: {str(e)}")
            return {"has_clipping": False, "error": str(e)}

    async def normalize_audio(self, audio_data: np.ndarray, target_level: float = 0.95) -> np.ndarray:
        """Normalize audio to target level"""
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Find peak amplitude
            peak_amplitude = np.max(np.abs(audio_data[0]))

            if peak_amplitude > 0:
                # Calculate normalization factor
                normalization_factor = target_level / peak_amplitude

                # Apply normalization
                normalized_audio = audio_data * normalization_factor
            else:
                normalized_audio = audio_data

            return normalized_audio[0] if normalized_audio.shape[0] == 1 else normalized_audio

        except Exception as e:
            logger.error(f"Audio normalization failed: {str(e)}")
            return audio_data

# Advanced LFM2-specific tools
class LFM2AdvancedTools:
    """Advanced LFM2-specific audio processing tools"""

    def __init__(self):
        self.lfm2_processor = None
        self.lfm2_model = None

    async def initialize_lfm2(self, model_name: str = "LiquidAI/LFM2-Audio-1.5B"):
        """Initialize LFM2 models"""
        try:
            if not LIQUID_AUDIO_AVAILABLE:
                raise ImportError("liquid-audio library not available")

            from liquid_audio import LFM2AudioProcessor, LFM2AudioModel

            self.lfm2_processor = LFM2AudioProcessor.from_pretrained(model_name).eval()
            self.lfm2_model = LFM2AudioModel.from_pretrained(model_name).eval()

            logger.info("LFM2 models initialized successfully")
            return True

        except Exception as e:
            logger.error(f"LFM2 initialization failed: {str(e)}")
            return False

    async def extract_voice_characteristics(self, audio_data: np.ndarray,
                                          sample_rate: int) -> Dict[str, Any]:
        """Extract detailed voice characteristics using LFM2"""
        try:
            if not self.lfm2_processor:
                await self.initialize_lfm2()

            if not self.lfm2_processor:
                raise Exception("LFM2 processor not available")

            # Use LFM2 for advanced voice analysis
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Extract voice characteristics
            characteristics = self.lfm2_processor.extract_voice_features(
                audio_data, sample_rate
            )

            return characteristics

        except Exception as e:
            logger.error(f"Voice characteristic extraction failed: {str(e)}")
            return {}

    async def perform_voice_conversion(self, audio_data: np.ndarray,
                                     sample_rate: int,
                                     target_characteristics: Dict[str, Any]) -> np.ndarray:
        """Perform voice conversion using LFM2"""
        try:
            if not self.lfm2_model:
                await self.initialize_lfm2()

            if not self.lfm2_model:
                raise Exception("LFM2 model not available")

            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Perform voice conversion
            converted_audio = self.lfm2_model.convert_voice(
                audio_data,
                target_characteristics=target_characteristics
            )

            return converted_audio

        except Exception as e:
            logger.error(f"Voice conversion failed: {str(e)}")
            return audio_data

    async def enhance_speech_quality(self, audio_data: np.ndarray,
                                   sample_rate: int,
                                   enhancement_level: float = 1.0) -> np.ndarray:
        """Enhance speech quality using LFM2"""
        try:
            if not self.lfm2_processor:
                await self.initialize_lfm2()

            if not self.lfm2_processor:
                raise Exception("LFM2 processor not available")

            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Apply LFM2 speech enhancement
            enhanced_audio = self.lfm2_processor.enhance_speech(
                audio_data,
                sample_rate=sample_rate,
                enhancement_strength=enhancement_level
            )

            return enhanced_audio

        except Exception as e:
            logger.error(f"Speech enhancement failed: {str(e)}")
            return audio_data

    async def separate_audio_sources(self, audio_data: np.ndarray,
                                   sample_rate: int) -> Dict[str, np.ndarray]:
        """Separate audio sources using LFM2"""
        try:
            if not self.lfm2_processor:
                await self.initialize_lfm2()

            if not self.lfm2_processor:
                raise Exception("LFM2 processor not available")

            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Perform source separation
            separated_sources = self.lfm2_processor.separate_sources(
                audio_data, sample_rate
            )

            return separated_sources

        except Exception as e:
            logger.error(f"Source separation failed: {str(e)}")
            return {"original": audio_data}

    async def generate_audio_embedding(self, audio_data: np.ndarray,
                                     sample_rate: int) -> np.ndarray:
        """Generate audio embedding using LFM2"""
        try:
            if not self.lfm2_processor:
                await self.initialize_lfm2()

            if not self.lfm2_processor:
                raise Exception("LFM2 processor not available")

            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Generate embedding
            embedding = self.lfm2_processor.get_embedding(
                audio_data, sample_rate
            )

            return embedding

        except Exception as e:
            logger.error(f"Audio embedding generation failed: {str(e)}")
            return np.array([])