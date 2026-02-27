"""
TabBar Demo

Demonstrates the TabBar and TabWidget components with:
- Dynamic add/remove tabs
- Theme switching
- Keyboard navigation
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit, QTextEdit,
    QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.theme_manager import ThemeManager
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from components.navigation.tab_bar import TabBar, TabWidget


class DemoPage(QWidget):
    """Demo page widget for tabs."""
    
    def __init__(self, title: str, color: QColor, parent=None):
        super().__init__(parent)
        
        self._init_ui(title, color)
    
    def _init_ui(self, title: str, color: QColor) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(title)
        label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 20px;
                background: {color.name()};
                border-radius: 8px;
            }}
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        info = QLabel(f"This is the content area for {title}")
        info.setStyleSheet("color: #888; font-size: 14px; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()


class TabBarDemoWindow(QMainWindow):
    """Main demo window for TabBar."""
    
    def __init__(self):
        super().__init__()
        
        self._tab_counter = 1
        
        self._init_theme()
        self._init_ui()
    
    def _init_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict('dark', DARK_THEME)
        theme_mgr.register_theme_dict('light', LIGHT_THEME)
        theme_mgr.set_theme('dark')
    
    def _init_ui(self) -> None:
        self.setWindowTitle("TabBar Demo")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        control_bar = self._create_control_bar()
        main_layout.addWidget(control_bar)
        
        self._tab_widget = TabWidget()
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self._tab_widget, 1)
        
        self._add_initial_tabs()
    
    def _create_control_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet("background: #252525; border-bottom: 1px solid #333;")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        add_btn = QPushButton("Add Tab")
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        add_btn.clicked.connect(self._add_tab)
        layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Current")
        remove_btn.setFixedHeight(36)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        remove_btn.clicked.connect(self._remove_current_tab)
        layout.addWidget(remove_btn)
        
        layout.addStretch()
        
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setFixedHeight(36)
        theme_btn.setStyleSheet("""
            QPushButton {
                background: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #27ae60;
            }
        """)
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)
        
        self._status_label = QLabel("Tabs: 0 | Current: None")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_label)
        
        return bar
    
    def _add_initial_tabs(self) -> None:
        colors = [
            QColor(52, 152, 219),
            QColor(46, 204, 113),
            QColor(155, 89, 182),
            QColor(241, 196, 15),
        ]
        
        for i, color in enumerate(colors):
            title = f"Tab {i + 1}"
            page = DemoPage(title, color)
            self._tab_widget.addTab(page, title, f"tab_{i + 1}")
        
        self._tab_counter = len(colors) + 1
        self._update_status()
    
    def _add_tab(self) -> None:
        colors = [
            QColor(231, 76, 60),
            QColor(26, 188, 156),
            QColor(52, 73, 94),
            QColor(230, 126, 34),
            QColor(149, 165, 166),
        ]
        
        color = colors[self._tab_counter % len(colors)]
        title = f"New Tab {self._tab_counter}"
        key = f"new_tab_{self._tab_counter}"
        
        page = DemoPage(title, color)
        self._tab_widget.addTab(page, title, key)
        
        self._tab_counter += 1
        self._update_status()
    
    def _remove_current_tab(self) -> None:
        key = self._tab_widget.currentKey()
        if key:
            self._tab_widget.removeTab(key)
            self._update_status()
    
    def _toggle_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        current = theme_mgr.current_theme()
        
        if current and current.name == 'dark':
            theme_mgr.set_theme('light')
        else:
            theme_mgr.set_theme('dark')
    
    def _on_tab_changed(self, index: int) -> None:
        self._update_status()
    
    def _update_status(self) -> None:
        count = self._tab_widget.count()
        current = self._tab_widget.tabBar().currentText()
        self._status_label.setText(f"Tabs: {count} | Current: {current or 'None'}")


def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = TabBarDemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
