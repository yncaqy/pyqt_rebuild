"""
Rich Text Edit Component

A themed rich text editor with:
- Theme integration with automatic updates
- Text formatting (bold, italic, underline, strikethrough)
- Font family and size selection
- Text color and background color
- Text alignment (left, center, right, justify)
- Lists (bullet, numbered)
- Indentation control
- Hyperlink support
- Image insertion
- Table support
- Undo/redo with history
- Context menu with formatting options
- Toolbar integration support
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, QSize
from PyQt6.QtGui import (
    QColor, QTextCursor, QTextCharFormat, QFont, QPalette,
    QTextListFormat, QTextBlockFormat, QTextImageFormat,
    QTextTableFormat, QKeySequence, QAction, QIcon, QDesktopServices
)
from PyQt6.QtWidgets import (
    QTextEdit, QWidget, QSizePolicy, QMenu, QApplication,
    QColorDialog, QFontDialog, QFileDialog, QMessageBox
)
from src.core.theme_manager import ThemeManager, Theme
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class TextEditConfig:
    """Configuration constants for rich text edit."""

    DEFAULT_MIN_WIDTH = 300
    DEFAULT_MIN_HEIGHT = 150
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_PADDING = 8
    DEFAULT_FONT_SIZE = 12
    DEFAULT_FONT_FAMILY = "Microsoft YaHei"


class TextFormatState:
    """Holds current text format state."""

    def __init__(self):
        self.bold: bool = False
        self.italic: bool = False
        self.underline: bool = False
        self.strikethrough: bool = False
        self.font_family: str = ""
        self.font_size: int = 12
        self.text_color: QColor = QColor(0, 0, 0)
        self.background_color: QColor = QColor(255, 255, 255)
        self.alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
        self.is_list: bool = False
        self.list_style: QTextListFormat.Style = QTextListFormat.Style.ListDisc


class TextEdit(QTextEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed rich text editor with comprehensive formatting support.

    Features:
    - Theme integration with automatic updates
    - Text formatting (bold, italic, underline, strikethrough)
    - Font family and size selection
    - Text color and background color
    - Text alignment (left, center, right, justify)
    - Lists (bullet, numbered)
    - Indentation control
    - Hyperlink support
    - Image insertion
    - Table support
    - Undo/redo with history
    - Context menu with formatting options
    - Format state tracking

    Signals:
        format_changed: Emitted when text format changes
        text_changed: Emitted when text changes
        cursor_position_changed: Emitted when cursor position changes

    Example:
        editor = TextEdit()
        editor.set_bold(True)
        editor.set_text_color(QColor(255, 0, 0))
        editor.set_font_size(14)
        editor.insert_hyperlink("https://example.com", "Example")
    """

    format_changed = pyqtSignal(object)
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)
    focus_in = pyqtSignal()
    focus_out = pyqtSignal()

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._error_state: bool = False
        self._read_only_style: bool = False
        self._format_state = TextFormatState()

        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._update_format_state)

        self.setMinimumSize(
            TextEditConfig.DEFAULT_MIN_WIDTH,
            TextEditConfig.DEFAULT_MIN_HEIGHT
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        font = QFont(
            TextEditConfig.DEFAULT_FONT_FAMILY,
            TextEditConfig.DEFAULT_FONT_SIZE
        )
        self.setFont(font)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        self.textChanged.connect(self._on_text_changed)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug("TextEdit initialized")

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to TextEdit: {e}")

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
        border_focus = self.get_style_color(
            theme, 'input.border.focus', QColor(52, 152, 219)
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

        link_color = self.get_style_color(
            theme, 'link.normal', QColor(52, 152, 219)
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
            border_focus.name(),
            border_error.name(),
            selection_bg.name(),
            selection_text.name(),
            link_color.name(),
            border_radius,
            padding,
            self._error_state,
            self._read_only_style,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(
                bg_normal, bg_disabled, bg_readonly, text_color, text_disabled,
                text_placeholder, border_color, border_focus, border_error,
                selection_bg, selection_text, link_color, border_radius, padding
            )
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, text_placeholder)
        palette.setColor(QPalette.ColorRole.Link, link_color)
        palette.setColor(QPalette.ColorRole.LinkVisited, link_color)
        self.setPalette(palette)

    def _build_stylesheet(
        self,
        bg_normal: QColor,
        bg_disabled: QColor,
        bg_readonly: QColor,
        text_color: QColor,
        text_disabled: QColor,
        text_placeholder: QColor,
        border_color: QColor,
        border_focus: QColor,
        border_error: QColor,
        selection_bg: QColor,
        selection_text: QColor,
        link_color: QColor,
        border_radius: int,
        padding: int
    ) -> str:
        return f"""
        TextEdit {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 2px solid {border_color.name()};
            border-radius: {border_radius}px;
            padding: {padding}px;
        }}
        TextEdit:focus {{
            border: 2px solid {border_focus.name()};
        }}
        TextEdit:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 2px solid {border_color.name()};
        }}
        TextEdit[readOnly="true"] {{
            background-color: {bg_readonly.name()};
        }}
        TextEdit[error="true"] {{
            border: 2px solid {border_error.name()};
        }}
        TextEdit::selection {{
            background-color: {selection_bg.name()};
            color: {selection_text.name()};
        }}
        TextEdit a {{
            color: {link_color.name()};
            text-decoration: underline;
        }}
        """

    def _on_text_changed(self) -> None:
        if self._cleanup_done:
            return
        self.text_changed.emit()

    def _on_cursor_position_changed(self) -> None:
        if self._cleanup_done:
            return

        try:
            cursor = self.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.cursor_position_changed.emit(line, column)
        except (RuntimeError, AttributeError):
            pass

        if not self._cleanup_done:
            self._update_timer.start(100)

    def _update_format_state(self) -> None:
        if self._cleanup_done:
            return

        try:
            cursor = self.textCursor()
            char_format = cursor.charFormat()
            block_format = cursor.blockFormat()

            self._format_state.bold = char_format.fontWeight() == QFont.Weight.Bold
            self._format_state.italic = char_format.fontItalic()
            self._format_state.underline = char_format.fontUnderline()
            self._format_state.strikethrough = char_format.fontStrikeOut()

            self._format_state.alignment = block_format.alignment()

            self.format_changed.emit(self._format_state)
        except Exception as e:
            logger.debug(f"更新格式状态失败: {e}")

    def get_format_state(self) -> TextFormatState:
        return self._format_state

    def set_bold(self, bold: bool) -> None:
        self._merge_char_format(
            QTextCharFormat.Property.FontWeight,
            QFont.Weight.Bold if bold else QFont.Weight.Normal
        )
        logger.debug(f"Bold set to: {bold}")

    def toggle_bold(self) -> None:
        self.set_bold(not self._format_state.bold)

    def set_italic(self, italic: bool) -> None:
        self._merge_char_format(QTextCharFormat.Property.FontItalic, italic)
        logger.debug(f"Italic set to: {italic}")

    def toggle_italic(self) -> None:
        self.set_italic(not self._format_state.italic)

    def set_underline(self, underline: bool) -> None:
        self._merge_char_format(QTextCharFormat.Property.FontUnderline, underline)
        logger.debug(f"Underline set to: {underline}")

    def toggle_underline(self) -> None:
        self.set_underline(not self._format_state.underline)

    def set_strikethrough(self, strikethrough: bool) -> None:
        self._merge_char_format(QTextCharFormat.Property.FontStrikeOut, strikethrough)
        logger.debug(f"Strikethrough set to: {strikethrough}")

    def toggle_strikethrough(self) -> None:
        self.set_strikethrough(not self._format_state.strikethrough)

    def set_font_family(self, family: str) -> None:
        format = QTextCharFormat()
        format.setFontFamily(family)
        self._merge_format(format)
        logger.debug(f"Font family set to: {family}")

    def set_font_size(self, size: int) -> None:
        format = QTextCharFormat()
        format.setFontPointSize(float(size))
        self._merge_format(format)
        logger.debug(f"Font size set to: {size}")

    def set_text_color(self, color: QColor) -> None:
        format = QTextCharFormat()
        format.setForeground(color)
        self._merge_format(format)
        logger.debug(f"Text color set to: {color.name()}")

    def set_background_color(self, color: QColor) -> None:
        format = QTextCharFormat()
        format.setBackground(color)
        self._merge_format(format)
        logger.debug(f"Background color set to: {color.name()}")

    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        cursor = self.textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.mergeBlockFormat(block_format)
        self._format_state.alignment = alignment
        self.format_changed.emit(self._format_state)
        logger.debug(f"Alignment set to: {alignment}")

    def align_left(self) -> None:
        self.set_alignment(Qt.AlignmentFlag.AlignLeft)

    def align_center(self) -> None:
        self.set_alignment(Qt.AlignmentFlag.AlignHCenter)

    def align_right(self) -> None:
        self.set_alignment(Qt.AlignmentFlag.AlignRight)

    def align_justify(self) -> None:
        self.set_alignment(Qt.AlignmentFlag.AlignJustify)

    def set_bullet_list(self) -> None:
        self._set_list(QTextListFormat.Style.ListDisc)

    def set_numbered_list(self) -> None:
        self._set_list(QTextListFormat.Style.ListDecimal)

    def set_list(self, style: QTextListFormat.Style) -> None:
        self._set_list(style)

    def _set_list(self, style: QTextListFormat.Style) -> None:
        cursor = self.textCursor()
        cursor.beginEditBlock()

        list_format = QTextListFormat()
        list_format.setStyle(style)
        list_format.setIndent(1)

        block = cursor.block()
        existing_list = block.textList()

        if existing_list:
            if existing_list.format().style() == style:
                existing_list.removeItem(block.blockNumber())
            else:
                existing_list.setFormat(list_format)
        else:
            cursor.createList(list_format)

        cursor.endEditBlock()
        self._update_format_state()
        logger.debug(f"List style set to: {style}")

    def remove_list(self) -> None:
        cursor = self.textCursor()
        block = cursor.block()
        text_list = block.textList()

        if text_list:
            text_list.removeItem(block.blockNumber())
            logger.debug("List removed")

    def increase_indent(self) -> None:
        cursor = self.textCursor()
        block_format = cursor.blockFormat()
        current_indent = block_format.indent()
        block_format.setIndent(current_indent + 1)
        cursor.mergeBlockFormat(block_format)
        logger.debug(f"Indent increased to: {current_indent + 1}")

    def decrease_indent(self) -> None:
        cursor = self.textCursor()
        block_format = cursor.blockFormat()
        current_indent = block_format.indent()
        if current_indent > 0:
            block_format.setIndent(current_indent - 1)
            cursor.mergeBlockFormat(block_format)
            logger.debug(f"Indent decreased to: {current_indent - 1}")

    def insert_hyperlink(
        self,
        url: str,
        text: Optional[str] = None
    ) -> None:
        cursor = self.textCursor()

        if text:
            cursor.insertText(text)
            cursor.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.KeepAnchor,
                len(text)
            )

        format = QTextCharFormat()
        format.setAnchor(True)
        format.setAnchorHref(url)
        format.setForeground(
            self.palette().color(QPalette.ColorRole.Link)
        )
        format.setFontUnderline(True)

        cursor.mergeCharFormat(format)
        logger.debug(f"Hyperlink inserted: {url}")

    def insert_image(
        self,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> bool:
        cursor = self.textCursor()
        image_format = QTextImageFormat()
        image_format.setName(path)

        if width:
            image_format.setWidth(width)
        if height:
            image_format.setHeight(height)

        cursor.insertImage(image_format)
        logger.debug(f"Image inserted: {path}")
        return True

    def insert_image_from_dialog(self) -> bool:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)"
        )

        if file_path:
            return self.insert_image(file_path)
        return False

    def insert_table(
        self,
        rows: int,
        columns: int,
        header: bool = False
    ) -> None:
        cursor = self.textCursor()

        table_format = QTextTableFormat()
        table_format.setBorder(1)
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        table = cursor.insertTable(rows, columns, table_format)

        if header:
            for col in range(columns):
                cell = table.cellAt(0, col)
                cell_cursor = cell.firstCursorPosition()
                cell_cursor.insertText(f"Header {col + 1}")

        logger.debug(f"Table inserted: {rows}x{columns}")

    def clear_formatting(self) -> None:
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)

        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontItalic(False)
        format.setFontUnderline(False)
        format.setFontStrikeOut(False)
        format.setForeground(self.palette().color(QPalette.ColorRole.Text))
        format.setBackground(QColor(255, 255, 255, 0))

        cursor.mergeCharFormat(format)

        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cursor.mergeBlockFormat(block_format)

        logger.debug("Formatting cleared")

    def _merge_char_format(self, property: QTextCharFormat.Property, value: Any) -> None:
        format = QTextCharFormat()
        format.setProperty(property, value)
        self._merge_format(format)

    def _merge_format(self, format: QTextCharFormat) -> None:
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(format)
        else:
            cursor.mergeCharFormat(format)
            self.mergeCurrentCharFormat(format)

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

    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()

        menu.addSeparator()

        format_menu = menu.addMenu("格式")

        bold_action = format_menu.addAction("粗体")
        bold_action.setCheckable(True)
        bold_action.setChecked(self._format_state.bold)
        bold_action.setShortcut(QKeySequence.StandardKey.Bold)
        bold_action.triggered.connect(self.toggle_bold)

        italic_action = format_menu.addAction("斜体")
        italic_action.setCheckable(True)
        italic_action.setChecked(self._format_state.italic)
        italic_action.setShortcut(QKeySequence.StandardKey.Italic)
        italic_action.triggered.connect(self.toggle_italic)

        underline_action = format_menu.addAction("下划线")
        underline_action.setCheckable(True)
        underline_action.setChecked(self._format_state.underline)
        underline_action.setShortcut(QKeySequence.StandardKey.Underline)
        underline_action.triggered.connect(self.toggle_underline)

        strikethrough_action = format_menu.addAction("删除线")
        strikethrough_action.setCheckable(True)
        strikethrough_action.setChecked(self._format_state.strikethrough)
        strikethrough_action.triggered.connect(self.toggle_strikethrough)

        format_menu.addSeparator()

        text_color_action = format_menu.addAction("文字颜色...")
        text_color_action.triggered.connect(self._choose_text_color)

        bg_color_action = format_menu.addAction("背景颜色...")
        bg_color_action.triggered.connect(self._choose_background_color)

        format_menu.addSeparator()

        font_action = format_menu.addAction("字体...")
        font_action.triggered.connect(self._choose_font)

        menu.addSeparator()

        align_menu = menu.addMenu("对齐")

        align_left_action = align_menu.addAction("左对齐")
        align_left_action.triggered.connect(self.align_left)

        align_center_action = align_menu.addAction("居中")
        align_center_action.triggered.connect(self.align_center)

        align_right_action = align_menu.addAction("右对齐")
        align_right_action.triggered.connect(self.align_right)

        align_justify_action = align_menu.addAction("两端对齐")
        align_justify_action.triggered.connect(self.align_justify)

        menu.addSeparator()

        list_menu = menu.addMenu("列表")

        bullet_action = list_menu.addAction("项目符号")
        bullet_action.triggered.connect(self.set_bullet_list)

        numbered_action = list_menu.addAction("编号列表")
        numbered_action.triggered.connect(self.set_numbered_list)

        remove_list_action = list_menu.addAction("移除列表")
        remove_list_action.triggered.connect(self.remove_list)

        menu.addSeparator()

        indent_menu = menu.addMenu("缩进")

        increase_indent_action = indent_menu.addAction("增加缩进")
        increase_indent_action.triggered.connect(self.increase_indent)

        decrease_indent_action = indent_menu.addAction("减少缩进")
        decrease_indent_action.triggered.connect(self.decrease_indent)

        menu.addSeparator()

        insert_menu = menu.addMenu("插入")

        link_action = insert_menu.addAction("超链接...")
        link_action.triggered.connect(self._insert_link_dialog)

        image_action = insert_menu.addAction("图片...")
        image_action.triggered.connect(self.insert_image_from_dialog)

        table_action = insert_menu.addAction("表格...")
        table_action.triggered.connect(self._insert_table_dialog)

        menu.addSeparator()

        clear_format_action = menu.addAction("清除格式")
        clear_format_action.triggered.connect(self.clear_formatting)

        menu.exec(event.globalPos())

    def _choose_text_color(self) -> None:
        color = QColorDialog.getColor(
            self._format_state.text_color,
            self,
            "选择文字颜色"
        )
        if color.isValid():
            self.set_text_color(color)

    def _choose_background_color(self) -> None:
        color = QColorDialog.getColor(
            self._format_state.background_color,
            self,
            "选择背景颜色"
        )
        if color.isValid():
            self.set_background_color(color)

    def _choose_font(self) -> None:
        font, ok = QFontDialog.getFont(self.font(), self, "选择字体")
        if ok:
            self.set_font_family(font.family())
            self.set_font_size(font.pointSize())

    def _insert_link_dialog(self) -> None:
        from PyQt6.QtWidgets import QInputDialog

        url, ok = QInputDialog.getText(
            self,
            "插入超链接",
            "请输入URL:",
            text="https://"
        )
        if ok and url:
            selected_text = self.textCursor().selectedText()
            self.insert_hyperlink(url, selected_text if selected_text else None)

    def _insert_table_dialog(self) -> None:
        from PyQt6.QtWidgets import QInputDialog

        rows, ok1 = QInputDialog.getInt(
            self,
            "插入表格",
            "行数:",
            value=3,
            min=1,
            max=100
        )
        if ok1:
            columns, ok2 = QInputDialog.getInt(
                self,
                "插入表格",
                "列数:",
                value=3,
                min=1,
                max=26
            )
            if ok2:
                self.insert_table(rows, columns, header=True)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focus_in.emit()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focus_out.emit()

    def _on_widget_destroyed(self) -> None:
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        if self._cleanup_done:
            return

        self._cleanup_done = True
        logger.debug("TextEdit cleanup started")

        try:
            self.textChanged.disconnect(self._on_text_changed)
        except (TypeError, RuntimeError):
            pass

        try:
            self.cursorPositionChanged.disconnect(self._on_cursor_position_changed)
        except (TypeError, RuntimeError):
            pass

        if self._update_timer:
            self._update_timer.stop()

        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            try:
                self._theme_mgr.unsubscribe(self)
                logger.debug("TextEdit unsubscribed from theme manager")
            except Exception as e:
                logger.warning(f"Error unsubscribing from theme manager: {e}")

        self._clear_stylesheet_cache()
        self.clear_overrides()

        logger.debug("TextEdit cleanup completed")

    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
        logger.debug("TextEdit scheduled for deletion")

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

    def get_html(self) -> str:
        return self.toHtml()

    def set_text(self, text: str) -> None:
        self.setPlainText(text)

    def set_html(self, html: str) -> None:
        self.setHtml(html)

    def append_text(self, text: str) -> None:
        self.append(text)

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

    def get_line_count(self) -> int:
        return self.document().blockCount()

    def get_current_line(self) -> int:
        return self.textCursor().blockNumber() + 1

    def get_current_column(self) -> int:
        return self.textCursor().columnNumber() + 1

    def can_undo(self) -> bool:
        return self.document().isUndoAvailable()

    def can_redo(self) -> bool:
        return self.document().isRedoAvailable()

    def clear_undo_redo_stack(self) -> None:
        self.document().clearUndoRedoStacks()

    def zoom_in(self, range: int = 1) -> None:
        self.zoomIn(range)

    def zoom_out(self, range: int = 1) -> None:
        self.zoomOut(range)

    def reset_zoom(self) -> None:
        self.zoomTo(0)
