#!/usr/bin/env python3
"""测试滚动条样式"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager
from components.containers.themed_scroll_area import ThemedScrollArea
from themes.dark import DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.set_theme('dark')
    
    window = QWidget()
    window.setWindowTitle("滚动条测试")
    window.resize(400, 500)
    
    layout = QVBoxLayout(window)
    
    scroll = ThemedScrollArea()
    scroll.setWidgetResizable(True)
    
    content = QWidget()
    content_layout = QVBoxLayout(content)
    
    for i in range(30):
        label = QLabel(f"项目 {i+1}")
        label.setStyleSheet("padding: 10px; background: #2a2a2a; margin: 2px; border-radius: 4px; color: white;")
        content_layout.addWidget(label)
    
    content_layout.addStretch()
    scroll.setWidget(content)
    
    layout.addWidget(scroll)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
