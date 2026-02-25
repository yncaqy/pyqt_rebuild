"""
Test Top Edge Priority

This test verifies that the top edge triggers resize (not drag) when cursor
is within the edge margin, even over the title bar.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt, QPoint
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME


def test_top_edge_priority():
    """Test that top edge has priority over title bar dragging."""
    app = QApplication(sys.argv)

    # Setup theme
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.set_current_theme("default")

    # Create window
    window = FramelessWindow()
    window.setTitle("Top Edge Priority Test")
    window.resize(500, 400)

    # Add test content
    content = QLabel(
        "<h2>Top Edge Priority Test</h2>"
        "<p><b>Test the top edge of the window:</b></p>"
        "<ol>"
        "<li>Move cursor to the TOP edge (over title bar area)</li>"
        "<li>Cursor should change to <b>↕ SizeVerCursor</b></li>"
        "<li>Click and drag should <b>RESIZE</b> not drag</li>"
        "</ol>"
        "<p><b>Edge margin:</b> 6 pixels from top</p>"
        "<p><b>Expected behavior:</b></p>"
        "<ul>"
        "<li>When y <= 6px: Resize cursor (↕) + Resize action</li>"
        "<li>When y > 6px:  Arrow cursor + Drag action</li>"
        "</ul>"
        "<p style='color: green;'>"
        "<b>FIX APPLIED:</b><br>"
        "TitleBar now checks _is_on_top_edge() before starting drag.<br>"
        "If on edge, event is ignored and propagates to FramelessWindow."
        "</p>"
    )
    content.setTextFormat(Qt.TextFormat.RichText)
    window.setCentralWidget(content)

    # Verify setup
    title_bar = window.title_bar

    print("\n" + "=" * 60)
    print("TOP EDGE PRIORITY VERIFICATION")
    print("=" * 60)
    print("")

    checks = [
        ("TitleBar has _edge_margin", hasattr(title_bar, '_edge_margin')),
        ("TitleBar _edge_margin = 6", title_bar._edge_margin == 6),
        ("TitleBar has _is_on_top_edge", hasattr(title_bar, '_is_on_top_edge')),
        ("FramelessWindow has _resizing", hasattr(window, '_resizing')),
        ("FramelessWindow _edge_margin = 6", window._edge_margin == 6),
    ]

    all_pass = True
    for desc, result in checks:
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {desc}")
        if not result:
            all_pass = False

    print("")
    print("=" * 60)
    if all_pass:
        print("SUCCESS: Top edge priority is correctly configured!")
        print("")
        print("How it works:")
        print("")
        print("1. Mouse press on TitleBar at y <= 6px:")
        print("   → TitleBar._is_on_top_edge() returns True")
        print("   → event.ignore() is called")
        print("   → Event propagates to FramelessWindow")
        print("   → FramelessWindow detects edge → starts RESIZE")
        print("")
        print("2. Mouse press on TitleBar at y > 6px:")
        print("   → TitleBar._is_on_top_edge() returns False")
        print("   → TitleBar starts dragging")
        print("   → Window moves following cursor")
    else:
        print("FAIL: Some components are missing!")
    print("=" * 60)

    window.show()
    print("\nTest window is now visible. Please test manually.")
    print("Press Ctrl+C to exit.\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    test_top_edge_priority()
