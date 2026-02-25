"""
Test close button icon color update on theme change
"""
import sys
import logging

# Set up logging to see all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

sys.path.insert(0, '../src')

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager, Theme


def test_close_icon_color_update():
    """Test that close button icon updates when theme changes."""
    app = QApplication(sys.argv)

    # Create window
    window = FramelessWindow()
    window.setWindowTitle("Close Icon Color Update Test")
    window.title_bar.setTitle("Close Icon Color Update Test")
    window.resize(800, 600)

    # Add content
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    info_label = QPushButton("Switch to Light Theme")
    info_label.clicked.connect(lambda: switch_theme('light'))
    layout.addWidget(info_label)

    info_label2 = QPushButton("Switch to Dark Theme")
    info_label2.clicked.connect(lambda: switch_theme('dark'))
    layout.addWidget(info_label2)

    window.setCentralWidget(central_widget)
    window.show()

    print("\n" + "="*70)
    print("Close Icon Color Update Test")
    print("="*70)
    print("Instructions:")
    print("1. Observe the close button (X) icon color in the title bar")
    print("2. Click the buttons to switch between light and dark themes")
    print("3. The close button icon color should update with each theme change")
    print("="*70 + "\n")

    sys.exit(app.exec())


def switch_theme(theme_name: str):
    """Switch theme and print status."""
    theme_mgr = ThemeManager.instance()

    if theme_name == 'light':
        theme = Theme(
            'light_test',
            {
                'titlebar.background': QColor(240, 240, 240),
                'titlebar.text': QColor(50, 50, 50),  # Dark text for light theme
                'window.background': QColor(255, 255, 255),
            }
        )
        print(f"\n[TEST] Switching to LIGHT theme")
        print(f"[TEST] Expected close button icon color: Dark (50, 50, 50)")
    else:
        theme = Theme(
            'dark_test',
            {
                'titlebar.background': QColor(30, 30, 30),
                'titlebar.text': QColor(220, 220, 220),  # Light text for dark theme
                'window.background': QColor(25, 25, 25),
            }
        )
        print(f"\n[TEST] Switching to DARK theme")
        print(f"[TEST] Expected close button icon color: Light (220, 220, 220)")

    theme_mgr.register_theme_dict(theme_name, theme._colors)
    theme_mgr.set_theme(theme_name)
    print(f"[TEST] Theme switched to: {theme_name}")
    print(f"[TEST] Check if close button icon color changed!")


if __name__ == '__main__':
    test_close_icon_color_update()
