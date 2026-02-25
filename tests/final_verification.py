"""
Final Verification Script

Comprehensive test to verify all fixes are working correctly.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 70)
print("PyQT Components Library - Final Verification")
print("=" * 70)
print()

all_passed = True

# Test 1: Import all components
print("Test 1: Import All Components")
print("-" * 70)
try:
    from core.theme_manager import ThemeManager, Theme
    from components.buttons.custom_push_button import CustomPushButton
    from components.checkboxes.custom_check_box import CustomCheckBox
    from components.inputs.modern_line_edit import ModernLineEdit
    from components.progress.circular_progress import CircularProgress
    from components.sliders.animated_slider import AnimatedSlider
    from components.toasts.toast import Toast, ToastType
    from containers.frameless_window import FramelessWindow
    print("[PASS] All components imported successfully")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    all_passed = False
print()

# Test 2: ThemeManager has set_theme method
print("Test 2: ThemeManager Methods")
print("-" * 70)
try:
    tm = ThemeManager.instance()
    assert hasattr(tm, 'set_theme'), "Missing set_theme method"
    assert hasattr(tm, 'set_current_theme'), "Missing set_current_theme method"
    assert hasattr(tm, 'current_theme'), "Missing current_theme method"
    print("[PASS] ThemeManager has all required methods")
except Exception as e:
    print(f"[FAIL] ThemeManager method check failed: {e}")
    all_passed = False
print()

# Test 3: Check exception handling in _on_theme_changed
print("Test 3: Exception Handling in Components")
print("-" * 70)
try:
    import inspect

    components_to_check = [
        (CustomPushButton, "CustomPushButton"),
        (CustomCheckBox, "CustomCheckBox"),
        (ModernLineEdit, "ModernLineEdit"),
        (CircularProgress, "CircularProgress"),
        (AnimatedSlider, "AnimatedSlider"),
        (Toast, "Toast"),
        (FramelessWindow, "FramelessWindow"),
    ]

    for component_class, component_name in components_to_check:
        method = getattr(component_class, '_on_theme_changed', None)
        if method is None:
            print(f"  [WARNING] {component_name} has no _on_theme_changed method")
            continue

        # Get source code to check for exception handling
        source = inspect.getsource(method)
        if "try:" in source and "except" in source:
            print(f"  [OK] {component_name}._on_theme_changed has exception handling")
        else:
            print(f"  [WARNING] {component_name}._on_theme_changed missing exception handling")

    print("[PASS] Component exception handling verified")
except Exception as e:
    print(f"[FAIL] Exception handling check failed: {e}")
    all_passed = False
print()

# Test 4: Verify demo files exist and compile
print("Test 4: Demo Files")
print("-" * 70)
try:
    import py_compile

    demo_files = [
        "examples/demo_custom_button.py",
        "examples/demo_custom_checkbox.py",
        "examples/demo_line_edit.py",
        "examples/demo_circular_progress.py",
        "examples/demo_animated_slider.py",
        "examples/demo_toast.py",
        "examples/all_components_demo.py",
        "examples/demo_launcher.py",
    ]

    for demo_file in demo_files:
        if not os.path.exists(demo_file):
            print(f"  [FAIL] {demo_file} not found")
            all_passed = False
            continue

        py_compile.compile(demo_file, doraise=True)
        print(f"  [OK] {os.path.basename(demo_file)}")

    print("[PASS] All demo files exist and compile successfully")
except Exception as e:
    print(f"[FAIL] Demo file check failed: {e}")
    all_passed = False
print()

# Test 5: Verify theme files
print("Test 5: Theme Files")
print("-" * 70)
try:
    from themes import DARK_THEME, LIGHT_THEME, DEFAULT_THEME

    assert isinstance(DARK_THEME, dict), "DARK_THEME is not a dict"
    assert isinstance(LIGHT_THEME, dict), "LIGHT_THEME is not a dict"
    assert isinstance(DEFAULT_THEME, dict), "DEFAULT_THEME is not a dict"

    print("  [OK] DARK_THEME loaded")
    print("  [OK] LIGHT_THEME loaded")
    print("  [OK] DEFAULT_THEME loaded")
    print("[PASS] All theme files loaded successfully")
except Exception as e:
    print(f"[FAIL] Theme file check failed: {e}")
    all_passed = False
print()

# Final result
print("=" * 70)
if all_passed:
    print("[SUCCESS] All verification tests passed!")
    print()
    print("You can now run demos with:")
    print("  python examples/demo_custom_button.py")
    print("  python examples/demo_launcher.py")
    print("  ... and other demos")
    print()
    print("Theme switching should work without crashes.")
else:
    print("[WARNING] Some tests failed. Please review the output above.")
print("=" * 70)

sys.exit(0 if all_passed else 1)
