#!/usr/bin/env python3
"""
Debug script to investigate title font switching issues.
"""

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import our components
from src.core.theme_manager import ThemeManager
from src.core.font_manager import FontManager
from src.themes.dark import THEME_DATA as dark_theme
from src.themes.light import THEME_DATA as light_theme

class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Title Font Debug")
        self.resize(600, 400)
        
        # Initialize managers
        self.theme_mgr = ThemeManager.instance()
        self.font_mgr = FontManager.instance()
        
        # Register themes
        self.theme_mgr.register_theme_dict('dark', dark_theme)
        self.theme_mgr.register_theme_dict('light', light_theme)
        
        # Create UI
        layout = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel("Complete Application Theme Switching Demo")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Debug info
        self.debug_label = QLabel("Current theme: None\nFont info will appear here")
        self.debug_label.setWordWrap(True)
        layout.addWidget(self.debug_label)
        
        # Control buttons
        dark_btn = QPushButton("Switch to Dark Theme")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        layout.addWidget(dark_btn)
        
        light_btn = QPushButton("Switch to Light Theme")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        layout.addWidget(light_btn)
        
        # Apply initial theme
        self.switch_theme('dark')
        
        self.setLayout(layout)
        
    def switch_theme(self, theme_name):
        """Switch theme and update display."""
        print(f"Switching to theme: {theme_name}")
        self.theme_mgr.set_theme(theme_name)
        
        # Get current theme
        current_theme = self.theme_mgr.current_theme()
        print(f"Current theme object: {current_theme}")
        
        # Apply font to title
        self.font_mgr.apply_font_to_widget(self.title_label, 'title')
        
        # Get the actual font that was applied
        applied_font = self.title_label.font()
        print(f"Applied font - Family: {applied_font.family()}, Size: {applied_font.pointSize()}, Weight: {applied_font.weight()}")
        
        # Update debug info
        debug_text = f"Current theme: {theme_name}\n"
        debug_text += f"Font family: {applied_font.family()}\n"
        debug_text += f"Font size: {applied_font.pointSize()}\n"
        debug_text += f"Font weight: {applied_font.weight()}\n"
        
        if current_theme:
            family = current_theme.get_value('font.family', 'Unknown')
            title_size = current_theme.get_value('font.size.title', 'Unknown')
            title_weight = current_theme.get_value('font.weight.title', 'Unknown')
            debug_text += f"\nTheme config:\n"
            debug_text += f"  Family: {family}\n"
            debug_text += f"  Title size: {title_size}\n"
            debug_text += f"  Title weight: {title_weight}\n"
        
        self.debug_label.setText(debug_text)

def main():
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()