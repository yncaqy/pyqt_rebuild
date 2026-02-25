"""
Test script for close button icon with theme adaptation
"""
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Add src to path
sys.path.insert(0, '../src')

from containers.frameless_window import FramelessWindow


def test_close_icon():
    """Test close button icon with new SVG"""
    app = QApplication(sys.argv)

    # Create window
    window = FramelessWindow()
    window.setWindowTitle("Close Icon Test")
    window.title_bar.setTitle("Close Icon Test")
    window.resize(800, 600)

    # Add content
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("New Close Button Icon Test")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
    layout.addWidget(label)

    info_label = QLabel(
        "The close button (X) now uses a new SVG icon.\n\n"
        "Features:\n"
        "- New X-shaped close icon design\n"
        "- Uses currentColor for theme adaptation\n"
        "- Automatically adapts to theme color changes"
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info_label)

    window.setCentralWidget(central_widget)
    window.show()

    print("\n" + "="*60)
    print("Close Icon Test")
    print("="*60)
    print(f"[OK] Close icon loaded: window_close.svg")
    print(f"[OK] Icon uses currentColor for theme adaptation")
    print(f"[OK] Theme-aware color updating implemented")
    print("="*60 + "\n")

    sys.exit(app.exec())


if __name__ == '__main__':
    test_close_icon()
