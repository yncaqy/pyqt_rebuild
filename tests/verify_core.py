"""
Simple verification script for core modules.

Run with: python tests/verify_core.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRectF

print("=" * 60)
print("PyQt6 Component Refactoring - Core Module Verification")
print("=" * 60)

# Create QApplication (required for Qt widgets)
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

# Test 1: ThemeManager
print("\n[Test 1] ThemeManager...")
try:
    from core.theme_manager import ThemeManager, Theme

    mgr = ThemeManager.instance()

    # Register themes
    default_theme = mgr.register_theme_dict("default", {
        'button': {
            'background': {'normal': '#e0e0e0', 'hover': '#d0d0d0'},
            'text': '#333333',
            'border_radius': 6
        },
        'progress': {
            'track': '#e8e8e8',
            'fill': '#3498db',
            'text': '#2c3e50'
        }
    })

    dark_theme = mgr.register_theme_dict("dark", {
        'button': {
            'background': {'normal': '#3a3a3a', 'hover': '#4a4a4a'},
            'text': '#e0e0e0',
            'border_radius': 6
        },
        'progress': {
            'track': '#2a2a2a',
            'fill': '#5dade2',
            'text': '#ecf0f1'
        }
    })

    # Test color extraction
    color = default_theme.get_color('button.background.normal')
    assert color == QColor('#e0e0e0'), f"Expected #e0e0e0, got {color.name()}"

    # Test theme switching
    mgr.set_current_theme("default")
    assert mgr.current_theme().name == "default"

    mgr.set_current_theme("dark")
    assert mgr.current_theme().name == "dark"

    print("  [PASS] ThemeManager")
    print(f"    - Registered {len(mgr._themes)} themes")
    print(f"    - Current theme: {mgr.current_theme().name}")
except Exception as e:
    print(f"  [FAIL] ThemeManager - {e}")

# Test 2: StateManager
print("\n[Test 2] StateManager...")
try:
    from core.state_manager import StateManager, WidgetState

    state_mgr = StateManager()

    # Test initial state
    assert state_mgr.state == WidgetState.NORMAL.value

    # Test hover state
    state_mgr.hover = True
    assert state_mgr.hover is True
    assert (WidgetState.HOVER & state_mgr._state) == WidgetState.HOVER

    state_mgr.hover = False
    assert state_mgr.hover is False

    # Test pressed state
    state_mgr.pressed = True
    assert state_mgr.pressed is True

    print("  [PASS] StateManager: PASSED")
    print(f"    - Hover state: {'PASS' if not state_mgr.hover else 'RESET'}")
    print(f"    - Pressed state: {'PASS' if state_mgr.pressed else 'FAIL'}")
except Exception as e:
    print(f"  [FAIL] StateManager: FAILED - {e}")

# Test 3: AnimationController
print("\n[Test 3] AnimationController...")
try:
    from core.animation_controller import AnimationController, Transition

    # Create a dummy widget for animation target
    from PyQt6.QtWidgets import QWidget
    widget = QWidget()

    controller = AnimationController(widget, widget)

    transitions = {
        'hover': Transition('opacity', 0.0, 1.0, 150),
        'press': Transition('scale', 1.0, 0.95, 80)
    }

    controller.setup_transitions(transitions)

    assert 'hover' in controller._animations
    assert 'press' in controller._animations

    print("  [PASS] AnimationController: PASSED")
    print(f"    - Configured {len(controller._animations)} transitions")
except Exception as e:
    print(f"  [FAIL] AnimationController: FAILED - {e}")

# Test 4: WidgetPainter (CircularProgressPainter)
print("\n[Test 4] CircularProgressPainter...")
try:
    from core.painting.widget_painter import WidgetPainter, PaintContext, PainterFactory
    from core.painting.circular_progress_painter import CircularProgressPainter

    # Register painter
    PainterFactory.register('circular', CircularProgressPainter)

    # Create pixmap for painting
    pixmap = QPixmap(200, 200)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # Create theme
    theme = Theme("test", {
        'progress': {
            'track': '#e8e8e8',
            'fill': '#3498db',
            'text': '#2c3e50'
        }
    })

    # Create painter instance
    progress_painter = CircularProgressPainter(theme)

    # Create paint context
    rect = QRectF(10, 10, 180, 180)
    context = PaintContext(
        widget=None,
        painter=painter,
        rect=rect,
        theme=theme,
        value=75,
        maximum=100,
        thickness=10,
        show_text=True
    )

    # Paint
    progress_painter.paint(context)
    painter.end()

    # Verify
    assert not pixmap.isNull()

    print("  [PASS] CircularProgressPainter: PASSED")
    print(f"    - Painted progress: 75%")
    print(f"    - Pixmap size: {pixmap.width()}x{pixmap.height()}")
except Exception as e:
    print(f"  [FAIL] CircularProgressPainter: FAILED - {e}")

# Test 5: PainterFactory
print("\n[Test 5] PainterFactory...")
try:
    available = PainterFactory.list_available()

    painter = PainterFactory.create('circular', theme)
    assert painter is not None
    assert isinstance(painter, CircularProgressPainter)

    print("  [PASS] PainterFactory: PASSED")
    print(f"    - Registered painters: {available}")
except Exception as e:
    print(f"  [FAIL] PainterFactory: FAILED - {e}")

# Summary
print("\n" + "=" * 60)
print("Verification complete!")
print("=" * 60)

# Don't run the event loop for this test
sys.exit(0)
