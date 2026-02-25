"""
Test to verify that dragging beyond minimum size doesn't trigger window drag

This test verifies the fix for the issue where:
- When resizing from top edge down to minimum size (300px)
- Continuing to drag down would incorrectly trigger window dragging
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt

from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME, DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Register themes
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.register_theme_dict("dark", DARK_THEME)
    theme_mgr.set_current_theme("dark")

    # Create window with smaller initial size for easier testing
    window = FramelessWindow()
    window.setTitle("Minimum Size Drag Test")
    window.resize(500, 350)  # Close to minimum (400x300)

    # Add content with test instructions
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("Minimum Size Drag Test")
    title.setStyleSheet("font-size: 18px; font-weight: bold;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    instructions = QLabel(
        "<b>Test Steps:</b><br><br>"
        "1. Move mouse to <b>TOP EDGE</b> of the window (y <= 6px)<br>"
        "2. Click and drag <b>DOWN</b> to resize the window<br>"
        "3. Continue dragging down when window reaches minimum height (300px)<br><br>"
        "<b>Expected Behavior:</b><br>"
        "&bull; Window should stop at 300px height<br>"
        "&bull; Continuing to drag down should <b>NOT</b> move the window<br>"
        "&bull; Window should stay in place<br><br>"
        "<b>What was broken:</b><br>"
        "&bull; After reaching minimum size, continuing to drag would<br>"
        "  incorrectly trigger window dragging/moving<br><br>"
        "<b>Current Window Size:</b><br>"
        "&bull; Initial: 500x350 (close to minimum 400x300)<br>"
        "&bull; Minimum: 400x300<br><br>"
        "<b>Try also:</b><br>"
        "&bull; Test other edges beyond minimum size<br>"
        "&bull; Test corners beyond minimum size<br>"
    )
    instructions.setTextFormat(Qt.TextFormat.RichText)
    instructions.setWordWrap(True)

    size_label = QLabel("Current Size: 500 x 350")
    size_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
    size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addWidget(size_label)
    layout.addStretch()

    # Update size display when window is resized
    def update_size():
        size_label.setText(f"Current Size: {window.width()} x {window.height()}")

    window.resizeEvent = lambda e: (update_size(), type(window).resizeEvent(window, e))

    window.setCentralWidget(content)

    # Center window
    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        window.move(
            geometry.center().x() - window.width() // 2,
            geometry.center().y() - window.height() // 2
        )

    print("=" * 70)
    print("MINIMUM SIZE DRAG TEST")
    print("=" * 70)
    print("")
    print("Fix: Prevent window dragging when resizing beyond minimum size")
    print("")
    print("Protective layers added:")
    print("  1. TitleBar.mousePressEvent() checks _resizing state")
    print("  2. TitleBar.mouseMoveEvent() checks _resizing state")
    print("  3. FramelessWindow.mouseReleaseEvent() resets all states")
    print("")
    print("Test the scenario:")
    print("  1. Drag top edge DOWN to minimum size (300px)")
    print("  2. Continue dragging DOWN beyond minimum")
    print("  3. Window should NOT move, should stay at minimum size")
    print("")
    print("=" * 70)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
