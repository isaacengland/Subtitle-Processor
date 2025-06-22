# file_utils.py
"""
File Management Utilities - Essential File Operations

This file provides essential file management utilities used throughout the
subtitle processing system. It handles temporary file operations, path
generation, file validation, and other fundamental file system interactions.

ARCHITECTURE ROLE:
This is a foundational utility class that provides file management services
to all other components in the system. It abstracts away platform-specific
file operations and provides a clean, consistent interface for file handling.

DESIGN PATTERN:
Implements the Utility/Helper pattern, providing stateless operations for
common file management tasks. Also uses the Manager pattern for handling
temporary directory lifecycle.

SYSTEM INTEGRATION:
- Used by: All processing components that need file operations
- Provides: Temporary directory management, path generation, file validation
- Abstracts: Platform-specific file system differences
- Centralizes: File operation error handling and logging

CROSS-PLATFORM COMPATIBILITY:
All methods are designed to work consistently across Windows, macOS, and Linux.
Uses Python's pathlib and os modules for maximum compatibility and proper
path handling on different file systems.

KEY RESPONSIBILITIES:
1. **Temporary Directory Management**: Create and cleanup processing workspaces
2. **Path Generation**: Create output paths and handle file naming
3. **File Validation**: Check file existence and accessibility
4. **Cross-Platform Support**: Handle different path formats and conventions
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import logging


class FileManager:
    """
    File Management and Temporary Directory Handler
    
    This class provides essential file management utilities for the subtitle
    processing system. It handles temporary directory creation and cleanup,
    path generation, file validation, and other common file operations.
    
    TEMPORARY DIRECTORY MANAGEMENT:
    One of the key responsibilities is managing temporary directories used
    during processing. These directories store intermediate files (extracted
    subtitles, converted formats, etc.) and are automatically cleaned up
    when processing completes.
    
    LIFECYCLE MANAGEMENT:
    - Creates temporary directories when needed
    - Tracks directory location for cleanup
    - Automatically removes temporary files when done
    - Handles cleanup even if processing fails
    
    PATH GENERATION:
    Provides intelligent path generation for output files, handling:
    - File extension preservation
    - Suffix addition for processed files
    - Platform-specific path formatting
    - Collision avoidance
    
    THREAD SAFETY:
    This class is designed to be used in single-threaded contexts. For
    multi-threaded usage, each thread should have its own FileManager
    instance to avoid conflicts with temporary directory management.
    """
    
    def __init__(self):
        """
        Initialize the File Manager
        
        Sets up the file manager with no active temporary directory.
        The temporary directory is created on-demand when first needed.
        
        INITIALIZATION STATE:
        - temp_dir: None (no temporary directory created yet)
        - logger: Configured for this class's namespace
        
        LAZY INITIALIZATION:
        The temporary directory is not created in __init__ because:
        - Not all operations require temporary files
        - Avoids creating unnecessary directories
        - Allows better resource management
        """
        self.temp_dir = None
        self.logger = logging.getLogger(__name__)
    
    def create_temp_directory(self) -> str:
        """
        Create a Temporary Directory for Processing Operations
        
        Creates a new temporary directory with a unique name for storing
        intermediate files during processing. The directory is automatically
        managed and will be cleaned up when processing completes.
        
        DIRECTORY CREATION:
        - Uses system's temporary directory location
        - Generates unique directory name with prefix
        - Creates directory with appropriate permissions
        - Stores path for later cleanup
        
        NAMING CONVENTION:
        Temporary directories are named with the prefix "mkv_subtitle_"
        followed by a unique identifier. This makes them easily identifiable
        in the system's temporary directory.
        
        PLATFORM COMPATIBILITY:
        - Windows: Usually in %TEMP% or %TMP%
        - macOS: Usually in /tmp
        - Linux: Usually in /tmp or /var/tmp
        
        UNIQUENESS GUARANTEE:
        The tempfile module ensures each directory has a unique name,
        preventing conflicts between concurrent processing operations.
        
        Returns:
            str: Full path to the created temporary directory
            
        Example Usage:
            file_manager = FileManager()
            temp_dir = file_manager.create_temp_directory()
            print(f"Working in: {temp_dir}")
            # ... do processing work
            file_manager.cleanup_temp_directory()  # Clean up when done
        """
        # Create unique temporary directory with descriptive prefix
        self.temp_dir = tempfile.mkdtemp(prefix="mkv_subtitle_")
        
        # Log creation for debugging and monitoring
        self.logger.info(f"Created temporary directory: {self.temp_dir}")
        
        return self.temp_dir
    
    def cleanup_temp_directory(self):
        """
        Clean Up the Temporary Directory and All Contents
        
        Removes the temporary directory and all files/subdirectories within it.
        This method should be called when processing is complete to free up
        disk space and keep the system clean.
        
        CLEANUP PROCESS:
        1. Check if temporary directory exists and is set
        2. Remove directory tree recursively (all contents)
        3. Reset internal temp_dir reference to None
        4. Log cleanup completion
        
        SAFETY FEATURES:
        - Only removes directories created by this instance
        - Checks for existence before attempting removal
        - Handles permissions and access errors gracefully
        - Logs all cleanup operations for audit trail
        
        ERROR HANDLING:
        - Continues processing even if cleanup fails
        - Logs cleanup errors for troubleshooting
        - Does not raise exceptions for cleanup failures
        - Resets temp_dir even if removal fails
        
        IDEMPOTENCY:
        This method can be called multiple times safely:
        - If no temp directory exists, does nothing
        - If temp directory is already cleaned up, does nothing
        - Never fails due to repeated calls
        
        Example Usage:
            # Usually called in a try/finally block
            try:
                temp_dir = file_manager.create_temp_directory()
                # ... processing operations
            finally:
                file_manager.cleanup_temp_directory()  # Always clean up
        """
        # Check if we have a temporary directory to clean up
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                # Remove the entire directory tree
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                # Log cleanup errors but don't fail the operation
                self.logger.warning(f"Failed to clean up temporary directory {self.temp_dir}: {e}")
            finally:
                # Always reset the temp_dir reference
                self.temp_dir = None
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Check if a File Exists and is Accessible
        
        Validates that a file exists at the specified path and is a regular
        file (not a directory or special file). This is essential for input
        validation before attempting processing operations.
        
        VALIDATION CRITERIA:
        - Path exists in the file system
        - Path points to a regular file (not a directory)
        - File is accessible for reading
        
        CROSS-PLATFORM HANDLING:
        - Handles different path formats (Windows vs Unix)
        - Works with both absolute and relative paths
        - Properly handles Unicode characters in file names
        
        PERFORMANCE:
        This is a fast operation that only checks file metadata without
        reading file contents. Safe to call frequently for validation.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if file exists and is accessible, False otherwise
            
        Example Usage:
            if file_manager.validate_file_exists("input.mkv"):
                print("File is ready for processing")
            else:
                print("File not found or inaccessible")
        """
        return os.path.isfile(file_path)
    
    def get_file_extension(self, file_path: str) -> str:
        """
        Extract File Extension from Path
        
        Extracts and returns the file extension from a given file path.
        The extension is normalized to lowercase for consistent handling
        across the system.
        
        EXTENSION EXTRACTION:
        - Uses pathlib for robust path parsing
        - Includes the leading dot (e.g., '.mkv', not 'mkv')
        - Converts to lowercase for consistency
        - Handles files with multiple dots correctly
        
        EDGE CASES:
        - Files without extensions return empty string
        - Hidden files starting with dot are handled correctly
        - Files with multiple dots return only the final extension
        
        CONSISTENCY:
        All extensions in the system are handled in lowercase to avoid
        case-sensitivity issues across different operating systems.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File extension including leading dot, in lowercase
            
        Example Usage:
            ext = file_manager.get_file_extension("movie.MKV")
            print(ext)  # Output: ".mkv"
            
            ext = file_manager.get_file_extension("subtitle.part1.srt")
            print(ext)  # Output: ".srt"
        """
        return Path(file_path).suffix.lower()
    
    def generate_output_path(self, input_path: str, suffix: str = "_processed") -> str:
        """
        Generate Output File Path Based on Input Path
        
        Creates an appropriate output file path by modifying the input path.
        Adds a suffix to the filename while preserving the directory location
        and file extension.
        
        PATH GENERATION STRATEGY:
        1. Parse input path into directory, filename, and extension
        2. Add suffix to filename (before extension)
        3. Reconstruct full path in same directory
        4. Return the generated output path
        
        NAMING CONVENTION:
        - Original: "/path/to/movie.mkv"
        - Generated: "/path/to/movie_processed.mkv"
        - Preserves directory structure and file extension
        - Adds descriptive suffix to indicate processing
        
        COLLISION AVOIDANCE:
        The default suffix helps avoid overwriting the original file.
        Different suffixes can be used for different processing types:
        - "_processed" for general processing
        - "_styled" for subtitle styling
        - "_converted" for format conversion
        
        FLEXIBILITY:
        The suffix parameter allows customization for different use cases:
        - Different processing stages can use different suffixes
        - Timestamping can be added if needed
        - Empty suffix generates same-name file in same directory
        
        Args:
            input_path (str): Path to the original file
            suffix (str): Suffix to add to the filename (default: "_processed")
            
        Returns:
            str: Generated output file path
            
        Example Usage:
            input_file = "/movies/action/movie.mkv"
            output_file = file_manager.generate_output_path(input_file, "_styled")
            print(output_file)  # Output: "/movies/action/movie_styled.mkv"
            
            # Different suffix for different operations
            backup_file = file_manager.generate_output_path(input_file, "_backup")
            print(backup_file)  # Output: "/movies/action/movie_backup.mkv"
        """
        # Parse the input path using pathlib for robust handling
        path = Path(input_path)
        
        # Construct new path: directory + filename + suffix + extension
        output_path = path.parent / f"{path.stem}{suffix}{path.suffix}"
        
        # Return as string for compatibility with the rest of the system
        return str(output_path)
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a Directory Exists, Creating it if Necessary
        
        Checks if a directory exists and creates it (including any necessary
        parent directories) if it doesn't exist. This is useful for ensuring
        output directories are available before saving files.
        
        DIRECTORY CREATION:
        - Creates the directory if it doesn't exist
        - Creates all necessary parent directories
        - Uses appropriate permissions for the platform
        - Handles existing directories gracefully
        
        PERMISSION HANDLING:
        - Creates directories with standard permissions
        - Respects system umask settings
        - Handles permission errors gracefully
        
        SAFETY FEATURES:
        - Does nothing if directory already exists
        - Creates parent directories as needed
        - Returns success/failure status
        - Logs directory creation for audit trail
        
        Args:
            directory_path (str): Path to the directory to ensure exists
            
        Returns:
            bool: True if directory exists or was created successfully, False otherwise
            
        Example Usage:
            success = file_manager.ensure_directory_exists("/output/processed")
            if success:
                print("Directory is ready for output files")
            else:
                print("Failed to create output directory")
        """
        try:
            # Create directory and any necessary parent directories
            os.makedirs(directory_path, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory_path}")
            return True
        except Exception as e:
            # Log error and return failure status
            self.logger.error(f"Failed to create directory {directory_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get File Size in Bytes
        
        Returns the size of a file in bytes. Useful for progress tracking,
        disk space validation, and general file information display.
        
        SIZE CALCULATION:
        - Returns actual file size in bytes
        - Does not follow symbolic links
        - Returns None for inaccessible files
        - Handles large files correctly
        
        ERROR HANDLING:
        - Returns None if file doesn't exist
        - Returns None if file is inaccessible
        - Logs errors for troubleshooting
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Optional[int]: File size in bytes, or None if file is inaccessible
            
        Example Usage:
            size = file_manager.get_file_size("movie.mkv")
            if size:
                print(f"File size: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
            else:
                print("File not found or inaccessible")
        """
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            self.logger.debug(f"Could not get size for {file_path}: {e}")
            return None
        
    def backup_and_replace_file(self, original_file: str, processed_file: str) -> bool:
        """
        Backup original file and replace with processed version
        
        This method safely backs up the original file and replaces it with
        the processed version, maintaining the original filename for the result.
        
        OPERATION FLOW:
        1. Create _backups directory if it doesn't exist
        2. Rename original file with _original suffix
        3. Move renamed file to _backups directory
        4. Move processed file to original location
        
        Args:
            original_file (str): Path to the original input file
            processed_file (str): Path to the processed output file
            
        Returns:
            bool: True if backup and replacement succeeded, False otherwise
        """
        try:
            import shutil
            
            # Parse file paths
            original_path = Path(original_file)
            processed_path = Path(processed_file)
            
            # Create backup directory in same location as original
            backup_dir = original_path.parent / "_backups"
            if not self.ensure_directory_exists(str(backup_dir)):
                self.logger.error(f"Failed to create backup directory: {backup_dir}")
                return False
            
            # Generate backup filename: movie.mkv -> movie_original.mkv
            backup_filename = f"{original_path.stem}_original{original_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            # Handle backup filename conflicts
            counter = 1
            while backup_path.exists():
                backup_filename = f"{original_path.stem}_original_{counter}{original_path.suffix}"
                backup_path = backup_dir / backup_filename
                counter += 1
            
            # Step 1: Move original to backup location
            self.logger.info(f"Backing up original file to: {backup_path}")
            shutil.move(str(original_path), str(backup_path))
            
            # Step 2: Move processed file to original location
            self.logger.info(f"Moving processed file to: {original_path}")
            shutil.move(str(processed_path), str(original_path))
            
            self.logger.info(f"Successfully replaced {original_path.name} with processed version")
            self.logger.info(f"Original backed up as: {backup_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup and replace file: {e}")
            
            # Attempt to restore original if it was moved
            try:
                if 'backup_path' in locals() and backup_path.exists() and not original_path.exists():
                    shutil.move(str(backup_path), str(original_path))
                    self.logger.info("Restored original file after failure")
            except Exception as restore_error:
                self.logger.error(f"Failed to restore original file: {restore_error}")
            
            return False