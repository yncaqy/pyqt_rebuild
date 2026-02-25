"""
测试默认图标功能

测试 IconManager 和 FramelessWindow 的默认图标功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont

from core.icon_manager import IconManager
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DARK_THEME


class IconTestWindow(FramelessWindow):
    """图标测试窗口"""

    def __init__(self):
        super().__init__()
        self.setTitle("默认图标测试")
        self.resize(600, 400)
        self._setup_content()

    def _setup_content(self):
        """设置测试内容"""
        content = QWidget()
        layout = QVBoxLayout(content)

        # 标题
        title = QLabel("默认图标测试")
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 信息标签
        info = QLabel("FramelessWindow 现在会自动加载默认的矢量图标")
        info.setStyleSheet("color: #666666; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # 测试 IconManager 的按钮
        layout.addSpacing(20)

        self._setup_icon_buttons(layout)

        # 说明
        layout.addStretch()
        note = QLabel("提示：查看标题栏左上角是否显示默认图标")
        note.setStyleSheet("color: #999999; font-size: 11px;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note)

        self.setCentralWidget(content)

    def _setup_icon_buttons(self, layout):
        """设置图标测试按钮"""
        btn_layout = QVBoxLayout()

        # 获取不同大小的图标
        icon_mgr = IconManager.instance()

        # 测试不同尺寸的图标
        sizes = [16, 24, 32, 48, 64]
        for size in sizes:
            icon = icon_mgr.get_icon('default_window_icon', size)

            btn = QPushButton(f"图标 ({size}x{size})")
            btn.setIcon(icon)
            btn.setIconSize(QSize(32, 32))
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

        # 测试彩色图标
        colored_btn = QPushButton("彩色图标 (红色)")
        icon_mgr_test = IconManager.instance()
        colored_icon = icon_mgr_test.get_colored_icon('default_window_icon', QColor(231, 76, 60), 32)
        colored_btn.setIcon(colored_icon)
        colored_btn.setIconSize(QSize(32, 32))
        colored_btn.setMinimumHeight(40)
        layout.addWidget(colored_btn)

        # 测试默认图标回退
        default_btn = QPushButton("不存在的图标 (显示默认)")
        missing_icon = icon_mgr.get_icon('non_existent_icon', 32)
        default_btn.setIcon(missing_icon)
        default_btn.setIconSize(QSize(32, 32))
        default_btn.setMinimumHeight(40)
        layout.addWidget(default_btn)

        btn_layout_widget = QWidget()
        btn_layout_widget.setLayout(btn_layout)
        layout.addWidget(btn_layout_widget)


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
    window = IconTestWindow()

    # 居中窗口
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())

    window.show()

    # 测试 IconManager 单例
    print("\n=== IconManager 测试 ===")
    icon_mgr = IconManager.instance()
    print(f"图标目录: {icon_mgr._icon_dir}")
    print(f"是否存在 default_window_icon: {icon_mgr.has_icon('default_window_icon')}")

    # 测试加载图标
    icon24 = icon_mgr.get_icon('default_window_icon', 24)
    print(f"加载 24x24 图标: {'成功' if not icon24.isNull() else '失败'}")

    icon48 = icon_mgr.get_icon('default_window_icon', 48)
    print(f"加载 48x48 图标: {'成功' if not icon48.isNull() else '失败'}")

    # 测试缓存
    icon24_cached = icon_mgr.get_icon('default_window_icon', 24)
    print(f"从缓存加载 24x24: {'成功' if not icon24_cached.isNull() else '失败'}")
    print(f"缓存大小: {len(icon_mgr._icon_cache)}")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
