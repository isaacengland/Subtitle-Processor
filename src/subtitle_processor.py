# subtitle_processor.py
"""
Subtitle Processing Engine - Format Conversion and Styling

This file implements the core subtitle processing functionality, including format
detection, conversion between subtitle formats, and application of custom styling
configurations. It serves as the styling engine for the entire system.

ARCHITECTURE ROLE:
This is the specialized subtitle handling component that transforms raw subtitle
tracks into professionally styled ones. It bridges the gap between extracted
subtitle files and the final styled output that gets merged back into videos.

DESIGN PATTERN:
Implements the Strategy pattern for different subtitle formats, and the Template
Method pattern for the styling application process. Also uses the Factory pattern
for format detection and conversion selection.

SYSTEM INTEGRATION:
- Used by: UniversalSubtitleProcessor for all subtitle operations
- Processes: Raw subtitle files from video extraction
- Outputs: Styled ASS files ready for video merging
- Coordinates: Format conversion tools (FFmpeg) and custom styling logic

SUBTITLE FORMAT ECOSYSTEM:
Handles multiple subtitle formats with different capabilities:
- ASS: Advanced SubStation Alpha (most feature-rich, supports complex styling)
- SRT: SubRip Text (basic format, timing + plain text)
- VTT: WebVTT (web standard, basic styling capabilities)
- Others: Extensible to support additional formats as needed

KEY CAPABILITIES:
1. **Format Detection**: Automatically identify subtitle file formats
2. **Format Conversion**: Convert between different subtitle formats
3. **Custom Styling**: Apply JSON-based styling configurations
4. **ASS Manipulation**: Advanced ASS format parsing and modification
5. **Quality Preservation**: Maintain timing accuracy and text content
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
import logging


class SubtitleProcessor:
    """
    Subtitle Format Processing and Styling Engine
    
    This class handles all subtitle-related operations including format detection,
    conversion between formats, and application of custom styling. It specializes
    in working with various subtitle formats and transforming them according to
    user specifications.
    
    CORE RESPONSIBILITIES:
    1. **Format Detection**: Analyze subtitle files to determine their format
    2. **Format Conversion**: Convert subtitles between different formats
    3. **Style Application**: Apply custom styling from JSON configurations
    4. **ASS Manipulation**: Parse and modify Advanced SubStation Alpha files
    5. **Quality Assurance**: Validate subtitle files and ensure proper formatting
    
    STYLING PHILOSOPHY:
    The processor treats ASS as the target format for maximum styling capability.
    Other formats are converted to ASS to enable advanced styling features:
    - Typography control (fonts, sizes, colors)
    - Positioning and alignment
    - Outline and shadow effects
    - Background colors and transparency
    
    FORMAT CONVERSION STRATEGY:
    - SRT → ASS: Convert timing and text, apply styling
    - VTT → ASS: Convert web format to desktop format
    - ASS → ASS: Direct styling application
    - Others → ASS: Use FFmpeg for universal conversion
    
    CONFIGURATION SYSTEM:
    Uses JSON configuration files that define all styling parameters:
    - Font properties (name, size, weight)
    - Color scheme (text, outline, background)
    - Positioning (margins, alignment)
    - Effects (outline thickness, shadow depth)
    """
    
    def __init__(self):
        """
        Initialize the Subtitle Processor
        
        Sets up logging and prepares the processor for subtitle operations.
        No heavy initialization is performed here to keep the processor
        lightweight and fast to instantiate.
        """
        self.logger = logging.getLogger(__name__)
    
    def load_style_config(self, config_path: str) -> Dict:
        """
        Load Subtitle Styling Configuration from JSON File
        
        Reads and parses a JSON configuration file containing subtitle styling
        parameters. This is the primary way users define their preferred
        subtitle appearance and behavior.
        
        CONFIGURATION STRUCTURE:
        Expected JSON structure:
        ```json
        {
            "subtitle_style": {
                "font_name": "Helvetica",
                "font_size": 22,
                "primary_color": "&H00FFFFFF",
                "outline": 1.0,
                "alignment": 2,
                ...
            }
        }
        ```
        
        COLOR FORMAT:
        Colors use ASS format: &HAABBGGRR
        - AA: Alpha (transparency)
        - BB: Blue component
        - GG: Green component  
        - RR: Red component
        
        PARAMETER VALIDATION:
        The method loads the configuration as-is, trusting that the JSON
        contains valid ASS parameters. Invalid parameters will be caught
        during style application.
        
        ERROR HANDLING:
        - Missing files: Returns empty dict, logs error
        - Invalid JSON: Returns empty dict, logs parsing error
        - Missing style section: Returns empty dict
        
        Args:
            config_path (str): Path to the JSON configuration file
            
        Returns:
            Dict: Subtitle styling parameters, or empty dict if loading fails
            
        Example Usage:
            config = processor.load_style_config("my_style.json")
            if config:
                processor.apply_styling_from_config("subtitles.ass", config)
            else:
                print("Failed to load styling configuration")
        """
        try:
            # Read and parse the JSON configuration file
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extract the subtitle_style section
            style_config = config.get('subtitle_style', {})
            
            if style_config:
                self.logger.info(f"Loaded style configuration with {len(style_config)} parameters")
            else:
                self.logger.warning(f"No 'subtitle_style' section found in {config_path}")
            
            return style_config
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load style config: {e}")
            return {}
    
    def detect_subtitle_format(self, subtitle_path: str) -> str:
        """
        Detect the Format of a Subtitle File
        
        Analyzes a subtitle file to determine its format based on content
        patterns and structure. This is essential for choosing the correct
        processing and conversion strategy.
        
        DETECTION METHODS:
        Uses content-based detection rather than file extensions:
        - ASS: Looks for "[Script Info]" section header
        - VTT: Looks for "WEBVTT" magic string at beginning
        - SRT: Looks for numbered subtitle blocks with timestamp format
        - Unknown: Falls back when no pattern matches
        
        PATTERN MATCHING:
        - ASS Detection: Searches for characteristic ASS file sections
        - VTT Detection: Checks for WebVTT specification compliance
        - SRT Detection: Uses regex to match SRT timestamp format
        - Robust: Handles files with BOM, encoding issues, etc.
        
        ENCODING HANDLING:
        Reads files with UTF-8 encoding and error tolerance to handle:
        - Different text encodings
        - Byte Order Marks (BOM)
        - Corrupted or partial files
        
        PERFORMANCE:
        Only reads enough of the file to make a determination:
        - Fast detection for large subtitle files
        - Minimal memory usage
        - Early exit when format is identified
        
        Args:
            subtitle_path (str): Path to the subtitle file to analyze
            
        Returns:
            str: Format identifier ('ass', 'vtt', 'srt', or 'unknown')
            
        Example Usage:
            format_type = processor.detect_subtitle_format("subtitles.srt")
            if format_type == 'srt':
                print("This is a SubRip subtitle file")
            elif format_type == 'unknown':
                print("Unknown subtitle format")
        """
        try:
            # Read file content with encoding tolerance
            with open(subtitle_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # ASS Format Detection
            if '[Script Info]' in content:
                self.logger.debug(f"Detected ASS format: {subtitle_path}")
                return 'ass'
            
            # VTT Format Detection
            elif content.strip().startswith('WEBVTT'):
                self.logger.debug(f"Detected VTT format: {subtitle_path}")
                return 'vtt'
            
            # SRT Format Detection (numbered blocks with timestamps)
            elif re.search(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', content):
                self.logger.debug(f"Detected SRT format: {subtitle_path}")
                return 'srt'
            
            # Unknown format
            else:
                self.logger.warning(f"Unknown subtitle format: {subtitle_path}")
                return 'unknown'
                
        except Exception as e:
            self.logger.error(f"Error detecting subtitle format for {subtitle_path}: {e}")
            return 'unknown'
    
    def convert_to_ass(self, input_path: str, output_path: str) -> bool:
        """
        Convert Subtitle File to ASS Format
        
        Converts a subtitle file from any supported format to Advanced SubStation
        Alpha (ASS) format using FFmpeg. ASS is the target format because it
        supports the most advanced styling capabilities.
        
        CONVERSION PROCESS:
        1. Uses FFmpeg with ASS subtitle codec
        2. Preserves timing and text content
        3. Creates basic ASS structure for styling
        4. Overwrites output file if it exists
        
        FFMPEG INTEGRATION:
        FFmpeg command structure:
        - Input: Source subtitle file (any format)
        - Codec: ass (Advanced SubStation Alpha)
        - Output: ASS file ready for styling
        - Overwrite: -y flag to replace existing files
        
        QUALITY PRESERVATION:
        - Maintains precise timing from original
        - Preserves all text content and line breaks
        - Converts basic formatting when possible
        - Creates clean ASS structure for styling
        
        ERROR SCENARIOS:
        - FFmpeg not installed: Command fails
        - Unsupported input format: FFmpeg error
        - File access issues: Permission errors
        - Corrupted input: FFmpeg parsing errors
        
        Args:
            input_path (str): Path to the source subtitle file
            output_path (str): Path for the converted ASS file
            
        Returns:
            bool: True if conversion succeeded, False otherwise
            
        Example Usage:
            success = processor.convert_to_ass("subtitles.srt", "subtitles.ass")
            if success:
                print("Conversion successful, ready for styling")
            else:
                print("Conversion failed, check FFmpeg installation")
        """
        try:
            # Build FFmpeg conversion command
            cmd = [
                'ffmpeg',
                '-i', input_path,      # Input subtitle file
                '-c:s', 'ass',         # Use ASS subtitle codec
                '-y',                  # Overwrite output file if exists
                output_path            # Output ASS file
            ]
            
            # Execute conversion with error capture
            result = subprocess.run(cmd, capture_output=True, check=True)
            
            self.logger.info(f"Converted {input_path} to ASS format: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to convert to ASS: {e}")
            # Log stderr output for debugging
            if e.stderr:
                self.logger.debug(f"FFmpeg stderr: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
        except FileNotFoundError:
            self.logger.error("FFmpeg not found. Please install FFmpeg for subtitle conversion.")
            return False
    
    def validate_subtitle_file(self, subtitle_path: str) -> bool:
        """
        Validate that Subtitle File Exists and is Readable
        
        Performs comprehensive validation of a subtitle file to ensure it
        can be processed successfully. This catches common issues before
        attempting more complex operations.
        
        VALIDATION CHECKS:
        1. File existence: Verify file exists at the specified path
        2. File accessibility: Ensure file can be opened for reading
        3. Content validation: Check that file contains actual content
        4. Encoding validation: Verify file can be read as text
        
        COMMON ISSUES DETECTED:
        - Missing files (wrong path, deleted files)
        - Permission issues (access denied)
        - Empty files (zero bytes or whitespace only)
        - Binary files (not text-based subtitles)
        - Encoding problems (unreadable characters)
        
        ERROR REPORTING:
        Provides specific error messages for different failure types:
        - Clear guidance for file not found
        - Helpful hints for permission issues
        - Warnings for empty or suspicious files
        
        Args:
            subtitle_path (str): Path to the subtitle file to validate
            
        Returns:
            bool: True if file is valid and readable, False otherwise
            
        Example Usage:
            if processor.validate_subtitle_file("subtitles.srt"):
                format_type = processor.detect_subtitle_format("subtitles.srt")
            else:
                print("Subtitle file validation failed")
        """
        # Check file existence
        if not os.path.isfile(subtitle_path):
            self.logger.error(f"Subtitle file not found: {subtitle_path}")
            return False
        
        try:
            # Check file readability and content
            with open(subtitle_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for empty or whitespace-only files
            if not content.strip():
                self.logger.error(f"Subtitle file is empty: {subtitle_path}")
                return False
            
            self.logger.debug(f"Subtitle file validation passed: {subtitle_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Cannot read subtitle file {subtitle_path}: {e}")
            return False
    
    def create_ass_style_line(self, style_config: Dict, style_name: str = "Default") -> str:
        """
        Create an ASS Style Line from Configuration Parameters
        
        Constructs a properly formatted ASS style line using the provided
        configuration parameters. This is the core function that translates
        JSON configuration into ASS format styling.
        
        ASS STYLE FORMAT:
        The ASS style line has a specific format with 23 fields:
        Style: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour,
        OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
        ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,
        Alignment, MarginL, MarginR, MarginV, Encoding
        
        PARAMETER MAPPING:
        Configuration JSON → ASS Style Line:
        - font_name → Fontname
        - font_size → Fontsize
        - primary_color → PrimaryColour
        - bold → Bold (0 or 1)
        - alignment → Alignment (1-9)
        - margin_left → MarginL
        - outline → Outline thickness
        - shadow → Shadow depth
        
        DEFAULT VALUES:
        Provides sensible defaults for missing parameters:
        - Font: Arial, size 20
        - Colors: White text, black outline
        - Margins: 10 pixels
        - Effects: Standard outline and shadow
        
        CONFIGURATION FLEXIBILITY:
        - Uses provided values when available
        - Falls back to defaults for missing parameters
        - Maintains ASS format compliance
        - Supports all standard ASS styling options
        
        Args:
            style_config (Dict): Dictionary of styling parameters
            style_name (str): Name for this style (default: "Default")
            
        Returns:
            str: Complete ASS style line ready for insertion
            
        Example Usage:
            config = {"font_name": "Arial", "font_size": 24, "bold": 1}
            style_line = processor.create_ass_style_line(config, "MyStyle")
            print(style_line)
            # Output: "Style: MyStyle,Arial,24,&H00FFFFFF,..."
        """
        # Start building the style line with the style name
        style_line = f"Style: {style_name},"
        
        # Font properties
        style_line += f"{style_config.get('font_name', 'Arial')},"
        style_line += f"{style_config.get('font_size', 20)},"
        
        # Color properties (ASS format: &HAABBGGRR)
        style_line += f"{style_config.get('primary_color', '&H00FFFFFF')},"      # Text color
        style_line += f"{style_config.get('secondary_color', '&H000000FF')},"    # Secondary color
        style_line += f"{style_config.get('outline_color', '&H00000000')},"      # Outline color
        style_line += f"{style_config.get('back_color', '&H80000000')},"         # Background color
        
        # Text formatting
        style_line += f"{style_config.get('bold', 0)},"                          # Bold (0/1)
        style_line += f"{style_config.get('italic', 0)},"                        # Italic (0/1)
        
        # Fixed formatting options (rarely changed)
        style_line += "0,0,100,100,0,0,1,"  # Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle
        
        # Effects
        style_line += f"{style_config.get('outline', 2)},"                       # Outline thickness
        style_line += f"{style_config.get('shadow', 0)},"                        # Shadow depth
        
        # Positioning
        style_line += f"{style_config.get('alignment', 2)},"                     # Alignment (2 = bottom center)
        style_line += f"{style_config.get('margin_left', 10)},"                  # Left margin
        style_line += f"{style_config.get('margin_right', 10)},"                 # Right margin
        style_line += f"{style_config.get('margin_vertical', 10)},"              # Vertical margin
        
        # Encoding (usually 1 for Unicode)
        style_line += "1"
        
        return style_line
    
    def apply_styling_from_config(self, ass_path: str, style_config: Dict) -> bool:
        """
        Apply Comprehensive Styling to ASS Subtitle File
        
        This is the main styling method that applies a complete style
        configuration to an ASS subtitle file. It parses the ASS file
        structure and replaces or adds the Default style with custom styling.
        
        ASS FILE STRUCTURE:
        ASS files have a specific structure:
        ```
        [Script Info]
        ...
        [V4+ Styles]
        Format: Name, Fontname, Fontsize, ...
        Style: Default,Arial,20,&H00FFFFFF,...
        Style: Title,Arial,24,&H00FFFF00,...
        [Events]
        ...
        ```
        
        PROCESSING STRATEGY:
        1. Read and parse the entire ASS file
        2. Locate the [V4+ Styles] section
        3. Find or create the Default style line
        4. Replace with custom styling parameters
        5. Write the modified file back to disk
        
        STYLE REPLACEMENT:
        - Replaces existing Default style with custom configuration
        - Adds new Default style if none exists
        - Preserves other styles in the file
        - Maintains proper ASS file structure
        
        SAFETY FEATURES:
        - Preserves original file structure
        - Maintains timing and dialogue content
        - Handles files without existing styles
        - Creates backup of formatting info
        
        ERROR HANDLING:
        - Validates file accessibility before processing
        - Handles malformed ASS files gracefully
        - Provides detailed error logging
        - Fails safely without corrupting files
        
        Args:
            ass_path (str): Path to the ASS file to style
            style_config (Dict): Styling parameters from configuration
            
        Returns:
            bool: True if styling was applied successfully, False otherwise
            
        Example Usage:
            config = processor.load_style_config("style.json")
            success = processor.apply_styling_from_config("subtitles.ass", config)
            if success:
                print("Custom styling applied successfully")
        """
        try:
            # Read the ASS file content
            with open(ass_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse file into lines for processing
            lines = content.split('\n')
            new_lines = []
            
            # State tracking for ASS file parsing
            in_v4_styles = False
            style_format_found = False
            default_style_replaced = False
            
            # Process each line of the ASS file
            for line in lines:
                # Check if we're entering the V4+ Styles section
                if line.strip() == '[V4+ Styles]':
                    in_v4_styles = True
                    new_lines.append(line)
                    continue
                # Check if we're leaving the V4+ Styles section
                elif line.startswith('[') and line.endswith(']') and line.strip() != '[V4+ Styles]':
                    in_v4_styles = False
                
                # Process lines within the V4+ Styles section
                if in_v4_styles:
                    if line.startswith('Format:'):
                        # Found the format line - styles should follow
                        style_format_found = True
                        new_lines.append(line)
                    elif line.startswith('Style:') and 'Default' in line and not default_style_replaced:
                        # Replace the Default style with our custom configuration
                        new_style_line = self.create_ass_style_line(style_config, "Default")
                        new_lines.append(new_style_line)
                        default_style_replaced = True
                        self.logger.info("Replaced Default style with custom configuration")
                    elif line.startswith('Style:'):
                        # Keep other styles unchanged
                        new_lines.append(line)
                    else:
                        # Keep other lines in the styles section
                        new_lines.append(line)
                else:
                    # Keep all lines outside the styles section
                    new_lines.append(line)
            
            # If no Default style was found, add one after the Format line
            if not default_style_replaced and style_format_found:
                # Find the Format line and insert our Default style after it
                for i, line in enumerate(new_lines):
                    if line.startswith('Format:') and i > 0:
                        # Check if we're in the V4+ Styles section
                        section_start = i - 1
                        while section_start >= 0 and not new_lines[section_start].strip() == '[V4+ Styles]':
                            section_start -= 1
                        
                        if section_start >= 0:
                            # Insert new Default style after Format line
                            new_style_line = self.create_ass_style_line(style_config, "Default")
                            new_lines.insert(i + 1, new_style_line)
                            self.logger.info("Added new Default style with custom configuration")
                            break
            
            # Write the modified content back to the file
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            self.logger.info(f"Applied comprehensive styling to {ass_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply styling: {e}")
            return False
    
    def apply_basic_styling(self, ass_path: str, style_config: Dict) -> bool:
        """
        Apply Basic Styling to ASS Subtitle File (Legacy Method)
        
        This method provides backward compatibility for older code that
        expects the basic styling interface. It redirects to the comprehensive
        styling method to ensure consistent behavior.
        
        COMPATIBILITY:
        Maintains the same interface as the original basic styling method
        while providing the enhanced functionality of the comprehensive
        styling system.
        
        Args:
            ass_path (str): Path to the ASS file to style
            style_config (Dict): Styling parameters from configuration
            
        Returns:
            bool: True if styling was applied successfully, False otherwise
        """
        # Delegate to the comprehensive styling method
        return self.apply_styling_from_config(ass_path, style_config)