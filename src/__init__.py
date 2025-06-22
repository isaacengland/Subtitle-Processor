"""
Universal Subtitle Processor - Main Package

This package provides comprehensive subtitle processing capabilities for video files.
It supports multiple video formats and provides both automated and manual styling options.

Main Components:
- UniversalSubtitleProcessor: Main processing orchestrator
- SubtitleProcessorGUI: Drag-and-drop GUI interface
- FileManager: File operations and temporary directory management
- SubtitleProcessor: Subtitle styling and format conversion
- AegisubProcessor: Manual editing integration

Video Processing:
- UniversalVideoProcessor: Format-agnostic video interface
- VideoProcessorFactory: Processor selection and management
- VideoProcessorBase: Abstract interface for format processors
- MKVProcessor: MKV format implementation

Usage:
    from src import UniversalSubtitleProcessor, SubtitleProcessorGUI
    
    # For programmatic use
    processor = UniversalSubtitleProcessor()
    
    # For GUI use
    app = SubtitleProcessorGUI()
"""

# Import main classes for easy access
from .gui import SubtitleProcessorGUI
from .file_utils import FileManager
from .subtitle_processor import SubtitleProcessor
from .aegisub_processor import AegisubProcessor

# Import video processing components
from .video import (
    UniversalVideoProcessor,
    VideoProcessorFactory,
    VideoProcessorBase,
    MKVProcessor
)

# Version information
__version__ = "1.0.0"
__author__ = "Subtitle Processor Team"
__description__ = "Universal subtitle processing system with extensible video format support"

# Package metadata
__all__ = [
    # Main components
    "SubtitleProcessorGUI",
    "FileManager", 
    "SubtitleProcessor",
    "AegisubProcessor",
    
    # Video processing
    "UniversalVideoProcessor",
    "VideoProcessorFactory", 
    "VideoProcessorBase",
    "MKVProcessor",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]