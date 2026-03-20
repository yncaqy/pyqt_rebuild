"""
Rich Text Edit with Toolbar Component

A themed rich text editor with integrated formatting toolbar.
Unified visual design with consistent styling.
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QResizeEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton,
    QSpinBox, QSizePolicy, QApplication
)
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from components.inputs.text_edit import TextEdit
from components.combo_box import ComboBox

logger = logging.getLogger(__name__)


class ToolbarSeparator(QFrame):
    """Visual separator for toolbar sections."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFixedWidth(1)
        self.setObjectName("toolbarSeparator")


class AlignmentButton(QToolButton):
    """Button with drawn alignment icon."""
    
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    
    def __init__(self, alignment: int, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._alignment = alignment
        self.setFixedSize(28, 28)
        self.setToolTip(self._get_tooltip())
        self.setCheckable(True)
    
    def _get_tooltip(self) -> str:
        tooltips = {
            self.LEFT: "左对齐",
            self.CENTER: "居中对齐",
            self.RIGHT: "右对齐"
        }
        return tooltips.get(self._alignment, "")
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = self.palette().color(self.foregroundRole())
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        w, h = self.width(), self.height()
        margin = 6
        line_height = 3
        spacing = 3
        center_y = h // 2 - (line_height * 2 + spacing) // 2
        
        for i in range(3):
            y = center_y + i * (line_height + spacing)
            
            if self._alignment == self.LEFT:
                widths = [w - margin * 2, w - margin * 2 - 6, w - margin * 2 - 4]
            elif self._alignment == self.CENTER:
                widths = [w - margin * 2 - 4, w - margin * 2, w - margin * 2 - 6]
            else:
                widths = [w - margin * 2 - 6, w - margin * 2 - 4, w - margin * 2]
            
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
        self.setFixedHeight(36)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
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
        self._font_family_combo.setMinimumWidth(110)
        self._font_family_combo.setMaximumWidth(130)
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
        self._font_size_spin.setMinimumWidth(36)
        self._font_size_spin.setMaximumWidth(40)
        self._font_size_spin.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._font_size_spin.valueChanged.connect(self._on_font_size_changed)
        
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        
        self._font_size_up = QToolButton()
        self._font_size_up.setObjectName("fontSizeBtn")
        self._font_size_up.setText("▴")
        self._font_size_up.setFixedSize(14, 10)
        self._font_size_up.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._font_size_up.clicked.connect(lambda: self._font_size_spin.stepBy(1))
        
        self._font_size_down = QToolButton()
        self._font_size_down.setObjectName("fontSizeBtn")
        self._font_size_down.setText("▾")
        self._font_size_down.setFixedSize(14, 10)
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
        btn.setFixedSize(26, 26)
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
        
        bg = self.get_style_color(
            theme, 'textedit.background', QColor(255, 255, 255)
        )
        toolbar_bg = self.get_style_color(
            theme, 'textedit.toolbar.background', QColor(248, 248, 248)
        )
        border = self.get_style_color(
            theme, 'input.border.normal', QColor(220, 220, 220)
        )
        text = self.get_style_color(
            theme, 'textedit.toolbar.text', QColor(51, 51, 51)
        )
        hover = self.get_style_color(
            theme, 'textedit.toolbar.hover', QColor(230, 230, 230)
        )
        pressed = self.get_style_color(
            theme, 'textedit.toolbar.pressed', QColor(210, 210, 210)
        )
        checked = self.get_style_color(
            theme, 'textedit.toolbar.checked', QColor(200, 220, 240)
        )
        accent = self.get_style_color(
            theme, 'primary.main', QColor(52, 152, 219)
        )
        
        style = f"""
            QWidget#formatToolbar {{
                background-color: {toolbar_bg.name()};
                border: none;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: {text.name()};
                font-size: 12px;
                font-weight: normal;
            }}
            QToolButton:hover {{
                background-color: {hover.name()};
            }}
            QToolButton:pressed {{
                background-color: {pressed.name()};
            }}
            QToolButton:checked {{
                background-color: {checked.name()};
                color: {accent.name()};
            }}
            
            QSpinBox {{
                background-color: {bg.name()};
                border: 1px solid {border.name()};
                border-radius: 4px;
                padding: 2px 4px;
                color: {text.name()};
                font-size: 11px;
                min-height: 20px;
            }}
            QSpinBox:hover {{
                border-color: {hover.name()};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0;
                border: none;
                background: transparent;
            }}
            
            QToolButton#fontSizeBtn {{
                background-color: {bg.name()};
                border: none;
                color: {text.name()};
                font-size: 10px;
            }}
            QToolButton#fontSizeBtn:hover {{
                background-color: {hover.name()};
            }}
            
            ToolbarSeparator, QFrame#toolbarSeparator {{
                background-color: {border.name()};
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
        
        self._toolbar = FormatToolbar(self._text_edit)
        
        layout.addWidget(self._toolbar)
        layout.addWidget(self._text_edit, 1)
        
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def _connect_signals(self):
        self._text_edit.format_changed.connect(self.format_changed.emit)
        self._text_edit.text_changed.connect(self.text_changed.emit)
        self._text_edit.cursor_position_changed.connect(self.cursor_position_changed.emit)
    
    def _update_border_style(self):
        if not self._current_theme:
            return
        
        border = self.get_style_color(
            self._current_theme, 'textedit.toolbar.border', QColor(235, 235, 235)
        )
        toolbar_bg = self.get_style_color(
            self._current_theme, 'textedit.toolbar.background', QColor(250, 250, 250)
        )
        
        style = f"""
            QFrame#textEditWithToolbar {{
                background-color: {toolbar_bg.name()};
                border: 1px solid {border.name()};
                border-radius: 6px;
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
        
        bg = self.get_style_color(
            theme, 'textedit.background', QColor(255, 255, 255)
        )
        text_color = self.get_style_color(
            theme, 'input.text.normal', QColor(51, 51, 51)
        )
        separator_color = self.get_style_color(
            theme, 'textedit.toolbar.border', QColor(235, 235, 235)
        )
        border_focus = self.get_style_color(
            theme, 'input.border.focus', QColor(52, 152, 219)
        )
        
        text_edit_style = f"""
            TextEdit {{
                background-color: {bg.name()};
                color: {text_color.name()};
                border: none;
                border-top: 1px solid {separator_color.name()};
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                padding: 0px;
            }}
            TextEdit:disabled {{
                background-color: {bg.name()};
                border: none;
                border-top: 1px solid {separator_color.name()};
            }}
            TextEdit::selection {{
                background-color: {border_focus.name()};
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
