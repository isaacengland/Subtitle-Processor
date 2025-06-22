# Extending The System - Developer Guide

## 🚀 **Adding New Video Format Support**

The Universal Subtitle Processor is designed to make adding new video format
support incredibly simple. This guide shows exactly how to extend the system
with minimal code changes.

**EXTENSIBILITY PHILOSOPHY:**
Adding a new format should require:

1. Creating one new processor class
2. Adding one line to register it
3. Zero changes to existing code

This keeps the system maintainable and allows community contributions
without affecting core functionality.

## 📖 **Implementation Examples**

_Note: These are template examples showing the pattern to follow. Copy and
modify these examples to create actual working processors._

# mp4_processor.py

"""
Example MP4 Processor Implementation

This example shows how to add MP4 support using FFmpeg tools.
Copy this pattern for any new video format you want to support.

IMPLEMENTATION STRATEGY:

-   Use FFmpeg for universal compatibility
-   Leverage ffprobe for track analysis
-   Use ffmpeg for extraction and merging
-   Follow same patterns as MKVProcessor

TOOLS REQUIRED:

-   ffprobe: For analyzing MP4 file structure
-   ffmpeg: For subtitle extraction and video merging

COMMAND EXAMPLES:

-   Track info: ffprobe -v quiet -print_format json -show_streams video.mp4
-   Extract: ffmpeg -i video.mp4 -map 0:s:0 -c:s ass subtitles.ass
-   Merge: ffmpeg -i video.mp4 -i subtitles.ass -c:v copy -c:a copy output.mp4
    """

import subprocess
import json
from typing import List, Dict
from .video_processor_base import VideoProcessorBase

class MP4Processor(VideoProcessorBase):
"""MP4 File Format Processor using FFmpeg"""

    def get_supported_extensions(self) -> List[str]:
        """MP4 and related format support"""
        return ['.mp4', '.m4v']

    def check_tools_available(self) -> bool:
        """Verify FFmpeg installation"""
        try:
            subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("FFmpeg not found. Please install FFmpeg.")
            return False

    def get_track_info(self, video_path: str) -> Dict:
        """Get MP4 track information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get MP4 track info: {e}")
            raise

    def get_subtitle_tracks(self, video_path: str) -> List[Dict]:
        """Extract subtitle track information from MP4"""
        info = self.get_track_info(video_path)
        subtitle_tracks = []

        subtitle_index = 0  # Counter for subtitle streams only
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'subtitle':
                subtitle_tracks.append({
                    'id': subtitle_index,  # Use subtitle-specific index
                    'codec': stream.get('codec_name', 'unknown'),
                    'language': stream.get('tags', {}).get('language', 'und'),
                    'track_name': stream.get('tags', {}).get('title', ''),
                    'default': stream.get('disposition', {}).get('default', False)
                })
                subtitle_index += 1

        return subtitle_tracks

    def extract_subtitle_track(self, video_path: str, track_id: int, output_path: str) -> bool:
        """Extract subtitle track using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-map', f'0:s:{track_id}',  # Map subtitle stream by index
                '-c:s', 'ass',              # Convert to ASS format
                '-y', output_path           # Overwrite output
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Extracted MP4 subtitle track {track_id}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to extract MP4 subtitle: {e}")
            return False

    def merge_video_with_subtitles(self, input_video: str, subtitle_file: str,
                                 output_video: str, subtitle_language: str = "eng",
                                 subtitle_name: str = "Styled Subtitles") -> bool:
        """Merge MP4 with new subtitles using ffmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_video,                           # Input MP4
                '-i', subtitle_file,                         # Input subtitle
                '-map', '0:v', '-map', '0:a', '-map', '1:s', # Map video, audio, subtitle
                '-c:v', 'copy',                              # Copy video (no re-encode)
                '-c:a', 'copy',                              # Copy audio (no re-encode)
                '-c:s', 'mov_text',                          # Use MP4 subtitle format
                '-metadata:s:s:0', f'language={subtitle_language}',
                '-metadata:s:s:0', f'title={subtitle_name}',
                '-y', output_video                           # Overwrite output
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Merged MP4 with subtitles: {output_video}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to merge MP4: {e}")
            return False

# avi_processor.py

"""
Example AVI Processor Implementation

AVI files are legacy format but still commonly used. This processor
shows how to handle older formats with FFmpeg.

AVI CONSIDERATIONS:

-   Legacy format with limited subtitle support
-   Often requires conversion to modern formats
-   May have embedded subtitle tracks
-   Usually requires FFmpeg for processing
    """

class AVIProcessor(VideoProcessorBase):
"""AVI File Format Processor"""

    def get_supported_extensions(self) -> List[str]:
        return ['.avi']

    def check_tools_available(self) -> bool:
        """AVI processing requires FFmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("FFmpeg required for AVI processing")
            return False

    # ... implement other methods following the same pattern as MP4Processor
    # Most AVI files will use similar FFmpeg commands to MP4

# webm_processor.py

"""
Example WebM Processor Implementation

WebM is a modern web-oriented format. This shows how to handle
web-optimized video formats.

WEBM CHARACTERISTICS:

-   Open source format
-   Optimized for web streaming
-   Uses VP8/VP9 video and Vorbis/Opus audio
-   Limited subtitle format support
    """

class WebMProcessor(VideoProcessorBase):
"""WebM File Format Processor"""

    def get_supported_extensions(self) -> List[str]:
        return ['.webm']

    # ... implement using FFmpeg similar to MP4Processor

# How to Register New Processors

"""
STEP 1: Create your processor class (as shown above)

STEP 2: Register it in video_processor_factory.py

Simply add ONE LINE to the \_register_default_processors method:
"""

def \_register_default_processors(self):
"""Register built-in video format processors""" # Existing processors
self.register_processor(MKVProcessor())

    # NEW PROCESSORS - Just add these lines!
    self.register_processor(MP4Processor())     # Enable MP4 support
    self.register_processor(AVIProcessor())     # Enable AVI support
    self.register_processor(WebMProcessor())    # Enable WebM support

"""
STEP 3: That's it! The entire system now supports your new formats:

✅ GUI automatically shows new formats in supported list
✅ CLI accepts new file types as input
✅ Universal processor routes to your implementation
✅ Factory manages your processor lifecycle
✅ Error handling works consistently
✅ Logging uses your processor's namespace

No changes needed anywhere else in the system!
"""

# Advanced Extension Examples

## streaming_processor.py

"""
Example Streaming/URL Processor

This shows how the system could be extended to support streaming
sources like YouTube, Twitch, or other online video platforms.

STREAMING CONCEPTS:

-   Input is URL instead of file path
-   Download temporary video file
-   Extract and process subtitles
-   Upload styled subtitles back (optional)

TOOLS INTEGRATION:

-   youtube-dl or yt-dlp for video download
-   Same subtitle processing pipeline
-   Cloud storage for temporary files
    """

class StreamingProcessor(VideoProcessorBase):
"""Streaming Video Source Processor"""

    def get_supported_extensions(self) -> List[str]:
        # Use custom "extensions" for URL patterns
        return ['.youtube', '.twitch', '.vimeo']

    def can_process(self, file_path: str) -> bool:
        """Override to detect URLs instead of file extensions"""
        url_patterns = [
            'youtube.com', 'youtu.be',
            'twitch.tv',
            'vimeo.com'
        ]
        return any(pattern in file_path.lower() for pattern in url_patterns)

    def check_tools_available(self) -> bool:
        """Check for streaming download tools"""
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['youtube-dl', '--version'], capture_output=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error("yt-dlp or youtube-dl required for streaming")
                return False

    # ... implement other methods with streaming-specific logic

## batch_processor.py

"""
Example Batch Processing Enhancement

Shows how to extend the system for advanced batch operations
like processing entire TV seasons or movie collections.

BATCH FEATURES:

-   Process multiple files with different configurations
-   Apply series-specific styling rules
-   Generate consistent output naming
-   Handle errors gracefully in large batches
    """

class BatchProcessor:
"""Enhanced batch processing capabilities"""

    def __init__(self, base_processor):
        self.base_processor = base_processor
        self.batch_configs = {}

    def add_batch_rule(self, pattern: str, config_path: str):
        """Add styling rule for files matching pattern"""
        self.batch_configs[pattern] = config_path

    def process_directory(self, directory: str, output_dir: str = None):
        """Process all compatible files in directory with smart config selection"""
        # Implementation would:
        # 1. Scan directory for video files
        # 2. Match files to configuration rules
        # 3. Process each file with appropriate config
        # 4. Generate organized output structure
        pass

## cloud_processor.py

"""
Example Cloud Integration

Shows how the system could be extended for cloud-based processing
using services like AWS, Google Cloud, or Azure.

CLOUD BENEFITS:

-   Process large files without local storage
-   Parallel processing of multiple files
-   Integration with cloud storage services
-   Scalable processing power
    """

class CloudProcessor(VideoProcessorBase):
"""Cloud-based video processing"""

    def __init__(self, cloud_provider='aws'):
        super().__init__()
        self.cloud_provider = cloud_provider
        self.setup_cloud_client()

    def setup_cloud_client(self):
        """Initialize cloud service connections"""
        # Would initialize AWS S3, Google Cloud Storage, etc.
        pass

    def process_cloud_file(self, cloud_url: str, config: Dict) -> str:
        """Process file stored in cloud storage"""
        # Implementation would:
        # 1. Download file from cloud storage
        # 2. Process locally or on cloud instances
        # 3. Upload processed file back to cloud
        # 4. Return cloud URL of processed file
        pass

# Plugin Architecture Example

"""
For even more extensibility, the system could support a plugin architecture:

## plugins/**init**.py

# Plugin discovery and loading

## plugins/custom_processor.py

# User-created processor plugins

## plugins/effects_processor.py

# Special effects and advanced styling

PLUGIN BENEFITS:

-   Third-party extensions
-   Community-contributed processors
-   Specialized industry formats
-   Custom business logic

PLUGIN REGISTRATION:
The factory could be enhanced to automatically discover
and register plugins from a plugins directory.
"""

def discover_plugins():
"""Automatically discover and register plugin processors"""
import importlib
import pkgutil

    # Scan plugins directory
    for finder, name, ispkg in pkgutil.iter_modules(['plugins']):
        module = importlib.import_module(f'plugins.{name}')

        # Look for processor classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, VideoProcessorBase) and
                attr != VideoProcessorBase):
                # Register discovered processor
                factory.register_processor(attr())

# Configuration-Driven Processors

"""
For ultimate flexibility, processors could be configuration-driven:

## config/mp4_config.json

{
"processor_name": "MP4Processor",
"tools": {
"info": ["ffprobe", "-v", "quiet", "-print_format", "json"],
"extract": ["ffmpeg", "-i", "{input}", "-map", "0:s:{track}", "{output}"],
"merge": ["ffmpeg", "-i", "{video}", "-i", "{subtitle}", "-c:v", "copy"]
},
"extensions": [".mp4", ".m4v"],
"subtitle_formats": ["mov_text", "srt"]
}

This would allow adding new formats without writing any Python code!
"""

# Real-World Extension Scenarios

"""
SCENARIO 1: Broadcasting Company

-   Needs support for proprietary formats
-   Requires specific styling standards
-   Wants integration with existing workflows

SOLUTION: Create custom processors for proprietary formats,
extend styling system with company-specific templates,
add API endpoints for workflow integration.

SCENARIO 2: Educational Institution

-   Processes lecture recordings
-   Needs accessibility compliance
-   Wants batch processing capabilities

SOLUTION: Add accessibility-focused styling configs,
create batch processor for course materials,
integrate with learning management systems.

SCENARIO 3: Streaming Platform

-   Processes user uploads
-   Needs cloud scalability
-   Requires multiple output formats

SOLUTION: Implement cloud processors,
add multi-format output capability,
create streaming-optimized subtitle formats.

SCENARIO 4: Post-Production House

-   Works with many exotic formats
-   Needs frame-accurate timing
-   Requires professional effects

SOLUTION: Add specialized format processors,
integrate with professional timing tools,
extend Aegisub integration for complex effects.
"""

"""
The beauty of this extensible architecture is that ALL of these scenarios
can be supported by creating new processor classes and registering them
with the factory. The core system remains unchanged while supporting
unlimited specialized use cases.

This is the power of good architectural design - infinite extensibility
with minimal complexity!
"""
