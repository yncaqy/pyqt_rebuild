"""
Test Theme Switching Crash

Simple test to reproduce theme switching crash.
"""
import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME

print("=" * 60)
print("Testing Theme Switching Crash")
print("=" * 60)
print()

# Create application
app = QApplication(sys.argv)

# Initialize theme manager
theme_mgr = ThemeManager.instance()
theme_mgr.register_theme_dict('dark', DARK_THEME)
theme_mgr.register_theme_dict('light', LIGHT_THEME)
theme_mgr.set_theme('dark')

print("[OK] Theme manager initialized")

# Create test widget
class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Test")

        layout = QVBoxLayout(self)

        # Label
        self.label = QLabel("Click the button to switch themes")
        layout.addWidget(self.label)

        # Theme button
        self.theme_btn = QPushButton("Switch Theme")
        self.theme_btn.clicked.connect(self._on_theme_clicked)
        layout.addWidget(self.theme_btn)

        print("[OK] Test widget created")

    def _on_theme_clicked(self):
        """Handle theme button click."""
        try:
            print("\n[INFO] Theme button clicked")
            current = ThemeManager.instance().current_theme()

            if current and current.name == 'dark':
                print("[INFO] Switching to light theme...")
                ThemeManager.instance().set_theme('light')
                print("[OK] Switched to light theme")
            else:
                print("[INFO] Switching to dark theme...")
                ThemeManager.instance().set_theme('dark')
                print("[OK] Switched to dark theme")

        except Exception as e:
            print(f"[ERROR] Theme switching failed: {e}")
            traceback.print_exc()

# Create and show widget
try:
    widget = TestWidget()
    widget.show()
    print("[OK] Widget shown")
    print("\n" + "=" * 60)
    print("Widget is running. Click 'Switch Theme' button to test.")
    print("Close the window to exit.")
    print("=" * 60)
except Exception as e:
    print(f"[ERROR] Failed to create widget: {e}")
    traceback.print_exc()
    sys.exit(1)

# Run application
sys.exit(app.exec())
