"""Test new components: LineEdit, Slider, CheckBox"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.theme_manager import ThemeManager
from components.inputs.modern_line_edit import ModernLineEdit
from components.sliders.animated_slider import AnimatedSlider
from components.checkboxes.custom_check_box import CustomCheckBox
from themes import DEFAULT_THEME, DARK_THEME


def test_modern_line_edit():
    """Test ModernLineEdit component."""
    print("Testing ModernLineEdit...")

    # Create component
    lineedit = ModernLineEdit("Test text")

    # Test initial state
    assert lineedit.text() == "Test text"
    assert lineedit.isEnabled() == True
    assert lineedit.get_theme() is not None

    # Test theme switching
    lineedit.set_theme("dark")
    theme_mgr = ThemeManager.instance()
    assert theme_mgr.current_theme().name == "dark"

    # Test error state
    lineedit.set_error(True)
    lineedit.set_error(False)

    print("SUCCESS: ModernLineEdit created and themed!")


def test_animated_slider():
    """Test AnimatedSlider component."""
    print("Testing AnimatedSlider...")

    # Create component
    slider = AnimatedSlider(Qt.Orientation.Horizontal)

    # Test initial state
    assert slider.minimum() == 0
    assert slider.maximum() == 99
    assert slider.get_theme() is not None

    # Test value setting
    slider.setValue(50)
    assert slider.value() == 50

    # Test animated value
    slider.set_value_animated(75, 100)

    # Test theme switching
    slider.set_theme("dark")
    theme_mgr = ThemeManager.instance()
    assert theme_mgr.current_theme().name == "dark"

    print("SUCCESS: AnimatedSlider created and themed!")


def test_custom_check_box():
    """Test CustomCheckBox component."""
    print("Testing CustomCheckBox...")

    # Create component
    checkbox = CustomCheckBox("Test checkbox")

    # Test initial state
    assert checkbox.text() == "Test checkbox"
    assert checkbox.isChecked() == False
    assert checkbox.get_theme() is not None

    # Test checked state
    checkbox.setChecked(True)
    assert checkbox.isChecked() == True

    # Test theme switching
    checkbox.set_theme("dark")
    theme_mgr = ThemeManager.instance()
    assert theme_mgr.current_theme().name == "dark"

    print("SUCCESS: CustomCheckBox created and themed!")


if __name__ == "__main__":
    # Initialize application
    app = QApplication(sys.argv)

    # Setup themes
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.register_theme_dict("dark", DARK_THEME)
    theme_mgr.set_current_theme("default")

    # Run tests
    test_modern_line_edit()
    test_animated_slider()
    test_custom_check_box()

    print("\nAll tests passed!")
