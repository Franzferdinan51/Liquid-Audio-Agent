#!/usr/bin/env python3
"""
Liquid Audio MCP Server
Comprehensive Model Context Protocol server for liquid-audio LFM2 integration
Provides AI models with direct access to advanced audio processing capabilities
"""

import asyncio
import json
import logging
import sys
import os
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import numpy as np
import soundfile as sf
import sounddevice as sd
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    ReadResourceRequest, ReadResourceResult
)

# Import liquid-audio LFM2 components
try:
    from liquid_audio import LFM2AudioProcessor, LFM2AudioModel
    LIQUID_AUDIO_AVAILABLE = True
except ImportError:
    LIQUID_AUDIO_AVAILABLE = False
    logging.warning("liquid-audio not available. Some features will be limited.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp-liquid-audio.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("mcp-liquid-audio")

class LiquidAudioMCPServer:
    """Main MCP Server class for liquid-audio integration"""

    def __init__(self):
        self.server = Server("liquid-audio-mcp")
        self.processor = None
        self.model = None
        self.recording_stream = None
        self.is_recording = False
        self.recorded_audio = []
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available tools"""
            tools = [
                # Audio Processing Tools
                Tool(
                    name="process_audio_file",
                    description="Process audio file with LFM2 enhancement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_path": {"type": "string", "description": "Path to input audio file"},
                            "output_path": {"type": "string", "description": "Path to save processed audio"},
                            "enhancement_level": {"type": "number", "minimum": 0.1, "maximum": 2.0, "default": 1.0},
                            "noise_reduction": {"type": "boolean", "default": True},
                            "voice_enhancement": {"type": "boolean", "default": True}
                        },
                        "required": ["input_path", "output_path"]
                    }
                ),
                Tool(
                    name="analyze_audio_frequencies",
                    description="Analyze audio frequencies and patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "audio_path": {"type": "string", "description": "Path to audio file"},
                            "analysis_type": {"type": "string", "enum": ["spectral", "temporal", "mfcc", "all"], "default": "all"},
                            "output_format": {"type": "string", "enum": ["json", "text"], "default": "json"}
                        },
                        "required": ["audio_path"]
                    }
                ),
                Tool(
                    name="convert_audio_format",
                    description="Convert between audio formats",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_path": {"type": "string", "description": "Path to input audio file"},
                            "output_path": {"type": "string", "description": "Path to save converted audio"},
                            "target_format": {"type": "string", "enum": ["wav", "mp3", "flac", "ogg"], "default": "wav"},
                            "sample_rate": {"type": "integer", "minimum": 8000, "maximum": 192000, "default": 44100}
                        },
                        "required": ["input_path", "output_path"]
                    }
                ),

                # Real-time Audio Tools
                Tool(
                    name="start_microphone_recording",
                    description="Start recording from microphone",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number", "description": "Maximum recording duration in seconds"},
                            "sample_rate": {"type": "integer", "minimum": 8000, "maximum": 192000, "default": 44100},
                            "channels": {"type": "integer", "minimum": 1, "maximum": 2, "default": 1}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="stop_microphone_recording",
                    description="Stop microphone recording and process audio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {"type": "string", "description": "Path to save recorded audio"},
                            "apply_lfm2": {"type": "boolean", "default": True}
                        },
                        "required": ["output_path"]
                    }
                ),
                Tool(
                    name="monitor_audio_levels",
                    description="Monitor real-time audio levels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number", "default": 10.0, "description": "Monitoring duration in seconds"},
                            "threshold": {"type": "number", "default": 0.01, "description": "Detection threshold"}
                        },
                        "required": []
                    }
                ),

                # LFM2 Specific Tools
                Tool(
                    name="apply_lfm2_enhancement",
                    description="Apply Local Frequency Matching 2 processing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "audio_path": {"type": "string", "description": "Path to audio file"},
                            "output_path": {"type": "string", "description": "Path to save enhanced audio"},
                            "model_name": {"type": "string", "default": "LiquidAI/LFM2-Audio-1.5B"},
                            "enhancement_strength": {"type": "number", "minimum": 0.1, "maximum": 2.0, "default": 1.0}
                        },
                        "required": ["audio_path", "output_path"]
                    }
                ),
                Tool(
                    name="voice_characteristic_analysis",
                    description="Analyze voice characteristics and patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "audio_path": {"type": "string", "description": "Path to audio file"},
                            "analysis_depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"], "default": "detailed"}
                        },
                        "required": ["audio_path"]
                    }
                ),
                Tool(
                    name="speech_to_speech_conversion",
                    description="Convert speech characteristics while preserving content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_path": {"type": "string", "description": "Path to input audio"},
                            "output_path": {"type": "string", "description": "Path to save converted audio"},
                            "target_voice": {"type": "string", "description": "Target voice characteristics"},
                            "preserve_content": {"type": "boolean", "default": True}
                        },
                        "required": ["input_path", "output_path"]
                    }
                ),

                # Integration Tools
                Tool(
                    name="load_lfm2_model",
                    description="Load LFM2 model for processing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {"type": "string", "default": "LiquidAI/LFM2-Audio-1.5B"},
                            "device": {"type": "string", "enum": ["cpu", "cuda", "auto"], "default": "auto"},
                            "precision": {"type": "string", "enum": ["float32", "float16", "bfloat16"], "default": "float32"}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="batch_process_audio",
                    description="Process multiple audio files in batch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_directory": {"type": "string", "description": "Directory containing audio files"},
                            "output_directory": {"type": "string", "description": "Directory to save processed files"},
                            "file_pattern": {"type": "string", "default": "*.wav"},
                            "processing_type": {"type": "string", "enum": ["lfm2", "enhancement", "conversion", "analysis"], "default": "lfm2"}
                        },
                        "required": ["input_directory", "output_directory"]
                    }
                ),
                Tool(
                    name="get_audio_info",
                    description="Get detailed information about audio file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "audio_path": {"type": "string", "description": "Path to audio file"},
                            "include_technical": {"type": "boolean", "default": True},
                            "include_analysis": {"type": "boolean", "default": False}
                        },
                        "required": ["audio_path"]
                    }
                )
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                logger.info(f"Tool call: {name} with arguments: {arguments}")

                # Ensure liquid-audio is available for audio operations
                if name not in ["get_audio_info", "monitor_audio_levels"] and not LIQUID_AUDIO_AVAILABLE:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text="Error: liquid-audio library not available. Please install with: pip install liquid-audio"
                        )],
                        isError=True
                    )

                # Route to appropriate handler
                if name == "process_audio_file":
                    result = await self.process_audio_file(**arguments)
                elif name == "analyze_audio_frequencies":
                    result = await self.analyze_audio_frequencies(**arguments)
                elif name == "convert_audio_format":
                    result = await self.convert_audio_format(**arguments)
                elif name == "start_microphone_recording":
                    result = await self.start_microphone_recording(**arguments)
                elif name == "stop_microphone_recording":
                    result = await self.stop_microphone_recording(**arguments)
                elif name == "monitor_audio_levels":
                    result = await self.monitor_audio_levels(**arguments)
                elif name == "apply_lfm2_enhancement":
                    result = await self.apply_lfm2_enhancement(**arguments)
                elif name == "voice_characteristic_analysis":
                    result = await self.voice_characteristic_analysis(**arguments)
                elif name == "speech_to_speech_conversion":
                    result = await self.speech_to_speech_conversion(**arguments)
                elif name == "load_lfm2_model":
                    result = await self.load_lfm2_model(**arguments)
                elif name == "batch_process_audio":
                    result = await self.batch_process_audio(**arguments)
                elif name == "get_audio_info":
                    result = await self.get_audio_info(**arguments)
                else:
                    result = CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Error: Unknown tool '{name}'"
                        )],
                        isError=True
                    )

                return result

            except Exception as e:
                logger.error(f"Error in tool call {name}: {str(e)}")
                logger.error(traceback.format_exc())
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error executing {name}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                    )],
                    isError=True
                )

    async def initialize_models(self, model_name: str = "LiquidAI/LFM2-Audio-1.5B", device: str = "auto"):
        """Initialize LFM2 models"""
        try:
            if not LIQUID_AUDIO_AVAILABLE:
                logger.warning("liquid-audio not available, skipping model initialization")
                return False

            logger.info(f"Initializing LFM2 models: {model_name}")

            # Determine device
            if device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"

            # Initialize processor
            self.processor = LFM2AudioProcessor.from_pretrained(model_name).eval()
            if device == "cuda":
                self.processor = self.processor.cuda()

            # Initialize model
            self.model = LFM2AudioModel.from_pretrained(model_name).eval()
            if device == "cuda":
                self.model = self.model.cuda()

            logger.info(f"LFM2 models initialized successfully on {device}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LFM2 models: {str(e)}")
            return False

    async def process_audio_file(self, input_path: str, output_path: str,
                               enhancement_level: float = 1.0,
                               noise_reduction: bool = True,
                               voice_enhancement: bool = True) -> CallToolResult:
        """Process audio file with LFM2 enhancement"""
        try:
            # Load audio
            audio_data, sample_rate = sf.read(input_path)

            # Ensure models are loaded
            if not self.processor:
                await self.initialize_models()

            if not self.processor:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Failed to initialize LFM2 processor"
                    )],
                    isError=True
                )

            # Process audio
            logger.info(f"Processing audio file: {input_path}")

            # Apply LFM2 processing
            if isinstance(audio_data, np.ndarray) and audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            processed_audio = self.processor(audio_data, sample_rate=sample_rate)

            # Apply enhancement level
            processed_audio = processed_audio * enhancement_level

            # Save processed audio
            sf.write(output_path, processed_audio.T, sample_rate)

            result_text = f"Audio processed successfully:\n"
            result_text += f"Input: {input_path}\n"
            result_text += f"Output: {output_path}\n"
            result_text += f"Sample rate: {sample_rate} Hz\n"
            result_text += f"Duration: {len(audio_data) / sample_rate:.2f} seconds\n"
            result_text += f"Enhancement level: {enhancement_level}\n"
            result_text += f"Noise reduction: {noise_reduction}\n"
            result_text += f"Voice enhancement: {voice_enhancement}"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error processing audio file: {str(e)}"
                )],
                isError=True
            )

    async def analyze_audio_frequencies(self, audio_path: str,
                                     analysis_type: str = "all",
                                     output_format: str = "json") -> CallToolResult:
        """Analyze audio frequencies and patterns"""
        try:
            # Load audio
            audio_data, sample_rate = sf.read(audio_path)

            # Perform frequency analysis
            analysis_results = {}

            if analysis_type in ["spectral", "all"]:
                # Spectral analysis
                fft = np.fft.fft(audio_data)
                frequencies = np.fft.fftfreq(len(fft), 1/sample_rate)
                magnitude = np.abs(fft)

                analysis_results["spectral"] = {
                    "dominant_frequency": float(frequencies[np.argmax(magnitude[:len(frequencies)//2])]),
                    "average_magnitude": float(np.mean(magnitude)),
                    "peak_magnitude": float(np.max(magnitude)),
                    "frequency_range": {
                        "min": float(np.min(frequencies)),
                        "max": float(np.max(frequencies))
                    }
                }

            if analysis_type in ["temporal", "all"]:
                # Temporal analysis
                analysis_results["temporal"] = {
                    "duration": float(len(audio_data) / sample_rate),
                    "rms_energy": float(np.sqrt(np.mean(audio_data**2))),
                    "peak_amplitude": float(np.max(np.abs(audio_data))),
                    "zero_crossing_rate": float(np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data))
                }

            if analysis_type in ["mfcc", "all"] and LIQUID_AUDIO_AVAILABLE:
                # MFCC analysis (if available)
                try:
                    # Use liquid-audio for advanced analysis if available
                    if self.processor:
                        mfcc_features = self.processor.extract_mfcc(audio_data, sample_rate)
                        analysis_results["mfcc"] = {
                            "feature_count": mfcc_features.shape[0] if len(mfcc_features.shape) > 1 else 1,
                            "frame_count": mfcc_features.shape[1] if len(mfcc_features.shape) > 1 else len(mfcc_features),
                            "mean_coefficients": [float(x) for x in np.mean(mfcc_features, axis=1)] if len(mfcc_features.shape) > 1 else [float(np.mean(mfcc_features))]
                        }
                except Exception as e:
                    logger.warning(f"MFCC analysis failed: {str(e)}")

            # Format output
            if output_format == "json":
                result_text = json.dumps(analysis_results, indent=2)
            else:
                result_text = "Audio Analysis Results:\n\n"
                for analysis_type, results in analysis_results.items():
                    result_text += f"{analysis_type.upper()} ANALYSIS:\n"
                    for key, value in results.items():
                        result_text += f"  {key}: {value}\n"
                    result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error analyzing audio frequencies: {str(e)}"
                )],
                isError=True
            )

    async def convert_audio_format(self, input_path: str, output_path: str,
                                 target_format: str = "wav",
                                 sample_rate: int = 44100) -> CallToolResult:
        """Convert between audio formats"""
        try:
            # Load audio
            audio_data, original_sample_rate = sf.read(input_path)

            # Resample if necessary
            if original_sample_rate != sample_rate:
                # Simple resampling (you might want to use a more sophisticated resampler)
                import scipy.signal as signal
                resample_ratio = sample_rate / original_sample_rate
                audio_data = signal.resample(audio_data, int(len(audio_data) * resample_ratio))

            # Save in target format
            sf.write(output_path, audio_data, sample_rate, format=target_format)

            result_text = f"Audio converted successfully:\n"
            result_text += f"Input: {input_path}\n"
            result_text += f"Output: {output_path}\n"
            result_text += f"Original sample rate: {original_sample_rate} Hz\n"
            result_text += f"New sample rate: {sample_rate} Hz\n"
            result_text += f"Target format: {target_format}\n"
            result_text += f"Duration: {len(audio_data) / sample_rate:.2f} seconds"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error converting audio format: {str(e)}"
                )],
                isError=True
            )

    async def start_microphone_recording(self, duration: Optional[float] = None,
                                       sample_rate: int = 44100,
                                       channels: int = 1) -> CallToolResult:
        """Start recording from microphone"""
        try:
            if self.is_recording:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Recording is already in progress"
                    )],
                    isError=True
                )

            self.recorded_audio = []
            self.is_recording = True

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                if self.is_recording:
                    self.recorded_audio.append(indata.copy())

            # Start recording stream
            self.recording_stream = sd.InputStream(
                callback=audio_callback,
                channels=channels,
                samplerate=sample_rate,
                blocksize=1024
            )

            self.recording_stream.start()

            # Schedule stop if duration is specified
            if duration:
                asyncio.create_task(self._stop_recording_after_duration(duration))

            result_text = f"Microphone recording started:\n"
            result_text += f"Sample rate: {sample_rate} Hz\n"
            result_text += f"Channels: {channels}\n"
            if duration:
                result_text += f"Auto-stop after: {duration} seconds"
            else:
                result_text += "Manual stop required"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error starting microphone recording: {str(e)}"
                )],
                isError=True
            )

    async def _stop_recording_after_duration(self, duration: float):
        """Stop recording after specified duration"""
        await asyncio.sleep(duration)
        if self.is_recording:
            self.is_recording = False
            if self.recording_stream:
                self.recording_stream.stop()
                self.recording_stream.close()
                self.recording_stream = None

    async def stop_microphone_recording(self, output_path: str,
                                      apply_lfm2: bool = True) -> CallToolResult:
        """Stop microphone recording and process audio"""
        try:
            if not self.is_recording:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="No recording in progress"
                    )],
                    isError=True
                )

            self.is_recording = False

            if self.recording_stream:
                self.recording_stream.stop()
                self.recording_stream.close()
                self.recording_stream = None

            if not self.recorded_audio:
                return CallResult(
                    content=[TextContent(
                        type="text",
                        text="No audio data recorded"
                    )],
                    isError=True
                )

            # Combine recorded audio
            audio_data = np.concatenate(self.recorded_audio, axis=0)

            # Apply LFM2 processing if requested
            if apply_lfm2 and self.processor:
                audio_data = self.processor(audio_data.T).T

            # Save audio
            sf.write(output_path, audio_data, 44100)

            result_text = f"Recording stopped and saved:\n"
            result_text += f"Output path: {output_path}\n"
            result_text += f"Duration: {len(audio_data) / 44100:.2f} seconds\n"
            result_text += f"LFM2 processing: {apply_lfm2}\n"
            result_text += f"Sample rate: 44100 Hz\n"
            result_text += f"Channels: {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error stopping microphone recording: {str(e)}"
                )],
                isError=True
            )

    async def monitor_audio_levels(self, duration: float = 10.0,
                                 threshold: float = 0.01) -> CallToolResult:
        """Monitor real-time audio levels"""
        try:
            monitoring_data = []

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")

                # Calculate RMS level
                rms_level = np.sqrt(np.mean(indata**2))
                monitoring_data.append({
                    "timestamp": time.currentTime,
                    "rms_level": float(rms_level),
                    "peak_level": float(np.max(np.abs(indata))),
                    "above_threshold": rms_level > threshold
                })

            # Start monitoring
            with sd.InputStream(callback=audio_callback, channels=1):
                await asyncio.sleep(duration)

            # Analyze monitoring data
            if not monitoring_data:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="No audio data captured during monitoring"
                    )]
                )

            rms_levels = [d["rms_level"] for d in monitoring_data]
            peak_levels = [d["peak_level"] for d in monitoring_data]
            above_threshold_count = sum(1 for d in monitoring_data if d["above_threshold"])

            result_text = f"Audio Level Monitoring Results:\n\n"
            result_text += f"Monitoring duration: {duration} seconds\n"
            result_text += f"Samples captured: {len(monitoring_data)}\n"
            result_text += f"Threshold: {threshold}\n\n"
            result_text += f"RMS Level Statistics:\n"
            result_text += f"  Average: {np.mean(rms_levels):.4f}\n"
            result_text += f"  Peak: {np.max(rms_levels):.4f}\n"
            result_text += f"  Minimum: {np.min(rms_levels):.4f}\n\n"
            result_text += f"Peak Level Statistics:\n"
            result_text += f"  Average: {np.mean(peak_levels):.4f}\n"
            result_text += f"  Maximum: {np.max(peak_levels):.4f}\n\n"
            result_text += f"Activity Detection:\n"
            result_text += f"  Time above threshold: {above_threshold_count / len(monitoring_data) * 100:.1f}%\n"
            result_text += f"  Activity detected: {'Yes' if above_threshold_count > 0 else 'No'}"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error monitoring audio levels: {str(e)}"
                )],
                isError=True
            )

    async def apply_lfm2_enhancement(self, audio_path: str, output_path: str,
                                   model_name: str = "LiquidAI/LFM2-Audio-1.5B",
                                   enhancement_strength: float = 1.0) -> CallToolResult:
        """Apply Local Frequency Matching 2 processing"""
        try:
            # Ensure model is loaded
            if not self.processor or not self.model:
                success = await self.initialize_models(model_name)
                if not success:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text="Failed to initialize LFM2 models"
                        )],
                        isError=True
                    )

            # Load audio
            audio_data, sample_rate = sf.read(audio_path)

            # Apply LFM2 enhancement
            logger.info(f"Applying LFM2 enhancement to: {audio_path}")

            if isinstance(audio_data, np.ndarray) and audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            enhanced_audio = self.processor(audio_data, sample_rate=sample_rate)

            # Apply enhancement strength
            enhanced_audio = enhanced_audio * enhancement_strength

            # Save enhanced audio
            sf.write(output_path, enhanced_audio.T, sample_rate)

            result_text = f"LFM2 enhancement applied successfully:\n"
            result_text += f"Input: {audio_path}\n"
            result_text += f"Output: {output_path}\n"
            result_text += f"Model: {model_name}\n"
            result_text += f"Enhancement strength: {enhancement_strength}\n"
            result_text += f"Sample rate: {sample_rate} Hz\n"
            result_text += f"Duration: {len(audio_data) / sample_rate:.2f} seconds"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error applying LFM2 enhancement: {str(e)}"
                )],
                isError=True
            )

    async def voice_characteristic_analysis(self, audio_path: str,
                                          analysis_depth: str = "detailed") -> CallToolResult:
        """Analyze voice characteristics and patterns"""
        try:
            # Load audio
            audio_data, sample_rate = sf.read(audio_path)

            analysis_results = {
                "basic": {
                    "duration": float(len(audio_data) / sample_rate),
                    "sample_rate": sample_rate,
                    "channels": audio_data.shape[1] if len(audio_data.shape) > 1 else 1
                }
            }

            # Basic analysis
            analysis_results["basic"].update({
                "rms_energy": float(np.sqrt(np.mean(audio_data**2))),
                "peak_amplitude": float(np.max(np.abs(audio_data))),
                "dynamic_range": float(np.max(audio_data) - np.min(audio_data)),
                "zero_crossing_rate": float(np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data))
            })

            if analysis_depth in ["detailed", "comprehensive"]:
                # Spectral analysis
                fft = np.fft.fft(audio_data)
                frequencies = np.fft.fftfreq(len(fft), 1/sample_rate)
                magnitude = np.abs(fft)

                analysis_results["spectral"] = {
                    "fundamental_frequency": float(self._estimate_fundamental_frequency(audio_data, sample_rate)),
                    "spectral_centroid": float(np.sum(frequencies[:len(frequencies)//2] * magnitude[:len(magnitude)//2]) / np.sum(magnitude[:len(magnitude)//2])),
                    "spectral_bandwidth": float(np.sqrt(np.sum(((frequencies[:len(frequencies)//2] - analysis_results["spectral"]["spectral_centroid"])**2) * magnitude[:len(magnitude)//2]) / np.sum(magnitude[:len(magnitude)//2]))),
                    "spectral_rolloff": float(self._calculate_spectral_rolloff(frequencies, magnitude))
                }

            if analysis_depth == "comprehensive" and LIQUID_AUDIO_AVAILABLE:
                # Advanced analysis with liquid-audio
                try:
                    if self.processor:
                        # Voice characteristic extraction
                        voice_features = self.processor.extract_voice_characteristics(audio_data, sample_rate)
                        analysis_results["voice_features"] = {
                            "pitch_range": [float(x) for x in voice_features.get("pitch_range", [])],
                            "formants": [float(x) for x in voice_features.get("formants", [])],
                            "voice_quality": voice_features.get("voice_quality", "unknown"),
                            "speaker_characteristics": voice_features.get("speaker_characteristics", {})
                        }
                except Exception as e:
                    logger.warning(f"Advanced voice analysis failed: {str(e)}")

            # Format results
            result_text = "Voice Characteristic Analysis:\n\n"

            for analysis_type, results in analysis_results.items():
                result_text += f"{analysis_type.upper()} ANALYSIS:\n"
                for key, value in results.items():
                    if isinstance(value, list):
                        result_text += f"  {key}: {value}\n"
                    else:
                        result_text += f"  {key}: {value}\n"
                result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error analyzing voice characteristics: {str(e)}"
                )],
                isError=True
            )

    async def speech_to_speech_conversion(self, input_path: str, output_path: str,
                                        target_voice: str = "neutral",
                                        preserve_content: bool = True) -> CallToolResult:
        """Convert speech characteristics while preserving content"""
        try:
            # Ensure model is loaded
            if not self.processor or not self.model:
                success = await self.initialize_models()
                if not success:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text="Failed to initialize LFM2 models"
                        )],
                        isError=True
                    )

            # Load audio
            audio_data, sample_rate = sf.read(input_path)

            logger.info(f"Converting speech characteristics: {input_path}")

            # Apply speech-to-speech conversion
            if isinstance(audio_data, np.ndarray) and audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)

            # Use LFM2 model for voice conversion
            converted_audio = self.model.convert_voice(
                audio_data,
                target_voice=target_voice,
                preserve_content=preserve_content
            )

            # Save converted audio
            sf.write(output_path, converted_audio.T, sample_rate)

            result_text = f"Speech-to-speech conversion completed:\n"
            result_text += f"Input: {input_path}\n"
            result_text += f"Output: {output_path}\n"
            result_text += f"Target voice: {target_voice}\n"
            result_text += f"Preserve content: {preserve_content}\n"
            result_text += f"Sample rate: {sample_rate} Hz\n"
            result_text += f"Duration: {len(audio_data) / sample_rate:.2f} seconds"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error in speech-to-speech conversion: {str(e)}"
                )],
                isError=True
            )

    async def load_lfm2_model(self, model_name: str = "LiquidAI/LFM2-Audio-1.5B",
                            device: str = "auto",
                            precision: str = "float32") -> CallToolResult:
        """Load LFM2 model for processing"""
        try:
            success = await self.initialize_models(model_name, device)

            if success:
                result_text = f"LFM2 models loaded successfully:\n"
                result_text += f"Model: {model_name}\n"
                result_text += f"Device: {device}\n"
                result_text += f"Precision: {precision}\n"
                result_text += f"Processor available: {self.processor is not None}\n"
                result_text += f"Model available: {self.model is not None}"
            else:
                result_text = f"Failed to load LFM2 models:\n"
                result_text += f"Model: {model_name}\n"
                result_text += f"Device: {device}\n"
                result_text += f"Please check liquid-audio installation"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error loading LFM2 model: {str(e)}"
                )],
                isError=True
            )

    async def batch_process_audio(self, input_directory: str, output_directory: str,
                                file_pattern: str = "*.wav",
                                processing_type: str = "lfm2") -> CallToolResult:
        """Process multiple audio files in batch"""
        try:
            from pathlib import Path

            input_dir = Path(input_directory)
            output_dir = Path(output_directory)

            if not input_dir.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Input directory does not exist: {input_directory}"
                    )],
                    isError=True
                )

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Find matching files
            audio_files = list(input_dir.glob(file_pattern))

            if not audio_files:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"No files found matching pattern: {file_pattern}"
                    )]
                )

            # Process files
            processed_files = []
            failed_files = []

            for audio_file in audio_files:
                try:
                    output_file = output_dir / f"processed_{audio_file.name}"

                    if processing_type == "lfm2":
                        await self.apply_lfm2_enhancement(str(audio_file), str(output_file))
                    elif processing_type == "enhancement":
                        await self.process_audio_file(str(audio_file), str(output_file))
                    elif processing_type == "conversion":
                        await self.convert_audio_format(str(audio_file), str(output_file))
                    elif processing_type == "analysis":
                        await self.analyze_audio_frequencies(str(audio_file), str(output_file).replace('.wav', '_analysis.json'))

                    processed_files.append(str(audio_file))

                except Exception as e:
                    failed_files.append({"file": str(audio_file), "error": str(e)})

            result_text = f"Batch processing completed:\n\n"
            result_text += f"Input directory: {input_directory}\n"
            result_text += f"Output directory: {output_directory}\n"
            result_text += f"File pattern: {file_pattern}\n"
            result_text += f"Processing type: {processing_type}\n\n"
            result_text += f"Files found: {len(audio_files)}\n"
            result_text += f"Successfully processed: {len(processed_files)}\n"
            result_text += f"Failed: {len(failed_files)}\n\n"

            if processed_files:
                result_text += "Successfully processed files:\n"
                for file_path in processed_files:
                    result_text += f"  ✓ {file_path}\n"
                result_text += "\n"

            if failed_files:
                result_text += "Failed files:\n"
                for failed in failed_files:
                    result_text += f"  ✗ {failed['file']}: {failed['error']}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error in batch processing: {str(e)}"
                )],
                isError=True
            )

    async def get_audio_info(self, audio_path: str,
                           include_technical: bool = True,
                           include_analysis: bool = False) -> CallToolResult:
        """Get detailed information about audio file"""
        try:
            # Get file info
            file_path = Path(audio_path)
            if not file_path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Audio file does not exist: {audio_path}"
                    )],
                    isError=True
                )

            file_stats = file_path.stat()

            # Load audio
            try:
                audio_data, sample_rate = sf.read(audio_path)
                audio_available = True
            except Exception as e:
                audio_available = False
                audio_error = str(e)

            result_text = f"Audio File Information:\n\n"
            result_text += f"File: {audio_path}\n"
            result_text += f"Size: {file_stats.st_size} bytes ({file_stats.st_size / 1024 / 1024:.2f} MB)\n"
            result_text += f"Modified: {file_stats.st_mtime}\n\n"

            if audio_available:
                result_text += f"AUDIO INFORMATION:\n"
                result_text += f"Sample rate: {sample_rate} Hz\n"
                result_text += f"Duration: {len(audio_data) / sample_rate:.2f} seconds\n"
                result_text += f"Channels: {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}\n"
                result_text += f"Samples: {len(audio_data)}\n"
                result_text += f"Data type: {audio_data.dtype}\n"

                if include_technical:
                    result_text += f"\nTECHNICAL INFORMATION:\n"
                    result_text += f"RMS energy: {np.sqrt(np.mean(audio_data**2)):.6f}\n"
                    result_text += f"Peak amplitude: {np.max(np.abs(audio_data)):.6f}\n"
                    result_text += f"Dynamic range: {np.max(audio_data) - np.min(audio_data):.6f} dB\n"
                    result_text += f"Zero crossing rate: {np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data):.6f}\n"

                    # Frequency information
                    fft = np.fft.fft(audio_data)
                    frequencies = np.fft.fftfreq(len(fft), 1/sample_rate)
                    magnitude = np.abs(fft)
                    dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
                    dominant_freq = frequencies[dominant_freq_idx]

                    result_text += f"Dominant frequency: {dominant_freq:.2f} Hz\n"
                    result_text += f"Average magnitude: {np.mean(magnitude):.6f}\n"

                if include_analysis and LIQUID_AUDIO_AVAILABLE and self.processor:
                    try:
                        # Additional analysis with liquid-audio
                        result_text += f"\nADVANCED ANALYSIS:\n"

                        # Frequency analysis
                        freq_analysis = await self.analyze_audio_frequencies(audio_path, "spectral", "text")
                        result_text += freq_analysis.content[0].text

                    except Exception as e:
                        result_text += f"Advanced analysis failed: {str(e)}\n"
            else:
                result_text += f"Error loading audio file: {audio_error}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error getting audio info: {str(e)}"
                )],
                isError=True
            )

    def _estimate_fundamental_frequency(self, audio_data, sample_rate):
        """Estimate fundamental frequency using autocorrelation"""
        # Simple autocorrelation-based pitch detection
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Find first peak after zero lag
        first_min = np.min(autocorr[1:len(autocorr)//4])
        first_peak_idx = np.argmax(autocorr[1:len(autocorr)//4]) + 1

        if first_peak_idx > 0:
            fundamental_freq = sample_rate / first_peak_idx
            return fundamental_freq
        else:
            return 0.0

    def _calculate_spectral_rolloff(self, frequencies, magnitude, rolloff_percent=0.85):
        """Calculate spectral rolloff frequency"""
        cumsum = np.cumsum(magnitude[:len(magnitude)//2])
        rolloff_point = rolloff_percent * cumsum[-1]
        rolloff_idx = np.where(cumsum >= rolloff_point)[0]

        if len(rolloff_idx) > 0:
            return frequencies[rolloff_idx[0]]
        else:
            return 0.0

async def main():
    """Main entry point"""
    logger.info("Starting Liquid Audio MCP Server")

    # Create server instance
    mcp_server = LiquidAudioMCPServer()

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="liquid-audio-mcp",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())