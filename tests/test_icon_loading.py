"""
直接测试图标加载
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.icon_manager import IconManager


def main():
    app = QApplication(sys.argv)

    # 创建测试窗口
    window = QWidget()
    window.setWindowTitle("图标加载测试")
    window.resize(300, 200)

    layout = QVBoxLayout()

    # 测试加载关闭图标
    icon_mgr = IconManager.instance()

    print("\n=== 图标加载测试 ===")

    # 测试 1: 检查图标文件是否存在
    print(f"图标目录: {icon_mgr._icon_dir}")
    print(f"window_close.svg 存在: {icon_mgr.has_icon('window_close')}")
    print(f"default_window_icon.svg 存在: {icon_mgr.has_icon('default_window_icon')}")

    # 测试 2: 加载图标
    try:
        close_icon = icon_mgr.get_icon('window_close', 24)
        print(f"关闭图标是否为空: {close_icon.isNull()}")
        if not close_icon.isNull():
            pixmap = close_icon.pixmap(24, 24)
            print(f"图标像素图是否为空: {pixmap.isNull()}")
            print(f"图标尺寸: {pixmap.width()}x{pixmap.height()}")
        else:
            print("错误: 加载的图标为空！")
    except Exception as e:
        print(f"加载图标异常: {e}")

    # 测试 3: 显示图标
    icon_label = QLabel()
    close_icon = icon_mgr.get_icon('window_close', 48)
    icon_label.setPixmap(close_icon.pixmap(48, 48))
    layout.addWidget(icon_label)

    window.setLayout(layout)
    window.show()

    print("\n=== 测试完成 ===\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
