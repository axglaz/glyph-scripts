# MenuTitle: Smart Italic Builder
# -*- coding: utf-8 -*-
__doc__ = """
Advanced Italic Generator for Sans-Serif Fonts
Creates italic masters with precise slant control, stem compensation,
glyph alternates, and pixel-grid alignment.

Designed for Special Gothic and similar grotesque sans-serifs.
Author: Claude Sonnet 4.5 Thinking prompted by Alex Glazier
"""

import math
from GlyphsApp import *
from vanilla import *

class SmartItalicBuilder:
    def __init__(self):
        # Validate font is open
        self.font = Glyphs.font
        if not self.font:
            Message("Please open a font file first.", "No Font Open")
            return
        
        # Get current master
        self.current_master = self.font.selectedFontMaster
        if not self.current_master:
            Message("No master selected.", "Error")
            return
        
        # Preset angle values (pixel-grid aligned)
        self.preset_angles = [7.1, 9.5, 11.3, 14.0, None]
        self.default_preset = 2  # 11.3° (1:5 ratio)
        
        # Glyph alternates mapping
        self.italic_alternates = {
            'a': ['a.ss01', 'a.italic'],
            'g': ['g.ss01', 'g.italic'],
            'f': ['f.italic', 'f.ss01']
        }
        
        # Build UI
        self.build_ui()
        self.w.open()
    
    def build_ui(self):
        """Construct the user interface"""
        window_width = 340
        window_height = 460
        margin = 15
        
        self.w = FloatingWindow((window_width, window_height), "Smart Italic Builder")
        
        y = margin
        
        # === SOURCE MASTER INFO ===
        self.w.text_source = TextBox((margin, y, -margin, 17), 
            "Source Master:", sizeStyle='regular')
        y += 20
        self.w.source_label = TextBox((margin, y, -margin, 22), 
            f"→ {self.current_master.name}", 
            sizeStyle='small')
        
        y += 35
        self.w.divider1 = HorizontalLine((margin, y, -margin, 1))
        
        # === SLANT PRESETS ===
        y += 15
        self.w.text_presets = TextBox((margin, y, -margin, 17), 
            "Slant Angle:", sizeStyle='regular')
        y += 22
        
        preset_labels = [
            "7.1° (1:8 ratio) — Subtle",
            "9.5° (1:6 ratio) — Classic",
            "11.3° (1:5 ratio) — Standard",
            "14.0° (1:4 ratio) — Aggressive",
            "Custom:"
        ]
        
        self.w.presets = RadioGroup((margin, y, -margin, 105), 
            preset_labels,
            callback=self.preset_changed,
            sizeStyle='small')
        self.w.presets.set(self.default_preset)
        
        y += 110
        self.w.custom_input = EditText((margin + 20, y - 28, 60, 22), 
            text="11.3",
            enable=False,
            sizeStyle='small')
        
        # === STEM COMPENSATION ===
        y += 20
        self.w.text_comp = TextBox((margin, y, 200, 17), 
            "Horizontal Compensation:", sizeStyle='regular')
        self.w.comp_percent = TextBox((-70, y, -margin, 17), 
            "2.0%", 
            sizeStyle='small', 
            alignment='right')
        y += 22
        
        self.w.slider_comp = Slider((margin, y, -margin, 20), 
            minValue=0, 
            maxValue=8, 
            value=2.0,
            callback=self.slider_changed,
            sizeStyle='small')
        
        y += 25
        self.w.comp_caption = TextBox((margin, y, -margin, 28), 
            "Widens glyphs to counteract vertical stem thinning.\n0% = none, 2% = calculated, 5%+ = overcorrection", 
            sizeStyle='mini')
        
        y += 35
        self.w.divider2 = HorizontalLine((margin, y, -margin, 1))
        
        # === OPTIONS ===
        y += 15
        self.w.check_alternates = CheckBox((margin, y, -margin, 20), 
            "Use Italic Alternates (a, g, f)", 
            value=True,
            sizeStyle='small')
        
        y += 25
        self.w.check_extremes = CheckBox((margin, y, -margin, 20), 
            "Add Extremes & Cleanup Paths", 
            value=True,
            sizeStyle='small')
        
        y += 25
        self.w.check_pixel = CheckBox((margin, y, -margin, 20), 
            "Snap to Pixel Grid (for screen fonts)", 
            value=False,
            sizeStyle='small')
        
        # === RUN BUTTON ===
        y += 35
        self.w.button_run = Button((margin, -50, -margin, 35), 
            "Create Italic Master", 
            callback=self.run_generation)
    
    def preset_changed(self, sender):
        """Handle preset radio button selection"""
        selected = sender.get()
        
        if selected == 4:  # Custom
            self.w.custom_input.enable(True)
        else:
            self.w.custom_input.enable(False)
            self.w.custom_input.set(str(self.preset_angles[selected]))
    
    def slider_changed(self, sender):
        """Update compensation percentage label"""
        value = sender.get()
        self.w.comp_percent.set(f"{value:.1f}%")
    
    def get_angle(self):
        """Retrieve the selected angle"""
        preset_idx = self.w.presets.get()
        if preset_idx == 4:  # Custom
            try:
                return float(self.w.custom_input.get())
            except ValueError:
                Message("Invalid custom angle. Using 11.3°", "Input Error")
                return 11.3
        else:
            return self.preset_angles[preset_idx]
    
    def find_alternate_glyph(self, base_name):
        """Find an alternate glyph for italic substitution"""
        if base_name not in self.italic_alternates:
            return None
        
        # Check if any alternates exist
        for alt_name in self.italic_alternates[base_name]:
            if alt_name in [g.name for g in self.font.glyphs]:
                return alt_name
        
        return None
    
    def run_generation(self, sender):
        """Main generation process"""
        self.font.disableUpdateInterface()
        
        try:
            # === GATHER PARAMETERS ===
            angle = self.get_angle()
            comp_percent = self.w.slider_comp.get()
            use_alternates = self.w.check_alternates.get()
            do_cleanup = self.w.check_extremes.get()
            snap_pixel = self.w.check_pixel.get()
            
            # Validation
            if angle < 1 or angle > 20:
                Message("Angle must be between 1° and 20°", "Invalid Input")
                return
            
            # === CREATE NEW MASTER ===
            source_id = self.current_master.id
            new_master = self.current_master.copy()
            
            # Generate italic name
            base_name = self.current_master.name
            if "Italic" in base_name:
                Message("Source master already appears to be italic.", "Warning")
                return
            
            new_master.name = base_name.replace("Regular", "Italic")
            if "Bold" in base_name and "Italic" not in new_master.name:
                new_master.name = base_name.replace("Bold", "Bold Italic")
            if "Italic" not in new_master.name:
                new_master.name = base_name + " Italic"
            
            # Set italic angle (negative = right slant in Glyphs)
            new_master.italicAngle = -angle
            
            # Add to font
            self.font.masters.append(new_master)
            new_master_id = new_master.id
            
            # === CALCULATE TRANSFORMATION MATRIX ===
            rad_angle = math.radians(angle)
            skew_tan = math.tan(rad_angle)
            
            # Compensation: base + user adjustment
            stretch_x = 1.0 + (comp_percent / 100.0)
            
            # Transformation matrix: [a, b, c, d, tx, ty]
            # For skew + stretch: x' = x*stretch + y*skew*stretch, y' = y
            transform_matrix = NSAffineTransformStruct()
            transform_matrix.m11 = stretch_x
            transform_matrix.m12 = 0
            transform_matrix.m21 = skew_tan * stretch_x
            transform_matrix.m22 = 1
            transform_matrix.tX = 0
            transform_matrix.tY = 0
            
            # === PROCESS GLYPHS ===
            processed_count = 0
            substituted_count = 0
            
            print(f"\n=== Generating {new_master.name} ===")
            print(f"Angle: {angle}°, Compensation: {comp_percent}%")
            print(f"Transform Matrix: [{transform_matrix.m11:.4f}, {transform_matrix.m12}, {transform_matrix.m21:.4f}, {transform_matrix.m22}]")
            
            for glyph in self.font.glyphs:
                # Get or create layer for new master
                layer = glyph.layers[new_master_id]
                
                if not layer:
                    # Sync layer from source
                    source_layer = glyph.layers[source_id]
                    if source_layer:
                        layer = source_layer.copy()
                        layer.associatedMasterId = new_master_id
                        glyph.layers[new_master_id] = layer
                    else:
                        continue
                
                # === ALTERNATE GLYPH SUBSTITUTION ===
                if use_alternates:
                    alt_name = self.find_alternate_glyph(glyph.name)
                    if alt_name:
                        alt_glyph = self.font.glyphs[alt_name]
                        alt_layer = alt_glyph.layers[source_id]
                        
                        if alt_layer:
                            # Replace layer content with alternate
                            layer.clear()
                            for path in alt_layer.paths:
                                layer.paths.append(path.copy())
                            for component in alt_layer.components:
                                layer.components.append(component.copy())
                            
                            layer.width = alt_layer.width
                            substituted_count += 1
                            print(f"  Substituted: {glyph.name} → {alt_name}")
                
                # === APPLY TRANSFORM ===
                if len(layer.paths) > 0 or len(layer.components) > 0:
                    transform = NSAffineTransform.transform()
                    transform.setTransformStruct_(transform_matrix)
                    layer.applyTransform(transform)
                    
                    # === POST-PROCESSING ===
                    if do_cleanup:
                        layer.addNodesAtExtremes()
                        layer.cleanUpPaths()
                        layer.correctPathDirection()
                    
                    if snap_pixel:
                        layer.roundCoordinates()
                    
                    processed_count += 1
            
            print(f"\n✓ Processed {processed_count} glyphs")
            if substituted_count > 0:
                print(f"✓ Substituted {substituted_count} alternates")
            
            # === SWITCH TO NEW MASTER ===
            self.font.selectedFontMaster = new_master
            
            # === SUCCESS MESSAGE ===
            summary = f"Created: {new_master.name}\n\n"
            summary += f"Processed: {processed_count} glyphs\n"
            if substituted_count > 0:
                summary += f"Substituted: {substituted_count} alternates\n"
            summary += f"\nNext Steps:\n"
            summary += f"1. Check 'H' and 'O' stem weights\n"
            summary += f"2. Adjust sidebearings/spacing\n"
            summary += f"3. Fix any curve distortions\n"
            summary += f"4. Run on Bold master with same settings"
            
            Message(summary, "✓ Italic Generation Complete")
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            Message(f"Script failed. Check Macro Panel for details.\n\n{str(e)}", "Error")
        
        finally:
            self.font.enableUpdateInterface()

# Run the script
SmartItalicBuilder()
