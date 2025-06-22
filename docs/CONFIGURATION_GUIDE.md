# Configuration Guide - Subtitle Styling & Setup

## 📋 **Understanding Your Configuration**

Your `subtitle_config.json` file controls every aspect of how your subtitles look. Here's a complete breakdown of each parameter and how to customize them.

### **Your Current Configuration**

```json
{
	"subtitle_style": {
		"font_name": "Helvetica", // Clean, professional font
		"font_size": 22, // Good readability size
		"primary_color": "&H00FFFFFF", // Pure white text
		"secondary_color": "&H000000FF", // Red for emphasis
		"outline_color": "&H00000000", // Black outline for contrast
		"back_color": "&H80000000", // Semi-transparent black background
		"bold": 1, // Bold text for visibility
		"italic": 0, // No italic styling
		"outline": 1.0, // 1-pixel outline thickness
		"shadow": 1.0, // 1-pixel shadow depth
		"alignment": 2, // Bottom center position
		"margin_left": 30, // 30px left margin
		"margin_right": 30, // 30px right margin
		"margin_vertical": 30 // 30px bottom margin
	}
}
```

## 🎨 **Color System Guide**

### **ASS Color Format: `&HAABBGGRR`**

-   **AA**: Alpha (transparency) - 00=opaque, FF=fully transparent
-   **BB**: Blue component (00-FF)
-   **GG**: Green component (00-FF)
-   **RR**: Red component (00-FF)

### **Common Color Values**

```json
// Text Colors
"primary_color": "&H00FFFFFF",    // Pure white
"primary_color": "&H00F0F0F0",    // Off-white (softer)
"primary_color": "&H0000FFFF",    // Yellow (anime style)
"primary_color": "&H00FFFF00",    // Cyan (sci-fi style)

// Outline Colors
"outline_color": "&H00000000",    // Pure black (standard)
"outline_color": "&H00404040",    // Dark gray (softer)
"outline_color": "&H00800000",    // Dark blue

// Background Colors
"back_color": "&H80000000",       // Semi-transparent black (your style)
"back_color": "&H60000000",       // More transparent
"back_color": "&HA0000000",       // Less transparent
"back_color": "&H00000000",       // Completely opaque black
```

### **Color Picker Tool**

Use this Python snippet to convert RGB to ASS format:

```python
def rgb_to_ass(r, g, b, alpha=0):
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"

# Example: Convert white (255,255,255) with no transparency
print(rgb_to_ass(255, 255, 255, 0))  # Output: &H00FFFFFF
```

## 📝 **Typography Guide**

### **Font Recommendations**

#### **Sans-Serif Fonts (Recommended)**

-   **Arial**: Universal compatibility, excellent readability
-   **Helvetica**: Your choice - professional, clean lines
-   **Calibri**: Modern, friendly, great for presentations
-   **Verdana**: Designed specifically for screen reading
-   **Open Sans**: Web-optimized, very readable

#### **Serif Fonts (Cinematic)**

-   **Times New Roman**: Classic, elegant for movies
-   **Georgia**: Good screen readability for serif fonts
-   **Book Antiqua**: Traditional, sophisticated

#### **Monospace Fonts (Technical)**

-   **Courier New**: Technical content, code snippets
-   **Consolas**: Modern monospace, good readability

#### **Fonts to Avoid**

-   Decorative fonts (Comic Sans, Papyrus) - poor readability
-   Very thin fonts - become invisible at viewing distance
-   Fonts with poor Unicode support - missing characters

### **Font Size Guidelines**

```json
// By viewing scenario
"font_size": 18,    // Small screens (phone, tablet)
"font_size": 22,    // Desktop/laptop (your setting)
"font_size": 26,    // TV/large monitor
"font_size": 30,    // Projector/cinema
"font_size": 34,    // Accessibility/low vision
```

## 📐 **Positioning & Alignment**

### **Alignment Values**

```
1 = Bottom Left    2 = Bottom Center    3 = Bottom Right
4 = Middle Left    5 = Middle Center    6 = Middle Right
7 = Top Left       8 = Top Center       9 = Top Right
```

### **When to Use Each Position**

-   **2 (Bottom Center)**: Standard subtitles, dialogue (your setting)
-   **8 (Top Center)**: When bottom is blocked by graphics/credits
-   **1/3 (Bottom Left/Right)**: Speaker identification
-   **5 (Middle Center)**: Emergency text, warnings
-   **7/9 (Top Left/Right)**: Chapter titles, episode info

### **Margin Guidelines**

```json
// Small screens (phone/tablet)
"margin_left": 15, "margin_right": 15, "margin_vertical": 15,

// Medium screens (desktop/laptop) - Your setting
"margin_left": 30, "margin_right": 30, "margin_vertical": 30,

// Large screens (TV/projector)
"margin_left": 50, "margin_right": 50, "margin_vertical": 50,

// Ultra-wide/cinema
"margin_left": 80, "margin_right": 80, "margin_vertical": 40,
```

## 🎭 **Alternative Style Configurations**

### **Anime Style** (`anime_style.json`)

```json
{
	"subtitle_style": {
		"font_name": "Arial",
		"font_size": 24,
		"primary_color": "&H0000FFFF",
		"secondary_color": "&H000000FF",
		"outline_color": "&H00000000",
		"back_color": "&H80000000",
		"bold": 1,
		"italic": 0,
		"outline": 2.0,
		"shadow": 1.0,
		"alignment": 2,
		"margin_left": 40,
		"margin_right": 40,
		"margin_vertical": 40
	}
}
```

### **Movie Theater Style** (`movie_style.json`)

```json
{
	"subtitle_style": {
		"font_name": "Times New Roman",
		"font_size": 20,
		"primary_color": "&H00FFFFFF",
		"secondary_color": "&H000000FF",
		"outline_color": "&H00000000",
		"back_color": "&H70000000",
		"bold": 0,
		"italic": 0,
		"outline": 1.0,
		"shadow": 2.0,
		"alignment": 2,
		"margin_left": 25,
		"margin_right": 25,
		"margin_vertical": 25
	}
}
```

### **Presentation Style** (`presentation_style.json`)

```json
{
	"subtitle_style": {
		"font_name": "Calibri",
		"font_size": 26,
		"primary_color": "&H00FFFFFF",
		"secondary_color": "&H000000FF",
		"outline_color": "&H00000000",
		"back_color": "&H90000000",
		"bold": 1,
		"italic": 0,
		"outline": 1.5,
		"shadow": 0.5,
		"alignment": 2,
		"margin_left": 50,
		"margin_right": 50,
		"margin_vertical": 50
	}
}
```

### **High Visibility/Accessibility** (`accessibility_style.json`)

```json
{
	"subtitle_style": {
		"font_name": "Arial Black",
		"font_size": 28,
		"primary_color": "&H00FFFFFF",
		"secondary_color": "&H000000FF",
		"outline_color": "&H00000000",
		"back_color": "&HB0000000",
		"bold": 1,
		"italic": 0,
		"outline": 3.0,
		"shadow": 2.0,
		"alignment": 2,
		"margin_left": 60,
		"margin_right": 60,
		"margin_vertical": 60
	}
}
```

## ⚙️ **Advanced Configuration**

### **Understanding Outline and Shadow**

```json
// Subtle (your style)
"outline": 1.0, "shadow": 1.0,

// Dramatic
"outline": 3.0, "shadow": 2.0,

// Minimal
"outline": 0.5, "shadow": 0.0,

// High contrast
"outline": 2.0, "shadow": 3.0,
```

### **Bold and Italic Settings**

```json
"bold": 0,      // Normal weight
"bold": 1,      // Bold (your setting)

"italic": 0,    // Normal (your setting)
"italic": 1,    // Italic
```

### **Creating Custom Configs**

1. **Copy your base config**:

    ```bash
    cp subtitle_config.json custom_style.json
    ```

2. **Edit for specific content**:

    - Movies: Larger margins, elegant fonts
    - Anime: Bright colors, larger outline
    - Presentations: Professional fonts, high contrast
    - Accessibility: Large size, maximum contrast

3. **Use different configs**:
    ```bash
    python main.py movie.mkv -c custom_style.json
    ```

## 🔧 **Configuration Validation**

### **Test Your Configuration**

Create this test script (`test_config.py`):

```python
import json

def validate_config(config_path):
    try:
        with open(config_path) as f:
            config = json.load(f)

        style = config.get('subtitle_style', {})

        # Check required fields
        required = ['font_name', 'font_size', 'primary_color', 'alignment']
        missing = [field for field in required if field not in style]

        if missing:
            print(f"Missing required fields: {missing}")
        else:
            print("✅ Configuration is valid!")

        return len(missing) == 0

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

# Test your config
validate_config('subtitle_config.json')
```

### **Common Configuration Mistakes**

-   **Wrong color format**: Use `&H00FFFFFF` not `#FFFFFF`
-   **Invalid alignment**: Must be 1-9, not 0 or 10+
-   **Missing quotes**: JSON strings need quotes
-   **Wrong brackets**: Use `{}` for objects, `[]` for arrays

## 📱 **Platform-Specific Considerations**

### **Windows**

-   **Font availability**: Check if your chosen font is installed
-   **Path handling**: Use forward slashes in JSON paths
-   **Performance**: Larger files may process slower

### **macOS**

-   **Font names**: Some fonts have different names on macOS
-   **Retina displays**: Consider larger sizes for high-DPI screens
-   **Case sensitivity**: Be careful with font name capitalization

### **Linux**

-   **Font packages**: Install Microsoft fonts if using Arial/Times
-   **Display scaling**: Adjust sizes for different DPI settings
-   **Performance**: Generally fastest processing platform

## 🎯 **Best Practices**

### **Do's**

-   ✅ Use high contrast between text and outline
-   ✅ Test your config with actual video content
-   ✅ Keep margins appropriate for your typical viewing setup
-   ✅ Use bold text for better visibility
-   ✅ Stick to standard, widely-available fonts

### **Don'ts**

-   ❌ Don't use extremely large fonts that overwhelm the video
-   ❌ Don't use colors that blend with typical video content
-   ❌ Don't set margins too small (text may be cut off)
-   ❌ Don't use decorative fonts that hurt readability
-   ❌ Don't make outlines so thick they distract from text

### **Testing Your Configuration**

1. **Process a test video** with varied content (bright/dark scenes)
2. **View on your typical display** at normal viewing distance
3. **Check different video types** (movies, animation, presentations)
4. **Test readability** with and without glasses if applicable
5. **Verify on different devices** if you watch on multiple screens

Your current configuration strikes an excellent balance between readability and aesthetics - perfect for most content types!
