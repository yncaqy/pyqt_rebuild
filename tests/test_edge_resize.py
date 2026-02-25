"""
Test Edge Resizing

This test verifies that all window edges (including top edge) can be used for resizing.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QRect
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME, DARK_THEME, LIGHT_THEME


class EdgeResizeTestWindow:
    """Test window for verifying edge resize functionality."""

    def __init__(self):
        # Setup themes
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict("default", DEFAULT_THEME)
        theme_mgr.register_theme_dict("dark", DARK_THEME)
        theme_mgr.register_theme_dict("light", LIGHT_THEME)
        theme_mgr.set_current_theme("light")

        # Create frameless window
        self.window = FramelessWindow()
        self.window.setTitle("Edge Resize Test")
        self.window.resize(500, 400)

        # Create content
        content = QLabel(
            "<h2>Window Edge Resize Test</h2>"
            "<p>Test resizing the window from all edges and corners.</p>"
            "<p><b>Edge margin:</b> 6 pixels from window edge</p>"
            "<p><b>What to test:</b></p>"
            "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
            "<tr><th>Edge/Corner</th><th>Expected Cursor</th><th>Status</th></tr>"
            "<tr><td>Top edge</td><td>↕ (SizeVerCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Bottom edge</td><td>↕ (SizeVerCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Left edge</td><td>↔ (SizeHorCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Right edge</td><td>↔ (SizeHorCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Top-left corner</td><td>↖ (SizeFDiagCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Top-right corner</td><td>↗ (SizeBDiagCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Bottom-left corner</td><td>↙ (SizeBDiagCursor)</td><td>&nbsp;</td></tr>"
            "<tr><td>Bottom-right corner</td><td>↘ (SizeFDiagCursor)</td><td>&nbsp;</td></tr>"
            "</table>"
            "<p><b>Instructions:</b></p>"
            "<ol>"
            "<li>Move mouse cursor to each edge/corner</li>"
            "<li>Verify the cursor changes to the correct resize icon</li>"
            "<li>Click and drag to resize the window</li>"
            "<li>Verify the window resizes smoothly</li>"
            "</ol>"
            "<p><b>Special Note:</b></p>"
            "<p>The <span style='color: red;'>top edge</span> includes the title bar area. "
            "When cursor is near the top edge (even over title bar), it should show the resize cursor.</p>"
        )
        content.setTextFormat(Qt.TextFormat.RichText)

        self.window.setCentralWidget(content)

        # Verify edge resize setup
        self._verify_edge_resize_setup()

    def _verify_edge_resize_setup(self):
        """Verify that all required components for edge resizing are in place."""
        window = self.window

        print("\n[Edge Resize Setup Verification]")
        print(f"  1. Window has _resizing variable: {'OK' if hasattr(window, '_resizing') else 'FAIL'}")
        print(f"  2. Window _resizing initial value: {'OK' if window._resizing == False else 'FAIL'}")
        print(f"  3. Window has _edge_margin: {'OK' if hasattr(window, '_edge_margin') else 'FAIL'}")
        print(f"  4. Window _edge_margin value: {'OK' if window._edge_margin == 6 else 'FAIL'} ({window._edge_margin})")
        print(f"  5. Window has _get_resize_edge: {'OK' if hasattr(window, '_get_resize_edge') else 'FAIL'}")
        print(f"  6. Window has _update_cursor: {'OK' if hasattr(window, '_update_cursor') else 'FAIL'}")
        print(f"  7. Window has _resize_window: {'OK' if hasattr(window, '_resize_window') else 'FAIL'}")
        print(f"  8. Window has eventFilter: {'OK' if hasattr(window, 'eventFilter') else 'FAIL'}")

        # Check critical logic
        checks = [
            ('_resizing variable exists', hasattr(window, '_resizing')),
            ('_resizing initialized to False', window._resizing == False),
            ('_edge_margin is 6', window._edge_margin == 6),
            ('_get_resize_edge method', hasattr(window, '_get_resize_edge')),
            ('_update_cursor method', hasattr(window, '_update_cursor')),
            ('_resize_window method', hasattr(window, '_resize_window')),
            ('eventFilter method', hasattr(window, 'eventFilter')),
        ]

        all_pass = all(result for _, result in checks)

        if all_pass:
            print("\n[SUCCESS] All edge resize requirements met!")
            print("          Edge resizing should work on all sides including TOP.")
        else:
            print("\n[FAIL] Some requirements are not met!")
            for desc, result in checks:
                if not result:
                    print(f"  FAIL: {desc}")

    def show(self):
        """Show the test window."""
        self.window.show()


def main():
    """Run the edge resize test."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    test = EdgeResizeTestWindow()
    test.show()

    print("\n" + "=" * 60)
    print("Edge Resize Test Window")
    print("=" * 60)
    print("\nInstructions:")
    print("  1. The test window should now be visible")
    print("  2. Move cursor to each edge and corner")
    print("  3. Verify cursor changes to resize icon")
    print("  4. Click and drag to resize")
    print("  5. Pay special attention to TOP edge over title bar")
    print("\n" + "=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
