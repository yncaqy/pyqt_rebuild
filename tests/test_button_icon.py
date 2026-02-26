#!/usr/bin/env python3
"""
Test script for CustomPushButton icon support

Tests the icon functionality of the CustomPushButton component, including:
- Icon loading and display
- Theme integration
- Icon size configuration
- Icon color role configuration
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QSize
from core.theme_manager import ThemeManager
from components.buttons.custom_push_button import CustomPushButton


class TestWindow(QMainWindow):
    """Test window for CustomPushButton icon support"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CustomPushButton Icon Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize theme manager
        self.theme_mgr = ThemeManager.instance()
        
        # Register a simple default theme
        default_theme = {
            'button.background.normal': '#7490E2',
            'button.background.hover': '#5A7BE2',
            'button.background.pressed': '#4A6BE2',
            'button.background.disabled': '#E1E1E1',
            'button.text.normal': '#FFFFFF',
            'button.text.disabled': '#A1A1A1',
            'button.border.normal': '#5A7BE2',
            'button.border.hover': '#4A6BE2',
            'button.border.pressed': '#3A5BE2',
            'button.border.disabled': '#E1E1E1',
            'button.icon.normal': '#FFFFFF'
        }
        
        self.theme_mgr.register_theme_dict('default', default_theme)
        self.theme_mgr.set_theme('default')
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create button with icon
        self.create_icon_buttons(layout)
        
        # Create theme toggle button
        self.create_theme_toggle(layout)
        
    def create_icon_buttons(self, layout):
        """Create buttons with different icon configurations"""
        # Test 1: Button with close icon
        close_button = CustomPushButton("Close", icon_name="window_close")
        layout.addWidget(close_button)
        
        # Test 2: Button with minimize icon
        minimize_button = CustomPushButton("Minimize", icon_name="window_minimize")
        layout.addWidget(minimize_button)
        
        # Test 3: Button with maximize icon
        maximize_button = CustomPushButton("Maximize", icon_name="window_maximize")
        layout.addWidget(maximize_button)
        
        # Test 4: Button with restore icon
        restore_button = CustomPushButton("Restore", icon_name="window_restore")
        layout.addWidget(restore_button)
        
        # Test 5: Button with default window icon
        default_button = CustomPushButton("Default", icon_name="default_window_icon")
        layout.addWidget(default_button)
        
    def create_theme_toggle(self, layout):
        """Create theme toggle button"""
        toggle_button = QPushButton("Toggle Theme")
        toggle_button.clicked.connect(self.toggle_theme)
        layout.addWidget(toggle_button)
        
    def toggle_theme(self):
        """Toggle between themes"""
        current_theme = self.theme_mgr.current_theme()
        if current_theme and current_theme.name == 'default':
            # Create a light theme
            light_theme = {
                'button.background.normal': '#F0F0F0',
                'button.background.hover': '#E0E0E0',
                'button.background.pressed': '#D0D0D0',
                'button.background.disabled': '#F5F5F5',
                'button.text.normal': '#333333',
                'button.text.disabled': '#A1A1A1',
                'button.border.normal': '#D0D0D0',
                'button.border.hover': '#C0C0C0',
                'button.border.pressed': '#B0B0B0',
                'button.border.disabled': '#E1E1E1',
                'button.icon.normal': '#333333'
            }
            self.theme_mgr.register_theme_dict('light', light_theme)
            self.theme_mgr.set_theme('light')
        else:
            # Switch back to default theme
            self.theme_mgr.set_theme('default')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
