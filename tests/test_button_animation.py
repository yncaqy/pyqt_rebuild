"""
Quick test to verify button animation works.

Run with: python tests/test_button_animation.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager
from components.buttons.custom_push_button import CustomPushButton
from themes import DEFAULT_THEME, DARK_THEME


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Animation Test")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Setup themes
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict("default", DEFAULT_THEME)
        theme_mgr.register_theme_dict("dark", DARK_THEME)
        theme_mgr.set_current_theme("default")

        # Create buttons with different sizes
        btn1 = CustomPushButton("Hover Me (Large)")
        btn1.setFixedSize(200, 60)

        btn2 = CustomPushButton("Click Me (Small)")
        btn2.setFixedSize(150, 40)

        btn3 = CustomPushButton("Toggle Theme")
        btn3.clicked.connect(self._toggle_theme)

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)

        self._is_dark = False

    def _toggle_theme(self):
        theme_mgr = ThemeManager.instance()
        if self._is_dark:
            theme_mgr.set_current_theme("default")
        else:
            theme_mgr.set_current_theme("dark")
        self._is_dark = not self._is_dark


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = TestWindow()
    window.show()

    print("Button Animation Test")
    print("=" * 40)
    print("Expected effects:")
    print("  - Hover: Button scales to 105% (elastic)")
    print("  - Press: Button shrinks to 92%")
    print("  - Release: Button bounces back")
    print("=" * 40)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
