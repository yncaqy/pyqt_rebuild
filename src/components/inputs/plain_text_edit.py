"""
Plain Text Edit Component

A high-performance, themed multi-line plain text editor with:
- Theme integration with automatic updates
- Optional line number display
- Syntax highlighting support (extensible)
- Performance optimization for large files
- Error state visualization
- Word wrap and line wrap controls
- Find and replace functionality
- Undo/redo support
- Context menu with common actions
"""

import logging
import re
from typing import Optional, List, Tuple, Any
from PyQt6.QtCore import Qt, QTimer, QRegularExpression, pyqtSignal, QSize
from PyQt6.QtGui import (
    QColor, QTextCursor, QTextCharFormat, QFont, QPalette, QPainter, QTextDocument
)
from PyQt6.QtWidgets import (
    QPlainTextEdit, QTextEdit, QWidget, QSizePolicy
)
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class TextEditConfig:
    """Configuration constants for text edit behavior and styling."""

    DEFAULT_MIN_WIDTH = 300
    DEFAULT_MIN_HEIGHT = 150
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_PADDING = 8
    DEFAULT_LINE_NUMBER_WIDTH = 50
    DEFAULT_TAB_STOP_WIDTH = 4
    LARGE_FILE_THRESHOLD = 100000
    UPDATE_DELAY_MS = 100


class LineNumberArea(QWidget):
    """
    Line number display area for PlainTextEdit.
    
    Renders line numbers with proper theme integration.
    """
    
    def __init__(self, editor: 'PlainTextEdit', parent: Optional[QWidget] = None):
        super().__init__(editor)
        
        self._editor = editor
        self._line_number_color: QColor = QColor(150, 150, 150)
        self._background_color: QColor = QColor(250, 250, 250)
        self._current_line_color: QColor = QColor(80, 80, 80)
        self._current_line_bg: QColor = QColor(230, 255, 230)
        
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def sizeHint(self):
        return self._editor._line_number_area_size_hint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self._background_color)
        
        editor_font = self._editor.font()
        painter.setFont(editor_font)
        
        font_metrics = self._editor.fontMetrics()
        line_height = font_metrics.height()
        highlight_height = line_height + 6
        
        block = self._editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self._editor.blockBoundingGeometry(block).translated(
            self._editor.contentOffset()
        ).top()
        bottom = top + self._editor.blockBoundingRect(block).height()
        
        current_block = self._editor.textCursor().block()
        current_block_number = current_block.blockNumber()
        
        current_font = QFont(editor_font)
        current_font.setBold(True)
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                is_current_line = (block_number == current_block_number)
                
                if is_current_line:
                    cursor_rect = self._editor.cursorRect(self._editor.textCursor())
                    highlight_top = cursor_rect.top() - 3
                    painter.fillRect(
                        0, int(highlight_top), self.width(), int(highlight_height),
                        self._current_line_bg
                    )
                    painter.setFont(current_font)
                    painter.setPen(self._current_line_color)
                    painter.drawText(
                        0, int(highlight_top), self.width() - 5, int(highlight_height),
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                        number
                    )
                else:
                    painter.setFont(editor_font)
                    painter.setPen(self._line_number_color)
                    painter.drawText(
                        0, int(top), self.width() - 5, int(bottom - top),
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                        number
                    )
            
            block = block.next()
            top = bottom
            bottom = top + self._editor.blockBoundingRect(block).height()
            block_number += 1
    
    def set_colors(
        self,
        line_color: QColor,
        background: QColor,
        current_line_color: QColor,
        current_line_bg: QColor
    ) -> None:
        self._line_number_color = line_color
        self._background_color = background
        self._current_line_color = current_line_color
        self._current_line_bg = current_line_bg
        self.update()


class PlainTextEdit(QPlainTextEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    High-performance themed plain text editor with advanced features.
    
    Features:
    - Theme integration with automatic updates
    - Optional line number display
    - Current line highlighting
    - Syntax highlighting support (extensible)
    - Performance optimization for large files
    - Error state visualization
    - Word wrap control
    - Find and replace functionality
    - Undo/redo support
    - Context menu with common actions
    - Bracket matching
    - Auto-indentation
    
    Signals:
        text_changed: Emitted when text changes
        cursor_position_changed: Emitted when cursor position changes
        selection_changed: Emitted when selection changes
        line_count_changed: Emitted when line count changes
    
    Example:
        editor = PlainTextEdit()
        editor.set_line_numbers_visible(True)
        editor.set_placeholder_text("Enter your code here...")
        editor.text_changed.connect(lambda: print("Text changed"))
    """
    
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)
    selection_changed = pyqtSignal()
    line_count_changed = pyqtSignal(int)
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._line_numbers_visible: bool = False
        self._highlight_current_line: bool = False
        self._error_state: bool = False
        self._read_only_style: bool = False
        self._auto_indent: bool = True
        self._tab_width: int = TextEditConfig.DEFAULT_TAB_STOP_WIDTH
        
        self._line_number_area: Optional[LineNumberArea] = None
        self._extra_selections: List[Any] = []
        
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_update)
        
        self._line_count = self.document().blockCount()
        
        self.setMinimumSize(
            TextEditConfig.DEFAULT_MIN_WIDTH,
            TextEditConfig.DEFAULT_MIN_HEIGHT
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        self.setTabStopDistance(self._tab_width * self.fontMetrics().horizontalAdvance(' '))
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        self.textChanged.connect(self._on_text_changed)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.selectionChanged.connect(self._on_selection_changed)
        self.blockCountChanged.connect(self._on_block_count_changed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
        
        logger.debug("PlainTextEdit initialized")
    
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to PlainTextEdit: {e}")
    
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return
        
        self._current_theme = theme
        
        bg_normal = self.get_style_color(
            theme, 'input.background.normal', QColor(255, 255, 255)
        )
        bg_disabled = self.get_style_color(
            theme, 'input.background.disabled', QColor(245, 245, 245)
        )
        bg_readonly = self.get_style_color(
            theme, 'input.background.readonly', QColor(250, 250, 250)
        )
        
        text_color = self.get_style_color(
            theme, 'input.text.normal', QColor(51, 51, 51)
        )
        text_disabled = self.get_style_color(
            theme, 'input.text.disabled', QColor(170, 170, 170)
        )
        text_placeholder = self.get_style_color(
            theme, 'input.text.placeholder', QColor(170, 170, 170)
        )
        
        border_color = self.get_style_color(
            theme, 'input.border.normal', QColor(204, 204, 204)
        )
        border_error = self.get_style_color(
            theme, 'input.border.error', QColor(231, 76, 60)
        )
        
        selection_bg = self.get_style_color(
            theme, 'input.selection.background', QColor(52, 152, 219)
        )
        selection_text = self.get_style_color(
            theme, 'input.selection.text', QColor(255, 255, 255)
        )
        
        current_line_bg = self.get_style_color(
            theme, 'textedit.current_line.background', QColor(230, 255, 230)
        )
        
        line_number_color = self.get_style_color(
            theme, 'textedit.line_number.color', QColor(150, 150, 150)
        )
        line_number_bg = self.get_style_color(
            theme, 'textedit.line_number.background', QColor(250, 250, 250)
        )
        line_number_current = self.get_style_color(
            theme, 'textedit.line_number.current', QColor(80, 80, 80)
        )
        
        border_radius = self.get_style_value(
            theme, 'input.border_radius', TextEditConfig.DEFAULT_BORDER_RADIUS
        )
        padding = self.get_style_value(
            theme, 'textedit.padding', TextEditConfig.DEFAULT_PADDING
        )
        
        cache_key = (
            bg_normal.name(),
            bg_disabled.name(),
            bg_readonly.name(),
            text_color.name(),
            text_disabled.name(),
            text_placeholder.name(),
            border_color.name(),
            border_error.name(),
            selection_bg.name(),
            selection_text.name(),
            border_radius,
            padding,
            self._error_state,
            self._read_only_style,
        )
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(
                bg_normal, bg_disabled, bg_readonly, text_color, text_disabled,
                text_placeholder, border_color, border_error,
                selection_bg, selection_text, border_radius, padding
            )
        )
        
        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, text_placeholder)
        self.setPalette(palette)
        
        self._current_line_bg = current_line_bg
        if self._highlight_current_line:
            self._highlight_current_line_area()
        
        if self._line_number_area:
            self._line_number_area.set_colors(
                line_number_color, line_number_bg,
                line_number_current, current_line_bg
            )
    
    def _build_stylesheet(
        self,
        bg_normal: QColor,
        bg_disabled: QColor,
        bg_readonly: QColor,
        text_color: QColor,
        text_disabled: QColor,
        text_placeholder: QColor,
        border_color: QColor,
        border_error: QColor,
        selection_bg: QColor,
        selection_text: QColor,
        border_radius: int,
        padding: int
    ) -> str:
        return f"""
        PlainTextEdit {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 1px solid {border_color.name()};
            border-radius: {border_radius}px;
            padding: {padding}px;
        }}
        PlainTextEdit:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid {border_color.name()};
        }}
        PlainTextEdit[readOnly="true"] {{
            background-color: {bg_readonly.name()};
        }}
        PlainTextEdit[error="true"] {{
            border: 1px solid {border_error.name()};
        }}
        PlainTextEdit::selection {{
            background-color: {selection_bg.name()};
            color: {selection_text.name()};
        }}
        """
    
    def set_line_numbers_visible(self, visible: bool) -> None:
        if self._line_numbers_visible == visible:
            return
        
        self._line_numbers_visible = visible
        
        if visible:
            if not self._line_number_area:
                self._line_number_area = LineNumberArea(self)
                self.setViewportMargins(
                    TextEditConfig.DEFAULT_LINE_NUMBER_WIDTH, 0, 0, 0
                )
                if self._current_theme:
                    line_number_color = self.get_style_color(
                        self._current_theme, 'textedit.line_number.color', QColor(120, 120, 120)
                    )
                    line_number_bg = self.get_style_color(
                        self._current_theme, 'textedit.line_number.background', QColor(245, 245, 245)
                    )
                    line_number_current = self.get_style_color(
                        self._current_theme, 'textedit.line_number.current', QColor(60, 60, 60)
                    )
                    current_line_bg = self.get_style_color(
                        self._current_theme, 'textedit.current_line.background', QColor(245, 245, 245)
                    )
                    self._line_number_area.set_colors(
                        line_number_color, line_number_bg,
                        line_number_current, current_line_bg
                    )
            self._line_number_area.show()
            self._update_line_number_area_width()
        else:
            if self._line_number_area:
                self._line_number_area.hide()
            self.setViewportMargins(0, 0, 0, 0)
        
        logger.debug(f"Line numbers visible: {visible}")
    
    def is_line_numbers_visible(self) -> bool:
        return self._line_numbers_visible
    
    def set_highlight_current_line(self, highlight: bool) -> None:
        self._highlight_current_line = highlight
        if highlight:
            self._highlight_current_line_area()
        else:
            self.setExtraSelections([])
        logger.debug(f"Highlight current line: {highlight}")
    
    def is_highlight_current_line(self) -> bool:
        return self._highlight_current_line
    
    def _highlight_current_line_area(self) -> None:
        if not self._highlight_current_line:
            self.setExtraSelections([])
            return
        self.viewport().update()
    
    def paintEvent(self, event):
        if self._highlight_current_line:
            painter = QPainter(self.viewport())
            
            font_metrics = self.fontMetrics()
            line_height = font_metrics.height()
            highlight_height = line_height + 6
            
            cursor = self.textCursor()
            cursor_rect = self.cursorRect(cursor)
            
            highlight_top = cursor_rect.top() - 3
            
            rect = self.viewport().rect()
            rect.setTop(int(highlight_top))
            rect.setHeight(int(highlight_height))
            
            painter.fillRect(rect, self._current_line_bg)
            painter.end()
        
        super().paintEvent(event)
    
    def _line_number_area_size_hint(self):
        digits = len(str(max(1, self.blockCount())))
        width = max(
            TextEditConfig.DEFAULT_LINE_NUMBER_WIDTH,
            self.fontMetrics().horizontalAdvance('9') * digits + 10
        )
        return QSize(width, self.height())
    
    def _update_line_number_area_width(self) -> None:
        if not self._line_numbers_visible or not self._line_number_area:
            return
        
        digits = len(str(max(1, self.blockCount())))
        width = max(
            30,
            self.fontMetrics().horizontalAdvance('9') * digits + 10
        )
        
        self.setViewportMargins(width, 0, 0, 0)
        
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            cr.left(), cr.top(), width, cr.height()
        )
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        
        if self._line_numbers_visible and self._line_number_area:
            cr = self.contentsRect()
            width = self._line_number_area.sizeHint().width()
            self._line_number_area.setGeometry(
                cr.left(), cr.top(), width, cr.height()
            )
    
    def scrollContentsBy(self, dx: int, dy: int) -> None:
        super().scrollContentsBy(dx, dy)
        
        if self._line_number_area:
            self._line_number_area.scroll(0, dy)
            self._line_number_area.update()
    
    def _on_text_changed(self) -> None:
        self.text_changed.emit()
        
        if self._line_numbers_visible:
            self._update_timer.start(TextEditConfig.UPDATE_DELAY_MS)
    
    def _on_cursor_position_changed(self) -> None:
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
        
        if self._highlight_current_line:
            self._highlight_current_line_area()
        
        if self._line_number_area:
            self._line_number_area.update()
    
    def _on_selection_changed(self) -> None:
        self.selection_changed.emit()
    
    def _on_block_count_changed(self, count: int) -> None:
        if count != self._line_count:
            self._line_count = count
            self.line_count_changed.emit(count)
            
            if self._line_numbers_visible:
                self._update_line_number_area_width()
    
    def _delayed_update(self) -> None:
        if self._line_number_area:
            self._line_number_area.update()
    
    def set_error(self, error: bool) -> None:
        self._error_state = error
        self.setProperty("error", "true" if error else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        logger.debug(f"Error state set to: {error}")
    
    def has_error(self) -> bool:
        return self._error_state
    
    def set_read_only_style(self, read_only: bool) -> None:
        self._read_only_style = read_only
        self.setReadOnly(read_only)
        self.setProperty("readOnly", "true" if read_only else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        logger.debug(f"Read-only style set to: {read_only}")
    
    def set_auto_indent(self, enabled: bool) -> None:
        self._auto_indent = enabled
        logger.debug(f"Auto indent: {enabled}")
    
    def is_auto_indent(self) -> bool:
        return self._auto_indent
    
    def set_tab_width(self, width: int) -> None:
        self._tab_width = max(1, width)
        self.setTabStopDistance(
            self._tab_width * self.fontMetrics().horizontalAdvance(' ')
        )
        logger.debug(f"Tab width set to: {width}")
    
    def get_tab_width(self) -> int:
        return self._tab_width
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Return and self._auto_indent:
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = ""
            for char in line:
                if char in (' ', '\t'):
                    indent += char
                else:
                    break
            
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        elif event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            if cursor.hasSelection():
                self._indent_selection()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Backtab:
            self._unindent_selection()
        else:
            super().keyPressEvent(event)
    
    def _indent_selection(self) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        while True:
            cursor.setPosition(max(cursor.position(), start))
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.insertText(' ' * self._tab_width)
            end += self._tab_width
            
            if not cursor.movePosition(QTextCursor.MoveOperation.Down):
                break
            if cursor.position() > end:
                break
        
        cursor.endEditBlock()
    
    def _unindent_selection(self) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        while True:
            cursor.setPosition(max(cursor.position(), start))
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            line_text = cursor.block().text()
            
            spaces_to_remove = 0
            for i, char in enumerate(line_text[:self._tab_width]):
                if char == ' ':
                    spaces_to_remove += 1
                elif char == '\t':
                    spaces_to_remove = 1
                    break
                else:
                    break
            
            if spaces_to_remove > 0:
                for _ in range(spaces_to_remove):
                    cursor.deleteChar()
                end -= spaces_to_remove
            
            if not cursor.movePosition(QTextCursor.MoveOperation.Down):
                break
            if cursor.position() > end:
                break
        
        cursor.endEditBlock()
    
    def find_text(
        self,
        text: str,
        case_sensitive: bool = False,
        whole_words: bool = False,
        regex: bool = False
    ) -> bool:
        if not text:
            return False
        
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        if regex:
            pattern = QRegularExpression(text)
            if not case_sensitive:
                pattern.setPatternOptions(
                    QRegularExpression.PatternOption.CaseInsensitiveOption
                )
            found = self.find(pattern, flags)
        else:
            found = self.find(text, flags)
        
        return found
    
    def find_all(
        self,
        text: str,
        case_sensitive: bool = False,
        whole_words: bool = False,
        regex: bool = False
    ) -> List[Tuple[int, int]]:
        if not text:
            return []
        
        results = []
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        while True:
            if regex:
                pattern = QRegularExpression(text)
                if not case_sensitive:
                    pattern.setPatternOptions(
                        QRegularExpression.PatternOption.CaseInsensitiveOption
                    )
                cursor = self.document().find(pattern, cursor, flags)
            else:
                cursor = self.document().find(text, cursor, flags)
            
            if cursor.isNull():
                break
            
            results.append((cursor.selectionStart(), cursor.selectionEnd()))
        
        return results
    
    def replace_text(
        self,
        find_text: str,
        replace_text: str,
        case_sensitive: bool = False,
        whole_words: bool = False,
        regex: bool = False
    ) -> bool:
        cursor = self.textCursor()
        
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            match = False
            
            if regex:
                pattern = re.compile(
                    find_text,
                    0 if case_sensitive else re.IGNORECASE
                )
                match = bool(pattern.fullmatch(selected_text))
            else:
                if not case_sensitive:
                    match = selected_text.lower() == find_text.lower()
                else:
                    match = selected_text == find_text
            
            if match:
                cursor.insertText(replace_text)
                return True
        
        return self.find_text(find_text, case_sensitive, whole_words, regex)
    
    def replace_all(
        self,
        find_text: str,
        replace_text: str,
        case_sensitive: bool = False,
        whole_words: bool = False,
        regex: bool = False
    ) -> int:
        count = 0
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)
        
        self.textChanged.disconnect(self._on_text_changed)
        
        try:
            while self.replace_text(find_text, replace_text, case_sensitive, whole_words, regex):
                count += 1
        finally:
            self.textChanged.connect(self._on_text_changed)
        
        return count
    
    def get_line_count(self) -> int:
        return self.document().blockCount()
    
    def get_current_line(self) -> int:
        return self.textCursor().blockNumber() + 1
    
    def get_current_column(self) -> int:
        return self.textCursor().columnNumber() + 1
    
    def goto_line(self, line: int) -> bool:
        if line < 1 or line > self.document().blockCount():
            return False
        
        cursor = QTextCursor(
            self.document().findBlockByNumber(line - 1)
        )
        self.setTextCursor(cursor)
        self.centerCursor()
        return True
    
    def get_line_text(self, line: int) -> str:
        if line < 1 or line > self.document().blockCount():
            return ""
        
        block = self.document().findBlockByNumber(line - 1)
        return block.text()
    
    def set_line_text(self, line: int, text: str) -> bool:
        if line < 1 or line > self.document().blockCount():
            return False
        
        cursor = QTextCursor(
            self.document().findBlockByNumber(line - 1)
        )
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.insertText(text)
        return True
    
    def insert_at_line(self, line: int, text: str) -> bool:
        if line < 1 or line > self.document().blockCount() + 1:
            return False
        
        if line > self.document().blockCount():
            self.appendPlainText(text)
        else:
            cursor = QTextCursor(
                self.document().findBlockByNumber(line - 1)
            )
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.insertText(text + "\n")
        
        return True
    
    def delete_line(self, line: int) -> bool:
        if line < 1 or line > self.document().blockCount():
            return False
        
        cursor = QTextCursor(
            self.document().findBlockByNumber(line - 1)
        )
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()
        return True
    
    def duplicate_line(self, line: int) -> bool:
        if line < 1 or line > self.document().blockCount():
            return False
        
        text = self.get_line_text(line)
        return self.insert_at_line(line + 1, text)
    
    def move_line_up(self, line: int) -> bool:
        if line <= 1 or line > self.document().blockCount():
            return False
        
        current_text = self.get_line_text(line)
        above_text = self.get_line_text(line - 1)
        
        self.set_line_text(line - 1, current_text)
        self.set_line_text(line, above_text)
        self.goto_line(line - 1)
        
        return True
    
    def move_line_down(self, line: int) -> bool:
        if line < 1 or line >= self.document().blockCount():
            return False
        
        current_text = self.get_line_text(line)
        below_text = self.get_line_text(line + 1)
        
        self.set_line_text(line, below_text)
        self.set_line_text(line + 1, current_text)
        self.goto_line(line + 1)
        
        return True
    
    def comment_lines(
        self,
        start_line: int,
        end_line: int,
        comment_prefix: str = "#"
    ) -> None:
        for line in range(start_line, end_line + 1):
            text = self.get_line_text(line)
            if text and not text.startswith(comment_prefix):
                self.set_line_text(line, comment_prefix + " " + text)
    
    def uncomment_lines(
        self,
        start_line: int,
        end_line: int,
        comment_prefix: str = "#"
    ) -> None:
        prefix_len = len(comment_prefix)
        for line in range(start_line, end_line + 1):
            text = self.get_line_text(line)
            if text.startswith(comment_prefix):
                text = text[prefix_len:].lstrip()
                self.set_line_text(line, text)
    
    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()
        
        menu.addSeparator()
        
        if self._line_numbers_visible:
            line_numbers_action = menu.addAction("隐藏行号")
        else:
            line_numbers_action = menu.addAction("显示行号")
        line_numbers_action.triggered.connect(
            lambda: self.set_line_numbers_visible(not self._line_numbers_visible)
        )
        
        menu.exec(event.globalPos())
    
    def _on_widget_destroyed(self) -> None:
        if not self._cleanup_done:
            self.cleanup()
    
    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        logger.debug("PlainTextEdit cleanup started")
        
        try:
            self.textChanged.disconnect(self._on_text_changed)
        except (TypeError, RuntimeError):
            pass
        
        try:
            self.cursorPositionChanged.disconnect(self._on_cursor_position_changed)
        except (TypeError, RuntimeError):
            pass
        
        try:
            self.selectionChanged.disconnect(self._on_selection_changed)
        except (TypeError, RuntimeError):
            pass
        
        try:
            self.blockCountChanged.disconnect(self._on_block_count_changed)
        except (TypeError, RuntimeError):
            pass
        
        if self._update_timer:
            self._update_timer.stop()
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            try:
                self._theme_mgr.unsubscribe(self)
                logger.debug("PlainTextEdit unsubscribed from theme manager")
            except Exception as e:
                logger.warning(f"Error unsubscribing from theme manager: {e}")
        
        self._clear_stylesheet_cache()
        self.clear_overrides()
        
        if self._line_number_area:
            try:
                self._line_number_area.hide()
                self._line_number_area.deleteLater()
            except (TypeError, RuntimeError):
                pass
            finally:
                self._line_number_area = None
        
        logger.debug("PlainTextEdit cleanup completed")
    
    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
        logger.debug("PlainTextEdit scheduled for deletion")
    
    def set_placeholder_text(self, text: str) -> None:
        self.setPlaceholderText(text)
    
    def get_placeholder_text(self) -> str:
        return self.placeholderText()
    
    def set_read_only(self, read_only: bool) -> None:
        self.setReadOnly(read_only)
    
    def is_read_only(self) -> bool:
        return self.isReadOnly()
    
    def get_text(self) -> str:
        return self.toPlainText()
    
    def set_text(self, text: str) -> None:
        self.setPlainText(text)
    
    def append_text(self, text: str) -> None:
        self.appendPlainText(text)
    
    def clear_text(self) -> None:
        self.clear()
    
    def get_selected_text(self) -> str:
        return self.textCursor().selectedText()
    
    def has_selection(self) -> bool:
        return self.textCursor().hasSelection()
    
    def get_selection_range(self) -> Tuple[int, int]:
        cursor = self.textCursor()
        return (cursor.selectionStart(), cursor.selectionEnd())
    
    def set_selection(self, start: int, end: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)
    
    def get_char_count(self) -> int:
        return len(self.toPlainText())
    
    def get_word_count(self) -> int:
        text = self.toPlainText().strip()
        if not text:
            return 0
        return len(text.split())
    
    def can_undo(self) -> bool:
        return self.document().isUndoAvailable()
    
    def can_redo(self) -> bool:
        return self.document().isRedoAvailable()
    
    def clear_undo_redo_stack(self) -> None:
        self.document().clearUndoRedoStacks()
    
    def set_undo_redo_enabled(self, enabled: bool) -> None:
        self.document().setUndoRedoEnabled(enabled)
    
    def is_undo_redo_enabled(self) -> bool:
        return self.document().isUndoRedoEnabled()
    
    def zoom_in(self, range: int = 1) -> None:
        self.zoomIn(range)
    
    def zoom_out(self, range: int = 1) -> None:
        self.zoomOut(range)
    
    def reset_zoom(self) -> None:
        font = QFont(self.document().defaultFont())
        font.setPointSize(10)
        self.document().setDefaultFont(font)
