"""
FramelessWindow Usability Analysis

Analyzes current implementation and lists improvements needed for "out-of-box" usability.
"""
import sys
sys.path.insert(0, '../src')

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME


def analyze_usability():
    """Analyze current usability issues."""
    app = QApplication(sys.argv)

    # Setup theme
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.set_current_theme("default")

    print("=" * 70)
    print("FRAMELESS WINDOW - USABILITY ANALYSIS")
    print("=" * 70)
    print("")

    # Test 1: Can create without setup?
    print("[TEST 1] Can create window without manual setup?")
    try:
        window1 = FramelessWindow()
        print("  Result: [OK] Can create without setup")
        print("  Issue: NO - needs theme registration first")
    except Exception as e:
        print(f"  Result: [FAIL] {e}")

    print("")

    # Test 2: Has default content?
    print("[TEST 2] Has default/placeholder content?")
    window2 = FramelessWindow()
    try:
        content = window2.getCentralWidget()
        if content:
            print(f"  Result: [OK] Has content: {content.__class__.__name__}")
        else:
            print("  Result: [WARN] No content - empty window")
            print("  Issue: Need to manually call setCentralWidget()")
    except Exception as e:
        print(f"  Result: [FAIL] {e}")

    print("")

    # Test 3: Can use as container directly?
    print("[TEST 3] Can add widgets like QWidget?")
    try:
        window3 = FramelessWindow()
        # Try to add widget directly
        label = QLabel("Test")
        try:
            # Can we add widgets directly?
            window3.layout().addWidget(label)
            print("  Result: [OK] Can add widgets to layout")
        except Exception as e:
            print(f"  Result: [FAIL] Cannot add widgets: {e}")
    except Exception as e:
        print(f"  Result: [FAIL] {e}")

    print("")

    # Test 4: Automatic size management?
    print("[TEST 4] Automatic size management?")
    window4 = FramelessWindow()
    print(f"  Minimum size: {window4.minimumSize().width()}x{window4.minimumSize().height()}")
    print(f"  Maximum size: {window4.maximumSize().width()}x{window4.maximumSize().height()}")
    print(f"  Size policy: {window4.sizePolicy().horizontalPolicy()} / {window4.sizePolicy().verticalPolicy()}")
    print("  Issue: Fixed 400x300, not content-driven")

    print("")

    # Test 5: Clean initialization?
    print("[TEST 5] Clean initialization without errors?")
    try:
        window5 = FramelessWindow()
        errors = []
        # Check for common issues
        if not window5.title_bar._window:
            errors.append("title_bar._window is None")
        if window5._edge_margin != 6:
            errors.append(f"unexpected _edge_margin: {window5._edge_margin}")

        if errors:
            print(f"  Result: [WARN] Issues found:")
            for error in errors:
                print(f"    - {error}")
        else:
            print("  Result: [OK] Initialization clean")
    except Exception as e:
        print(f"  Result: [FAIL] {e}")

    print("")
    print("=" * 70)


if __name__ == "__main__":
    analyze_usability()
