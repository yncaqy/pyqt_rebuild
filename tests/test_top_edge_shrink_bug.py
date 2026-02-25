"""
Top Edge Shrink Bug Test

This test reproduces the bug where dragging the top edge beyond minimum size
causes the window to move downward instead of staying fixed.

Bug Description:
When window is at minimum height (300px) and user continues dragging the top edge
downward, the window moves down instead of staying in place.

Expected Behavior:
Window should remain stationary when at minimum size and user tries to shrink further.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt

from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME, DARK_THEME, LIGHT_THEME


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Register themes
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.register_theme_dict("dark", DARK_THEME)
    theme_mgr.register_theme_dict("light", LIGHT_THEME)
    theme_mgr.set_current_theme("light")

    # Create window with size close to minimum (400x300)
    window = FramelessWindow()
    window.setTitle("Top Edge Shrink Bug Test")
    window.resize(450, 320)  # Close to minimum size to easily test the bug

    # Add content with detailed instructions
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("🔍 Top Edge Shrink Bug Test")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    instructions = QLabel(
        "<b>Bug Reproduction Steps:</b><br><br>"
        "1. Move mouse to <b>TOP EDGE</b> of the window (cursor becomes ↕)<br>"
        "2. Click and drag <b>DOWNWARD</b> to shrink the window<br>"
        "3. Watch as window shrinks to minimum height (300px)<br>"
        "4. <b>Continue dragging downward</b> beyond minimum size<br><br>"
        "<b>🐛 Current Bug Behavior:</b><br>"
        "&bull; Window continues moving downward instead of stopping<br>"
        "&bull; Window position changes even though size is at minimum<br><br>"
        "<b>✅ Expected Correct Behavior:</b><br>"
        "&bull; Window should <b>STOP MOVING</b> when at minimum size<br>"
        "&bull; Continuing to drag should have <b>NO EFFECT</b><br>"
        "&bull; Window stays in fixed position<br><br>"
        "<b>Technical Details:</b><br>"
        "&bull; Minimum size: 400 x 300 pixels<br>"
        "&bull; Current size: 450 x 320 pixels<br>"
        "&bull; Edge margin: 6 pixels<br><br>"
        "<b>Test Other Edges Too:</b><br>"
        "&bull; Left edge - should not move window when at minimum width<br>"
        "&bull; Right edge - should not move window when at minimum width<br>"
        "&bull; Bottom edge - should not move window when at minimum height<br>"
    )
    instructions.setTextFormat(Qt.TextFormat.RichText)
    instructions.setWordWrap(True)

    size_label = QLabel("Current Size: 450 x 320 (close to minimum 400x300)")
    size_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
    size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    warning = QLabel(
        "⚠️ <b>Warning:</b> This demonstrates a known bug in the resize logic. "
        "The fix involves adding proper boundary checks in _resize_window()."
    )
    warning.setStyleSheet("color: #f39c12; padding: 10px; border: 1px solid #f39c12; border-radius: 5px;")
    warning.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addWidget(size_label)
    layout.addWidget(warning)
    layout.addStretch()

    window.setCentralWidget(content)

    # Center window on screen
    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        window.move(
            geometry.center().x() - window.width() // 2,
            geometry.center().y() - window.height() // 2
        )

    window.show()
    print("[TEST STARTED] Try dragging the top edge downward beyond minimum size")
    print("[EXPECTED] Window should stop moving when it reaches minimum height")
    print("[BUG] Window continues moving downward instead of stopping")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()