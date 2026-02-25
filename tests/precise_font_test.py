#!/usr/bin/env python3
"""
精确测试字体切换问题
"""

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import our components
from src.core.theme_manager import ThemeManager
from src.core.font_manager import FontManager
from src.themes.dark import THEME_DATA as dark_theme
from src.themes.light import THEME_DATA as light_theme

class PreciseTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Precise Font Switching Test")
        self.resize(800, 600)
        
        # Initialize managers
        self.theme_mgr = ThemeManager.instance()
        self.font_mgr = FontManager.instance()
        
        # Register themes with SAME font sizes but different families/styles
        # 这样可以排除字体大小变化的干扰
        modified_light_theme = light_theme.copy()
        modified_light_theme['font'] = {
            'family': 'Times New Roman',  # 明显不同的字体族
            'size': {
                'title': 16,  # 保持相同大小
                'header': 14,
                'body': 12,
                'small': 10
            },
            'weight': {
                'title': 'normal',  # 不同的粗细
                'header': 'normal',
                'body': 'normal',
                'small': 'normal'
            }
        }
        
        self.theme_mgr.register_theme_dict('dark', dark_theme)
        self.theme_mgr.register_theme_dict('light', modified_light_theme)
        
        # Create UI
        main_layout = QVBoxLayout()
        
        # Test area
        test_area = QWidget()
        test_layout = QVBoxLayout(test_area)
        
        # 标题标签 - 我们要测试的对象
        self.main_title = QLabel("Complete Application Theme Switching Demo")
        self.main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_title.setStyleSheet("border: 2px solid red; padding: 10px;")  # 添加边框便于观察
        test_layout.addWidget(self.main_title)
        
        # 字体信息显示
        self.font_info = QLabel("Font info will appear here")
        self.font_info.setWordWrap(True)
        self.font_info.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        test_layout.addWidget(self.font_info)
        
        main_layout.addWidget(test_area)
        
        # 控制面板
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        dark_btn = QPushButton("🌙 Dark Theme (Segoe UI, Bold)")
        dark_btn.clicked.connect(lambda: self.switch_theme('dark'))
        control_layout.addWidget(dark_btn)
        
        light_btn = QPushButton("☀️ Light Theme (Times New Roman, Normal)")
        light_btn.clicked.connect(lambda: self.switch_theme('light'))
        control_layout.addWidget(light_btn)
        
        refresh_btn = QPushButton("🔄 Refresh Font")
        refresh_btn.clicked.connect(self.refresh_font)
        control_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(control_panel)
        
        self.setLayout(main_layout)
        
        # Apply initial theme
        self.switch_theme('dark')
        
    def switch_theme(self, theme_name):
        """Switch theme and show detailed font information."""
        print(f"\n=== Switching to {theme_name.upper()} theme ===")
        
        # 切换主题
        self.theme_mgr.set_theme(theme_name)
        
        # 获取当前主题
        current_theme = self.theme_mgr.current_theme()
        print(f"Current theme: {current_theme.name if current_theme else 'None'}")
        
        # 应用字体到标题
        print("Applying font to title label...")
        self.font_mgr.apply_font_to_widget(self.main_title, 'title')
        
        # 获取应用后的字体信息
        applied_font = self.main_title.font()
        print(f"Applied font details:")
        print(f"  Family: {applied_font.family()}")
        print(f"  Point Size: {applied_font.pointSize()}")
        print(f"  Pixel Size: {applied_font.pixelSize()}")
        print(f"  Weight: {applied_font.weight()}")
        print(f"  Bold: {applied_font.bold()}")
        print(f"  Italic: {applied_font.italic()}")
        
        # 从主题中获取配置信息进行对比
        if current_theme:
            theme_family = current_theme.get_value('font.family', 'Unknown')
            theme_size = current_theme.get_value('font.size.title', 'Unknown')
            theme_weight = current_theme.get_value('font.weight.title', 'Unknown')
            print(f"Theme configuration:")
            print(f"  Configured family: {theme_family}")
            print(f"  Configured size: {theme_size}")
            print(f"  Configured weight: {theme_weight}")
            
            # 检查是否匹配
            family_match = applied_font.family() == theme_family
            size_match = applied_font.pointSize() == theme_size
            print(f"Family match: {family_match}")
            print(f"Size match: {size_match}")
        
        # 更新UI显示
        self.update_display(applied_font, current_theme)
        
    def refresh_font(self):
        """手动刷新字体应用."""
        print("\n=== Manual Font Refresh ===")
        current_theme = self.theme_mgr.current_theme()
        if current_theme:
            self.font_mgr.apply_font_to_widget(self.main_title, 'title')
            applied_font = self.main_title.font()
            self.update_display(applied_font, current_theme)
            print("Font manually refreshed")
        
    def update_display(self, font, theme):
        """更新显示信息."""
        info_text = f"<h3>当前字体信息:</h3>"
        info_text += f"<b>字体族:</b> {font.family()}<br>"
        info_text += f"<b>点大小:</b> {font.pointSize()}<br>"
        info_text += f"<b>像素大小:</b> {font.pixelSize()}<br>"
        info_text += f"<b>粗细:</b> {font.weight()} ({'Bold' if font.bold() else 'Normal'})<br>"
        info_text += f"<b>斜体:</b> {'Yes' if font.italic() else 'No'}<br>"
        
        if theme:
            theme_family = theme.get_value('font.family', 'Unknown')
            theme_size = theme.get_value('font.size.title', 'Unknown')
            theme_weight = theme.get_value('font.weight.title', 'Unknown')
            info_text += f"<br><h3>主题配置:</h3>"
            info_text += f"<b>配置字体族:</b> {theme_family}<br>"
            info_text += f"<b>配置大小:</b> {theme_size}<br>"
            info_text += f"<b>配置粗细:</b> {theme_weight}<br>"
            
        self.font_info.setText(info_text)

def main():
    app = QApplication(sys.argv)
    window = PreciseTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()