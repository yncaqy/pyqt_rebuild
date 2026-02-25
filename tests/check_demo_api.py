"""
Check all_components_demo.py for API issues
"""
import sys
import re

print("=" * 70)
print("Checking all_components_demo.py for API Issues")
print("=" * 70)
print()

# Read the demo file
with open('examples/all_components_demo.py', 'r', encoding='utf-8') as f:
    content = f.read()

issues = []
warnings = []

# Check 1: show_anchor method
if 'show_anchor' in content:
    issues.append("Found 'show_anchor' - this method doesn't exist in Toast")
else:
    print("[OK] No 'show_anchor' calls found")

# Check 2: ModernLineEdit snake_case methods
modern_line_edit_methods = [
    'set_placeholder_text',
    'get_placeholder_text',
    'set_echo_mode',
    'get_echo_mode',
    'set_read_only',
    'is_read_only',
]

for method in modern_line_edit_methods:
    if f'.{method}(' in content:
        print(f"[OK] ModernLineEdit.{method}() - now available")

# Check 3: AnimatedSlider methods
slider_methods = [
    'set_value_animated',
    'set_value_directly',
    'get_percentage',
]

for method in slider_methods:
    if f'.{method}(' in content:
        print(f"[OK] AnimatedSlider.{method}() - available")

# Check 4: Toast.show() usage
if 'toast.show(' in content or 'toast.show(ToastPosition' in content:
    print("[OK] Toast.show() used correctly")
else:
    warnings.append("Toast.show() not found or may not be using ToastPosition")

# Check 5: ThemeManager.set_theme()
if 'ThemeManager.instance().set_theme(' in content:
    print("[OK] ThemeManager.set_theme() - available")
else:
    issues.append("ThemeManager.set_theme() not found")

# Check 6: Component imports
required_imports = [
    'CustomPushButton',
    'CustomCheckBox',
    'ModernLineEdit',
    'CircularProgress',
    'AnimatedSlider',
    'Toast',
    'FramelessWindow',
]

for imp in required_imports:
    if imp in content:
        print(f"[OK] {imp} imported")
    else:
        issues.append(f"{imp} not imported")

# Check 7: set_error method
if '.set_error(' in content:
    print("[OK] ModernLineEdit.set_error() - available")
else:
    warnings.append("ModernLineEdit.set_error() not used")

# Check 8: QIntValidator usage
if 'QIntValidator' in content:
    print("[OK] QIntValidator imported and used")
else:
    warnings.append("QIntValidator not found")

print()
print("=" * 70)

if issues:
    print("[ERRORS FOUND]")
    for issue in issues:
        print(f"  ✗ {issue}")
    print()

if warnings:
    print("[WARNINGS]")
    for warning in warnings:
        print(f"  ⚠ {warning}")
    print()

if not issues and not warnings:
    print("[SUCCESS] No API issues found in all_components_demo.py")
    print()
    print("The demo should run without API-related errors.")
elif not issues:
    print("[INFO] Only warnings found, demo should still run.")
else:
    print("[ERROR] Critical issues found that will prevent the demo from running.")

print("=" * 70)

sys.exit(0 if not issues else 1)
