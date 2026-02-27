"""
Pivot Component Demo

Demonstrates the Pivot component with:
- Basic usage
- Dynamic add/remove items
- Keyboard navigation
- Theme switching
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QWidget, 
    QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt

from containers.frameless_window import FramelessWindow
from components.navigation.pivot import Pivot
from components.buttons.custom_push_button import CustomPushButton
from components.buttons.primary_push_button import PrimaryPushButton
from components.containers.themed_group_box import ThemedGroupBox
from components.containers.themed_widget import ThemedWidget
from components.labels.themed_label import ThemedLabel
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME


class PivotDemoWindow(FramelessWindow):
    """Demo window for Pivot component."""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_content()
    
    def _setup_window(self):
        """Setup window properties."""
        self.setTitle("Pivot Component Demo")
        self.resize(800, 500)
    
    def _setup_content(self):
        """Setup content."""
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = ThemedLabel("Pivot 组件演示", font_role='title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Basic usage demo
        layout.addWidget(self._create_basic_demo())
        
        # Dynamic demo
        layout.addWidget(self._create_dynamic_demo())
        
        # Keyboard navigation info
        layout.addWidget(self._create_keyboard_info())
        
        layout.addStretch()
        
        self.setCentralWidget(container)
    
    def _create_basic_demo(self):
        """Create basic usage demo."""
        group = ThemedGroupBox("基本用法")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create pivot
        self._basic_pivot = Pivot()
        self._basic_pivot.addItem("首页", "home")
        self._basic_pivot.addItem("设置", "settings")
        self._basic_pivot.addItem("关于", "about")
        
        # Create stacked widget for content
        self._basic_stack = QStackedWidget()
        
        # Create pages
        home_page = ThemedLabel("这是首页内容\n\n欢迎使用 Pivot 组件！")
        home_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        settings_page = ThemedLabel("这是设置页面\n\n可以在这里配置各种选项")
        settings_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        about_page = ThemedLabel("这是关于页面\n\nPivot 组件 v1.0\n支持平滑下划线动画")
        about_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._basic_stack.addWidget(home_page)
        self._basic_stack.addWidget(settings_page)
        self._basic_stack.addWidget(about_page)
        
        # Connect pivot to stack
        self._basic_pivot.currentChanged.connect(self._on_basic_pivot_changed)
        
        layout.addWidget(self._basic_pivot)
        layout.addWidget(self._basic_stack)
        
        group.setLayout(layout)
        return group
    
    def _create_dynamic_demo(self):
        """Create dynamic add/remove demo."""
        group = ThemedGroupBox("动态操作")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create pivot
        self._dynamic_pivot = Pivot()
        self._dynamic_pivot.addItem("标签 1", "tab1")
        self._dynamic_pivot.addItem("标签 2", "tab2")
        self._dynamic_pivot.addItem("标签 3", "tab3")
        
        self._tab_counter = 3
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = PrimaryPushButton("添加标签")
        add_btn.clicked.connect(self._add_tab)
        
        remove_btn = CustomPushButton("移除当前")
        remove_btn.clicked.connect(self._remove_current_tab)
        
        clear_btn = CustomPushButton("清空所有")
        clear_btn.clicked.connect(self._clear_tabs)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        
        # Status label
        self._status_label = ThemedLabel("当前: 标签 1", font_role='small')
        
        self._dynamic_pivot.currentChanged.connect(self._on_dynamic_pivot_changed)
        
        layout.addWidget(self._dynamic_pivot)
        layout.addLayout(btn_layout)
        layout.addWidget(self._status_label)
        
        group.setLayout(layout)
        return group
    
    def _create_keyboard_info(self):
        """Create keyboard navigation info."""
        group = ThemedGroupBox("键盘导航")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        info = ThemedLabel(
            "← : 切换到上一个标签\n"
            "→ : 切换到下一个标签\n"
            "Home : 切换到第一个标签\n"
            "End : 切换到最后一个标签",
            font_role='body'
        )
        
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def _on_basic_pivot_changed(self, key: str):
        """Handle basic pivot change."""
        index_map = {"home": 0, "settings": 1, "about": 2}
        if key in index_map:
            self._basic_stack.setCurrentIndex(index_map[key])
    
    def _on_dynamic_pivot_changed(self, key: str):
        """Handle dynamic pivot change."""
        item = self._dynamic_pivot.item(key)
        if item:
            self._status_label.setText(f"当前: {item.text()}")
    
    def _add_tab(self):
        """Add a new tab."""
        self._tab_counter += 1
        key = f"tab{self._tab_counter}"
        text = f"标签 {self._tab_counter}"
        self._dynamic_pivot.addItem(text, key, select=True)
    
    def _remove_current_tab(self):
        """Remove current tab."""
        key = self._dynamic_pivot.currentKey()
        if key:
            self._dynamic_pivot.removeItem(key)
    
    def _clear_tabs(self):
        """Clear all tabs."""
        self._dynamic_pivot.clear()
        self._status_label.setText("无选中标签")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Initialize theme
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.register_theme_dict('light', LIGHT_THEME)
    theme_mgr.set_theme('dark')
    
    window = PivotDemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
