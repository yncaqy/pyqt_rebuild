"""
Verify All Components

Quick verification script to test that all components can be imported and instantiated.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 60)
print("PyQT Components Library - Component Verification")
print("=" * 60)
print()

success_count = 0
fail_count = 0

def test_component(name, import_path, create_func, require_cleanup=True):
    """Test a single component."""
    global success_count, fail_count

    try:
        print(f"Testing {name}...", end=" ")

        # Import
        import importlib
        module = importlib.import_module(import_path)

        # Create instance
        instance = create_func(module)

        # Test cleanup if required
        if require_cleanup:
            assert hasattr(instance, 'cleanup'), f"{name} missing cleanup() method"
            instance.cleanup()

        print("[PASS]")
        success_count += 1
        return True

    except Exception as e:
        print("[FAIL]")
        print(f"  Error: {e}")
        fail_count += 1
        return False

# Initialize QApplication for Qt components
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

# Test theme manager (singleton, no cleanup needed)
print("Core Components:")
print("-" * 40)
test_component(
    "ThemeManager",
    "core.theme_manager",
    lambda m: m.ThemeManager.instance(),
    require_cleanup=False
)

print()
print("UI Components:")
print("-" * 40)

# Test CustomPushButton
test_component(
    "CustomPushButton",
    "components.buttons.custom_push_button",
    lambda m: m.CustomPushButton("Test Button")
)

# Test CustomCheckBox
test_component(
    "CustomCheckBox",
    "components.checkboxes.custom_check_box",
    lambda m: m.CustomCheckBox("Test Checkbox")
)

# Test ModernLineEdit
test_component(
    "ModernLineEdit",
    "components.inputs.modern_line_edit",
    lambda m: m.ModernLineEdit()
)

# Test CircularProgress
test_component(
    "CircularProgress",
    "components.progress.circular_progress",
    lambda m: m.CircularProgress()
)

# Test AnimatedSlider
from PyQt6.QtCore import Qt
test_component(
    "AnimatedSlider",
    "components.sliders.animated_slider",
    lambda m: m.AnimatedSlider(Qt.Orientation.Horizontal)
)

# Test Toast
test_component(
    "Toast",
    "components.toasts.toast",
    lambda m: m.Toast("Test Message", m.ToastType.INFO)
)

print()
print("Containers:")
print("-" * 40)

# Test FramelessWindow (container, no cleanup needed)
test_component(
    "FramelessWindow",
    "containers.frameless_window",
    lambda m: m.FramelessWindow(),
    require_cleanup=False
)

print()
print("=" * 60)
print(f"Results: {success_count} passed, {fail_count} failed")
print("=" * 60)

if fail_count == 0:
    print("[OK] All components verified successfully!")
    sys.exit(0)
else:
    print("[ERROR] Some components failed verification")
    sys.exit(1)
