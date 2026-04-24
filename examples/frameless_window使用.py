#导入需要的包和模板
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget
import sys

from src.containers import FramelessWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = FramelessWindow()
    w.show()
    app.exec()
