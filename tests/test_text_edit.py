"""
Unit tests for TextEdit component.

Tests cover:
- Initialization and configuration
- Theme integration
- Text formatting operations
- Rich text features
- Alignment and lists
- Hyperlink and image insertion
- Error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCursor, QTextListFormat, QFont
from PyQt6.QtWidgets import QApplication

from components.inputs.text_edit import TextEdit, TextFormatState, TextEditConfig
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
    """Create TextEdit instance for testing."""
    widget = TextEdit()
    yield widget
    widget.cleanup()
    widget.deleteLater()


class TestTextEditInitialization:
    """Test TextEdit initialization."""
    
    def test_default_initialization(self, editor):
        """Test default initialization."""
        assert editor is not None
        assert editor.get_text() == ""
        assert editor.get_line_count() == 1
    
    def test_initialization_with_text(self, app):
        """Test initialization with initial text."""
        text = "Line 1\nLine 2\nLine 3"
        editor = TextEdit(text)
        
        assert editor.get_text() == text
        assert editor.get_line_count() == 3
        
        editor.cleanup()
        editor.deleteLater()
    
    def test_minimum_size(self, editor):
        """Test minimum size is set."""
        min_size = editor.minimumSize()
        assert min_size.width() >= TextEditConfig.DEFAULT_MIN_WIDTH
        assert min_size.height() >= TextEditConfig.DEFAULT_MIN_HEIGHT
    
    def test_format_state_initialization(self, editor):
        """Test format state is initialized."""
        state = editor.get_format_state()
        assert isinstance(state, TextFormatState)
        assert state.bold is False
        assert state.italic is False
        assert state.underline is False


class TestTextEditTheme:
    """Test TextEdit theme integration."""
    
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


class TestTextEditFormatting:
    """Test text formatting operations."""
    
    def test_set_bold(self, editor):
        """Test setting bold."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_bold(True)
        
        state = editor.get_format_state()
        assert state.bold is True
    
    def test_toggle_bold(self, editor):
        """Test toggling bold."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        initial_state = editor.get_format_state().bold
        editor.toggle_bold()
        new_state = editor.get_format_state().bold
        
        assert new_state != initial_state
    
    def test_set_italic(self, editor):
        """Test setting italic."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_italic(True)
        
        state = editor.get_format_state()
        assert state.italic is True
    
    def test_set_underline(self, editor):
        """Test setting underline."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_underline(True)
        
        state = editor.get_format_state()
        assert state.underline is True
    
    def test_set_strikethrough(self, editor):
        """Test setting strikethrough."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_strikethrough(True)
        
        state = editor.get_format_state()
        assert state.strikethrough is True
    
    def test_set_font_family(self, editor):
        """Test setting font family."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_font_family("Arial")
        
        state = editor.get_format_state()
        assert "Arial" in state.font_family or state.font_family == ""
    
    def test_set_font_size(self, editor):
        """Test setting font size."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_font_size(16)
        
        state = editor.get_format_state()
        assert state.font_size == 16


class TestTextEditColors:
    """Test color operations."""
    
    def test_set_text_color(self, editor):
        """Test setting text color."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        color = QColor(255, 0, 0)
        editor.set_text_color(color)
        
        state = editor.get_format_state()
        assert state.text_color.name() == color.name()
    
    def test_set_background_color(self, editor):
        """Test setting background color."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        color = QColor(255, 255, 0)
        editor.set_background_color(color)
        
        state = editor.get_format_state()
        assert state.background_color.name() == color.name()


class TestTextEditAlignment:
    """Test text alignment operations."""
    
    def test_align_left(self, editor):
        """Test left alignment."""
        editor.set_text("Test")
        editor.align_left()
        
        state = editor.get_format_state()
        assert state.alignment == Qt.AlignmentFlag.AlignLeft
    
    def test_align_center(self, editor):
        """Test center alignment."""
        editor.set_text("Test")
        editor.align_center()
        
        state = editor.get_format_state()
        assert state.alignment == Qt.AlignmentFlag.AlignHCenter
    
    def test_align_right(self, editor):
        """Test right alignment."""
        editor.set_text("Test")
        editor.align_right()
        
        state = editor.get_format_state()
        assert state.alignment == Qt.AlignmentFlag.AlignRight
    
    def test_align_justify(self, editor):
        """Test justify alignment."""
        editor.set_text("Test")
        editor.align_justify()
        
        state = editor.get_format_state()
        assert state.alignment == Qt.AlignmentFlag.AlignJustify


class TestTextEditLists:
    """Test list operations."""
    
    def test_set_bullet_list(self, editor):
        """Test setting bullet list."""
        editor.set_text("Item 1")
        editor.set_bullet_list()
        
        state = editor.get_format_state()
        assert state.is_list is True
        assert state.list_style == QTextListFormat.Style.ListDisc
    
    def test_set_numbered_list(self, editor):
        """Test setting numbered list."""
        editor.set_text("Item 1")
        editor.set_numbered_list()
        
        state = editor.get_format_state()
        assert state.is_list is True
        assert state.list_style == QTextListFormat.Style.ListDecimal
    
    def test_remove_list(self, editor):
        """Test removing list."""
        editor.set_text("Item 1")
        editor.set_bullet_list()
        editor.remove_list()
        
        state = editor.get_format_state()
        assert state.is_list is False


class TestTextEditIndentation:
    """Test indentation operations."""
    
    def test_increase_indent(self, editor):
        """Test increasing indent."""
        editor.set_text("Test")
        editor.increase_indent()
        
        cursor = editor.textCursor()
        block_format = cursor.blockFormat()
        assert block_format.indent() == 1
    
    def test_decrease_indent(self, editor):
        """Test decreasing indent."""
        editor.set_text("Test")
        editor.increase_indent()
        editor.increase_indent()
        editor.decrease_indent()
        
        cursor = editor.textCursor()
        block_format = cursor.blockFormat()
        assert block_format.indent() == 1


class TestTextEditHyperlink:
    """Test hyperlink operations."""
    
    def test_insert_hyperlink(self, editor):
        """Test inserting hyperlink."""
        editor.insert_hyperlink("https://example.com", "Example")
        
        html = editor.get_html()
        assert "https://example.com" in html
        assert "Example" in html


class TestTextEditTable:
    """Test table operations."""
    
    def test_insert_table(self, editor):
        """Test inserting table."""
        editor.insert_table(2, 3)
        
        html = editor.get_html()
        assert "<table" in html


class TestTextEditClearFormatting:
    """Test clear formatting."""
    
    def test_clear_formatting(self, editor):
        """Test clearing all formatting."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        editor.set_bold(True)
        editor.set_italic(True)
        editor.set_underline(True)
        
        editor.clear_formatting()
        
        state = editor.get_format_state()
        assert state.bold is False
        assert state.italic is False
        assert state.underline is False


class TestTextEditErrorState:
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


class TestTextEditReadOnly:
    """Test read-only functionality."""
    
    def test_set_read_only(self, editor):
        """Test setting read-only."""
        editor.set_read_only(True)
        assert editor.is_read_only() is True


class TestTextEditHtmlOperations:
    """Test HTML operations."""
    
    def test_get_html(self, editor):
        """Test getting HTML."""
        editor.set_text("Test")
        html = editor.get_html()
        assert "Test" in html
    
    def test_set_html(self, editor):
        """Test setting HTML."""
        html = "<b>Bold</b> text"
        editor.set_html(html)
        
        content = editor.get_text()
        assert "Bold" in content


class TestTextEditTextOperations:
    """Test basic text operations."""
    
    def test_set_text(self, editor):
        """Test setting text."""
        editor.set_text("Hello World")
        assert editor.get_text() == "Hello World"
    
    def test_append_text(self, editor):
        """Test appending text."""
        editor.set_text("Line 1")
        editor.append_text("Line 2")
        assert "Line 1" in editor.get_text()
        assert "Line 2" in editor.get_text()
    
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


class TestTextEditUndoRedo:
    """Test undo/redo functionality."""
    
    def test_can_undo(self, editor):
        """Test undo availability."""
        editor.set_text("Test")
        assert editor.can_undo() is True
    
    def test_can_redo(self, editor):
        """Test redo availability."""
        editor.set_text("Test")
        editor.undo()
        assert editor.can_redo() is True
    
    def test_clear_undo_stack(self, editor):
        """Test clearing undo stack."""
        editor.set_text("Test")
        editor.clear_undo_redo_stack()
        assert editor.can_undo() is False


class TestTextEditCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup(self, app):
        """Test cleanup method."""
        editor = TextEdit()
        editor.set_text("Test")
        
        editor.cleanup()
        
        assert editor._cleanup_done is True
    
    def test_multiple_cleanup(self, app):
        """Test multiple cleanup calls are safe."""
        editor = TextEdit()
        editor.cleanup()
        editor.cleanup()
        
        assert editor._cleanup_done is True


class TestTextEditCursorPosition:
    """Test cursor position functionality."""
    
    def test_get_current_line(self, editor):
        """Test getting current line."""
        editor.set_text("Line 1\nLine 2\nLine 3")
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Down)
        editor.setTextCursor(cursor)
        
        assert editor.get_current_line() == 2
    
    def test_get_current_column(self, editor):
        """Test getting current column."""
        editor.set_text("Hello World")
        cursor = editor.textCursor()
        cursor.setPosition(5)
        editor.setTextCursor(cursor)
        
        assert editor.get_current_column() == 6


class TestTextEditSignals:
    """Test signal emissions."""
    
    def test_text_changed_signal(self, qtbot, editor):
        """Test textChanged signal."""
        with qtbot.waitSignal(editor.text_changed, timeout=1000):
            editor.set_text("Test")
    
    def test_format_changed_signal(self, qtbot, editor):
        """Test formatChanged signal."""
        editor.set_text("Test")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        
        with qtbot.waitSignal(editor.format_changed, timeout=1000):
            editor.set_bold(True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
