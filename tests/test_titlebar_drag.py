"""
Test TitleBar Dragging

This test verifies that the title bar can drag the window after the refactoring fix.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME, DARK_THEME, LIGHT_THEME


class DragTestWindow:
    """Test window for verifying title bar drag functionality."""

    def __init__(self):
        # Setup themes
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict("default", DEFAULT_THEME)
        theme_mgr.register_theme_dict("dark", DARK_THEME)
        theme_mgr.register_theme_dict("light", LIGHT_THEME)
        theme_mgr.set_current_theme("light")

        # Create frameless window
        self.window = FramelessWindow()
        self.window.setTitle("TitleBar Drag Test")
        self.window.resize(500, 400)

        # Create content
        content = QLabel(
            "<h2>TitleBar Drag Test</h2>"
            "<p>Try dragging the window by the title bar above.</p>"
            "<p><b>What to test:</b></p>"
            "<ul>"
            "<li>Click and hold on the title bar (top area with buttons)</li>"
            "<li>Move the mouse to drag the window</li>"
            "<li>Release to drop the window</li>"
            "</ul>"
            "<p><b>Additional tests:</b></p>"
            "<ul>"
            "<li>Double-click title bar to maximize/restore</li>"
            "<li>Drag window edges to resize</li>"
            "<li>Click minimize/maximize/close buttons</li>"
            "</ul>"
        )
        content.setTextFormat(Qt.TextFormat.RichText)

        self.window.setCentralWidget(content)

        # Verify dragging setup
        self._verify_drag_setup()

    def _verify_drag_setup(self):
        """Verify that all required components for dragging are in place."""
        title_bar = self.window.title_bar

        print("\n[Drag Setup Verification]")
        print(f"  1. TitleBar _window reference: {'OK' if title_bar._window is self.window else 'FAIL'}")
        print(f"  2. TitleBar has _drag_position: {'OK' if hasattr(title_bar, '_drag_position') else 'FAIL'}")
        print(f"  3. TitleBar has StateManager: {'OK' if hasattr(title_bar, '_state_mgr') else 'FAIL'}")
        print(f"  4. TitleBar has mousePressEvent: {'OK' if hasattr(title_bar, 'mousePressEvent') else 'FAIL'}")
        print(f"  5. TitleBar has mouseMoveEvent: {'OK' if hasattr(title_bar, 'mouseMoveEvent') else 'FAIL'}")

        # Check for the critical setWindow() call
        if title_bar._window is self.window:
            print("\n[SUCCESS] setWindow(self) was called correctly!")
            print("          Window dragging should work.")
        else:
            print("\n[FAIL] setWindow(self) was NOT called!")
            print("       Window dragging will NOT work.")

    def show(self):
        """Show the test window."""
        self.window.show()


def main():
    """Run the drag test."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    test = DragTestWindow()
    test.show()

    print("\n" + "=" * 60)
    print("TitleBar Drag Test Window")
    print("=" * 60)
    print("\nInstructions:")
    print("  1. The test window should now be visible")
    print("  2. Try clicking and dragging the title bar")
    print("  3. The window should follow your mouse movement")
    print("  4. Try the other tests listed in the window")
    print("\n" + "=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
