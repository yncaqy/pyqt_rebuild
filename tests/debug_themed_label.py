#!/usr/bin/env python3
"""
ThemedLabel主题更新问题调试脚本
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from components.labels.themed_label import ThemedLabel
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME


class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThemedLabel Debug Test")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # 创建ThemedLabel
        self.label = ThemedLabel("测试主题标签", font_role='title')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 添加主题切换按钮
        dark_btn = QPushButton("切换到深色主题")
        dark_btn.clicked.connect(self.switch_to_dark)
        layout.addWidget(dark_btn)
        
        light_btn = QPushButton("切换到浅色主题")
        light_btn.clicked.connect(self.switch_to_light)
        layout.addWidget(light_btn)
        
        # 添加状态显示
        self.status_label = ThemedLabel("状态: 未初始化", font_role='body')
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 初始化主题
        self.init_themes()
        
    def init_themes(self):
        """初始化主题"""
        theme_mgr = ThemeManager.instance()
        
        # 注册主题
        theme_mgr.register_theme_dict('dark', DARK_THEME)
        theme_mgr.register_theme_dict('light', LIGHT_THEME)
        
        # 设置初始主题
        theme_mgr.set_theme('light')
        
        # 更新状态
        current_theme = theme_mgr.current_theme()
        self.status_label.setText(f"状态: 主题已初始化 - {current_theme.name if current_theme else 'None'}")
        print(f"主题初始化完成，当前主题: {current_theme.name if current_theme else 'None'}")
        print(f"订阅者数量: {len(theme_mgr._subscribers)}")
        
    def switch_to_dark(self):
        """切换到深色主题"""
        theme_mgr = ThemeManager.instance()
        theme_mgr.set_theme('dark')
        current_theme = theme_mgr.current_theme()
        self.status_label.setText(f"状态: 已切换到深色主题 - {current_theme.name if current_theme else 'None'}")
        print(f"切换到深色主题，订阅者数量: {len(theme_mgr._subscribers)}")
        
    def switch_to_light(self):
        """切换到浅色主题"""
        theme_mgr = ThemeManager.instance()
        theme_mgr.set_theme('light')
        current_theme = theme_mgr.current_theme()
        self.status_label.setText(f"状态: 已切换到浅色主题 - {current_theme.name if current_theme else 'None'}")
        print(f"切换到浅色主题，订阅者数量: {len(theme_mgr._subscribers)}")


def main():
    app = QApplication(sys.argv)
    
    # 检查主题管理器初始状态
    theme_mgr = ThemeManager.instance()
    print(f"初始状态 - 当前主题: {theme_mgr.current_theme().name if theme_mgr.current_theme() else 'None'}")
    print(f"初始状态 - 订阅者数量: {len(theme_mgr._subscribers)}")
    
    window = DebugWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())