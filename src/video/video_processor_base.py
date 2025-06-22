# video_processor_base.py
"""
Video Processor Base Class - Abstract Interface Contract

This file defines the abstract base class that establishes the interface contract
for all video format processors in the system. It ensures consistency across
different format implementations and enables the extensible architecture.

ARCHITECTURE ROLE:
This is the foundational interface layer that sits at the bottom of the processor
hierarchy. It defines the contract that all concrete processors must implement,
enabling polymorphism and ensuring consistent behavior across formats.

DESIGN PATTERN:
Implements the Template Method pattern through abstract methods, and enables
the Strategy pattern by providing a common interface for different processing
strategies (MKV, MP4, AVI, etc.).

SYSTEM INTEGRATION:
- Inherited by: All concrete processor classes (MKVProcessor, MP4Processor, etc.)
- Used by: VideoProcessorFactory for type checking and interface guarantees
- Enables: Polymorphic behavior in UniversalVideoProcessor
- Defines: The minimum interface required for format support

EXTENSIBILITY FOUNDATION:
This abstract base class is what makes the system so easily extensible. To add
support for a new video format, you simply:
1. Create a class that inherits from VideoProcessorBase
2. Implement all the abstract methods
3. Register it with the factory
The entire system automatically supports the new format!

KEY PRINCIPLES:
1. **Interface Segregation**: Only includes methods essential for video processing
2. **Liskov Substitution**: All implementations can be used interchangeably
3. **Open/Closed Principle**: Open for extension, closed for modification
4. **Dependency Inversion**: Higher-level code depends on abstractions
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import logging


class VideoProcessorBase(ABC):
    """
    Abstract Base Class for Video Format Processors
    
    This class defines the essential interface that all video format processors
    must implement. It serves as the architectural foundation that enables the
    system's extensible design and ensures consistent behavior across formats.
    
    ABSTRACT BASE CLASS BENEFITS:
    1. **Enforced Interface**: Guarantees all processors implement required methods
    2. **Type Safety**: Enables static type checking and IDE support
    3. **Documentation Contract**: Clearly defines what each processor must do
    4. **Polymorphic Usage**: All processors can be used interchangeably
    5. **Future Proofing**: New methods can be added with default implementations
    
    INHERITANCE REQUIREMENTS:
    Any class inheriting from VideoProcessorBase MUST implement all abstract
    methods marked with @abstractmethod. Failure to do so will result in a
    TypeError when attempting to instantiate the class.
    
    IMPLEMENTATION GUIDELINES:
    - Each method should handle its specific format optimally
    - Error handling should be consistent across implementations
    - Logging should use the inherited logger for consistency
    - Return types and formats should match the interface exactly
    
    EXTENSIBILITY PATTERN:
    To add support for a new video format:
    
    ```python
    class NewFormatProcessor(VideoProcessorBase):
        def get_supported_extensions(self) -> List[str]:
            return ['.newformat']
        
        def check_tools_available(self) -> bool:
            # Check for format-specific tools
            return True
        
        # ... implement all other abstract methods
    ```
    """
    
    def __init__(self):
        """
        Initialize the Video Processor Base
        
        Sets up logging using the class name as the logger identifier.
        This ensures each concrete processor has its own logger namespace
        for easy debugging and log filtering.
        
        LOGGING STRATEGY:
        - Each processor class gets its own logger
        - Logger names reflect the actual implementation class
        - Enables fine-grained log level control per format
        
        Example Logger Names:
        - MKVProcessor → 'MKVProcessor'
        - MP4Processor → 'MP4Processor'
        """
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get File Extensions Supported by This Processor
        
        Returns a list of file extensions that this processor can handle.
        Extensions should include the leading dot and be lowercase.
        
        IMPLEMENTATION REQUIREMENTS:
        - Must return at least one extension
        - Extensions must include the leading dot (e.g., '.mkv', not 'mkv')
        - Extensions should be lowercase for consistency
        - Multiple extensions are allowed for related formats
        
        EXTENSION EXAMPLES:
        - Video formats: ['.mkv'], ['.mp4', '.m4v'], ['.avi']
        - Audio formats: ['.mka'], ['.m4a']
        - Container variants: ['.mov', '.qt']
        
        Returns:
            List[str]: File extensions supported by this processor
            
        Example Implementation:
            def get_supported_extensions(self) -> List[str]:
                return ['.mkv']  # MKV processor
                # or
                return ['.mp4', '.m4v']  # MP4 processor with variants
        """
        pass
    
    @abstractmethod
    def check_tools_available(self) -> bool:
        """
        Check if Required External Tools are Available
        
        Verifies that all external tools required by this processor are
        installed and accessible. This is critical for ensuring the
        processor can actually perform its operations.
        
        VALIDATION STRATEGY:
        - Test actual tool execution (not just file existence)
        - Use harmless commands like --version or --help
        - Check all tools required for complete functionality
        - Return False if any required tool is missing
        
        TOOL EXAMPLES BY FORMAT:
        - MKV: mkvinfo, mkvextract, mkvmerge (MKVToolNix)
        - MP4: ffmpeg, ffprobe (FFmpeg)
        - AVI: ffmpeg, avidemux (format-specific tools)
        
        ERROR HANDLING:
        - Log helpful error messages indicating which tools are missing
        - Provide installation guidance in log messages
        - Handle both missing tools and permission issues
        
        Returns:
            bool: True if all required tools are available, False otherwise
            
        Example Implementation:
            def check_tools_available(self) -> bool:
                try:
                    subprocess.run(['mkvinfo', '--version'], 
                                 capture_output=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.logger.error("MKVToolNix not found. Please install MKVToolNix.")
                    return False
        """
        pass
    
    @abstractmethod
    def get_track_info(self, video_path: str) -> Dict:
        """
        Get Comprehensive Track Information from Video File
        
        Extracts detailed information about all tracks (video, audio, subtitles)
        in the video file. This raw information is used by other methods to
        provide more specific track details.
        
        INFORMATION SCOPE:
        - All track types: video, audio, subtitles, chapters, attachments
        - Track metadata: codecs, languages, names, properties
        - Container metadata: duration, file size, creation info
        - Technical details: resolutions, bitrates, frame rates
        
        RETURN FORMAT:
        The exact structure depends on the format and tools used, but should
        include at minimum:
        - List of tracks with their types and IDs
        - Codec information for each track
        - Language and naming metadata where available
        
        ERROR HANDLING:
        - Raise appropriate exceptions for file access errors
        - Handle corrupted or incomplete files gracefully
        - Provide meaningful error messages for debugging
        
        Args:
            video_path (str): Path to the video file to analyze
            
        Returns:
            Dict: Complete track and metadata information
            
        Raises:
            Various exceptions depending on implementation and tool used
            
        Example Implementation:
            def get_track_info(self, video_path: str) -> Dict:
                cmd = ['mkvmerge', '-J', video_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return json.loads(result.stdout)
        """
        pass
    
    @abstractmethod
    def get_subtitle_tracks(self, video_path: str) -> List[Dict]:
        """
        Get Subtitle Track Information from Video File
        
        Extracts and standardizes information about all subtitle tracks in
        the video file. This method filters the complete track information
        to focus specifically on subtitle tracks.
        
        STANDARDIZED FORMAT:
        Each subtitle track dictionary must contain:
        - id: Track identifier used for extraction (int or str)
        - codec: Subtitle format (e.g., 'ass', 'srt', 'vobsub')
        - language: ISO language code (e.g., 'eng', 'spa', 'und')
        - track_name: Human-readable track description (str, can be empty)
        - default: Whether this track is marked as default (bool)
        
        LANGUAGE CODES:
        - Use ISO 639-2/B three-letter codes when available
        - Fall back to 'und' (undetermined) for missing language info
        - Preserve original language metadata from the file
        
        TRACK IDENTIFICATION:
        - IDs must be suitable for use with extract_subtitle_track()
        - Should be stable and reliable for the specific format
        - May be numeric or string depending on the underlying tool
        
        Args:
            video_path (str): Path to the video file to analyze
            
        Returns:
            List[Dict]: Standardized subtitle track information
            
        Example Return Value:
            [
                {
                    'id': 2,
                    'codec': 'ass',
                    'language': 'eng', 
                    'track_name': 'English (Full)',
                    'default': True
                },
                {
                    'id': 3,
                    'codec': 'srt',
                    'language': 'spa',
                    'track_name': 'Spanish',
                    'default': False
                }
            ]
        """
        pass
    
    @abstractmethod
    def extract_subtitle_track(self, video_path: str, track_id: int, 
                             output_path: str) -> bool:
        """
        Extract a Specific Subtitle Track from Video File
        
        Extracts a single subtitle track from the video file and saves it
        to the specified output path. The extraction should preserve the
        original subtitle format without conversion.
        
        EXTRACTION REQUIREMENTS:
        - Must extract in native format (no format conversion)
        - Should preserve all subtitle metadata and styling
        - Must be compatible with track IDs from get_subtitle_tracks()
        - Should handle various subtitle formats (ASS, SRT, VobSub, etc.)
        
        FORMAT PRESERVATION:
        - ASS subtitles: Extract with all styling and effects intact
        - SRT subtitles: Preserve timing and basic formatting
        - VobSub subtitles: Extract both .sub and .idx files if needed
        - Other formats: Maintain format-specific features
        
        ERROR HANDLING:
        - Return False for any extraction failure
        - Log specific error messages for troubleshooting
        - Handle missing tracks, file permission issues, etc.
        - Validate track_id corresponds to an actual subtitle track
        
        Args:
            video_path (str): Path to the source video file
            track_id (int): ID of the subtitle track to extract
            output_path (str): Path where extracted subtitle should be saved
            
        Returns:
            bool: True if extraction succeeded, False otherwise
            
        Example Implementation:
            def extract_subtitle_track(self, video_path: str, track_id: int, 
                                     output_path: str) -> bool:
                try:
                    cmd = ['mkvextract', video_path, 'tracks', f"{track_id}:{output_path}"]
                    subprocess.run(cmd, capture_output=True, check=True)
                    return True
                except subprocess.CalledProcessError:
                    return False
        """
        pass
    
    @abstractmethod
    def merge_video_with_subtitles(self, input_video: str, subtitle_file: str, 
                                 output_video: str, subtitle_language: str = "eng",
                                 subtitle_name: str = "Styled Subtitles") -> bool:
        """
        Merge Video with New Subtitle File
        
        Creates a new video file that combines the original video/audio content
        with a new subtitle track. This operation should preserve video quality
        and remove any existing subtitle tracks.
        
        QUALITY PRESERVATION REQUIREMENTS:
        - Video streams: Copy without re-encoding (lossless)
        - Audio streams: Copy without re-encoding (lossless)
        - Container metadata: Preserve where possible
        - File size: Minimize increase (only subtitle data added)
        
        SUBTITLE INTEGRATION:
        - Remove all existing subtitle tracks to avoid conflicts
        - Add new subtitle as the primary/default track
        - Set appropriate language metadata
        - Configure track naming for media player display
        
        METADATA CONFIGURATION:
        - subtitle_language: ISO 639-2 language code (eng, spa, fra, etc.)
        - subtitle_name: Display name for media players
        - Default track: Mark new subtitle as default for auto-selection
        
        FORMAT COMPATIBILITY:
        - Output format should match input format when possible
        - Handle format-specific subtitle integration requirements
        - Ensure compatibility with common media players
        
        Args:
            input_video (str): Path to the original video file
            subtitle_file (str): Path to the subtitle file to merge
            output_video (str): Path for the final merged video file
            subtitle_language (str): ISO language code for subtitle metadata
            subtitle_name (str): Human-readable name for the subtitle track
            
        Returns:
            bool: True if merging succeeded, False otherwise
            
        Example Implementation:
            def merge_video_with_subtitles(self, input_video: str, subtitle_file: str,
                                         output_video: str, subtitle_language: str = "eng",
                                         subtitle_name: str = "Styled Subtitles") -> bool:
                try:
                    cmd = ['mkvmerge', '-o', output_video, '--no-subtitles', 
                           input_video, '--language', f'0:{subtitle_language}',
                           '--track-name', f'0:{subtitle_name}', subtitle_file]
                    subprocess.run(cmd, capture_output=True, check=True)
                    return True
                except subprocess.CalledProcessError:
                    return False
        """
        pass
    
    def can_process(self, file_path: str) -> bool:
        """
        Check if This Processor Can Handle the Given File
        
        Convenience method that checks if a file can be processed by this
        processor based on its file extension. This method is provided
        with a default implementation that uses get_supported_extensions().
        
        DEFAULT IMPLEMENTATION:
        This method is NOT abstract because it has a sensible default
        implementation that works for most processors. Concrete classes
        can override it if they need more sophisticated file detection.
        
        EXTENSION-BASED DETECTION:
        The default implementation:
        1. Extracts the file extension from the path
        2. Normalizes it to lowercase
        3. Checks if it's in the supported extensions list
        
        OVERRIDE SCENARIOS:
        Processors might override this method to:
        - Perform content-based file detection
        - Handle files with missing or incorrect extensions
        - Implement more sophisticated format validation
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if this processor can handle the file
            
        Example Override:
            def can_process(self, file_path: str) -> bool:
                # First check extension
                if not super().can_process(file_path):
                    return False
                # Then check file content
                return self._validate_file_format(file_path)
        """
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_extensions()