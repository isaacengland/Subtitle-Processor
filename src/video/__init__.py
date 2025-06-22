"""
Video Processing Package

This package handles all video format processing operations. It provides a flexible,
extensible architecture for supporting multiple video formats through specialized
processor implementations.

Architecture:
- VideoProcessorBase: Abstract interface that all processors must implement
- VideoProcessorFactory: Central registry and factory for processor selection
- UniversalVideoProcessor: Format-agnostic interface that delegates to specific processors
- Format Processors: Concrete implementations for specific video formats (MKV, MP4, etc.)

Extensibility:
To add support for a new video format:
1. Create a new processor class inheriting from VideoProcessorBase
2. Implement all abstract methods for your format
3. Register it with the factory in _register_default_processors()
4. The entire system automatically supports the new format!

Usage:
    from src.video import UniversalVideoProcessor, MKVProcessor
    
    # Use universal processor (recommended)
    processor = UniversalVideoProcessor()
    
    # Or use specific processor directly
    mkv_processor = MKVProcessor()
"""

# Core video processing components
from .video_processor_base import VideoProcessorBase
from .video_processor_factory import VideoProcessorFactory  
from .universal_video_processor import UniversalVideoProcessor

# Format-specific processors
from .mkv_processor import MKVProcessor

# Package information
__all__ = [
    # Core components
    "VideoProcessorBase",
    "VideoProcessorFactory",
    "UniversalVideoProcessor",
    
    # Format processors
    "MKVProcessor",
]

# Supported formats (dynamically generated)
def get_supported_formats():
    """Get list of all supported video format extensions."""
    factory = VideoProcessorFactory()
    return factory.get_supported_extensions()

# Convenience function for checking format support
def can_process_format(file_path: str) -> bool:
    """Check if a video file format is supported."""
    factory = VideoProcessorFactory()
    return factory.can_process(file_path)