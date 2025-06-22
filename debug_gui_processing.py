# debug_gui_processing.py - Test the GUI processing logic directly
"""
Test the exact same processing logic the GUI uses
"""

import sys
import os
sys.path.append('.')

from src.gui import SubtitleProcessorGUI

def test_gui_processing():
    print("Testing GUI processing logic...")
    
    # Create GUI instance (but don't show it)
    gui = SubtitleProcessorGUI()
    
    # Test file path
    test_file = r"C:\Users\iengl\Documents\Projects\Subtitle-Processor\The Clone Wars - S01E01 - Ambush.mkv"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    # Add file to GUI's file list (simulate drag-and-drop)
    gui.file_list = [test_file]
    print(f"Added file to GUI: {test_file}")
    
    # Get the processing parameters the GUI would use
    style_config_file = getattr(gui, 'current_config_file', None)
    manual_styling = getattr(gui, 'manual_styling_var', None)
    if manual_styling:
        manual_styling = manual_styling.get()
    
    print(f"Style config file: {style_config_file}")
    print(f"Manual styling: {manual_styling}")
    
    # Try to process using the same logic as GUI
    print("\nAttempting to process file...")
    try:
        # This should be similar to what the GUI does
        from main import UniversalSubtitleProcessor
        processor = UniversalSubtitleProcessor()
        
        result = processor.process_video_file(
            input_video=test_file,
            output_video=None,  # Auto-generate
            track_id=None,      # Auto-select first track
            style_config=None,
            style_config_file=style_config_file,
            manual_styling=manual_styling if manual_styling is not None else True
        )
        
        print(f"Processing result: {result}")
        if result:
            print("✓ SUCCESS: Processing completed successfully")
        else:
            print("✗ FAILED: Processing returned False")
            
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_processing()