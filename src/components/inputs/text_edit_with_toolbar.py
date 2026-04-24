"""
Rich Text Edit with Toolbar Component

遵循 Microsoft WinUI 3 设计规范实现。
A themed rich text editor with integrated formatting toolbar.

WinUI 3 Design Guidelines:
- Transparent/subtle background with low contrast border
- Compact toolbar with consistent button sizing
- Focus accent color border
- Theme-aware colors
- Unified visual design with consistent styling
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QResizeEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton,
    QSpinBox, QSizePolicy, QApplication
)
from src.core.theme_manager import ThemeManager, Theme
from src.core.style_override import StyleOverrideMixin
from src.core.font_manager import FontManager
from src.components.inputs.text_edit import TextEdit
from src.components.combo_box import ComboBox
from src.themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class ToolbarSeparator(QFrame):
    """Visual separator for toolbar sections, following WinUI 3 design."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFixedWidth(1)
        self.setObjectName("toolbarSeparator")


class AlignmentButton(QToolButton):
    """Button with drawn alignment icon, following WinUI 3 design."""

    LEFT = 0
    CENTER = 1
    RIGHT = 2

    def __init__(self, alignment: int, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._alignment = alignment
        self.setFixedSize(24, 24)
        self.setToolTip(self._get_tooltip())
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _get_tooltip(self) -> str:
        tooltips = {
            self.LEFT: "左对齐",
            self.CENTER: "居中对齐",
            self.RIGHT: "右对齐"
        }
        return tooltips.get(self._alignment, "")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.underMouse() or self.isChecked():
            hover_color = QColor(255, 255, 255, 30) if self.underMouse() else QColor(255, 255, 255, 20)
            painter.fillRect(self.rect(), hover_color)

        color = self.palette().color(self.foregroundRole())
        if self.isChecked():
            color = QColor(96, 205, 255)

        painter.setPen(QPen(color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        w, h = self.width(), self.height()
        margin = 7
        line_height = 2
        spacing = 3
        center_y = h // 2 - (line_height * 2 + spacing) // 2

        for i in range(3):
            y = center_y + i * (line_height + spacing)

            if self._alignment == self.LEFT:
                widths = [w - margin * 2, w - margin * 2 - 5, w - margin * 2 - 3]
            elif self._alignment == self.CENTER:
                widths = [w - margin * 2 - 3, w - margin * 2, w - margin * 2 - 5]
            else:
                widths = [w - margin * 2 - 5, w - margin * 2 - 3, w - margin * 2]

            line_width = widths[i]

            if self._alignment == self.LEFT:
                x = margin
            elif self._alignment == self.CENTER:
                x = (w - line_width) // 2
            else:
                x = w - margin - line_width

            painter.drawLine(x, y, x + line_width, y)

        painter.end()


class FormatToolbar(QWidget, StyleOverrideMixin):
    """Formatting toolbar for rich text editor with unified styling."""

    format_changed = pyqtSignal()

    def __init__(self, text_edit: TextEdit, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_style_override()

        self._text_edit = text_edit
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._buttons: dict = {}
        self._updating_state: bool = False

        self._setup_ui()
        self._connect_signals()
        self._apply_initial_theme()

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _setup_ui(self):
        self.setObjectName("formatToolbar")
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(2)

        self._create_format_buttons(layout)
        self._add_separator(layout)
        self._create_font_controls(layout)
        self._add_separator(layout)
        self._create_color_buttons(layout)
        self._add_separator(layout)
        self._create_alignment_buttons(layout)
        self._add_separator(layout)
        self._create_list_buttons(layout)
        layout.addStretch()
        self._create_extra_buttons(layout)

    def _add_separator(self, layout: QHBoxLayout):
        separator = ToolbarSeparator()
        layout.addWidget(separator)
        layout.addSpacing(4)

    def _create_format_buttons(self, layout: QHBoxLayout):
        self._buttons['bold'] = self._create_tool_button("B", "粗体 (Ctrl+B)", checkable=True)
        self._buttons['bold'].clicked.connect(lambda: self._toggle_format('bold'))
        layout.addWidget(self._buttons['bold'])

        self._buttons['italic'] = self._create_tool_button("I", "斜体 (Ctrl+I)", checkable=True)
        self._buttons['italic'].clicked.connect(lambda: self._toggle_format('italic'))
        layout.addWidget(self._buttons['italic'])

        self._buttons['underline'] = self._create_tool_button("U", "下划线 (Ctrl+U)", checkable=True)
        self._buttons['underline'].clicked.connect(lambda: self._toggle_format('underline'))
        layout.addWidget(self._buttons['underline'])

        self._buttons['strikethrough'] = self._create_tool_button("S", "删除线", checkable=True)
        self._buttons['strikethrough'].clicked.connect(lambda: self._toggle_format('strikethrough'))
        layout.addWidget(self._buttons['strikethrough'])

    def _create_font_controls(self, layout: QHBoxLayout):
        self._font_family_combo = ComboBox()
        self._font_family_combo.setMinimumWidth(100)
        self._font_family_combo.setMaximumWidth(120)
        self._font_family_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        font_families = [
            "Microsoft YaHei",
            "SimSun",
            "SimHei",
            "KaiTi",
            "Arial",
            "Times New Roman",
            "Courier New",
        ]
        self._font_family_combo.addItems(font_families)
        self._font_family_combo.currentTextChanged.connect(self._on_font_family_changed)

        layout.addWidget(self._font_family_combo)

        font_size_widget = QWidget()
        font_size_layout = QHBoxLayout(font_size_widget)
        font_size_layout.setContentsMargins(0, 0, 0, 0)
        font_size_layout.setSpacing(0)

        self._font_size_spin = QSpinBox()
        self._font_size_spin.setObjectName("fontSizeSpin")
        self._font_size_spin.setMinimum(8)
        self._font_size_spin.setMaximum(72)
        self._font_size_spin.setValue(12)
        self._font_size_spin.setMinimumWidth(32)
        self._font_size_spin.setMaximumWidth(36)
        self._font_size_spin.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._font_size_spin.valueChanged.connect(self._on_font_size_changed)

        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self._font_size_up = QToolButton()
        self._font_size_up.setObjectName("fontSizeBtn")
        self._font_size_up.setText("▴")
        self._font_size_up.setFixedSize(12, 8)
        self._font_size_up.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._font_size_up.clicked.connect(lambda: self._font_size_spin.stepBy(1))

        self._font_size_down = QToolButton()
        self._font_size_down.setObjectName("fontSizeBtn")
        self._font_size_down.setText("▾")
        self._font_size_down.setFixedSize(12, 8)
        self._font_size_down.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._font_size_down.clicked.connect(lambda: self._font_size_spin.stepBy(-1))

        btn_layout.addWidget(self._font_size_up)
        btn_layout.addWidget(self._font_size_down)

        font_size_layout.addWidget(self._font_size_spin)
        font_size_layout.addWidget(btn_container)

        layout.addWidget(font_size_widget)

    def _create_color_buttons(self, layout: QHBoxLayout):
        self._buttons['text_color'] = self._create_tool_button("A", "文字颜色")
        self._buttons['text_color'].clicked.connect(self._choose_text_color)
        layout.addWidget(self._buttons['text_color'])

        self._buttons['bg_color'] = self._create_tool_button("H", "高亮颜色")
        self._buttons['bg_color'].clicked.connect(self._choose_bg_color)
        layout.addWidget(self._buttons['bg_color'])

    def _create_alignment_buttons(self, layout: QHBoxLayout):
        self._buttons['align_left'] = AlignmentButton(AlignmentButton.LEFT)
        self._buttons['align_left'].clicked.connect(self._text_edit.align_left)
        layout.addWidget(self._buttons['align_left'])

        self._buttons['align_center'] = AlignmentButton(AlignmentButton.CENTER)
        self._buttons['align_center'].clicked.connect(self._text_edit.align_center)
        layout.addWidget(self._buttons['align_center'])

        self._buttons['align_right'] = AlignmentButton(AlignmentButton.RIGHT)
        self._buttons['align_right'].clicked.connect(self._text_edit.align_right)
        layout.addWidget(self._buttons['align_right'])

    def _create_list_buttons(self, layout: QHBoxLayout):
        self._buttons['bullet_list'] = self._create_tool_button("•", "项目列表")
        self._buttons['bullet_list'].clicked.connect(self._text_edit.set_bullet_list)
        layout.addWidget(self._buttons['bullet_list'])

        self._buttons['number_list'] = self._create_tool_button("1.", "编号列表")
        self._buttons['number_list'].clicked.connect(self._text_edit.set_numbered_list)
        layout.addWidget(self._buttons['number_list'])

    def _create_extra_buttons(self, layout: QHBoxLayout):
        self._buttons['link'] = self._create_tool_button("⎙", "插入链接")
        self._buttons['link'].clicked.connect(self._insert_link)
        layout.addWidget(self._buttons['link'])

        self._buttons['clear'] = self._create_tool_button("×", "清除格式")
        self._buttons['clear'].clicked.connect(self._text_edit.clear_formatting)
        layout.addWidget(self._buttons['clear'])

    def _create_tool_button(self, text: str, tooltip: str, checkable: bool = False) -> QToolButton:
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setCheckable(checkable)
        btn.setAutoRaise(True)
        btn.setFixedSize(24, 24)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _connect_signals(self):
        self._text_edit.format_changed.connect(self._update_button_states)

    def _apply_initial_theme(self):
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)

    def _on_theme_changed(self, theme: Theme):
        if not theme:
            return

        self._current_theme = theme
        is_dark = getattr(theme, 'is_dark', True)

        bg_normal = QColor(255, 255, 255, 9) if is_dark else QColor(0, 0, 0, 6)
        toolbar_bg = QColor(255, 255, 255, 6) if is_dark else QColor(0, 0, 0, 4)
        border_normal = QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24)
        text_color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0, 228)
        hover_bg = QColor(255, 255, 255, 30) if is_dark else QColor(0, 0, 0, 20)
        pressed_bg = QColor(255, 255, 255, 40) if is_dark else QColor(0, 0, 0, 30)
        checked_bg = QColor(255, 255, 255, 20) if is_dark else QColor(0, 0, 0, 15)
        accent = QColor('#60CDFF') if is_dark else QColor('#595959')

        style = f"""
            QWidget#formatToolbar {{
                background-color: {toolbar_bg.name(QColor.NameFormat.HexArgb)};
                border: none;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                font-size: 12px;
                font-weight: normal;
            }}
            QToolButton:hover {{
                background-color: {hover_bg.name(QColor.NameFormat.HexArgb)};
            }}
            QToolButton:pressed {{
                background-color: {pressed_bg.name(QColor.NameFormat.HexArgb)};
            }}
            QToolButton:checked {{
                background-color: {checked_bg.name(QColor.NameFormat.HexArgb)};
                color: {accent.name(QColor.NameFormat.HexArgb)};
            }}
            
            QSpinBox {{
                background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
                border: 1px solid {border_normal.name(QColor.NameFormat.HexArgb)};
                border-radius: 4px;
                padding: 1px 2px;
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                font-size: 11px;
                min-height: 18px;
            }}
            QSpinBox:hover {{
                border-color: {hover_bg.name(QColor.NameFormat.HexArgb)};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0;
                border: none;
                background: transparent;
            }}
            
            QToolButton#fontSizeBtn {{
                background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
                border: none;
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                font-size: 10px;
            }}
            QToolButton#fontSizeBtn:hover {{
                background-color: {hover_bg.name(QColor.NameFormat.HexArgb)};
            }}
            
            ToolbarSeparator, QFrame#toolbarSeparator {{
                background-color: {border_normal.name(QColor.NameFormat.HexArgb)};
                border: none;
                margin: 4px 2px;
            }}
        """
        self.setStyleSheet(style)

    def _toggle_format(self, format_type: str):
        if self._updating_state:
            return

        if format_type == 'bold':
            self._text_edit.toggle_bold()
        elif format_type == 'italic':
            self._text_edit.toggle_italic()
        elif format_type == 'underline':
            self._text_edit.toggle_underline()
        elif format_type == 'strikethrough':
            self._text_edit.toggle_strikethrough()

    def _on_font_family_changed(self, family: str):
        if self._updating_state:
            return
        self._text_edit.set_font_family(family)

    def _on_font_size_changed(self, size: int):
        if self._updating_state:
            return
        self._text_edit.set_font_size(size)

    def _choose_text_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self._text_edit.set_text_color(color)

    def _choose_bg_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self._text_edit.set_background_color(color)

    def _insert_link(self):
        from PyQt6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "插入链接", "请输入URL:")
        if ok and url:
            text, ok = QInputDialog.getText(self, "链接文本", "请输入链接显示文本:")
            if ok:
                self._text_edit.insert_hyperlink(url, text if text else url)

    def _update_button_states(self, state):
        self._updating_state = True
        try:
            self._buttons['bold'].setChecked(state.bold)
            self._buttons['italic'].setChecked(state.italic)
            self._buttons['underline'].setChecked(state.underline)
            self._buttons['strikethrough'].setChecked(state.strikethrough)

            self._buttons['align_left'].setChecked(
                state.alignment == Qt.AlignmentFlag.AlignLeft
            )
            self._buttons['align_center'].setChecked(
                state.alignment == Qt.AlignmentFlag.AlignHCenter
            )
            self._buttons['align_right'].setChecked(
                state.alignment == Qt.AlignmentFlag.AlignRight
            )

            if state.font_family:
                index = self._font_family_combo.findText(state.font_family)
                if index >= 0:
                    self._font_family_combo.setCurrentIndex(index)

            if state.font_size > 0:
                self._font_size_spin.setValue(state.font_size)
        finally:
            self._updating_state = False

    def cleanup(self):
        self._theme_mgr.unsubscribe(self)


class TextEditWithToolbar(QFrame, StyleOverrideMixin):
    """
    Rich text editor with integrated formatting toolbar.

    Unified visual design with:
    - Single border around the entire component
    - Consistent color scheme
    - Unified interaction states
    - Responsive layout

    Signals:
        format_changed: Emitted when text format changes
        text_changed: Emitted when text changes
        cursor_position_changed: Emitted when cursor position changes
    """

    format_changed = pyqtSignal(object)
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_style_override()

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._setup_ui(text)
        self._connect_signals()
        self._apply_initial_theme()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

    def _setup_ui(self, text: str):
        self.setObjectName("textEditWithToolbar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._text_edit = TextEdit(text)
        self._text_edit.setMinimumHeight(100)

        self._setup_font()

        self._toolbar = FormatToolbar(self._text_edit)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._text_edit, 1)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def _setup_font(self) -> None:
        """设置字体，遵循 WinUI 3 设计规范。"""
        font = FontManager.get_body_font()
        self._text_edit.setFont(font)

    def _connect_signals(self):
        self._text_edit.format_changed.connect(self.format_changed.emit)
        self._text_edit.text_changed.connect(self.text_changed.emit)
        self._text_edit.cursor_position_changed.connect(self.cursor_position_changed.emit)

    def _update_border_style(self):
        if not self._current_theme:
            return

        is_dark = getattr(self._current_theme, 'is_dark', True)

        border_normal = QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24)
        bg_normal = QColor(255, 255, 255, 9) if is_dark else QColor(0, 0, 0, 6)

        style = f"""
            QFrame#textEditWithToolbar {{
                background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
                border: 1px solid {border_normal.name(QColor.NameFormat.HexArgb)};
                border-radius: 4px;
            }}
        """
        self.setStyleSheet(style)

    def _apply_initial_theme(self):
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)

    def _on_theme_changed(self, theme: Theme):
        if not theme:
            return

        self._current_theme = theme
        self._update_border_style()

        is_dark = getattr(theme, 'is_dark', True)

        bg_normal = QColor(255, 255, 255, 9) if is_dark else QColor(0, 0, 0, 6)
        text_color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0, 228)
        separator_color = QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24)
        border_focus = QColor('#60CDFF') if is_dark else QColor('#595959')
        selection_bg = QColor(0, 120, 212, 128)

        text_edit_style = f"""
            TextEdit {{
                background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                border: none;
                border-top: 1px solid {separator_color.name(QColor.NameFormat.HexArgb)};
                border-bottom-left-radius: 3px;
                border-bottom-right-radius: 3px;
                padding: 0px;
            }}
            TextEdit:disabled {{
                background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
                border: none;
                border-top: 1px solid {separator_color.name(QColor.NameFormat.HexArgb)};
            }}
            TextEdit::selection {{
                background-color: {selection_bg.name(QColor.NameFormat.HexArgb)};
                color: white;
            }}
        """
        self._text_edit.setStyleSheet(text_edit_style)

    def _on_widget_destroyed(self):
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)

    def text_edit(self) -> TextEdit:
        return self._text_edit

    def toolbar(self) -> FormatToolbar:
        return self._toolbar

    def setPlainText(self, text: str):
        self._text_edit.setPlainText(text)

    def toPlainText(self) -> str:
        return self._text_edit.toPlainText()

    def setHtml(self, html: str):
        self._text_edit.setHtml(html)

    def toHtml(self) -> str:
        return self._text_edit.toHtml()

    def clear(self):
        self._text_edit.clear()

    def set_read_only(self, read_only: bool):
        self._text_edit.setReadOnly(read_only)

    def set_placeholder_text(self, text: str):
        self._text_edit.setPlaceholderText(text)

    def cleanup(self):
        if self._cleanup_done:
            return
        self._cleanup_done = True
        self._toolbar.cleanup()
        self._text_edit.cleanup()
        self._theme_mgr.unsubscribe(self)
