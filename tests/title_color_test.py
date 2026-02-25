#!/usr/bin/env python3
"""
专门测试标题文本颜色切换的程序
"""

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.containers import FramelessWindow
from src.core.theme_manager import ThemeManager
from src.core.font_manager import FontManager

class TitleColorTest(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("标题颜色切换测试")
        self.resize(600, 400)

        # 初始化管理器
        self._theme_mgr = ThemeManager.instance()
        self._font_mgr = FontManager.instance()

        # 注册主题
        self._register_themes()

        # 创建UI
        self._init_ui()

        # 应用初始主题
        self._theme_mgr.set_theme('dark')

    def _register_themes(self):
        """注册测试主题"""
        # Dark theme
        dark_theme = {
            'label': {
                'text': '#ff6b6b',  # 亮红色 - 更明显
                'text.disabled': '#787878',
                'background': '#00000000'
            },
            'font': {
                'family': 'Segoe UI',
                'size': {
                    'title': 18,
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

        # Light theme
        light_theme = {
            'label': {
                'text': '#2e8b57',  # 海绿色 - 更明显
                'text.disabled': '#999999',
                'background': '#00000000'
            },
            'font': {
                'family': 'Segoe UI',
                'size': {
                    'title': 18,
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

        self._theme_mgr.register_theme_dict('dark', dark_theme)
        self._theme_mgr.register_theme_dict('light', light_theme)

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题标签
        self.title_label = QLabel("Complete Application Theme Switching Demo")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 应用标题字体
        self._font_mgr.apply_font_to_widget(self.title_label, 'title')
        layout.addWidget(self.title_label)

        # 状态显示
        self.status_label = QLabel("当前主题: 未知")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 颜色信息显示
        self.color_info = QLabel("颜色信息将在此显示")
        self.color_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.color_info)

        # 控制按钮
        button_layout = QVBoxLayout()

        self.dark_btn = QPushButton("切换到深色主题")
        self.dark_btn.clicked.connect(lambda: self._switch_theme('dark'))
        button_layout.addWidget(self.dark_btn)

        self.light_btn = QPushButton("切换到浅色主题")
        self.light_btn.clicked.connect(lambda: self._switch_theme('light'))
        button_layout.addWidget(self.light_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        # 订阅主题变更
        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _switch_theme(self, theme_name):
        """切换主题"""
        print(f"[TEST] 切换到主题: {theme_name}")
        self._theme_mgr.set_theme(theme_name)

    def _on_theme_changed(self, theme):
        """处理主题变更"""
        print(f"[TEST] 接收到主题变更通知: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        # 更新状态显示
        self.status_label.setText(f"当前主题: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        # 获取主题颜色
        text_color = theme.get_color('label.text', QColor(0, 0, 0))
        print(f"[TEST] 获取到文本颜色: {text_color.name()}")

        # 应用样式
        style = f"color: {text_color.name()}; font-size: 18px; font-weight: bold;"
        self.title_label.setStyleSheet(style)
        print(f"[TEST] 应用样式: {style}")

        # 显示颜色信息
        self.color_info.setText(f"文本颜色: {text_color.name()} | RGB: ({text_color.red()}, {text_color.green()}, {text_color.blue()})")

        # 强制刷新
        self.title_label.update()
        self.update()

        print(f"[TEST] 标题标签更新完成")

def main():
    app = QApplication(sys.argv)
    window = TitleColorTest()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
