"""
Test Package for Universal Subtitle Processor

This package contains unit tests, integration tests, and test utilities
for the subtitle processing system.

Test Structure:
- test_subtitle_processor.py: Tests for subtitle styling and format conversion
- test_video_processors.py: Tests for video format processors
- test_file_utils.py: Tests for file management utilities
- test_gui.py: Tests for GUI components (when applicable)

Running Tests:
    # Run all tests
    python -m pytest tests/
    
    # Run specific test file
    python -m pytest tests/test_subtitle_processor.py
    
    # Run with coverage
    python -m pytest tests/ --cov=src

Test Dependencies:
    pip install pytest pytest-cov

Future Test Areas:
- Mock external tool dependencies (MKVToolNix, FFmpeg)
- Test configuration file parsing and validation
- Test error handling and edge cases
- Integration tests with sample video files
- GUI testing with automated UI frameworks
"""

# Test package metadata
__version__ = "1.0.0"
__description__ = "Test suite for Universal Subtitle Processor"

# Common test utilities can be imported here when created
# from .test_utils import create_test_video, create_test_config

__all__ = [
    "__version__",
    "__description__"
]