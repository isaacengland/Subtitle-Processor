# Universal Subtitle Processor - Complete Setup & Extensibility Guide

## 🚀 **Quick Start Guide**

### **System Requirements**

-   **Python 3.7+** - Download from [python.org](https://python.org)
-   **Operating System**: Windows 10+, macOS 10.14+, or Linux (any modern distribution)
-   **Disk Space**: ~50MB for the application + space for video processing
-   **Memory**: 4GB RAM recommended for smooth video processing

### **Required External Tools**

The system uses external tools for video processing. Install the ones you need:

#### **MKVToolNix (Essential for MKV files)**

-   **Download**: [mkvtoolnix.download](https://mkvtoolnix.download/)
-   **Purpose**: MKV file analysis, subtitle extraction, and video merging
-   **Installation**:
    -   Windows: Use the installer, ensure "Add to PATH" is checked
    -   macOS: Use Homebrew (`brew install mkvtoolnix`) or download DMG
    -   Linux: Use package manager (`sudo apt install mkvtoolnix` or equivalent)

#### **FFmpeg (Required for format conversion)**

-   **Download**: [ffmpeg.org](https://ffmpeg.org/)
-   **Purpose**: Subtitle format conversion (SRT/VTT → ASS)
-   **Installation**:
    -   Windows: Download static build, add to PATH manually
    -   macOS: Use Homebrew (`brew install ffmpeg`)
    -   Linux: Use package manager (`sudo apt install ffmpeg`)

#### **Aegisub (Optional - for manual editing)**

-   **Download**: [aegisub.org](https://aegisub.org/)
-   **Purpose**: Professional subtitle editing and advanced styling
-   **Installation**: Standard installer for your platform

### **Verification Commands**

Test that tools are properly installed:

```bash
# Test MKVToolNix
mkvinfo --version
mkvextract --version
mkvmerge --version

# Test FFmpeg
ffmpeg -version
ffprobe -version

# Test Aegisub (optional)
aegisub --version
```

## 📁 **Installation Steps**

### **1. Create Project Directory**

```bash
mkdir Universal_Subtitle_Processor
cd Universal_Subtitle_Processor
```

### **2. Download and Save All Files**

Save each of the following files in your project directory:

#### **Core System Files:**

-   `video_processor_base.py` - Abstract interface for all video processors
-   `mkv_processor.py` - MKV file format handler
-   `video_processor_factory.py` - Format selection and management
-   `universal_video_processor.py` - Universal format interface
-   `file_utils.py` - File management utilities
-   `subtitle_processor.py` - Subtitle styling engine
-   `aegisub_processor.py` - Manual editing integration
-   `gui.py` - Drag & drop GUI interface
-   `main.py` - Launcher

#### **Configuration and Setup Files:**

-   `subtitle_config.json` - Your styling configuration
-   `requirements.txt` - Python dependencies
-   `launch_gui.bat` - Windows launcher script
-   `launch_gui.sh` - Linux/macOS launcher script

#### **Documentation (Optional):**

-   `README.md` - This setup guide
-   `CONFIGURATION_GUIDE.md` - Detailed styling and config help
-   `EXTENDING_THE_SYSTEM.md` - How to add new video format support

### **3. Install Python Dependencies**

```bash
pip install tkinterdnd2
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### **4. Verify Installation**

```bash
python main.py --help
```

Should show the command-line help without errors.

## 🎯 **Usage Guide**

### **Method 1: Double-Click GUI (Recommended)**

1. **Double-click `main.py`** to launch the GUI
2. **Select your config file**: Click "Browse" and choose `subtitle_config.json`
3. **Drag and drop files**: Drop MKV files or entire folders onto the interface
4. **Start processing**: Click "Start Processing" and watch the magic happen!

### **Method 2: Command Line Interface**

```bash
# Basic processing with your config
python main.py movie.mkv -c subtitle_config.json --no-manual

# Process with manual Aegisub styling
python main.py movie.mkv -c subtitle_config.json

# Specify output file and subtitle track
python main.py movie.mkv -o styled_movie.mkv -t 2 -c subtitle_config.json

# Quick styling without config file
python main.py movie.mkv --font-name "Arial" --font-size 24 --no-manual
```

### **Method 3: Launcher Scripts**

-   **Windows**: Double-click `launch_gui.bat`
-   **Linux/macOS**: Run `./launch_gui.sh` or `bash launch_gui.sh`

## 🎨 **Configuration Guide**

### **Understanding Your Styling Configuration**

Your `subtitle_config.json` file controls how subtitles look. Here's what each parameter does:

```json
{
	"subtitle_style": {
		"font_name": "Helvetica", // Font family name
		"font_size": 22, // Size in points
		"primary_color": "&H00FFFFFF", // Text color (white)
		"secondary_color": "&H000000FF", // Secondary color (red)
		"outline_color": "&H00000000", // Outline color (black)
		"back_color": "&H80000000", // Background (semi-transparent black)
		"bold": 1, // Bold text (0=off, 1=on)
		"italic": 0, // Italic text (0=off, 1=on)
		"outline": 1.0, // Outline thickness in pixels
		"shadow": 1.0, // Shadow depth in pixels
		"alignment": 2, // Position (2=bottom center)
		"margin_left": 30, // Left margin in pixels
		"margin_right": 30, // Right margin in pixels
		"margin_vertical": 30 // Bottom margin in pixels
	}
}
```

### **Color Format Explanation**

Colors use ASS format: `&HAABBGGRR`

-   **AA**: Alpha (transparency) - 00=opaque, FF=transparent
-   **BB**: Blue component (00-FF)
-   **GG**: Green component (00-FF)
-   **RR**: Red component (00-FF)

**Common Colors:**

-   White: `&H00FFFFFF`
-   Black: `&H00000000`
-   Red: `&H000000FF`
-   Blue: `&H00FF0000`
-   Semi-transparent black: `&H80000000`

### **Alignment Values**

```
1 = Bottom Left    2 = Bottom Center    3 = Bottom Right
4 = Middle Left    5 = Middle Center    6 = Middle Right
7 = Top Left       8 = Top Center       9 = Top Right
```

### **Creating Custom Configurations**

Copy and modify `subtitle_config.json` for different styles:

```bash
# Create multiple style configs
cp subtitle_config.json movie_style.json
cp subtitle_config.json anime_style.json
cp subtitle_config.json presentation_style.json
```

Then edit each for different use cases.

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **"No video processing tools available"**

**Problem**: MKVToolNix or FFmpeg not found
**Solution**:

1. Install the missing tools
2. Ensure they're added to your system PATH
3. Restart your terminal/command prompt
4. Test with version commands shown above

#### **"tkinterdnd2 not found"**

**Problem**: GUI dependencies missing
**Solution**: `pip install tkinterdnd2`

#### **"No subtitle tracks found"**

**Problem**: Video file doesn't contain subtitle tracks
**Solution**:

1. Verify subtitles exist using MKVToolNix GUI
2. Try a different video file
3. Check if subtitles are in a separate file

#### **GUI won't start**

**Problem**: Python or dependency issues
**Solution**:

1. Run `python main.py` from command line to see error messages
2. Check Python version: `python --version` (needs 3.7+)
3. Reinstall dependencies: `pip install --force-reinstall tkinterdnd2`

#### **Processing fails with permission errors**

**Problem**: File access or tool permissions
**Solution**:

1. Check file permissions (read/write access)
2. Run as administrator (Windows) or with sudo (Linux/macOS) if needed
3. Ensure output directory is writable

#### **Aegisub integration not working**

**Problem**: Aegisub not found or not launching
**Solution**:

1. Install Aegisub from official website
2. Ensure it's in your system PATH
3. Try launching Aegisub manually first
4. Check logs for specific error messages

### **Getting Help**

1. **Check the logs**: The system provides detailed logging information
2. **Test components individually**: Use command-line tools directly
3. **Verify file formats**: Ensure your video files are supported
4. **Check configurations**: Validate your JSON syntax

## 🏗️ **System Architecture Overview**

Understanding how the system works helps with troubleshooting and customization:

```
User Input (GUI/CLI)
        ↓
main.py (Universal Launcher)
        ↓
UniversalSubtitleProcessor (Orchestrator)
        ↓
UniversalVideoProcessor (Format Abstraction)
        ↓
VideoProcessorFactory (Format Selection)
        ↓
MKVProcessor (Format Implementation)
        ↓
External Tools (MKVToolNix, FFmpeg)
```

### **Component Responsibilities**

-   **main.py**: Entry point, CLI/GUI detection
-   **gui.py**: Drag-and-drop interface, user interaction
-   **UniversalSubtitleProcessor**: Workflow orchestration
-   **UniversalVideoProcessor**: Format-agnostic interface
-   **VideoProcessorFactory**: Processor selection and management
-   **MKVProcessor**: MKV-specific operations
-   **SubtitleProcessor**: Styling and format conversion
-   **AegisubProcessor**: Manual editing integration
-   **FileManager**: File operations and cleanup

## 📈 **Performance Optimization**

### **Processing Speed Tips**

1. **Use SSDs**: Faster disk I/O improves processing speed
2. **Close other applications**: Free up system resources
3. **Process smaller batches**: Handle files in groups rather than all at once
4. **Use automatic styling**: Skip manual editing for bulk processing

### **Quality vs Speed Trade-offs**

-   **Fastest**: Automatic styling only (`--no-manual`)
-   **Balanced**: Automatic styling with spot-checking
-   **Highest Quality**: Manual editing for every file

### **Disk Space Management**

-   **Temporary files**: Automatically cleaned up after processing
-   **Output files**: Generated with `_styled` suffix by default
-   **Backup strategy**: Keep originals until you're satisfied with results

## 🔮 **Future Enhancements**

The system is designed to be easily extensible. Here are some planned improvements:

### **Additional Format Support**

-   **MP4 Processor**: Coming soon for MP4/M4V files
-   **AVI Processor**: Legacy format support
-   **Universal Format**: Streaming and web video support

### **Advanced Features**

-   **Batch Configuration**: Different styles for different file types
-   **Template System**: Reusable styling templates
-   **Preview Mode**: See styling before processing
-   **Cloud Integration**: Process files in the cloud

### **Automation Enhancements**

-   **Watch Folders**: Automatically process new files
-   **Scheduling**: Process files at specific times
-   **Integration APIs**: Connect with other tools
-   **Streaming Support**: Real-time subtitle processing

## 🤝 **Contributing and Extending**

### **Adding New Video Format Support**

The system is designed to make adding new formats trivial:

1. **Create processor class** inheriting from `VideoProcessorBase`
2. **Implement all abstract methods** for your format
3. **Register in factory** by adding one line to `_register_default_processors()`
4. **Test and deploy** - the entire system automatically supports your format!

### **Customizing Styling**

-   **Modify configurations**: Create new JSON configs for different styles
-   **Extend styling logic**: Add new parameters to the styling engine
-   **Custom effects**: Integrate with Aegisub automation scripts

### **Integration Opportunities**

-   **Media players**: Direct integration with video playback software
-   **Content management**: Batch processing for media libraries
-   **Streaming platforms**: Automated subtitle preparation
-   **Accessibility tools**: Enhanced subtitle processing for accessibility

The system's modular architecture makes it easy to extend and customize for specific needs while maintaining the core functionality and ease of use.
