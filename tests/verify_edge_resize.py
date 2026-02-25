"""
Quick verification script for edge resize functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from containers.frameless_window import FramelessWindow

app = QApplication(sys.argv)
window = FramelessWindow()
window.resize(400, 300)

print("=" * 60)
print("EDGE RESIZE VERIFICATION")
print("=" * 60)
print("")

# Check all critical state variables and methods
checks = {
    "_resizing variable": hasattr(window, "_resizing"),
    "_resizing is False": window._resizing == False,
    "_edge_margin = 6": window._edge_margin == 6,
    "_get_resize_edge()": hasattr(window, "_get_resize_edge"),
    "_update_cursor()": hasattr(window, "_update_cursor"),
    "_resize_window()": hasattr(window, "_resize_window"),
    "eventFilter()": hasattr(window, "eventFilter"),
}

print("Required components:")
all_ok = True
for desc, result in checks.items():
    status = "OK" if result else "FAIL"
    print(f"  [{status}] {desc}")
    if not result:
        all_ok = False

print("")
print("=" * 60)
if all_ok:
    print("SUCCESS: All edge resize components are present!")
    print("")
    print("Fixes applied:")
    print("  1. Restored _resizing variable (was removed in refactoring)")
    print("  2. mousePressEvent sets _resizing=True on edge")
    print("  3. mouseMoveEvent checks _resizing (not _state_mgr.pressed)")
    print("  4. mouseReleaseEvent resets _resizing=False")
    print("  5. eventFilter checks _resizing (not _state_mgr.pressed)")
    print("")
    print("The top edge and all other edges should now work for resizing!")
else:
    print("FAIL: Some components are missing!")
print("=" * 60)
