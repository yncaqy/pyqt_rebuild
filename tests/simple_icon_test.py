"""
简单的默认图标测试

验证 FramelessWindow 的默认矢量图标是否正确加载和显示
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DARK_THEME


class SimpleIconTest(FramelessWindow):
    """简单图标测试窗口"""

    def __init__(self):
        super().__init__()
        self.setTitle("FramelessWindow 默认图标测试")
        self.resize(500, 300)
        self._setup_content()

    def _setup_content(self):
        """设置测试内容"""
        content = QWidget()
        layout = QVBoxLayout(content)

        # 标题
        title = QLabel("默认矢量图标已加载")
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #4facfe; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 说明
        info = QLabel("请查看窗口左上角的标题栏\n应该显示默认的应用图标")
        info.setStyleSheet("color: #666666; font-size: 14px; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # 提示
        layout = QVBoxLayout(self)
        layout.addWidget(content)
        layout.addStretch()


def main():
    """运行测试应用"""
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 初始化主题管理器
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.set_theme('dark')

    # 创建测试窗口
    window = SimpleIconTest()

    # 居中窗口
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())

    print("\n=== FramelessWindow 默认图标测试 ===")
    print("窗口已创建，请检查标题栏左上角是否显示图标")
    print("=" * 40)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
