# aegisub_processor.py
"""
Aegisub Integration - Manual Subtitle Editing Interface

This file provides integration with Aegisub, a professional subtitle editing
application. It enables users to manually edit and style subtitles using
Aegisub's advanced editing capabilities when automatic styling isn't sufficient.

ARCHITECTURE ROLE:
This is a specialized integration component that bridges the gap between the
automated subtitle processing system and manual editing workflows. It provides
a seamless way to hand off subtitle files to professional editing tools.

DESIGN PATTERN:
Implements the Adapter pattern, adapting the external Aegisub application to
work within the system's processing workflow. Also uses the Command pattern
for executing external tool operations.

SYSTEM INTEGRATION:
- Used by: UniversalSubtitleProcessor when manual_styling option is enabled
- Manages: External Aegisub application lifecycle and file handoff
- Coordinates: User interaction workflow for manual editing
- Abstracts: Platform-specific Aegisub installation details

AEGISUB OVERVIEW:
Aegisub is the industry-standard subtitle editing application featuring:
- Advanced ASS subtitle format support
- Real-time preview with video synchronization
- Professional typography and styling tools
- Precise timing adjustment capabilities
- Visual typesetting and positioning
- Effects and animation support

USE CASES:
1. **Complex Styling**: When JSON config isn't sufficient for complex designs
2. **Timing Adjustment**: Fine-tuning subtitle timing and duration
3. **Visual Positioning**: Placing subtitles at specific screen locations
4. **Quality Control**: Manual review and correction of automated processing
5. **Creative Effects**: Adding animations, karaoke effects, or special styling
"""

import subprocess
import os
import time
import shutil
from typing import Optional, Dict
import logging


class AegisubProcessor:
    """
    Aegisub Application Integration Manager
    
    This class handles all interactions with the Aegisub subtitle editing
    application. It manages Aegisub discovery, launching, and integration
    within the automated processing workflow.
    
    INTEGRATION PHILOSOPHY:
    The processor acts as a bridge between automated and manual workflows:
    - Automated: Fast, consistent, good for bulk processing
    - Manual: Precise, creative, good for complex or artistic subtitles
    - Hybrid: Use automation for basic processing, manual for refinement
    
    AEGISUB DISCOVERY:
    Automatically searches for Aegisub installations in common locations:
    - System PATH (preferred method)
    - Standard installation directories
    - Platform-specific default locations
    - User-specified custom paths
    
    WORKFLOW INTEGRATION:
    Fits seamlessly into the processing pipeline:
    1. Automated processing extracts and converts subtitles
    2. AegisubProcessor opens the subtitle file in Aegisub
    3. User performs manual editing and styling
    4. User saves and closes Aegisub
    5. Automated processing continues with the edited file
    
    PLATFORM SUPPORT:
    Designed to work across different operating systems:
    - Windows: Searches Program Files directories
    - macOS: Searches Applications directory
    - Linux: Searches standard binary paths
    """
    
    def __init__(self, aegisub_path: Optional[str] = None):
        """
        Initialize the Aegisub Processor
        
        Sets up the processor with automatic Aegisub discovery or uses a
        user-specified path. The processor is ready to launch Aegisub
        once initialization completes.
        
        INITIALIZATION STRATEGY:
        1. If aegisub_path provided: Use the specified path
        2. If no path provided: Attempt automatic discovery
        3. Store the final path for later use
        4. Set up logging for this component
        
        AUTOMATIC DISCOVERY:
        The _find_aegisub() method searches common installation locations
        and returns the first working Aegisub executable found.
        
        Args:
            aegisub_path (Optional[str]): Custom path to Aegisub executable,
                                        None for automatic discovery
        """
        
        # Set up logging for this component
        self.logger = logging.getLogger(__name__)

        # Use provided path or attempt automatic discovery
        self.aegisub_path = aegisub_path or self._find_aegisub()
        
        # Log the discovery result
        if self.aegisub_path:
            self.logger.info(f"Aegisub found at: {self.aegisub_path}")
        else:
            self.logger.warning("Aegisub not found in standard locations")
    
    def _find_aegisub(self) -> Optional[str]:
        """
        Automatically Discover Aegisub Installation
        
        Searches for Aegisub executable in common installation locations
        across different operating systems. Returns the first working
        installation found.
        
        SEARCH STRATEGY:
        1. Check system PATH first (most reliable)
        2. Search platform-specific standard locations
        3. Try both 64-bit and 32-bit installations
        4. Verify executable actually works
        
        SEARCH LOCATIONS:
        The method searches in order of preference:
        - System PATH: aegisub command
        - Linux: /usr/bin, /usr/local/bin
        - Windows: Program Files directories (64-bit and 32-bit)
        - macOS: Applications directory
        
        EXECUTABLE VERIFICATION:
        Uses shutil.which() to verify that found executables are:
        - Actually executable files
        - Accessible with current permissions
        - Available in the system PATH
        
        CROSS-PLATFORM COMPATIBILITY:
        Handles path differences between operating systems:
        - Windows: Uses .exe extensions and Program Files paths
        - Unix-like: Uses standard bin directories
        - macOS: Searches Applications and standard paths
        
        Returns:
            Optional[str]: Path to working Aegisub executable, or None if not found
            
        Example Discovered Paths:
            - Windows: "C:\\Program Files\\Aegisub\\aegisub64.exe"
            - Linux: "/usr/bin/aegisub"
            - macOS: "/Applications/Aegisub.app/Contents/MacOS/aegisub"
        """
        # List of possible Aegisub executable locations
        possible_paths = [
            # System PATH (most reliable)
            'aegisub',
            
            # Linux standard locations
            '/usr/bin/aegisub',
            '/usr/local/bin/aegisub',
            
            # Windows standard installations
            'C:\\Program Files\\Aegisub\\aegisub64.exe',      # 64-bit installation
            'C:\\Program Files (x86)\\Aegisub\\aegisub32.exe', # 32-bit installation
            
            # macOS standard installation
            '/Applications/Aegisub.app/Contents/MacOS/aegisub',
        ]
        
        # Search for working Aegisub installation
        for path in possible_paths:
            if shutil.which(path):
                self.logger.debug(f"Found Aegisub at: {path}")
                return path
        
        # No working installation found
        self.logger.debug("Aegisub not found in any standard location")
        return None
    
    def is_available(self) -> bool:
        """
        Check if Aegisub is Available for Use
        
        Simple boolean check to determine if Aegisub has been found and is
        ready for use. This is used by other components to decide whether
        to offer manual editing options to users.
        
        AVAILABILITY CRITERIA:
        Returns True if:
        - Aegisub executable path has been discovered or provided
        - Path is not None or empty
        
        USAGE SCENARIOS:
        - GUI: Show/hide manual editing options
        - CLI: Decide whether to offer manual editing
        - Processing: Skip manual editing if not available
        - Error handling: Provide appropriate error messages
        
        Returns:
            bool: True if Aegisub is available, False otherwise
            
        Example Usage:
            if processor.is_available():
                print("Manual editing with Aegisub is available")
                processor.open_for_styling("subtitles.ass")
            else:
                print("Aegisub not found, using automatic styling only")
        """
        return self.aegisub_path is not None
    
    def open_for_styling(self, subtitle_path: str, auto_save: bool = False) -> bool:
        """
        Open Subtitle File in Aegisub for Manual Editing
        
        Launches Aegisub with the specified subtitle file loaded for editing.
        This is the main method for integrating manual editing into the
        processing workflow.
        
        LAUNCH MODES:
        Two modes of operation based on the auto_save parameter:
        
        1. **Interactive Mode (auto_save=False)**:
           - Launches Aegisub in background
           - Returns immediately
           - User manually saves and closes Aegisub
           - Processing waits for user input to continue
        
        2. **Blocking Mode (auto_save=True)**:
           - Launches Aegisub and waits for it to close
           - Returns when user closes Aegisub
           - Assumes user has saved their changes
           - Processing continues automatically
        
        WORKFLOW INTEGRATION:
        Typical usage in processing workflow:
        ```python
        # Extract subtitle to temporary file
        processor.open_for_styling(temp_subtitle_file)
        input("Press Enter after editing in Aegisub...")
        # Continue with edited file
        ```
        
        ERROR HANDLING:
        - Checks Aegisub availability before launching
        - Validates subtitle file exists
        - Handles process launch failures
        - Provides helpful error messages
        
        PLATFORM CONSIDERATIONS:
        - Windows: Launches .exe with proper argument handling
        - macOS: May launch app bundle or direct executable
        - Linux: Launches binary with standard argument format
        
        Args:
            subtitle_path (str): Path to the subtitle file to edit
            auto_save (bool): Whether to wait for Aegisub to close
            
        Returns:
            bool: True if Aegisub launched successfully, False otherwise
            
        Example Usage:
            # Interactive mode (default)
            success = processor.open_for_styling("subtitles.ass")
            if success:
                input("Edit subtitles in Aegisub, then press Enter...")
            
            # Blocking mode
            success = processor.open_for_styling("subtitles.ass", auto_save=True)
            # Continues automatically when Aegisub closes
        """
        # Check if Aegisub is available
        if not self.is_available():
            self.logger.error("Aegisub not found. Please install Aegisub or specify path.")
            return False
        
        # Validate subtitle file exists
        if not os.path.isfile(subtitle_path):
            self.logger.error(f"Subtitle file not found: {subtitle_path}")
            return False
        
        try:
            # Choose launch mode based on auto_save parameter
            if auto_save:
                # Blocking mode: wait for Aegisub to close
                self.logger.info(f"Opening {subtitle_path} in Aegisub (blocking mode)")
                process = subprocess.Popen([self.aegisub_path, subtitle_path])
                process.wait()  # Wait for Aegisub to close
                self.logger.info("Aegisub closed, continuing processing")
            else:
                # Interactive mode: launch in background
                self.logger.info(f"Opening {subtitle_path} in Aegisub (interactive mode)")
                subprocess.Popen([self.aegisub_path, subtitle_path])
            
            self.logger.info(f"Opened {subtitle_path} in Aegisub")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open Aegisub: {e}")
            return False
    
    def apply_automation_script(self, subtitle_path: str, 
                              script_path: str) -> bool:
        """
        Apply Aegisub Automation Script (Framework for Future Enhancement)
        
        This method provides a framework for applying Aegisub automation
        scripts programmatically. Currently logs a warning that manual
        setup is required, but provides the foundation for future automation.
        
        AEGISUB AUTOMATION:
        Aegisub supports Lua-based automation scripts that can:
        - Apply complex styling transformations
        - Perform batch operations on subtitle lines
        - Implement custom effects and animations
        - Automate repetitive editing tasks
        
        CURRENT LIMITATIONS:
        Aegisub automation requires:
        - Scripts to be manually installed in Aegisub
        - Interactive execution from within Aegisub
        - No direct command-line automation interface
        
        FUTURE POSSIBILITIES:
        This method could be enhanced to:
        - Copy scripts to Aegisub's automation directory
        - Use Aegisub's command-line interface (if available)
        - Integrate with Aegisub's scripting system
        - Provide batch automation capabilities
        
        IMPLEMENTATION NOTES:
        Current implementation serves as:
        - Placeholder for future automation features
        - Documentation of the intended capability
        - Framework for community contributions
        
        Args:
            subtitle_path (str): Path to the subtitle file to process
            script_path (str): Path to the Aegisub automation script
            
        Returns:
            bool: Currently always returns False (not implemented)
            
        Example Future Usage:
            # This would apply a script automatically
            success = processor.apply_automation_script(
                "subtitles.ass",
                "scripts/fancy_styling.lua"
            )
        """
        # Log that this feature requires manual implementation
        self.logger.warning(
            "Automation scripts require manual Aegisub setup. "
            "Please install and run scripts manually within Aegisub."
        )
        
        # Future implementation would go here
        # This could involve:
        # 1. Copying script to Aegisub automation directory
        # 2. Using Aegisub command-line interface (if available)
        # 3. Integrating with Aegisub's scripting system
        
        return False
    
    def get_version(self) -> Optional[str]:
        """
        Get Aegisub Version Information
        
        Attempts to retrieve version information from the installed Aegisub.
        Useful for compatibility checking and troubleshooting.
        
        VERSION DETECTION:
        Tries to execute Aegisub with version flag to get version string.
        Different Aegisub versions may use different version flags.
        
        COMPATIBILITY CHECKING:
        Version information can be used to:
        - Verify Aegisub installation is working
        - Check compatibility with specific features
        - Provide better error messages
        - Log system configuration details
        
        ERROR HANDLING:
        - Returns None if Aegisub is not available
        - Returns None if version command fails
        - Handles different version flag formats
        - Logs version detection attempts
        
        Returns:
            Optional[str]: Aegisub version string, or None if unavailable
            
        Example Usage:
            version = processor.get_version()
            if version:
                print(f"Using Aegisub version: {version}")
            else:
                print("Could not determine Aegisub version")
        """
        if not self.is_available():
            return None
        
        try:
            # Try common version flags
            version_flags = ['--version', '-v', '--help']
            
            for flag in version_flags:
                try:
                    result = subprocess.run(
                        [self.aegisub_path, flag],
                        capture_output=True,
                        text=True,
                        timeout=10  # Don't wait too long
                    )
                    
                    # Look for version information in output
                    output = result.stdout + result.stderr
                    if 'aegisub' in output.lower() or 'version' in output.lower():
                        # Extract and return version info
                        lines = output.strip().split('\n')
                        for line in lines:
                            if 'aegisub' in line.lower() or 'version' in line.lower():
                                return line.strip()
                
                except subprocess.TimeoutExpired:
                    continue
                except subprocess.CalledProcessError:
                    continue
            
            self.logger.debug("Could not determine Aegisub version")
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting Aegisub version: {e}")
            return None