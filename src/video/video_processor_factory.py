# video_processor_factory.py
"""
Video Processor Factory - Format Selection and Management

This file implements the factory pattern for creating and managing video format
processors. It serves as the central registry for all supported video formats
and automatically selects the appropriate processor for any given file.

ARCHITECTURE ROLE:
This is the processor management layer that sits between the universal interface
and the format-specific implementations. It handles processor registration,
selection, and lifecycle management without exposing complexity to higher layers.

DESIGN PATTERN:
Implements the Factory Method pattern, providing an interface for creating
processor objects without specifying their exact classes. Also serves as a
Registry pattern, maintaining a central database of available processors.

SYSTEM INTEGRATION:
- Used by: UniversalVideoProcessor for format selection
- Manages: All format-specific processor instances (MKVProcessor, MP4Processor, etc.)
- Coordinates: Processor registration and retrieval

EXTENSIBILITY STRATEGY:
Adding new video format support is incredibly simple:
1. Create a new processor class implementing VideoProcessorBase
2. Register it in _register_default_processors()
3. That's it! The entire system automatically supports the new format

KEY BENEFITS:
1. **Centralized Management**: Single place to register all format processors
2. **Automatic Selection**: Picks the right processor based on file extension
3. **Zero Configuration**: New processors are automatically discovered
4. **Loose Coupling**: Higher-level code doesn't know about specific processors
5. **Easy Testing**: Can register mock processors for testing
"""

from typing import Optional, List, Dict
import os
from .video_processor_base import VideoProcessorBase
from .mkv_processor import MKVProcessor


class VideoProcessorFactory:
    """
    Processor Factory and Registry
    
    This class manages the creation, registration, and selection of video format
    processors. It acts as a central registry where all supported formats are
    registered and provides methods to automatically select the appropriate
    processor for any given file.
    
    FACTORY RESPONSIBILITIES:
    1. **Processor Registration**: Maintain a registry of all available processors
    2. **Format Mapping**: Map file extensions to appropriate processors
    3. **Processor Selection**: Choose the right processor for a given file
    4. **Capability Reporting**: Report what formats are supported
    
    REGISTRY PATTERN:
    The factory maintains an internal registry (dictionary) that maps file
    extensions to processor instances. This allows for O(1) lookup time
    and easy management of processor lifecycles.
    
    EXTENSIBILITY DESIGN:
    New processors are added by simply:
    1. Implementing the VideoProcessorBase interface
    2. Calling register_processor() with an instance
    3. The factory handles all the complexity automatically
    """
    
    def __init__(self):
        """
        Initialize the Processor Factory
        
        Creates an empty processor registry and automatically registers
        all default (built-in) processors. This ensures the factory is
        immediately ready to handle common video formats.
        
        INITIALIZATION PROCESS:
        1. Create empty processor registry dictionary
        2. Call _register_default_processors() to add built-in support
        3. Factory is ready to process video files
        """
        # Internal registry mapping file extensions to processor instances
        # Structure: {'.mkv': MKVProcessor(), '.mp4': MP4Processor(), ...}
        self._processors = {}
        
        # Register all built-in processors automatically
        self._register_default_processors()
    
    def _register_default_processors(self):
        """
        Register Built-in Video Format Processors
        
        This method registers all the processors that come built-in with
        the system. Currently includes MKV support, with a clear path
        for adding additional formats.
        
        CURRENT PROCESSORS:
        - MKVProcessor: Handles MKV files using MKVToolNix
        
        FUTURE PROCESSORS (examples):
        When ready to add new formats, simply uncomment/add lines like:
        - self.register_processor(MP4Processor())    # For MP4 files
        - self.register_processor(AVIProcessor())    # For AVI files
        - self.register_processor(MOVProcessor())    # For MOV files
        
        EXTENSIBILITY:
        This is the main place where new format support is added to the
        system. Adding a single line here gives the entire system support
        for a new video format.
        """
        # Register MKV support (currently the only built-in processor)
        self.register_processor(MKVProcessor())
        
        # Future processors can be easily added here:
        # self.register_processor(MP4Processor())     # Uncomment when MP4 support is ready
        # self.register_processor(AVIProcessor())     # Uncomment when AVI support is ready
        # self.register_processor(MOVProcessor())     # Uncomment when MOV support is ready
        # self.register_processor(WMVProcessor())     # Uncomment when WMV support is ready
        
        # The beauty of this design is that adding support for new formats
        # requires only implementing the processor class and adding one line here.
        # No changes needed anywhere else in the system!
    
    def register_processor(self, processor: VideoProcessorBase):
        """
        Register a New Video Format Processor
        
        Adds a processor to the factory's registry, making it available for
        processing files of the formats it supports. A single processor can
        support multiple file extensions.
        
        REGISTRATION PROCESS:
        1. Get list of extensions supported by the processor
        2. For each extension, map it to this processor instance
        3. Processor is now available for files with those extensions
        
        MULTIPLE EXTENSIONS:
        Some processors might support multiple related formats:
        - MP4Processor might support ['.mp4', '.m4v']
        - AVIProcessor might support ['.avi', '.divx']
        
        PROCESSOR LIFECYCLE:
        Processors are registered as instances, not classes. This means:
        - The factory manages the processor lifecycle
        - Processors can maintain state if needed
        - Same instance is reused for all files of that format
        
        Args:
            processor (VideoProcessorBase): An instance of a processor class
                                          that implements the VideoProcessorBase interface
                                          
        Example Usage:
            factory = VideoProcessorFactory()
            factory.register_processor(MP4Processor())  # Adds MP4 support
            factory.register_processor(CustomProcessor())  # Adds custom format support
        """
        # Get all extensions supported by this processor
        supported_extensions = processor.get_supported_extensions()
        
        # Register this processor for each extension it supports
        for ext in supported_extensions:
            self._processors[ext] = processor
            
        # Log successful registration for debugging
        self.logger = getattr(self, 'logger', None)
        if self.logger:
            self.logger.debug(f"Registered {processor.__class__.__name__} for extensions: {supported_extensions}")
    
    def get_processor(self, file_path: str) -> Optional[VideoProcessorBase]:
        """
        Get the Appropriate Processor for a File
        
        Given a file path, determines the file format and returns the
        appropriate processor instance. This is the main method used by
        the UniversalVideoProcessor to delegate operations.
        
        SELECTION LOGIC:
        1. Extract file extension from the path
        2. Normalize extension to lowercase
        3. Look up processor in registry
        4. Return processor instance or None
        
        EXTENSION HANDLING:
        - Handles mixed case extensions ('.MKV' → '.mkv')
        - Supports files with multiple dots ('movie.part1.mkv')
        - Returns None for unsupported formats
        
        Args:
            file_path (str): Path to the video file (can be relative or absolute)
            
        Returns:
            Optional[VideoProcessorBase]: Processor instance for the file format,
                                        or None if format is not supported
                                        
        Example Usage:
            processor = factory.get_processor("movie.mkv")
            if processor:
                tracks = processor.get_subtitle_tracks("movie.mkv")
            else:
                print("Unsupported format")
        """
        # Extract and normalize the file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        # Look up and return the appropriate processor
        return self._processors.get(ext)
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get All Supported File Extensions
        
        Returns a list of all file extensions that can be processed by
        the currently registered processors. This list is dynamically
        generated from the registry contents.
        
        DYNAMIC GENERATION:
        The list is generated from the current registry state, which means:
        - Automatically includes newly registered processors
        - Automatically excludes unregistered processors
        - Always reflects the current system capabilities
        
        USAGE SCENARIOS:
        - GUI: Display supported formats to users
        - Validation: Check if a file can be processed before attempting
        - Documentation: Generate help text with current capabilities
        - Filtering: Filter file lists to show only processable files
        
        Returns:
            List[str]: All supported file extensions (e.g., ['.mkv', '.mp4', '.avi'])
            
        Example Usage:
            extensions = factory.get_supported_extensions()
            print(f"Supported formats: {', '.join(extensions)}")
            
            # Check if specific format is supported
            if '.mp4' in extensions:
                print("MP4 files are supported!")
        """
        return list(self._processors.keys())
    
    def can_process(self, file_path: str) -> bool:
        """
        Check if a File Can Be Processed
        
        Quick boolean check to determine if the factory has a processor
        capable of handling the specified file. This is a convenience
        method that combines format detection and processor lookup.
        
        VALIDATION LOGIC:
        1. Extract file extension from path
        2. Check if extension exists in processor registry
        3. Return boolean result
        
        PERFORMANCE:
        This is a very fast operation (O(1)) since it's just a dictionary
        lookup. Safe to call frequently for file filtering or validation.
        
        COMPARISON WITH get_processor():
        - can_process(): Returns bool, fast check for existence
        - get_processor(): Returns actual processor instance, for processing
        
        Args:
            file_path (str): Path to the video file to check
            
        Returns:
            bool: True if the file can be processed, False otherwise
            
        Example Usage:
            if factory.can_process("movie.mkv"):
                print("This file can be processed!")
                processor = factory.get_processor("movie.mkv")
                # ... do processing
            else:
                print("Unsupported file format")
        """
        return self.get_processor(file_path) is not None
    
    def list_processors(self) -> Dict[str, str]:
        """
        List All Registered Processors
        
        Returns a mapping of file extensions to processor class names.
        Useful for debugging, documentation, and system introspection.
        
        INTROSPECTION:
        This method allows other parts of the system to understand
        what processors are available without needing to know the
        internal registry structure.
        
        DEBUG INFORMATION:
        The returned dictionary shows exactly which processor handles
        each format, making it easy to debug format selection issues.
        
        Returns:
            Dict[str, str]: Mapping of extensions to processor class names
            
        Example Return Value:
            {
                '.mkv': 'MKVProcessor',
                '.mp4': 'MP4Processor', 
                '.avi': 'AVIProcessor'
            }
            
        Example Usage:
            processors = factory.list_processors()
            for ext, processor_name in processors.items():
                print(f"{ext} files handled by {processor_name}")
        """
        return {
            ext: processor.__class__.__name__ 
            for ext, processor in self._processors.items()
        }
    
    def get_processor_count(self) -> int:
        """
        Get Number of Registered Processors
        
        Returns the count of unique processor instances registered
        with the factory. Note that this counts processor instances,
        not file extensions (one processor might handle multiple extensions).
        
        UNIQUE COUNTING:
        Since the same processor instance can be registered for multiple
        extensions, this method counts unique processor objects, not
        registry entries.
        
        Returns:
            int: Number of unique processor instances
            
        Example Usage:
            count = factory.get_processor_count()
            extensions = len(factory.get_supported_extensions())
            print(f"{count} processors supporting {extensions} file extensions")
        """
        # Count unique processor instances (not extensions)
        unique_processors = set(self._processors.values())
        return len(unique_processors)