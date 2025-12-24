# Glyphs Scripts

Custom Python scripts for Glyphs 3 font editor.

## Smart Italic Builder

Advanced italic generator for sans-serif fonts with:
- Pixel-grid aligned slant presets (7.1°, 9.5°, 11.3°, 14.0°)
- Horizontal stem compensation control
- Automatic glyph alternate substitution (a, g, f)
- Path cleanup and extrema addition
- Pixel grid snapping

### Installation
1. Copy `SmartItalicBuilder.py` to: ~/Library/Application Support/Glyphs 3/Scripts/
2. Restart Glyphs
3. Access via: `Script > SmartItalicBuilderPro`

### Usage
1. Select your Regular master
2. Run the script from Script menu
3. Configure slant angle (11.3° is a good starting point)
4. Adjust compensation (2% is a good starting point)
5. Click "Create Italic Master"

### Requirements
- Glyphs 3.x
- Vanilla UI library (included with Glyphs)

### License
MIT License - Free to use and modify

### Author
Alex Glazier - December 2025
