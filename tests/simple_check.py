"""
Simple check for FramelessWindow
"""
import sys
sys.path.insert(0, 'src')

from containers.frameless_window import FramelessWindow
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
window = FramelessWindow()
window.show()

print(f'Check: Window created')
print(f'Title: {window.windowTitle()}')
print('Success: Basic functionality works')
