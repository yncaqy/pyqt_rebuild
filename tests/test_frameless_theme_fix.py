#!/usr/bin/env python3
"""
FramelessWindow主题切换功能修复验证测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager


class ThemeTestWindow(FramelessWindow):
    """用于测试主题切换的窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frameless Theme Test")
        self.setMinimumSize(600, 400)
        
        # 创建测试内容
        self._setup_test_content()
        
    def _setup_test_content(self):
        """设置测试内容"""
        # 创建一个简单的垂直布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加一些测试组件
        test_btn1 = QPushButton("测试按钮 1")
        test_btn2 = QPushButton("测试按钮 2")
        test_btn2.setEnabled(False)  # 禁用状态测试
        
        layout.addWidget(test_btn1)
        layout.addWidget(test_btn2)
        
        # 添加主题切换按钮
        theme_toggle_btn = QPushButton("切换到深色主题")
        theme_toggle_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_toggle_btn)
        
        # 设置布局到内容区域
        content_widget = QWidget()
        content_widget.setLayout(layout)
        self.setCentralWidget(content_widget)
        
    def _toggle_theme(self):
        """切换主题测试"""
        theme_mgr = ThemeManager.instance()
        current = theme_mgr.current_theme().name if theme_mgr.current_theme() else "none"
        
        if current == "light":
            theme_mgr.set_theme("dark")
            sender = self.sender()
            if sender:
                sender.setText("切换到浅色主题")
        else:
            theme_mgr.set_theme("light")
            sender = self.sender()
            if sender:
                sender.setText("切换到深色主题")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 初始化主题管理器
    theme_mgr = ThemeManager.instance()
    
    # 注册测试主题
    light_theme = {
        'window': {
            'background': '#f0f0f0',
            'border': '#cccccc'
        },
        'titlebar': {
            'background': '#e0e0e0',
            'text': '#333333',
            'button': {
                'hover': '#d0d0d0',
                'close_hover': '#e74c3c'
            }
        },
        'button': {
            'background': {
                'normal': '#ffffff',
                'hover': '#f0f0f0',
                'pressed': '#e0e0e0',
                'disabled': '#f8f8f8'
            },
            'text': '#333333',
            'text': {
                'disabled': '#999999'
            },
            'border': '#cccccc',
            'border': {
                'hover': '#aaaaaa',
                'pressed': '#888888'
            },
            'border_radius': 4,
            'padding': '6px 12px'
        }
    }
    
    dark_theme = {
        'window': {
            'background': '#2d2d2d',
            'border': '#444444'
        },
        'titlebar': {
            'background': '#3d3d3d',
            'text': '#e0e0e0',
            'button': {
                'hover': '#555555',
                'close_hover': '#e74c3c'
            }
        },
        'button': {
            'background': {
                'normal': '#3a3a3a',
                'hover': '#4a4a4a',
                'pressed': '#5a5a5a',
                'disabled': '#2a2a2a'
            },
            'text': '#e0e0e0',
            'text': {
                'disabled': '#666666'
            },
            'border': '#555555',
            'border': {
                'hover': '#666666',
                'pressed': '#777777'
            },
            'border_radius': 4,
            'padding': '6px 12px'
        }
    }
    
    theme_mgr.register_theme_dict("light", light_theme)
    theme_mgr.register_theme_dict("dark", dark_theme)
    
    # 设置初始主题
    theme_mgr.set_theme("light")
    
    # 创建并显示测试窗口
    window = ThemeTestWindow()
    window.show()
    
    print("FramelessWindow主题切换测试启动...")
    print(f"初始主题: {theme_mgr.current_theme().name if theme_mgr.current_theme() else 'None'}")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())