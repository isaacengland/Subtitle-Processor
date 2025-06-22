# main.py
"""
Universal Subtitle Processor - Main Entry Point

This is the highest-level file in the system and serves as the smart launcher.
It automatically detects whether to launch the GUI or CLI interface.

ARCHITECTURE OVERVIEW:
This file sits at the top of the system hierarchy and orchestrates the entire
subtitle processing workflow. It acts as the bridge between user interaction
and the underlying processing engine.

USAGE:
- Double-click this file to launch the GUI interface
- Run with command-line arguments for CLI mode
- Acts as the single entry point for all user interactions

SYSTEM FLOW:
1. User double-clicks main.py or runs with CLI args
2. This file determines GUI vs CLI mode
3. For GUI: Imports and launches the drag-drop interface
4. For CLI: Parses arguments and runs processing directly
5. Coordinates with UniversalSubtitleProcessor for actual work

DEPENDENCIES:
- Imports the main processor class (UniversalSubtitleProcessor)
- Imports all processor modules through the src package
- Optionally imports GUI components if available

EXTENSIBILITY:
- When adding new features, this file typically doesn't need changes
- New command-line options can be added to the argument parser
- GUI enhancements are handled in src/gui.py
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import List

# Import our main processing engine from the organized package structure
from src.file_utils import FileManager
from src.video import UniversalVideoProcessor
from src.subtitle_processor import SubtitleProcessor as SubtitleStyleProcessor
from src.aegisub_processor import AegisubProcessor


class UniversalSubtitleProcessor:
    """
    Universal Subtitle Processing Engine - The Heart of the System
    
    This class orchestrates the entire subtitle processing workflow for ANY
    supported video format by coordinating between different specialized 
    processors. It acts as the conductor of the orchestra, ensuring each 
    component works together harmoniously.
    
    UNIVERSAL DESIGN:
    Unlike format-specific processors, this class is completely format-agnostic.
    It uses the UniversalVideoProcessor to automatically handle any supported
    video format (MKV, MP4, AVI, etc.) without knowing the specifics.
    
    ROLE IN SYSTEM:
    - **Workflow Orchestration**: Manages the complete processing pipeline
    - **Component Coordination**: Links file management, video processing, and styling
    - **Error Handling**: Provides centralized error handling and logging
    - **Configuration Management**: Handles style configs and processing options
    - **Format Abstraction**: Provides same interface regardless of video format
    
    PROCESSING WORKFLOW:
    1. Validates input files and checks tool availability
    2. Creates temporary workspace for processing
    3. Extracts subtitle tracks from video files (any format)
    4. Converts subtitle formats as needed (SRT/VTT → ASS)
    5. Applies styling (automatic via JSON or manual via Aegisub)
    6. Merges styled subtitles back into video (preserving original format)
    7. Cleans up temporary files
    
    EXTENSIBILITY:
    - Uses UniversalVideoProcessor for format-agnostic video handling
    - Can be extended to support multiple tracks, batch operations, etc.
    - Modular design allows easy addition of new processing steps
    - Works with any video format supported by the processor factory
    """
    
    def __init__(self):
        """
        Initialize the Universal Processing Engine
        
        Sets up logging and creates instances of all specialized processors:
        - FileManager: Handles temporary files and path generation
        - UniversalVideoProcessor: Handles video format detection and processing
        - SubtitleStyleProcessor: Handles subtitle styling and format conversion
        - AegisubProcessor: Handles manual subtitle editing integration
        """
        self.setup_logging()
        
        # Core processing components (all format-agnostic)
        self.file_manager = FileManager()                    # File operations and temp directory management
        self.video_processor = UniversalVideoProcessor()     # Universal video format handling
        self.subtitle_processor = SubtitleStyleProcessor()   # Subtitle styling and format conversion
        self.aegisub_processor = AegisubProcessor()          # Manual editing with Aegisub
        
    def setup_logging(self):
        """
        Configure logging for the entire system.
        
        Sets up a centralized logging system that all components can use.
        Logs are formatted with timestamps and component names for easy debugging.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of all supported video formats.
        
        This method delegates to the UniversalVideoProcessor to get the current
        list of supported formats. As new format processors are added to the
        system, this list automatically updates.
        
        Returns:
            List[str]: File extensions that can be processed (e.g., ['.mkv', '.mp4'])
        """
        return self.video_processor.get_supported_extensions()
    
    def can_process_file(self, file_path: str) -> bool:
        """
        Check if a specific file can be processed by the system.
        
        This is a high-level check that determines file compatibility
        before attempting any processing operations.
        
        Args:
            file_path (str): Path to the video file to check
            
        Returns:
            bool: True if the file can be processed, False otherwise
        """
        return self.video_processor.can_process(file_path)
    
    def process_video_file(self, input_video: str, output_video: str = None, 
                          track_id: int = None, style_config: dict = None,
                          style_config_file: str = None, manual_styling: bool = True) -> bool:
        """
        Main Processing Method - The Universal Workflow
        
        This is the primary method that executes the complete subtitle processing
        pipeline for ANY supported video format. It coordinates all the specialized 
        processors to transform a video file with basic subtitles into one with 
        professionally styled subtitles, preserving the original format.
        
        UNIVERSAL PROCESSING PIPELINE:
        1. **Validation Phase**: Check file existence and tool availability
        2. **Setup Phase**: Create temporary workspace and determine output path
        3. **Analysis Phase**: Extract subtitle track information from video
        4. **Extraction Phase**: Extract the target subtitle track
        5. **Conversion Phase**: Convert subtitle format to ASS if needed
        6. **Styling Phase**: Apply styling (JSON config or manual Aegisub)
        7. **Merging Phase**: Merge styled subtitles back into video (same format)
        8. **Cleanup Phase**: Remove temporary files and report results
        
        FORMAT INDEPENDENCE:
        This method works identically whether processing MKV, MP4, AVI, or any
        other supported format. The UniversalVideoProcessor handles all
        format-specific operations transparently.
        
        Args:
            input_video (str): Path to input video file (any supported format)
            output_video (str, optional): Path for output file. Auto-generated if None.
            track_id (int, optional): Specific subtitle track to process. Uses first if None.
            style_config (dict, optional): Direct styling configuration
            style_config_file (str, optional): Path to JSON configuration file
            manual_styling (bool): Whether to open Aegisub for manual editing
            
        Returns:
            bool: True if processing succeeded, False if any step failed
            
        Raises:
            Exception: Various exceptions can be raised during processing,
                      all are caught and logged with appropriate error messages
        """
        try:
            # === VALIDATION PHASE ===
            # Ensure the input file exists before proceeding
            if not self.file_manager.validate_file_exists(input_video):
                self.logger.error(f"Input file not found: {input_video}")
                return False
            
            # Check that we have the necessary tools available for processing
            tools_status = self.video_processor.check_tools_available()
            if not any(tools_status.values()):
                self.logger.error("No video processing tools available")
                return False
            
            # Verify this file type is supported by our system
            if not self.can_process_file(input_video):
                self.logger.error(f"Unsupported file type: {input_video}")
                return False
            
            # === SETUP PHASE ===
            # Create a temporary directory for intermediate files
            temp_dir = self.file_manager.create_temp_directory()
            
            # Generate output path if not provided by user
            if not output_video:
                output_video = self.file_manager.generate_output_path(input_video)
            
            # === ANALYSIS PHASE ===
            # Extract information about all subtitle tracks in the video
            subtitle_tracks = self.video_processor.get_subtitle_tracks(input_video)
            if not subtitle_tracks:
                self.logger.error("No subtitle tracks found in video file")
                return False
            
            # Select which subtitle track to process
            if track_id is None:
                # Auto-select the first available track
                selected_track = subtitle_tracks[0]
                self.logger.info(f"Auto-selected track {selected_track['id']}")
            else:
                # Use the user-specified track ID
                selected_track = next((t for t in subtitle_tracks if t['id'] == track_id), None)
                if not selected_track:
                    self.logger.error(f"Track {track_id} not found")
                    return False
            
            # === EXTRACTION PHASE ===
            # Extract the selected subtitle track to a temporary file
            extracted_subtitle = os.path.join(temp_dir, f"extracted_{selected_track['id']}.ass")
            if not self.video_processor.extract_subtitle_track(
                input_video, selected_track['id'], extracted_subtitle
            ):
                return False
            
            # === CONVERSION PHASE ===
            # Ensure subtitle is in ASS format for maximum styling capability
            subtitle_format = self.subtitle_processor.detect_subtitle_format(extracted_subtitle)
            if subtitle_format != 'ass':
                ass_subtitle = os.path.join(temp_dir, "converted.ass")
                if not self.subtitle_processor.convert_to_ass(extracted_subtitle, ass_subtitle):
                    return False
                extracted_subtitle = ass_subtitle
            
            # === STYLING PHASE ===
            # Determine which styling configuration to use
            final_style_config = None
            if style_config_file:
                # Load styling from JSON file (preferred method)
                final_style_config = self.subtitle_processor.load_style_config(style_config_file)
                self.logger.info(f"Loaded style configuration from {style_config_file}")
            elif style_config:
                # Use directly provided styling configuration
                final_style_config = style_config
            
            # Apply the styling using the appropriate method
            if manual_styling and self.aegisub_processor.is_available():
                # Manual styling: Open Aegisub for user to edit subtitles
                self.logger.info("Opening Aegisub for manual styling...")
                self.aegisub_processor.open_for_styling(extracted_subtitle)
                input("Press Enter after you've finished styling the subtitles in Aegisub...")
            elif final_style_config:
                # Automatic styling: Apply JSON configuration
                self.subtitle_processor.apply_styling_from_config(extracted_subtitle, final_style_config)
            
            # === MERGING PHASE ===
            # Merge the styled subtitles back into the video file (preserving format)
            success = self.video_processor.merge_video_with_subtitles(
                input_video, extracted_subtitle, output_video
            )
            
            if success:
                self.logger.info(f"Successfully processed video: {output_video}")
            
            return success
            
        except Exception as e:
            # Centralized error handling with detailed logging
            self.logger.error(f"Processing failed: {e}")
            return False
        finally:
            # === CLEANUP PHASE ===
            # Always clean up temporary files, even if processing failed
            self.file_manager.cleanup_temp_directory()


def launch_gui():
    """
    Launch the Graphical User Interface
    
    This function attempts to start the drag-and-drop GUI interface.
    It handles missing dependencies gracefully and provides helpful
    error messages to guide users toward solutions.
    
    DEPENDENCY HANDLING:
    - Checks for tkinterdnd2 (required for drag-and-drop functionality)
    - Provides installation instructions if dependencies are missing
    - Falls back gracefully if GUI cannot be started
    
    Returns:
        bool: True if GUI launched successfully, False otherwise
    """
    try:
        # Import GUI dependencies (may fail if not installed)
        import tkinterdnd2
        from src.gui import SubtitleProcessorGUI
        
        # Create and run the GUI application
        app = SubtitleProcessorGUI()
        return app.run()
    except ImportError:
        # Handle missing dependencies with helpful message
        print("GUI dependencies not available.")
        print("Install with: pip install tkinterdnd2")
        print("Or use command line interface with --help for options.")
        return False
    except Exception as e:
        # Handle other GUI startup errors
        print(f"Error starting GUI: {e}")
        return False


def main():
    """
    Main Entry Point - Smart Mode Detection
    
    This function serves as the intelligent entry point that automatically
    determines whether to launch the GUI or CLI interface based on how
    the script was invoked.
    
    SMART MODE DETECTION:
    - No arguments: Launch GUI interface (user-friendly default)
    - With arguments: Parse and execute CLI commands
    - Special --gui flag: Force GUI mode even with other arguments
    
    This approach provides the best user experience:
    - Double-clicking the file launches the GUI
    - Command-line users get full CLI functionality
    - Power users can force GUI mode when needed
    """
    
    # Check if this is a GUI launch (no command-line arguments)
    if len(sys.argv) == 1:
        print("No command line arguments detected. Launching GUI...")
        success = launch_gui()
        if not success:
            input("Press Enter to exit...")
        return
    
    # === COMMAND-LINE INTERFACE ===
    # Set up argument parser for CLI mode
    parser = argparse.ArgumentParser(
        description="Process video files with styled subtitles",
        epilog="""
Examples:
  python main.py video.mkv                           # Process with GUI config
  python main.py video.mp4 -c config.json           # Use specific config
  python main.py video.avi --no-manual              # Skip Aegisub editing
  python main.py video.mov -o output.mov -t 2       # Specify output and track
        """
    )
    
    # Required arguments
    parser.add_argument("input", 
                       help="Input video file path (any supported format)")
    
    # Optional arguments for fine-tuned control
    parser.add_argument("-o", "--output", 
                       help="Output video file path (auto-generated if not specified)")
    parser.add_argument("-t", "--track", type=int, 
                       help="Subtitle track ID to extract (uses first track if not specified)")
    parser.add_argument("-c", "--config", 
                       help="Path to subtitle style configuration JSON file")
    parser.add_argument("--no-manual", action="store_true", 
                       help="Skip manual styling in Aegisub")
    
    # Quick styling options (alternative to JSON config)
    parser.add_argument("--font-name", 
                       help="Font name for automatic styling")
    parser.add_argument("--font-size", type=int, 
                       help="Font size for automatic styling")
    
    # Mode control
    parser.add_argument("--gui", action="store_true", 
                       help="Force launch GUI mode")
    
    args = parser.parse_args()
    
    # Handle forced GUI mode
    if args.gui:
        success = launch_gui()
        sys.exit(0 if success else 1)
    
    # === COMMAND-LINE PROCESSING ===
    # Prepare style configuration from command-line arguments
    style_config = {}
    if args.font_name:
        style_config['font_name'] = args.font_name
    if args.font_size:
        style_config['font_size'] = args.font_size
    
    # Create and run the universal processor
    processor = UniversalSubtitleProcessor()
    success = processor.process_video_file(
        input_video=args.input,
        output_video=args.output,
        track_id=args.track,
        style_config=style_config if style_config else None,
        style_config_file=args.config,
        manual_styling=not args.no_manual
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


# Entry point - this runs when the file is executed directly
if __name__ == "__main__":
    main()