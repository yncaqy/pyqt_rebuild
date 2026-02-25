"""
Top Edge Resize Test

Manual test to verify that the top edge of the frameless window
can be used to resize the window.

Instructions:
1. Run this script
2. Move your mouse to the TOP EDGE of the window (y <= 6px)
3. The cursor should change to SizeVerCursor (up/down arrows)
4. Click and drag to resize the window height
5. Move your mouse below the top edge (y > 6px)
6. The cursor should change to ArrowCursor
7. Click and drag to move the window
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

    # Create window
    window = FramelessWindow()
    window.setTitle("Top Edge Resize Test")
    window.resize(600, 400)

    # Add content with instructions
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("Top Edge Resize Test")
    title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    instructions = QLabel(
        "<b>Instructions:</b><br><br>"
        "&bull; Move mouse to <b>TOP EDGE</b> (y <= 6px)<br>"
        "  - Cursor should be: <b>&#8597; SizeVerCursor</b><br>"
        "  - Action: <b>RESIZE</b> window height<br><br>"
        "&bull; Move mouse below top edge (y > 6px)<br>"
        "  - Cursor should be: <b>&#8594; ArrowCursor</b><br>"
        "  - Action: <b>DRAG</b> window<br><br>"
        "&bull; Also test other edges:<br>"
        "  - Bottom, Left, Right edges<br>"
        "  - Four corners<br>"
    )
    instructions.setTextFormat(Qt.TextFormat.RichText)
    instructions.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addStretch()

    window.setCentralWidget(content)

    # Center window
    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        window.move(
            geometry.center().x() - window.width() // 2,
            geometry.center().y() - window.height() // 2
        )

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
