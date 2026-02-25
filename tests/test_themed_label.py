#!/usr/bin/env python3
"""
Simple test for ThemedLabel component
"""

import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from src.components.labels.themed_label import ThemedLabel
from src.core.theme_manager import ThemeManager

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThemedLabel Test")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create themed labels with different categories
        title_label = ThemedLabel("This is a Title")
        title_label.set_category('title')
        
        header_label = ThemedLabel("This is a Header")
        header_label.set_category('header')
        
        body_label = ThemedLabel("This is body text with normal styling")
        body_label.set_category('body')
        
        small_label = ThemedLabel("This is small text")
        small_label.set_category('small')
        
        # Add to layout
        layout.addWidget(title_label)
        layout.addWidget(header_label)
        layout.addWidget(body_label)
        layout.addWidget(small_label)
        
        # Setup themes
        self._setup_themes()
        
    def _setup_themes(self):
        """Setup basic themes for testing."""
        theme_mgr = ThemeManager.instance()
        
        # Simple dark theme
        dark_theme = {
            'label': {
                'text': '#e0e0e0',
                'text.disabled': '#666666',
                'background': '#00000000'  # Transparent
            },
            'font': {
                'family': 'Segoe UI',
                'size': {
                    'title': 16,
                    'header': 14,
                    'body': 12,
                    'small': 10
                },
                'weight': {
                    'title': 'bold',
                    'header': 'bold',
                    'body': 'normal',
                    'small': 'normal'
                }
            }
        }
        
        # Simple light theme
        light_theme = {
            'label': {
                'text': '#333333',
                'text.disabled': '#999999',
                'background': '#00000000'  # Transparent
            },
            'font': {
                'family': 'Segoe UI',
                'size': {
                    'title': 16,
                    'header': 14,
                    'body': 12,
                    'small': 10
                },
                'weight': {
                    'title': 'bold',
                    'header': 'bold',
                    'body': 'normal',
                    'small': 'normal'
                }
            }
        }
        
        theme_mgr.register_theme_dict('dark', dark_theme)
        theme_mgr.register_theme_dict('light', light_theme)
        theme_mgr.set_theme('dark')

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())