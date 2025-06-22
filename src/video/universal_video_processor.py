# universal_video_processor.py
"""
Universal Video Processor - Format-Agnostic Interface

This file provides a unified interface for video processing that automatically
delegates to the appropriate format-specific processor. It acts as the main
entry point for all video operations in the system.

ARCHITECTURE ROLE:
This is the abstraction layer that hides the complexity of different video
formats from the higher-level components. It provides a single, consistent
interface regardless of whether you're processing MKV, MP4, AVI, or any other
format.

DESIGN PATTERN:
Implements the Facade pattern, providing a simplified interface to the complex
subsystem of format-specific processors. Also uses the Delegation pattern to
forward requests to the appropriate specialized processor.

SYSTEM INTEGRATION:
- Used by: main.py and gui.py for all video operations
- Uses: VideoProcessorFactory to select appropriate processors
- Coordinates: All format-specific processors through a common interface

EXTENSIBILITY:
When new video formats are added to the system, this class automatically
supports them without any code changes. The factory pattern handles processor
registration and selection transparently.

KEY BENEFITS:
1. **Format Transparency**: Higher-level code doesn't need to know about specific formats
2. **Automatic Delegation**: Requests are automatically routed to the right processor
3. **Unified Error Handling**: Consistent error reporting across all formats
4. **Tool Management**: Centralized checking of all required processing tools
"""

from typing import List, Dict, Optional
import logging
from .video_processor_factory import VideoProcessorFactory


class UniversalVideoProcessor:
    """
    Universal Video Processing Interface
    
    This class provides a single, unified interface for processing video files
    of any supported format. It automatically determines the correct processor
    to use based on the file extension and delegates all operations appropriately.
    
    DELEGATION STRATEGY:
    Rather than implementing video processing logic directly, this class acts
    as an intelligent dispatcher that:
    1. Analyzes the file format
    2. Selects the appropriate specialized processor
    3. Delegates the operation to that processor
    4. Returns the results in a consistent format
    
    PROCESSOR LIFECYCLE:
    1. Initialize with factory containing all available processors
    2. Receive processing request from higher-level component
    3. Determine file format and select appropriate processor
    4. Delegate operation to selected processor
    5. Return standardized results
    
    ERROR HANDLING:
    Provides consistent error handling across all formats. If a specific
    processor fails, the error is caught and returned in a standardized format.
    """
    
    def __init__(self):
        """
        Initialize the Universal Processor
        
        Creates the processor factory which automatically registers all
        available format-specific processors. The factory handles all
        the complexity of processor management and selection.
        """
        self.logger = logging.getLogger(__name__)
        
        # Create factory containing all available processors
        # The factory automatically discovers and registers format processors
        self.factory = VideoProcessorFactory()
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get All Supported File Extensions
        
        Returns a comprehensive list of all file extensions that can be
        processed by the system. This list is dynamically generated from
        all registered processors.
        
        DYNAMIC UPDATES:
        As new format processors are added to the system, this list
        automatically includes their supported extensions without any
        code changes to this class.
        
        Returns:
            List[str]: All supported file extensions (e.g., ['.mkv', '.mp4', '.avi'])
            
        Usage Example:
            processor = UniversalVideoProcessor()
            formats = processor.get_supported_extensions()
            print(f"Supported formats: {', '.join(formats)}")
        """
        return self.factory.get_supported_extensions()
    
    def can_process(self, file_path: str) -> bool:
        """
        Check if a File Can Be Processed
        
        Determines whether the system has a processor capable of handling
        the specified file. This is a quick check based on file extension
        and processor availability.
        
        VALIDATION LOGIC:
        1. Extract file extension from path
        2. Check if any registered processor supports this extension
        3. Return boolean result
        
        Args:
            file_path (str): Path to the video file to check
            
        Returns:
            bool: True if the file can be processed, False otherwise
            
        Usage Example:
            if processor.can_process("movie.mkv"):
                print("This file can be processed!")
            else:
                print("Unsupported format")
        """
        return self.factory.can_process(file_path)
    
    def check_tools_available(self) -> Dict[str, bool]:
        """
        Check Availability of All Processing Tools
        
        Verifies that all required external tools (MKVToolNix, FFmpeg, etc.)
        are installed and accessible. This is essential for ensuring the
        system can actually perform processing operations.
        
        COMPREHENSIVE CHECKING:
        - Iterates through all registered processors
        - Checks each processor's tool requirements
        - Returns a detailed status report
        - Avoids duplicate checks for tools used by multiple processors
        
        TOOL MANAGEMENT:
        Different processors may require different tools:
        - MKVProcessor requires MKVToolNix
        - MP4Processor might require FFmpeg
        - Future processors might require other tools
        
        Returns:
            Dict[str, bool]: Mapping of processor names to tool availability status
            
        Example Return Value:
            {
                'MKVProcessor': True,     # MKVToolNix is available
                'MP4Processor': False,    # FFmpeg is missing
                'AVIProcessor': True      # Required tools are available
            }
            
        Usage Example:
            tools = processor.check_tools_available()
            if not any(tools.values()):
                print("No video processing tools are available!")
            else:
                available = [name for name, status in tools.items() if status]
                print(f"Available processors: {', '.join(available)}")
        """
        tools_status = {}
        
        # Check each registered processor type
        for ext in self.factory.get_supported_extensions():
            processor = self.factory.get_processor(f"dummy{ext}")
            if processor:
                processor_name = processor.__class__.__name__
                # Avoid duplicate checks for the same processor type
                if processor_name not in tools_status:
                    tools_status[processor_name] = processor.check_tools_available()
        
        return tools_status
    
    def get_subtitle_tracks(self, video_path: str) -> List[Dict]:
        """
        Get Subtitle Tracks from Any Video Format
        
        Extracts information about all subtitle tracks in a video file,
        regardless of the video format. The specific extraction method
        is handled by the appropriate format processor.
        
        UNIVERSAL EXTRACTION:
        - Determines video format automatically
        - Selects appropriate processor for the format
        - Returns standardized track information
        - Handles format-specific differences transparently
        
        TRACK INFORMATION:
        Each track dictionary contains:
        - id: Track identifier for extraction
        - codec: Subtitle format (SRT, ASS, VTT, etc.)
        - language: Language code (e.g., 'eng', 'spa', 'und')
        - track_name: Human-readable track name
        - default: Whether this is the default track
        
        Args:
            video_path (str): Path to the video file to analyze
            
        Returns:
            List[Dict]: List of subtitle track information dictionaries
            
        Raises:
            ValueError: If no processor is available for the file format
            
        Usage Example:
            tracks = processor.get_subtitle_tracks("movie.mkv")
            for track in tracks:
                print(f"Track {track['id']}: {track['language']} ({track['codec']})")
        """
        processor = self.factory.get_processor(video_path)
        if not processor:
            raise ValueError(f"No processor available for {video_path}")
        
        return processor.get_subtitle_tracks(video_path)
    
    def extract_subtitle_track(self, video_path: str, track_id: int, 
                             output_path: str) -> bool:
        """
        Extract a Subtitle Track from Any Video Format
        
        Extracts a specific subtitle track from a video file and saves it
        to the specified output path. The extraction method is automatically
        selected based on the video format.
        
        FORMAT-SPECIFIC HANDLING:
        - MKV files: Uses MKVToolNix for precise track extraction
        - MP4 files: Uses FFmpeg for universal compatibility
        - Other formats: Uses appropriate format-specific tools
        
        EXTRACTION PROCESS:
        1. Determine video format from file extension
        2. Select appropriate processor for the format
        3. Delegate extraction to the specialized processor
        4. Return success/failure status
        
        Args:
            video_path (str): Path to the source video file
            track_id (int): ID of the subtitle track to extract
            output_path (str): Path where extracted subtitle should be saved
            
        Returns:
            bool: True if extraction succeeded, False otherwise
            
        Usage Example:
            success = processor.extract_subtitle_track(
                "movie.mkv", 
                track_id=2, 
                "subtitles.ass"
            )
            if success:
                print("Subtitle track extracted successfully!")
        """
        processor = self.factory.get_processor(video_path)
        if not processor:
            self.logger.error(f"No processor available for {video_path}")
            return False
        
        return processor.extract_subtitle_track(video_path, track_id, output_path)
    
    def merge_video_with_subtitles(self, input_video: str, subtitle_file: str, 
                                 output_video: str, subtitle_language: str = "eng",
                                 subtitle_name: str = "Styled Subtitles") -> bool:
        """
        Merge Subtitles Back into Any Video Format
        
        Takes a video file and a styled subtitle file and merges them together,
        creating a new video file with the subtitles embedded. The merging
        process is format-specific but the interface is universal.
        
        FORMAT PRESERVATION:
        The output video maintains the same format as the input video:
        - MKV input → MKV output (using MKVToolNix)
        - MP4 input → MP4 output (using FFmpeg)
        - Maintains video/audio quality and metadata
        
        SUBTITLE INTEGRATION:
        - Removes all existing subtitle tracks
        - Adds the new styled subtitle track
        - Sets appropriate metadata (language, track name)
        - Makes the new track the default subtitle track
        
        QUALITY PRESERVATION:
        - Video streams are copied without re-encoding
        - Audio streams are copied without re-encoding
        - Only subtitle tracks are modified/replaced
        - Maintains file size and quality
        
        Args:
            input_video (str): Path to the original video file
            subtitle_file (str): Path to the styled subtitle file (usually ASS)
            output_video (str): Path for the final merged video file
            subtitle_language (str): Language code for the subtitle track
            subtitle_name (str): Human-readable name for the subtitle track
            
        Returns:
            bool: True if merging succeeded, False otherwise
            
        Usage Example:
            success = processor.merge_video_with_subtitles(
                input_video="movie.mkv",
                subtitle_file="styled_subtitles.ass",
                output_video="movie_with_subtitles.mkv",
                subtitle_language="eng",
                subtitle_name="English (Styled)"
            )
            if success:
                print("Video merged successfully with styled subtitles!")
        """
        processor = self.factory.get_processor(input_video)
        if not processor:
            self.logger.error(f"No processor available for {input_video}")
            return False
        
        return processor.merge_video_with_subtitles(
            input_video, subtitle_file, output_video, 
            subtitle_language, subtitle_name
        )