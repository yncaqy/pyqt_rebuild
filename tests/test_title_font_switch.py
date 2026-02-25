#!/usr/bin/env python3
"""
Test script specifically for verifying title font switching functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication
from examples.complete_theme_demo import CompleteThemeDemo

def test_title_font_switching():
    """Test that the main window title font switches with themes."""
    app = QApplication(sys.argv)
    
    # Create the demo window
    window = CompleteThemeDemo()
    window.show()
    
    print("=== Title Font Switching Test ===")
    print("Instructions:")
    print("1. Observe the main window title: 'Complete Application Theme Switching Demo'")
    print("2. Click the different theme buttons (Dark/Light/Default)")
    print("3. Watch if the title font changes (family, size, weight)")
    print("4. The title should update immediately when themes are switched")
    print("\nExpected behavior:")
    print("- Dark theme: Usually bold, larger font")
    print("- Light theme: May have different font family/size")
    print("- Default theme: Standard application font")
    print("\nPress Ctrl+C or close the window to exit")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_title_font_switching())