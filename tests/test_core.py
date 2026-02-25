"""
Unit tests for core modules.

Run with: python -m pytest tests/test_core.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtCore import QRectF

import pytest

from core.theme_manager import ThemeManager, Theme
from core.animation_controller import AnimationController, Transition
from core.state_manager import StateManager, WidgetState
from core.painting.widget_painter import WidgetPainter, PaintContext, PainterFactory
from core.painting.circular_progress_painter import CircularProgressPainter


class TestThemeManager:
    """Tests for ThemeManager."""

    def test_singleton(self):
        """Test that ThemeManager is a singleton."""
        mgr1 = ThemeManager.instance()
        mgr2 = ThemeManager.instance()
        assert mgr1 is mgr2

    def test_register_theme(self):
        """Test theme registration."""
        mgr = ThemeManager.instance()
        theme_data = {'button': {'background': '#e0e0e0'}}
        theme = mgr.register_theme_dict("test", theme_data)

        assert theme.name == "test"
        assert mgr.get_theme("test") is theme

    def test_theme_colors(self):
        """Test color extraction from theme."""
        theme = Theme("test", {
            'button': {
                'background': {
                    'normal': '#e0e0e0',
                    'hover': '#d0d0d0'
                }
            }
        })

        # Test nested access
        color = theme.get_color('button.background.normal')
        assert color == QColor('#e0e0e0')

        # Test default
        default_color = theme.get_color('nonexistent', QColor(255, 0, 0))
        assert default_color == QColor(255, 0, 0)

    def test_set_current_theme(self):
        """Test setting current theme."""
        app = QApplication.instance() or QApplication([])

        mgr = ThemeManager.instance()
        mgr.register_theme_dict("theme1", {'button': {'background': '#e0e0e0'}})
        mgr.register_theme_dict("theme2", {'button': {'background': '#f0f0f0'}})

        mgr.set_current_theme("theme1")
        assert mgr.current_theme().name == "theme1"

        mgr.set_current_theme("theme2")
        assert mgr.current_theme().name == "theme2"


class TestStateManager:
    """Tests for StateManager."""

    def test_initial_state(self):
        """Test initial state is NORMAL."""
        mgr = StateManager()
        assert mgr.state == WidgetState.NORMAL.value

    def test_hover_property(self):
        """Test hover property setter and signal."""
        app = QApplication.instance() or QApplication([])

        mgr = StateManager()
        received = []

        mgr.hoverChanged.connect(lambda v: received.append(v))

        mgr.hover = True
        assert mgr.hover is True
        assert received == [True]

        mgr.hover = False
        assert mgr.hover is False
        assert received == [True, False]

    def test_pressed_property(self):
        """Test pressed property."""
        mgr = StateManager()
        mgr.pressed = True
        assert mgr.pressed is True
        mgr.pressed = False
        assert mgr.pressed is False

    def test_combined_states(self):
        """Test multiple states combined."""
        mgr = StateManager()
        mgr.hover = True
        mgr.pressed = True

        assert mgr.hover is True
        assert mgr.pressed is True


class TestAnimationController:
    """Tests for AnimationController."""

    def test_setup_transitions(self):
        """Test setting up transitions."""
        app = QApplication.instance() or QApplication([])

        widget = QApplication.instance() or []
        controller = AnimationController(widget, widget)

        transitions = {
            'hover': Transition('opacity', 0.0, 1.0, 150)
        }

        controller.setup_transitions(transitions)
        assert 'hover' in controller._animations


class TestCircularProgressPainter:
    """Tests for CircularProgressPainter."""

    def test_paint(self):
        """Test painting to pixmap."""
        app = QApplication.instance() or QApplication([])

        # Create pixmap as paint device
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Create theme
        theme = Theme("test", {
            'progress': {
                'track': '#e0e0e0',
                'fill': '#3498db',
                'text': '#2c3e50'
            }
        })

        # Create painter
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

        # Verify output
        assert not pixmap.isNull()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
