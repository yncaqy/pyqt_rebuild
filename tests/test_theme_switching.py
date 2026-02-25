"""
Test Theme Switching

Verify that theme switching works correctly without crashes.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME

print("=" * 60)
print("Theme Switching Test")
print("=" * 60)
print()

# Create application
app = QApplication(sys.argv)

# Initialize theme manager
theme_mgr = ThemeManager.instance()

# Register themes
theme_mgr.register_theme_dict('dark', DARK_THEME)
theme_mgr.register_theme_dict('light', LIGHT_THEME)

print("[OK] Themes registered")

# Test set_current_theme
print("\nTesting set_current_theme()...")
try:
    theme_mgr.set_current_theme('dark')
    print(f"[OK] Current theme: {theme_mgr.current_theme().name}")

    theme_mgr.set_current_theme('light')
    print(f"[OK] Current theme: {theme_mgr.current_theme().name}")
except Exception as e:
    print(f"[FAIL] set_current_theme failed: {e}")
    sys.exit(1)

# Test set_theme (convenience method)
print("\nTesting set_theme()...")
try:
    theme_mgr.set_theme('dark')
    print(f"[OK] Current theme: {theme_mgr.current_theme().name}")

    theme_mgr.set_theme('light')
    print(f"[OK] Current theme: {theme_mgr.current_theme().name}")

    theme_mgr.set_theme('dark')
    print(f"[OK] Current theme: {theme_mgr.current_theme().name}")
except Exception as e:
    print(f"[FAIL] set_theme failed: {e}")
    sys.exit(1)

# Test rapid switching
print("\nTesting rapid theme switching...")
try:
    for i in range(5):
        theme = 'dark' if i % 2 == 0 else 'light'
        theme_mgr.set_theme(theme)
        print(f"  Switch {i+1}: {theme} [OK]")
except Exception as e:
    print(f"[FAIL] Rapid switching failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("[OK] All theme switching tests passed!")
print("=" * 60)

sys.exit(0)
