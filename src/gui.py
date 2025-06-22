# gui.py
"""
Universal Subtitle Processor - Graphical User Interface

This file implements the drag-and-drop GUI interface that provides an intuitive,
user-friendly way to process video files with styled subtitles.

ARCHITECTURE ROLE:
This is the primary user interface layer that sits between the user and the
processing engine. It translates user actions (drag/drop, button clicks) into
processing commands and provides real-time feedback.

SYSTEM INTEGRATION:
- Imports and uses all the core processing components
- Provides visual feedback for the underlying processing pipeline
- Handles batch operations and user configuration management
- Bridges the gap between user intent and system execution

DESIGN PHILOSOPHY:
- Make complex subtitle processing accessible to non-technical users
- Provide immediate visual feedback for all operations
- Handle errors gracefully with helpful messages
- Support both single-file and batch processing workflows

GUI WORKFLOW:
1. User launches GUI (via main.py)
2. User selects configuration file (JSON styling config)
3. User drags/drops video files or folders
4. System validates files and shows supported formats
5. User clicks "Start Processing" to begin batch operation
6. GUI shows real-time progress and results
7. User receives completion notification with results summary
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinterdnd2 as tkdnd  # Enables drag-and-drop functionality
import os
import threading
from pathlib import Path
import queue
import time


class SubtitleProcessorGUI:
    """
    Main GUI Application Class
    
    This class creates and manages the entire graphical user interface for the
    subtitle processor. It handles all user interactions, file management,
    and coordination with the processing engine.
    
    ARCHITECTURE PATTERN:
    Uses the MVC (Model-View-Controller) pattern where:
    - Model: The processing engine and file system
    - View: The tkinter GUI components
    - Controller: This class coordinating between them
    
    KEY RESPONSIBILITIES:
    - Create and layout all GUI components
    - Handle drag-and-drop file operations
    - Manage processing queue and user configuration
    - Provide real-time feedback during processing
    - Handle errors and edge cases gracefully
    
    THREADING DESIGN:
    - GUI runs on the main thread for responsiveness
    - File processing runs on background threads to prevent freezing
    - Thread-safe communication using tkinter's after() method
    """
    
    def __init__(self):
        """
        Initialize the GUI Application
        
        Sets up the main window, imports all processing components, and
        initializes the user interface. This constructor establishes the
        foundation for all GUI operations.
        """
        # Create the main application window using tkinterdnd2 for drag-drop support
        self.root = tkdnd.Tk()
        self.root.title("Universal Subtitle Processor")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Import and initialize all processing components
        # These are the same components used by the CLI interface
        from .file_utils import FileManager
        from .video import UniversalVideoProcessor
        from .subtitle_processor import SubtitleProcessor as SubtitleStyleProcessor
        from .aegisub_processor import AegisubProcessor
        
        self.file_manager = FileManager()                    # File operations and temp management
        self.video_processor = UniversalVideoProcessor()     # Video format handling
        self.subtitle_processor = SubtitleStyleProcessor()   # Subtitle styling engine
        self.aegisub_processor = AegisubProcessor()          # Manual editing integration
        
        # Application state management
        self.processing_queue = queue.Queue()               # Thread-safe processing queue
        self.processing_active = False                       # Flag to prevent concurrent processing
        self.current_config_file = None                     # Path to selected JSON config
        
        # Get supported formats dynamically from the processing engine
        # This automatically updates when new format processors are added
        self.supported_formats = self.video_processor.get_supported_extensions()
        
        # Initialize the user interface components
        self.setup_ui()
        self.setup_drag_drop()
        
    def setup_ui(self):
        """
        Create and Layout All GUI Components
        
        This method constructs the entire user interface using a hierarchical
        approach with logical groupings. Each section has a specific purpose
        in the user workflow.
        
        UI HIERARCHY:
        1. Title and branding
        2. Configuration section (style settings)
        3. Drag-and-drop area (main user interaction)
        4. Progress feedback (real-time status)
        5. Control buttons (start/clear operations)
        6. File list (queue management)
        
        DESIGN PRINCIPLES:
        - Clear visual hierarchy with labeled sections
        - Logical flow from configuration to processing
        - Immediate feedback for all user actions
        - Accessible and intuitive layout
        """
        
        # === TITLE SECTION ===
        # Main application title and branding
        title_label = tk.Label(
            self.root, 
            text="Universal Subtitle Processor", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # === CONFIGURATION SECTION ===
        # This section handles all user configuration options
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding="10")
        config_frame.pack(fill="x", padx=20, pady=5)
        
        # Configuration file selection subsection
        config_btn_frame = tk.Frame(config_frame, bg='#f0f0f0')
        config_btn_frame.pack(fill="x", pady=5)
        
        tk.Label(config_btn_frame, text="Style Config:", bg='#f0f0f0').pack(side="left")
        
        # Display currently selected configuration file
        self.config_label = tk.Label(
            config_btn_frame, 
            text="No config file selected", 
            bg='white', 
            relief="sunken",
            anchor="w"
        )
        self.config_label.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        # Button to browse for configuration file
        config_btn = ttk.Button(
            config_btn_frame, 
            text="Browse", 
            command=self.select_config_file
        )
        config_btn.pack(side="right")
        
        # Processing options subsection
        options_frame = tk.Frame(config_frame, bg='#f0f0f0')
        options_frame.pack(fill="x", pady=5)
        
        # Option to use manual styling with Aegisub
        self.manual_styling_var = tk.BooleanVar(value=False)
        manual_check = tk.Checkbutton(
            options_frame,
            text="Open Aegisub for manual styling",
            variable=self.manual_styling_var,
            bg='#f0f0f0'
        )
        manual_check.pack(side="left")
        
        # === DRAG-AND-DROP SECTION ===
        # This is the main user interaction area
        drop_frame = ttk.LabelFrame(self.root, text="Drag & Drop Files/Folders", padding="20")
        drop_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create dynamic text showing supported formats
        formats_text = ", ".join(self.supported_formats)
        self.drop_area = tk.Label(
            drop_frame,
            text=f"📁 Drag and drop video files or folders here\n\n"
                 f"• Supported formats: {formats_text}\n"
                 "• Drop a single file to process it\n"
                 "• Drop a folder to process all supported files inside\n"
                 "• Multiple files/folders supported",
            font=("Arial", 12),
            bg='white',
            relief="sunken",
            bd=2,
            fg='#666666'
        )
        self.drop_area.pack(fill="both", expand=True)
        
        # === PROGRESS SECTION ===
        # Real-time feedback during processing operations
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill="x", padx=20, pady=5)
        
        # Text-based progress updates
        self.progress_var = tk.StringVar(value="Ready to process files...")
        self.progress_label = tk.Label(
            progress_frame, 
            textvariable=self.progress_var,
            bg='#f0f0f0'
        )
        self.progress_label.pack(fill="x")
        
        # Visual progress indicator
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate'  # Animated progress bar for ongoing operations
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # === CONTROL SECTION ===
        # Primary action buttons for processing control
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Main processing button
        self.process_btn = ttk.Button(
            button_frame,
            text="Start Processing",
            command=self.start_processing,
            state="disabled"  # Disabled until files are added
        )
        self.process_btn.pack(side="left")
        
        # Queue management button
        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear Queue",
            command=self.clear_queue
        )
        self.clear_btn.pack(side="left", padx=(10, 0))
        
        # === FILE LIST SECTION ===
        # Display and manage the processing queue
        list_frame = ttk.LabelFrame(self.root, text="Files to Process", padding="10")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create listbox with scrollbar for file queue
        list_container = tk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)
        
        # Listbox to show queued files
        self.file_listbox = tk.Listbox(list_container, height=6)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_drag_drop(self):
        """
        Configure Drag-and-Drop Functionality
        
        This method sets up the drag-and-drop event handlers that allow users
        to drag files from their file manager directly into the application.
        This is the primary way users add files to the processing queue.
        
        DRAG-DROP EVENTS:
        - DragEnter: Visual feedback when dragging over the drop area
        - DragLeave: Reset visual feedback when leaving the drop area
        - Drop: Process the dropped files and add them to the queue
        
        VISUAL FEEDBACK:
        The drop area changes appearance during drag operations to provide
        clear visual feedback about where files can be dropped.
        """
        # Register the drop area as a valid drop target for files
        self.drop_area.drop_target_register(tkdnd.DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Set up visual feedback during drag operations
        self.drop_area.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_area.dnd_bind('<<DragLeave>>', self.on_drag_leave)
    
    def on_drag_enter(self, event):
        """
        Visual Feedback: Drag Enter
        
        Called when the user drags files over the drop area.
        Changes the appearance to indicate this is a valid drop target.
        """
        self.drop_area.configure(bg='#e6f3ff', relief="solid", bd=2)
    
    def on_drag_leave(self, event):
        """
        Visual Feedback: Drag Leave
        
        Called when the user drags files away from the drop area.
        Resets the appearance to the normal state.
        """
        self.drop_area.configure(bg='white', relief="sunken", bd=2)
    
    def handle_drop(self, event):
        """
        Process Dropped Files and Folders
        
        This is the main entry point for user file input. It handles both
        individual files and entire folders, automatically filtering for
        supported video formats.
        
        PROCESSING LOGIC:
        1. Parse the dropped file paths from the event
        2. For each path, determine if it's a file or folder
        3. For files: Check if the format is supported and add to queue
        4. For folders: Recursively scan for supported video files
        5. Update the UI to reflect the new files in the queue
        
        Args:
            event: Tkinter drop event containing file path information
        """
        # Reset visual feedback
        self.drop_area.configure(bg='white', relief="sunken", bd=2)
        
        # Extract file paths from the drop event
        # tkinterdnd2 provides paths as a space-separated string that needs parsing
        files = self.root.tk.splitlist(event.data)
        
        # Process each dropped item
        for file_path in files:
            if os.path.isfile(file_path) and self.video_processor.can_process(file_path):
                # Single supported video file
                self.add_file_to_queue(file_path)
            elif os.path.isdir(file_path):
                # Folder - scan for supported video files
                self.add_folder_to_queue(file_path)
        
        # Update UI state based on new queue contents
        self.update_ui_state()
    
    def add_file_to_queue(self, file_path):
        """
        Add a Single Video File to the Processing Queue
        
        Validates the file and adds it to the visual queue if it's not already present.
        Provides user feedback about the addition.
        
        DUPLICATE PREVENTION:
        Checks the current queue to prevent adding the same file multiple times.
        
        Args:
            file_path (str): Full path to the video file to add
        """
        # Check for duplicates in the current queue
        current_files = [self.file_listbox.get(i) for i in range(self.file_listbox.size())]
        if file_path not in current_files:
            # Add to the visual queue
            self.file_listbox.insert(tk.END, file_path)
            # Provide user feedback
            self.progress_var.set(f"Added: {os.path.basename(file_path)}")
    
    def add_folder_to_queue(self, folder_path):
        """
        Add All Supported Video Files from a Folder
        
        Recursively scans a folder and all its subfolders for supported video files.
        This enables batch processing of entire directory structures.
        
        RECURSIVE SCANNING:
        Uses os.walk() to traverse the entire directory tree, finding all
        video files regardless of their location in the folder structure.
        
        VALIDATION:
        Each found file is validated against the supported formats list
        before being added to the queue.
        
        Args:
            folder_path (str): Path to the folder to scan
        """
        video_files = []
        
        # Recursively scan the folder structure
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Check if this file can be processed by our system
                if self.video_processor.can_process(file_path):
                    video_files.append(file_path)
        
        # Process the results
        if video_files:
            # Add all found files to the queue
            for video_file in video_files:
                self.add_file_to_queue(video_file)
            self.progress_var.set(f"Added {len(video_files)} video files from folder")
        else:
            # Inform user if no supported files were found
            messagebox.showwarning("No Video Files", f"No supported video files found in {folder_path}")
    
    def select_config_file(self):
        """
        Configuration File Selection Dialog
        
        Opens a file browser dialog to let the user select their subtitle
        styling configuration JSON file. This file contains all the styling
        parameters that will be applied to the subtitles.
        
        FILE VALIDATION:
        The dialog filters for JSON files but also allows "All files" in case
        the user has a configuration file with a different extension.
        """
        file_path = filedialog.askopenfilename(
            title="Select Subtitle Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            # Store the selected configuration
            self.current_config_file = file_path
            # Update the UI to show the selected file
            self.config_label.configure(text=os.path.basename(file_path))
            # Provide user feedback
            self.progress_var.set(f"Configuration loaded: {os.path.basename(file_path)}")
    
    def clear_queue(self):
        """
        Clear All Files from the Processing Queue
        
        Removes all files from the queue and resets the UI state.
        Useful when the user wants to start over with a different set of files.
        """
        self.file_listbox.delete(0, tk.END)
        self.progress_var.set("Queue cleared")
        self.update_ui_state()
    
    def update_ui_state(self):
        """
        Update UI Element States Based on Current Application State
        
        This method ensures that UI elements (buttons, etc.) are enabled or
        disabled appropriately based on the current state of the application.
        
        STATE LOGIC:
        - Start Processing button: Enabled only when files are queued and not currently processing
        - Other UI elements: Enabled/disabled based on processing state
        """
        has_files = self.file_listbox.size() > 0
        not_processing = not self.processing_active
        
        # Enable processing button only when conditions are met
        self.process_btn.configure(
            state="normal" if (has_files and not_processing) else "disabled"
        )
    
    def start_processing(self):
        """
        Begin Processing All Queued Files
        
        This method initiates the batch processing workflow. It validates
        the current state, confirms user settings, and starts the processing
        in a background thread to keep the UI responsive.
        
        PRE-PROCESSING VALIDATION:
        1. Check that files are queued for processing
        2. Check configuration file (optional but recommended)
        3. Confirm user wants to proceed if no configuration
        
        THREADING DESIGN:
        Processing runs in a background thread to prevent the GUI from freezing
        during long operations. Progress updates are sent back to the main thread
        using tkinter's thread-safe after() method.
        """

        # Prevent concurrent processing operations
        if self.processing_active:
            return
        
        # Get the list of files to process
        files_to_process = [self.file_listbox.get(i) for i in range(self.file_listbox.size())]
        
        # Validate that we have files to process
        if not files_to_process:
            messagebox.showwarning("No Files", "No files in queue to process")
            return
        
        # Check for configuration file and confirm if missing
        if not self.current_config_file:
            result = messagebox.askyesno(
                "No Configuration", 
                "No style configuration file selected. Continue with default styling?"
            )
            if not result:
                return
        
        # Update UI for processing state
        self.processing_active = True
        self.progress_bar.start()  # Start animated progress indicator
        self.update_ui_state()
        
        # Start processing in a background thread
        processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(files_to_process,)
        )
        processing_thread.daemon = True  # Thread will close when main program closes
        processing_thread.start()
    
    def process_files_thread(self, files_to_process):
        """
        Background Thread: Process All Files in the Queue
        
        This method runs in a separate thread to process all queued files
        without blocking the GUI. It provides progress updates and handles
        errors for individual files while continuing with the batch operation.
        
        THREAD SAFETY:
        All GUI updates are made using root.after() to ensure thread safety.
        Direct GUI manipulation from background threads can cause crashes.
        
        ERROR HANDLING:
        Individual file failures don't stop the batch operation. Each file
        is processed independently with its own error handling.
        
        Args:
            files_to_process (List[str]): List of file paths to process
        """
        try:
            total_files = len(files_to_process)
            processed = 0
            failed = 0
            
            # Process each file in the queue
            for i, file_path in enumerate(files_to_process, 1):
                # Update progress (thread-safe GUI update)
                self.root.after(0, lambda f=file_path, i=i, t=total_files: 
                               self.progress_var.set(f"Processing ({i}/{t}): {os.path.basename(f)}"))
                
                try:
                    # Generate output path for this file
                    output_path = self.file_manager.generate_output_path(file_path, "_styled")
                    
                    # Load style configuration if available
                    style_config = None
                    if self.current_config_file:
                        style_config = self.subtitle_processor.load_style_config(self.current_config_file)
                    
                    # Process this file using the main processing engine
                    from main import UniversalSubtitleProcessor
                    processor = UniversalSubtitleProcessor()
                    
                    success = processor.process_video_file(
                        input_video=file_path,
                        output_video=output_path,
                        style_config=style_config,
                        manual_styling=self.manual_styling_var.get()
                    )
                    
                    # Update counters and provide feedback
                    if success:
                        processed += 1
                        self.root.after(0, lambda f=file_path: self.progress_var.set(
                            f"✅ Completed: {os.path.basename(f)}"
                        ))
                    else:
                        failed += 1
                        self.root.after(0, lambda f=file_path: self.progress_var.set(
                            f"❌ Failed: {os.path.basename(f)}"
                        ))
                    
                    # Brief pause for UI updates and to prevent overwhelming the system
                    time.sleep(0.5)
                    
                except Exception as e:
                    # Handle individual file processing errors
                    failed += 1
                    self.root.after(0, lambda e=e: self.progress_var.set(f"❌ Error: {str(e)}"))
            
            # Provide final summary of the batch operation
            self.root.after(0, lambda: self.progress_var.set(
                f"Completed! Processed: {processed}, Failed: {failed}"
            ))
            
        except Exception as e:
            # Handle overall processing errors
            self.root.after(0, lambda: self.progress_var.set(f"Processing error: {str(e)}"))
        
        finally:
            # Always reset the UI state when processing completes
            self.root.after(0, self.processing_finished)
    
    def processing_finished(self):
        """
        Reset UI After Processing Completion
        
        This method is called when batch processing completes (successfully or with errors).
        It resets the UI to its ready state and notifies the user of completion.
        
        UI RESET:
        - Stop progress bar animation
        - Re-enable processing controls
        - Show completion message
        """
        self.processing_active = False
        self.progress_bar.stop()
        self.update_ui_state()
        
        # Show completion notification
        messagebox.showinfo("Processing Complete", "File processing has finished!")
    
    def run(self):
        """
        Start the GUI Application
        
        This method performs final startup checks and launches the main GUI loop.
        It validates that required tools are available before allowing the user
        to proceed with processing operations.
        
        STARTUP VALIDATION:
        Checks that the necessary video processing tools (MKVToolNix, FFmpeg, etc.)
        are available. If not, shows an error message with installation guidance.
        
        Returns:
            bool: True if GUI launched successfully, False if startup failed
        """
        # Check that required processing tools are available
        tools_status = self.video_processor.check_tools_available()
        if not any(tools_status.values()):
            messagebox.showerror(
                "Missing Tools", 
                "No video processing tools are available.\n"
                "Please install MKVToolNix or FFmpeg to use this application."
            )
            return False
        
        # Start the main GUI event loop
        self.root.mainloop()
        return True