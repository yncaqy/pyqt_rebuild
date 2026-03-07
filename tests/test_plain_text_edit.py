"""
Unit tests for PlainTextEdit component.

Tests cover:
- Initialization and configuration
- Theme integration
- Text operations
- Line number display
- Find and replace
- Line operations
- Error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QTextCursor
from PyQt6.QtWidgets import QApplication

from components.inputs.plain_text_edit import PlainTextEdit, TextEditConfig, LineNumberArea
from core.theme_manager import ThemeManager


@pytest.fixture(scope='module')
def app():
    """Create QApplication for tests."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication(sys.argv)
    yield test_app


@pytest.fixture
def editor(app):
    """Create PlainTextEdit instance for testing."""
    widget = PlainTextEdit()
    yield widget
    widget.cleanup()
    widget.deleteLater()


class TestPlainTextEditInitialization:
    """Test PlainTextEdit initialization."""
    
    def test_default_initialization(self, editor):
        """Test default initialization."""
        assert editor is not None
        assert editor.get_text() == ""
        assert editor.get_line_count() == 1
        assert editor.get_char_count() == 0
    
    def test_initialization_with_text(self, app):
        """Test initialization with initial text."""
        text = "Line 1\nLine 2\nLine 3"
        editor = PlainTextEdit(text)
        
        assert editor.get_text() == text
        assert editor.get_line_count() == 3
        
        editor.cleanup()
        editor.deleteLater()
    
    def test_minimum_size(self, editor):
        """Test minimum size is set."""
        min_size = editor.minimumSize()
        assert min_size.width() >= TextEditConfig.DEFAULT_MIN_WIDTH
        assert min_size.height() >= TextEditConfig.DEFAULT_MIN_HEIGHT
    
    def test_default_settings(self, editor):
        """Test default settings."""
        assert editor.is_auto_indent() is True
        assert editor.is_highlight_current_line() is True
        assert editor.is_line_numbers_visible() is False
        assert editor.get_tab_width() == TextEditConfig.DEFAULT_TAB_STOP_WIDTH


class TestPlainTextEditTheme:
    """Test PlainTextEdit theme integration."""
    
    def test_theme_manager_subscription(self, editor):
        """Test that editor subscribes to theme manager."""
        theme_mgr = ThemeManager.instance()
        assert theme_mgr is not None
    
    def test_theme_change(self, editor):
        """Test theme change updates editor style."""
        theme_mgr = ThemeManager.instance()
        theme_mgr.set_theme('dark')
        
        editor._apply_theme(theme_mgr.current_theme())
        
        theme_mgr.set_theme('light')
        editor._apply_theme(theme_mgr.current_theme())
        
        assert editor.styleSheet() != ""


class TestPlainTextEditTextOperations:
    """Test text operations."""
    
    def test_set_text(self, editor):
        """Test setting text."""
        text = "Hello World"
        editor.set_text(text)
        assert editor.get_text() == text
    
    def test_append_text(self, editor):
        """Test appending text."""
        editor.set_text("Line 1")
        editor.append_text("\nLine 2")
        assert editor.get_text() == "Line 1\nLine 2"
    
    def test_clear_text(self, editor):
        """Test clearing text."""
        editor.set_text("Some text")
        editor.clear_text()
        assert editor.get_text() == ""
    
    def test_get_char_count(self, editor):
        """Test character count."""
        editor.set_text("Hello")
        assert editor.get_char_count() == 5
    
    def test_get_word_count(self, editor):
        """Test word count."""
        editor.set_text("Hello World Test")
        assert editor.get_word_count() == 3
    
    def test_get_line_count(self, editor):
        """Test line count."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        assert editor.get_line_count() == 3
    
    def test_get_selected_text(self, editor):
        """Test getting selected text."""
        editor.set_text("Hello World")
        cursor = editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(5, QTextCursor.MoveMode.KeepAnchor)
        editor.setTextCursor(cursor)
        
        assert editor.has_selection() is True
        assert editor.get_selected_text() == "Hello"
    
    def test_set_selection(self, editor):
        """Test setting selection."""
        editor.set_text("Hello World")
        editor.set_selection(0, 5)
        
        assert editor.has_selection() is True
        assert editor.get_selection_range() == (0, 5)


class TestPlainTextEditLineNumbers:
    """Test line number display."""
    
    def test_show_line_numbers(self, editor):
        """Test showing line numbers."""
        editor.set_line_numbers_visible(True)
        assert editor.is_line_numbers_visible() is True
        assert editor._line_number_area is not None
    
    def test_hide_line_numbers(self, editor):
        """Test hiding line numbers."""
        editor.set_line_numbers_visible(True)
        editor.set_line_numbers_visible(False)
        assert editor.is_line_numbers_visible() is False
    
    def test_line_number_area_creation(self, editor):
        """Test line number area is created properly."""
        editor.set_line_numbers_visible(True)
        assert isinstance(editor._line_number_area, LineNumberArea)


class TestPlainTextEditFindReplace:
    """Test find and replace functionality."""
    
    def test_find_text(self, editor):
        """Test finding text."""
        editor.set_text("Hello World\nTest Line")
        found = editor.find_text("World")
        assert found is True
    
    def test_find_text_not_found(self, editor):
        """Test finding text that doesn't exist."""
        editor.set_text("Hello World")
        found = editor.find_text("NotFound")
        assert found is False
    
    def test_find_text_case_sensitive(self, editor):
        """Test case sensitive find."""
        editor.set_text("Hello World")
        found = editor.find_text("hello", case_sensitive=True)
        assert found is False
        
        found = editor.find_text("hello", case_sensitive=False)
        assert found is True
    
    def test_find_all(self, editor):
        """Test finding all occurrences."""
        editor.set_text("test test test")
        results = editor.find_all("test")
        assert len(results) == 3
    
    def test_replace_text(self, editor):
        """Test replacing text."""
        editor.set_text("Hello World")
        cursor = editor.textCursor()
        cursor.setPosition(6)
        cursor.setPosition(11, QTextCursor.MoveMode.KeepAnchor)
        editor.setTextCursor(cursor)
        
        replaced = editor.replace_text("World", "PyQt")
        assert replaced is True
    
    def test_replace_all(self, editor):
        """Test replacing all occurrences."""
        editor.set_text("test test test")
        count = editor.replace_all("test", "demo")
        assert count == 3
        assert editor.get_text() == "demo demo demo"


class TestPlainTextEditLineOperations:
    """Test line operations."""
    
    def test_goto_line(self, editor):
        """Test going to specific line."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        result = editor.goto_line(2)
        assert result is True
        assert editor.get_current_line() == 2
    
    def test_goto_invalid_line(self, editor):
        """Test going to invalid line."""
        editor.set_text("Line 1\nLine 2")
        result = editor.goto_line(10)
        assert result is False
    
    def test_get_line_text(self, editor):
        """Test getting line text."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        text = editor.get_line_text(2)
        assert text == "Line 2"
    
    def test_set_line_text(self, editor):
        """Test setting line text."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        result = editor.set_line_text(2, "Modified")
        assert result is True
        assert editor.get_line_text(2) == "Modified"
    
    def test_insert_at_line(self, editor):
        """Test inserting at line."""
        editor.set_text("Line 1\nLine 3")
        result = editor.insert_at_line(2, "Line 2")
        assert result is True
        assert editor.get_line_text(2) == "Line 2"
    
    def test_delete_line(self, editor):
        """Test deleting line."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        result = editor.delete_line(2)
        assert result is True
        assert editor.get_line_count() == 2
    
    def test_duplicate_line(self, editor):
        """Test duplicating line."""
        editor.set_text("Line 1\nLine 2")
        result = editor.duplicate_line(1)
        assert result is True
        assert editor.get_line_text(1) == "Line 1"
        assert editor.get_line_text(2) == "Line 1"


class TestPlainTextEditErrorState:
    """Test error state functionality."""
    
    def test_set_error(self, editor):
        """Test setting error state."""
        editor.set_error(True)
        assert editor.has_error() is True
    
    def test_clear_error(self, editor):
        """Test clearing error state."""
        editor.set_error(True)
        editor.set_error(False)
        assert editor.has_error() is False


class TestPlainTextEditReadOnly:
    """Test read-only functionality."""
    
    def test_set_read_only(self, editor):
        """Test setting read-only."""
        editor.set_read_only(True)
        assert editor.is_read_only() is True
    
    def test_set_read_only_style(self, editor):
        """Test read-only style."""
        editor.set_read_only_style(True)
        assert editor.is_read_only() is True


class TestPlainTextEditUndoRedo:
    """Test undo/redo functionality."""
    
    def test_can_undo(self, editor):
        """Test undo availability."""
        editor.set_text("Test")
        editor.textCursor().insertText(" More")
        QApplication.processEvents()
        assert editor.can_undo() is True
    
    def test_can_redo(self, editor):
        """Test redo availability."""
        editor.set_text("Test")
        editor.textCursor().insertText(" More")
        QApplication.processEvents()
        editor.undo()
        QApplication.processEvents()
        assert editor.can_redo() is True
    
    def test_clear_undo_stack(self, editor):
        """Test clearing undo stack."""
        editor.set_text("Test")
        editor.textCursor().insertText(" More")
        QApplication.processEvents()
        editor.clear_undo_redo_stack()
        assert editor.can_undo() is False


class TestPlainTextEditCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup(self, app):
        """Test cleanup method."""
        editor = PlainTextEdit()
        editor.set_text("Test")
        
        editor.cleanup()
        
        assert editor._cleanup_done is True
    
    def test_multiple_cleanup(self, app):
        """Test multiple cleanup calls are safe."""
        editor = PlainTextEdit()
        editor.cleanup()
        editor.cleanup()
        
        assert editor._cleanup_done is True


class TestPlainTextEditCursorPosition:
    """Test cursor position functionality."""
    
    def test_get_current_line(self, editor):
        """Test getting current line."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        QApplication.processEvents()
        editor.goto_line(2)
        QApplication.processEvents()
        assert editor.get_current_line() == 2
    
    def test_get_current_column(self, editor):
        """Test getting current column."""
        editor.set_text("Hello World")
        cursor = editor.textCursor()
        cursor.setPosition(5)
        editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        assert editor.get_current_column() == 6


class TestPlainTextEditSignals:
    """Test signal emissions."""
    
    def test_text_changed_signal(self, qtbot, editor):
        """Test textChanged signal."""
        with qtbot.waitSignal(editor.text_changed, timeout=1000):
            editor.set_text("Test")
            QApplication.processEvents()
    
    def test_line_count_changed_signal(self, qtbot, editor):
        """Test lineCountChanged signal."""
        with qtbot.waitSignal(editor.line_count_changed, timeout=1000):
            editor.set_text("Line 1\nLine 2")
            QApplication.processEvents()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
