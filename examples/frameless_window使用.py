#导入需要的包和模板
import os
import sys

# 添加项目根目录和src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from src.containers.frameless_window import FramelessWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = FramelessWindow()
    w.show()
    app.exec()
