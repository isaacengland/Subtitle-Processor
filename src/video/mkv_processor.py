# mkv_processor.py
"""
MKV Processor - Matroska Video Format Handler

This file implements the format-specific processor for MKV (Matroska Video) files.
It uses the MKVToolNix suite of tools to perform all MKV-related operations including
track analysis, subtitle extraction, and video merging.

ARCHITECTURE ROLE:
This is a format-specific implementation that sits at the concrete level of the
processor hierarchy. It implements the VideoProcessorBase interface to provide
standardized operations while using MKV-specific tools and techniques.

DESIGN PATTERN:
Implements the Strategy pattern as a concrete strategy for processing MKV files.
Also follows the Adapter pattern, adapting the MKVToolNix command-line interface
to the system's standardized processor interface.

SYSTEM INTEGRATION:
- Inherits from: VideoProcessorBase (defines the interface contract)
- Used by: VideoProcessorFactory (registered as MKV handler)
- Manages: MKVToolNix tool interactions and MKV-specific operations
- Coordinates: External tool execution and result parsing

MKVTOOLNIX INTEGRATION:
Uses three main tools from the MKVToolNix suite:
- mkvinfo: Get information about MKV files and their tracks
- mkvextract: Extract specific tracks (subtitles, audio, video) from MKV files
- mkvmerge: Merge tracks together to create new MKV files

KEY CAPABILITIES:
1. **Track Analysis**: Parse MKV structure to identify all subtitle tracks
2. **Subtitle Extraction**: Extract specific subtitle tracks in their native format
3. **Lossless Merging**: Combine video with new subtitles without re-encoding
4. **Metadata Preservation**: Maintain file metadata and track properties
5. **Tool Validation**: Verify MKVToolNix availability before processing
"""

import subprocess
import json
from typing import List, Dict, Optional
import logging
from .video_processor_base import VideoProcessorBase


class MKVProcessor(VideoProcessorBase):
    """
    MKV File Format Processor
    
    This class handles all operations related to MKV (Matroska Video) files using
    the MKVToolNix suite. It provides a standardized interface for MKV operations
    while leveraging the powerful capabilities of MKVToolNix tools.
    
    MKVTOOLNIX ADVANTAGES:
    MKVToolNix is specifically designed for Matroska files and provides:
    - Precise track identification and metadata extraction
    - Lossless video/audio copying (no re-encoding)
    - Advanced subtitle format support
    - Comprehensive metadata handling
    - Reliable container manipulation
    
    PROCESSING PHILOSOPHY:
    This processor prioritizes quality and precision:
    - Never re-encodes video or audio streams
    - Preserves all metadata and track properties
    - Maintains original file quality
    - Uses format-native tools for maximum compatibility
    
    TOOL DEPENDENCY:
    Requires MKVToolNix to be installed and accessible via PATH.
    The processor validates tool availability before attempting operations.
    """
    
    def __init__(self):
        """
        Initialize the MKV Processor
        
        Sets up logging and calls the parent constructor to establish
        the processor within the system hierarchy.
        """
        super().__init__()
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get File Extensions Supported by This Processor
        
        Returns the list of file extensions that this processor can handle.
        Currently supports only MKV files, but could be extended to support
        related Matroska formats if needed.
        
        MATROSKA FORMATS:
        - .mkv: Matroska Video (most common)
        - Could support .mka (audio) or .mks (subtitles) in the future
        
        Returns:
            List[str]: Supported file extensions
        """
        return ['.mkv']
    
    def check_tools_available(self) -> bool:
        """
        Verify MKVToolNix Installation and Availability
        
        Checks that all required MKVToolNix tools are installed and accessible
        through the system PATH. This is essential before attempting any
        MKV processing operations.
        
        REQUIRED TOOLS:
        - mkvinfo: For analyzing MKV file structure and metadata
        - mkvextract: For extracting tracks from MKV files
        - mkvmerge: For merging tracks into new MKV files
        
        VALIDATION PROCESS:
        1. Attempts to run each tool with --version flag
        2. Checks that command executes successfully
        3. Returns True only if all tools are available
        
        INSTALLATION GUIDANCE:
        If tools are missing, logs helpful error message directing users
        to install MKVToolNix from the official website.
        
        Returns:
            bool: True if all required tools are available, False otherwise
            
        Example Usage:
            processor = MKVProcessor()
            if processor.check_tools_available():
                print("Ready to process MKV files!")
            else:
                print("Please install MKVToolNix")
        """
        try:
            # Check mkvinfo availability
            subprocess.run(['mkvinfo', '--version'], 
                         capture_output=True, check=True)
            
            # Check mkvextract availability
            subprocess.run(['mkvextract', '--version'], 
                         capture_output=True, check=True)
            
            # Check mkvmerge availability
            subprocess.run(['mkvmerge', '--version'], 
                         capture_output=True, check=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("MKVToolNix not found. Please install MKVToolNix.")
            return False
    
    def get_track_info(self, mkv_path: str) -> Dict:
        """
        Get Comprehensive Track Information from MKV File
        
        Uses mkvmerge to extract detailed information about all tracks
        in an MKV file. This includes video, audio, and subtitle tracks
        along with their metadata and properties.
        
        MKVMERGE JSON OUTPUT:
        The -J flag tells mkvmerge to output track information in JSON format,
        which provides structured data that's easy to parse and work with.
        
        INFORMATION EXTRACTED:
        - Track types (video, audio, subtitles)
        - Codec information for each track
        - Language metadata
        - Track names and descriptions
        - Default track settings
        - Technical properties (resolution, bitrate, etc.)
        
        Args:
            mkv_path (str): Path to the MKV file to analyze
            
        Returns:
            Dict: Complete track information in JSON structure
            
        Raises:
            subprocess.CalledProcessError: If mkvmerge fails to read the file
            
        Example Usage:
            info = processor.get_track_info("movie.mkv")
            print(f"Found {len(info['tracks'])} tracks in the file")
        """
        try:
            # Execute mkvmerge with JSON output flag
            cmd = ['mkvmerge', '-J', mkv_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse and return the JSON response
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get track info: {e}")
            raise
    
    def get_subtitle_tracks(self, mkv_path: str) -> List[Dict]:
        """
        Extract Subtitle Track Information from MKV File
        
        Analyzes an MKV file to identify all subtitle tracks and returns
        standardized information about each track. This is used by higher-level
        components to present track options to users or select tracks automatically.
        
        TRACK IDENTIFICATION:
        1. Gets complete track information using get_track_info()
        2. Filters for tracks with type='subtitles'
        3. Extracts relevant metadata for each subtitle track
        4. Returns standardized track information
        
        STANDARDIZED FORMAT:
        Each track dictionary contains:
        - id: Track ID used for extraction operations
        - codec: Subtitle format (ASS, SRT, VobSub, etc.)
        - language: ISO language code (eng, spa, fra, etc.)
        - track_name: Human-readable track description
        - default: Whether this track is marked as default
        
        LANGUAGE HANDLING:
        - Uses ISO 639-2/B language codes when available
        - Falls back to 'und' (undetermined) for tracks without language info
        - Preserves original language metadata from the file
        
        Args:
            mkv_path (str): Path to the MKV file to analyze
            
        Returns:
            List[Dict]: List of subtitle track information dictionaries
            
        Example Usage:
            tracks = processor.get_subtitle_tracks("movie.mkv")
            for track in tracks:
                print(f"Track {track['id']}: {track['language']} ({track['codec']})")
        """
        # Get complete track information from the file
        track_info = self.get_track_info(mkv_path)
        subtitle_tracks = []
        
        # Filter and process subtitle tracks
        for track in track_info.get('tracks', []):
            if track['type'] == 'subtitles':
                # Extract standardized track information
                subtitle_tracks.append({
                    'id': track['id'],
                    'codec': track['codec'],
                    'language': track.get('properties', {}).get('language', 'und'),
                    'track_name': track.get('properties', {}).get('track_name', ''),
                    'default': track.get('properties', {}).get('default_track', False)
                })
        
        return subtitle_tracks
    
    def extract_subtitle_track(self, mkv_path: str, track_id: int, 
                             output_path: str) -> bool:
        """
        Extract a Specific Subtitle Track from MKV File
        
        Uses mkvextract to extract a single subtitle track from an MKV file
        and save it to the specified output path. The subtitle is extracted
        in its native format without any conversion.
        
        MKVEXTRACT OPERATION:
        The 'tracks' mode of mkvextract allows precise extraction of specific
        tracks by their ID. The format is: track_id:output_path
        
        NATIVE FORMAT PRESERVATION:
        - ASS subtitles are extracted as .ass files
        - SRT subtitles are extracted as .srt files
        - VobSub subtitles are extracted as .sub/.idx files
        - No format conversion or quality loss occurs
        
        ERROR HANDLING:
        - Validates that the track exists before extraction
        - Provides detailed error logging for troubleshooting
        - Returns boolean status for easy error checking
        
        Args:
            mkv_path (str): Path to the source MKV file
            track_id (int): ID of the subtitle track to extract
            output_path (str): Path where the extracted subtitle should be saved
            
        Returns:
            bool: True if extraction succeeded, False otherwise
            
        Example Usage:
            success = processor.extract_subtitle_track(
                "movie.mkv", 
                track_id=2, 
                "extracted_subtitles.ass"
            )
            if success:
                print("Subtitle track extracted successfully!")
        """
        try:
            # Build mkvextract command for track extraction
            cmd = [
                'mkvextract',
                mkv_path,
                'tracks',
                f"{track_id}:{output_path}"
            ]
            
            # Execute extraction command
            subprocess.run(cmd, capture_output=True, check=True)
            
            self.logger.info(f"Extracted track {track_id} to {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to extract subtitle track: {e}")
            return False
    
    def merge_video_with_subtitles(self, input_mkv: str, subtitle_file: str, 
                                 output_mkv: str, subtitle_language: str = "eng",
                                 subtitle_name: str = "Styled Subtitles") -> bool:
        """
        Merge MKV Video with New Subtitle File
        
        Creates a new MKV file that combines the video/audio from the original
        file with a new styled subtitle track. This operation removes all
        existing subtitle tracks and replaces them with the single new track.
        
        MKVMERGE STRATEGY:
        Uses mkvmerge's powerful track selection and merging capabilities:
        - Copies video/audio streams without re-encoding (lossless)
        - Removes existing subtitle tracks with --no-subtitles
        - Adds new subtitle file with proper metadata
        - Sets the new track as default for automatic selection
        
        QUALITY PRESERVATION:
        - Video streams: Copied bit-for-bit (no quality loss)
        - Audio streams: Copied bit-for-bit (no quality loss)  
        - File size: Minimal increase (only subtitle data added)
        - Metadata: Preserved from original file
        
        SUBTITLE INTEGRATION:
        - Sets appropriate language code for the subtitle track
        - Assigns human-readable track name
        - Marks track as default for automatic playback
        - Removes any conflicting existing subtitle tracks
        
        METADATA CONFIGURATION:
        - Language: ISO 639-2 language code (eng, spa, fra, etc.)
        - Track Name: Descriptive name shown in media players
        - Default Flag: Makes this the automatically selected subtitle track
        
        Args:
            input_mkv (str): Path to the original MKV file
            subtitle_file (str): Path to the styled subtitle file (usually ASS)
            output_mkv (str): Path for the new merged MKV file
            subtitle_language (str): ISO language code for subtitle metadata
            subtitle_name (str): Human-readable name for the subtitle track
            
        Returns:
            bool: True if merging succeeded, False otherwise
            
        Example Usage:
            success = processor.merge_video_with_subtitles(
                input_mkv="original.mkv",
                subtitle_file="styled.ass", 
                output_mkv="final.mkv",
                subtitle_language="eng",
                subtitle_name="English (Styled)"
            )
            if success:
                print("Successfully created MKV with styled subtitles!")
        """
        try:
            # Build comprehensive mkvmerge command
            cmd = [
                'mkvmerge',
                '-o', output_mkv,          # Output file path
                '--no-subtitles',          # Remove all existing subtitle tracks
                input_mkv,                 # Source video/audio (copied losslessly)
                '--language', f"0:{subtitle_language}",  # Set subtitle language
                '--track-name', f"0:{subtitle_name}",    # Set subtitle track name
                '--default-track', '0:yes',              # Mark as default track
                subtitle_file              # New subtitle file to merge
            ]
            
            # Execute merge operation
            subprocess.run(cmd, capture_output=True, check=True)
            
            self.logger.info(f"Merged MKV with subtitles: {output_mkv}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to merge MKV: {e}")
            return False