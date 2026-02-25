"""
Fix Verification Test

This test verifies that the top edge shrink bug has been fixed.
After applying the fix, dragging beyond minimum size should not move the window.
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
    window.setTitle("🔧 Fix Verification - Top Edge Shrink")
    window.resize(420, 320)  # Very close to minimum size

    # Add content with verification instructions
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("🔧 Fix Verification Test")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    instructions = QLabel(
        "<b>Verification Steps:</b><br><br>"
        "1. Move mouse to <b>TOP EDGE</b> of the window (cursor becomes ↕)<br>"
        "2. Click and drag <b>DOWNWARD</b> to shrink the window<br>"
        "3. Watch as window shrinks to minimum height (300px)<br>"
        "4. <b>Continue dragging downward</b> beyond minimum size<br><br>"
        "<b>✅ Expected Fixed Behavior:</b><br>"
        "&bull; Window <b>STOPS MOVING</b> when it reaches minimum height<br>"
        "&bull; Continuing to drag has <b>NO EFFECT</b> on window position<br>"
        "&bull; Window stays in fixed position<br><br>"
        "<b>🐛 Previous Bug Behavior:</b><br>"
        "&bull; Window continued moving downward even at minimum size<br>"
        "&bull; Window position changed despite being at minimum dimensions<br><br>"
        "<b>Technical Details:</b><br>"
        "&bull; Minimum size: 400 x 300 pixels<br>"
        "&bull; Current size: 420 x 320 pixels<br>"
        "&bull; Edge margin: 6 pixels<br><br>"
        "<b>Also Test These Edges:</b><br>"
        "&bull; Left edge - should not move when at minimum width (400px)<br>"
        "&bull; Right edge - should not move when at minimum width (400px)<br>"
        "&bull; Bottom edge - should not move when at minimum height (300px)<br>"
        "&bull; All four corners - should respect both width and height limits<br>"
    )
    instructions.setTextFormat(Qt.TextFormat.RichText)
    instructions.setWordWrap(True)

    size_label = QLabel("Current Size: 420 x 320 (very close to minimum 400x300)")
    size_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
    size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    success_message = QLabel(
        "✅ <b>Success Criteria:</b> Window should remain completely stationary "
        "once it reaches minimum size, regardless of continued dragging."
    )
    success_message.setStyleSheet("color: #27ae60; padding: 10px; border: 1px solid #27ae60; border-radius: 5px;")
    success_message.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addWidget(size_label)
    layout.addWidget(success_message)
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
    print("[VERIFICATION TEST STARTED]")
    print("[BEFORE FIX] Window would continue moving downward beyond minimum size")
    print("[AFTER FIX] Window should stop moving completely at minimum size")
    print("[TEST] Drag the top edge downward and verify window stays fixed")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()