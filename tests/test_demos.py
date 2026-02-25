"""
Test Demo Initialization

Verify that all demo files can be imported and basic initialization works.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 60)
print("Demo Initialization Test")
print("=" * 60)
print()

# Set QT_QPA_PLATFORM to offscreen for non-GUI testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication

# Create application instance
app = QApplication(sys.argv)

success_count = 0
fail_count = 0

def test_demo(name, module_path, setup_func):
    """Test a demo module."""
    global success_count, fail_count

    try:
        print(f"Testing {name}...", end=" ")

        # Import the demo module
        import importlib
        os.chdir('examples')
        demo_module = importlib.import_module(module_path)
        os.chdir('..')

        # Setup the demo
        window = setup_func(demo_module)

        # Verify it was created
        assert window is not None, f"{name} returned None"

        print("[PASS]")
        success_count += 1
        return True

    except Exception as e:
        print("[FAIL]")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        fail_count += 1
        return False

# Test individual demo modules
print("Demo Modules:")
print("-" * 40)

# Test ComponentsDemo (from all_components_demo.py)
test_demo(
    "ComponentsDemo",
    "all_components_demo",
    lambda m: m.ComponentsDemo()
)

# Test basic_usage demo
try:
    print("Testing basic_usage module...", end=" ")
    import importlib
    os.chdir('examples')
    basic_demo = importlib.import_module('basic_usage')
    os.chdir('..')
    print("[PASS]")
    success_count += 1
except Exception as e:
    print("[FAIL]")
    print(f"  Error: {e}")
    fail_count += 1

# Test frameless_demo
try:
    print("Testing frameless_demo module...", end=" ")
    import importlib
    os.chdir('examples')
    frameless = importlib.import_module('frameless_demo')
    os.chdir('..')
    print("[PASS]")
    success_count += 1
except Exception as e:
    print("[FAIL]")
    print(f"  Error: {e}")
    fail_count += 1

print()
print("=" * 60)
print(f"Results: {success_count} passed, {fail_count} failed")
print("=" * 60)

if fail_count == 0:
    print("[OK] All demo modules can be imported!")
    sys.exit(0)
else:
    print("[ERROR] Some demo modules failed")
    sys.exit(1)
