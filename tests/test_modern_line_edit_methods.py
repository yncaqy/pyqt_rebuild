"""
Test ModernLineEdit snake_case methods
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from components.inputs.modern_line_edit import ModernLineEdit

print("Testing ModernLineEdit snake_case methods...")

app = QApplication(sys.argv)

lineedit = ModernLineEdit()

# Test set_placeholder_text
lineedit.set_placeholder_text("Test placeholder")
assert lineedit.get_placeholder_text() == "Test placeholder", "set_placeholder_text failed"
print("[OK] set_placeholder_text() works")

# Test set_echo_mode
lineedit.set_echo_mode(ModernLineEdit.EchoMode.Password)
assert lineedit.get_echo_mode() == ModernLineEdit.EchoMode.Password, "set_echo_mode failed"
print("[OK] set_echo_mode() works")

# Test set_read_only
lineedit.set_read_only(True)
assert lineedit.is_read_only() == True, "set_read_only failed"
print("[OK] set_read_only() works")

# Test unset read-only
lineedit.set_read_only(False)
assert lineedit.is_read_only() == False, "unset read_only failed"
print("[OK] unset read_only works")

print()
print("[SUCCESS] All ModernLineEdit snake_case methods work correctly!")
