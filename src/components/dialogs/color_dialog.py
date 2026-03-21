"""
Color Dialog Component

Provides a modern color picker dialog with Fluent-style design.

Features:
- Color wheel/square picker for intuitive color selection
- Hue, Saturation, Value sliders
- RGB and HEX input fields
- Preset color palette
- Color preview with before/after comparison
- colorChanged signal for real-time updates
- Theme integration
- Smooth animations
"""

import logging
from typing import Optional, Tuple
from PyQt6.QtCore import (
    Qt, QRect, QSize, QPoint,
    pyqtSignal, QPropertyAnimation, QEasingCurve,
    QTimer, QEventLoop
)
from PyQt6.QtGui import (
    QColor, QPainter, QBrush, QPen, QFont,
    QLinearGradient, QCursor
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGraphicsOpacityEffect
)
from core.theme_manager import ThemeManager, Theme
from core.font_manager import FontManager
from components.dialogs.message_box import MaskWidget
from components.inputs.modern_line_edit import ModernLineEdit
from components.buttons.custom_push_button import CustomPushButton

logger = logging.getLogger(__name__)


def safe_hsv_color(h: int, s: int, v: int, a: int = 255) -> QColor:
    """安全创建 HSV 颜色，确保参数在有效范围内。"""
    h = max(0, min(359, int(h)))
    s = max(0, min(255, int(s)))
    v = max(0, min(255, int(v)))
    a = max(0, min(255, int(a)))
    return QColor.fromHsv(h, s, v, a)


class ColorPickerConfig:
    """Configuration constants for color picker."""
    
    PICKER_SIZE = 200
    HUE_SLIDER_WIDTH = 20
    PREVIEW_SIZE = 60
    PRESET_COLORS = [
        "#E81123", "#FF8C00", "#FFF100", "#107C10",
        "#00BCF2", "#0078D4", "#5C2D91", "#C30052",
        "#D13438", "#FFB900", "#00CC6A", "#00B7C3",
        "#8764B8", "#E74856", "#FF6B6B", "#4ECDC4",
        "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD",
        "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    ]


class ColorPickerWidget(QWidget):
    """
    Color picker widget with saturation-value square and hue slider.
    
    Allows intuitive color selection through:
    - A square picker for saturation and value
    - A vertical slider for hue
    """
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._color = QColor(255, 0, 0)
        self._hue = 0
        self._pressed = False
        
        self.setFixedSize(ColorPickerConfig.PICKER_SIZE, ColorPickerConfig.PICKER_SIZE)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
    @property
    def _saturation(self) -> int:
        return self._color.saturation()
    
    @property  
    def _value(self) -> int:
        return self._color.value()
    
    def get_color(self) -> QColor:
        return QColor(self._color)
    
    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        hue = color.hue()
        if hue >= 0:
            self._hue = max(0, min(359, hue))
        self.update()
        self.colorChanged.emit(self._color)
    
    def _hsv_to_pos(self, s: int, v: int) -> Tuple[int, int]:
        size = ColorPickerConfig.PICKER_SIZE - 10
        x = int(s / 255.0 * size) + 5
        y = int((255 - v) / 255.0 * size) + 5
        return x, y
    
    def _pos_to_hsv(self, x: int, y: int) -> Tuple[int, int]:
        size = ColorPickerConfig.PICKER_SIZE - 10
        s = max(0, min(255, int((x - 5) / size * 255)))
        v = max(0, min(255, int(255 - (y - 5) / size * 255)))
        return s, v
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        size = ColorPickerConfig.PICKER_SIZE - 10
        rect = QRect(5, 5, size, size)
        
        hue = max(0, min(359, self._hue))
        hue_color = safe_hsv_color(hue, 255, 255)
        
        gradient_h = QLinearGradient(rect.left(), 0, rect.right(), 0)
        gradient_h.setColorAt(0, QColor(255, 255, 255))
        gradient_h.setColorAt(1, hue_color)
        
        gradient_v = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient_v.setColorAt(0, QColor(0, 0, 0, 0))
        gradient_v.setColorAt(1, QColor(0, 0, 0, 255))
        
        painter.fillRect(rect, gradient_h)
        painter.fillRect(rect, gradient_v)
        
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        
        x, y = self._hsv_to_pos(self._saturation, self._value)
        painter.drawEllipse(QPoint(x, y), 6, 6)
        
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(x, y), 7, 7)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._update_color(event.pos())
    
    def mouseMoveEvent(self, event) -> None:
        if self._pressed:
            self._update_color(event.pos())
    
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
    
    def _update_color(self, pos: QPoint) -> None:
        s, v = self._pos_to_hsv(pos.x(), pos.y())
        self._color = safe_hsv_color(self._hue, s, v)
        self.update()
        self.colorChanged.emit(self._color)


class HueSlider(QWidget):
    """Vertical hue slider widget."""
    
    hueChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._hue = 0
        self._pressed = False
        
        self.setFixedWidth(ColorPickerConfig.HUE_SLIDER_WIDTH + 10)
        self.setFixedHeight(ColorPickerConfig.PICKER_SIZE)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
    
    def get_hue(self) -> int:
        return self._hue
    
    def set_hue(self, hue: int) -> None:
        hue = max(0, min(359, hue))
        self._hue = hue
        self.update()
        self.hueChanged.emit(self._hue)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = ColorPickerConfig.HUE_SLIDER_WIDTH
        height = ColorPickerConfig.PICKER_SIZE - 10
        
        rect = QRect(5, 5, width, height)
        
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        for i in range(13):
            hue = min(359, int(i * 30))
            color = safe_hsv_color(hue, 255, 255)
            gradient.setColorAt(i / 12.0, color)
        
        painter.fillRect(rect, gradient)
        
        y = int((359 - self._hue) / 359.0 * height) + 5
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(0, y, rect.left() - 2, y)
        painter.drawLine(rect.right() + 2, y, self.width(), y)
        
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawLine(0, y, rect.left() - 2, y)
        painter.drawLine(rect.right() + 2, y, self.width(), y)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._update_hue(event.pos())
    
    def mouseMoveEvent(self, event) -> None:
        if self._pressed:
            self._update_hue(event.pos())
    
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
    
    def _update_hue(self, pos: QPoint) -> None:
        height = ColorPickerConfig.PICKER_SIZE - 10
        if height <= 0:
            return
        y = max(5, min(self.height() - 5, pos.y()))
        hue = int(359 - (y - 5) / height * 359)
        self.set_hue(max(0, min(359, hue)))


class ColorLineEdit(ModernLineEdit):
    """Line edit for color value input (HEX format)."""
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("", parent)
        self.setPlaceholderText("#RRGGBB")
        self.setMaxLength(7)
        self._color = QColor()
        
        self.textChanged.connect(self._on_text_changed)
    
    def set_color(self, color: QColor) -> None:
        self._color = color
        hex_color = color.name().upper()
        self.blockSignals(True)
        self.setText(hex_color)
        self.blockSignals(False)
    
    def get_color(self) -> QColor:
        return QColor(self._color)
    
    def _on_text_changed(self, text: str) -> None:
        if len(text) == 7 and text.startswith('#'):
            color = QColor(text)
            if color.isValid():
                self._color = color
                self.set_error(False)
                self.colorChanged.emit(color)
            else:
                self.set_error(True)
        elif len(text) > 0 and not text.startswith('#'):
            self.blockSignals(True)
            self.setText('#' + text.lstrip('#'))
            self.blockSignals(False)


class ColorPreviewWidget(QWidget):
    """Widget showing current and previous color side by side."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_color = QColor(255, 255, 255)
        self._previous_color = QColor(255, 255, 255)
        
        self.setFixedSize(ColorPickerConfig.PREVIEW_SIZE * 2 + 10, ColorPickerConfig.PREVIEW_SIZE)
    
    def set_current_color(self, color: QColor) -> None:
        self._current_color = color
        self.update()
    
    def set_previous_color(self, color: QColor) -> None:
        self._previous_color = color
        self.update()
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        size = ColorPickerConfig.PREVIEW_SIZE - 4
        radius = 4
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._previous_color))
        painter.drawRoundedRect(2, 2, size, size, radius, radius)
        
        painter.setBrush(QBrush(self._current_color))
        painter.drawRoundedRect(size + 8, 2, size, size, radius, radius)


class PresetColorWidget(QWidget):
    """Widget showing preset colors for quick selection."""
    
    colorClicked = pyqtSignal(QColor)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._colors = [QColor(c) for c in ColorPickerConfig.PRESET_COLORS]
        self._hovered_index = -1
        
        self.setMouseTracking(True)
        self.setFixedHeight(30)
    
    def sizeHint(self) -> QSize:
        return QSize(len(self._colors) * 26 + 10, 30)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i, color in enumerate(self._colors):
            x = 5 + i * 26
            y = 5
            size = 20
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(x, y, size, size, 3, 3)
            
            if i == self._hovered_index:
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(x, y, size, size, 3, 3)
    
    def mouseMoveEvent(self, event) -> None:
        x = event.pos().x()
        index = (x - 5) // 26
        if 0 <= index < len(self._colors):
            if self._hovered_index != index:
                self._hovered_index = index
                self.update()
        else:
            if self._hovered_index != -1:
                self._hovered_index = -1
                self.update()
    
    def leaveEvent(self, event) -> None:
        self._hovered_index = -1
        self.update()
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            index = (x - 5) // 26
            if 0 <= index < len(self._colors):
                self.colorClicked.emit(self._colors[index])


class ColorDialog(QWidget):
    """
    Modern color picker dialog with Fluent-style design.
    
    Features:
    - Color wheel/square picker for intuitive selection
    - Hue slider for quick hue adjustment
    - RGB and HEX input fields
    - Preset color palette
    - Color preview with before/after comparison
    - Real-time colorChanged signal
    - Theme integration
    
    Usage:
        dialog = ColorDialog(parent, initial_color=QColor(255, 0, 0))
        dialog.colorChanged.connect(lambda c: print(f"Color: {c.name()}"))
        result = dialog.exec()
        if result == ColorDialog.Accepted:
            final_color = dialog.get_color()
    """
    
    Accepted = 1
    Rejected = 0
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "选择颜色",
        initial_color: QColor = None
    ):
        super().__init__(parent)
        
        self._title = title
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._result = self.Rejected
        self._mask: Optional[MaskWidget] = None
        self._initial_color = initial_color if initial_color else QColor(255, 255, 255)
        self._current_color = QColor(self._initial_color)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        self._setup_animation()
        self._connect_signals()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._apply_theme()
        
        logger.debug("ColorDialog initialized")
    
    def _setup_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._content_widget = QWidget()
        self._content_widget.setObjectName("colorDialogContent")
        
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("colorDialogTitle")
        self._title_label.setFont(FontManager.get_header_font())
        content_layout.addWidget(self._title_label)
        
        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(10)
        
        self._color_picker = ColorPickerWidget()
        picker_layout.addWidget(self._color_picker)
        
        self._hue_slider = HueSlider()
        picker_layout.addWidget(self._hue_slider)
        
        picker_layout.addStretch()
        content_layout.addLayout(picker_layout)
        
        self._preset_widget = PresetColorWidget()
        content_layout.addWidget(self._preset_widget)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self._hex_label = QLabel("HEX:")
        input_layout.addWidget(self._hex_label)
        
        self._hex_input = ColorLineEdit()
        self._hex_input.setFixedWidth(100)
        input_layout.addWidget(self._hex_input)
        
        input_layout.addSpacing(20)
        
        self._rgb_label = QLabel("RGB:")
        input_layout.addWidget(self._rgb_label)
        
        self._r_spin = self._create_spin_box()
        self._g_spin = self._create_spin_box()
        self._b_spin = self._create_spin_box()
        
        input_layout.addWidget(self._r_spin)
        input_layout.addWidget(QLabel("R"))
        input_layout.addWidget(self._g_spin)
        input_layout.addWidget(QLabel("G"))
        input_layout.addWidget(self._b_spin)
        input_layout.addWidget(QLabel("B"))
        
        input_layout.addStretch()
        content_layout.addLayout(input_layout)
        
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(10)
        
        self._preview_label = QLabel("预览:")
        preview_layout.addWidget(self._preview_label)
        
        self._color_preview = ColorPreviewWidget()
        self._color_preview.set_previous_color(self._initial_color)
        preview_layout.addWidget(self._color_preview)
        
        preview_layout.addStretch()
        content_layout.addLayout(preview_layout)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self._ok_button = CustomPushButton("确定")
        self._ok_button.setFixedWidth(80)
        button_layout.addWidget(self._ok_button)
        
        self._cancel_button = CustomPushButton("取消")
        self._cancel_button.setFixedWidth(80)
        button_layout.addWidget(self._cancel_button)
        
        content_layout.addLayout(button_layout)
        
        self._main_layout.addWidget(self._content_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        self._set_color(self._initial_color)
    
    def _create_spin_box(self) -> QLineEdit:
        spin = QLineEdit()
        spin.setFixedWidth(50)
        spin.setMaxLength(3)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setText("0")
        return spin
    
    def _setup_animation(self) -> None:
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _connect_signals(self) -> None:
        self._color_picker.colorChanged.connect(self._on_picker_color_changed)
        self._hue_slider.hueChanged.connect(self._on_hue_changed)
        self._hex_input.colorChanged.connect(self._on_hex_changed)
        self._preset_widget.colorClicked.connect(self._on_preset_clicked)
        
        self._r_spin.textChanged.connect(self._on_rgb_changed)
        self._g_spin.textChanged.connect(self._on_rgb_changed)
        self._b_spin.textChanged.connect(self._on_rgb_changed)
        
        self._ok_button.clicked.connect(self._on_ok)
        self._cancel_button.clicked.connect(self._on_cancel)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._apply_theme()
        self._refresh_color_display()
    
    def _apply_theme(self) -> None:
        if not self._theme:
            return
        
        bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
        text_color = self._theme.get_color('label.text.title', QColor(255, 255, 255))
        border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        input_bg = self._theme.get_color('input.background.normal', QColor(60, 60, 60))
        
        self._content_widget.setStyleSheet(f"""
            #colorDialogContent {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 8px;
            }}
            #colorDialogTitle {{
                color: {text_color.name()};
            }}
            QLabel {{
                color: {text_color.name()};
            }}
            QLineEdit {{
                background-color: {input_bg.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
    
    def _refresh_color_display(self) -> None:
        self._set_color(self._current_color)
    
    def _set_color(self, color: QColor) -> None:
        self._current_color = color
        
        self._color_picker.blockSignals(True)
        self._color_picker.set_color(color)
        self._color_picker.blockSignals(False)
        
        hue = color.hue()
        if hue >= 0:
            self._hue_slider.blockSignals(True)
            self._hue_slider.set_hue(hue)
            self._hue_slider.blockSignals(False)
        
        self._hex_input.blockSignals(True)
        self._hex_input.set_color(color)
        self._hex_input.blockSignals(False)
        
        self._r_spin.blockSignals(True)
        self._g_spin.blockSignals(True)
        self._b_spin.blockSignals(True)
        self._r_spin.setText(str(color.red()))
        self._g_spin.setText(str(color.green()))
        self._b_spin.setText(str(color.blue()))
        self._r_spin.blockSignals(False)
        self._g_spin.blockSignals(False)
        self._b_spin.blockSignals(False)
        
        self._color_preview.set_current_color(color)
    
    def _on_picker_color_changed(self, color: QColor) -> None:
        self._current_color = color
        
        hue = color.hue()
        if hue >= 0:
            self._hue_slider.blockSignals(True)
            self._hue_slider.set_hue(hue)
            self._hue_slider.blockSignals(False)
        
        self._hex_input.set_color(color)
        self._update_rgb_spins(color)
        self._color_preview.set_current_color(color)
        self.colorChanged.emit(color)
    
    def _on_hue_changed(self, hue: int) -> None:
        color = safe_hsv_color(hue, self._current_color.saturation(), self._current_color.value())
        self._set_color(color)
        self.colorChanged.emit(color)
    
    def _on_hex_changed(self, color: QColor) -> None:
        self._set_color(color)
        self.colorChanged.emit(color)
    
    def _on_preset_clicked(self, color: QColor) -> None:
        self._set_color(color)
        self.colorChanged.emit(color)
    
    def _on_rgb_changed(self) -> None:
        try:
            r = int(self._r_spin.text()) if self._r_spin.text() else 0
            g = int(self._g_spin.text()) if self._g_spin.text() else 0
            b = int(self._b_spin.text()) if self._b_spin.text() else 0
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            color = QColor(r, g, b)
            self._set_color(color)
            self.colorChanged.emit(color)
        except ValueError:
            pass
    
    def _update_rgb_spins(self, color: QColor) -> None:
        self._r_spin.blockSignals(True)
        self._g_spin.blockSignals(True)
        self._b_spin.blockSignals(True)
        self._r_spin.setText(str(color.red()))
        self._g_spin.setText(str(color.green()))
        self._b_spin.setText(str(color.blue()))
        self._r_spin.blockSignals(False)
        self._g_spin.blockSignals(False)
        self._b_spin.blockSignals(False)
    
    def _on_ok(self) -> None:
        self._result = self.Accepted
        self.hide()
    
    def _on_cancel(self) -> None:
        self._result = self.Rejected
        self._current_color = QColor(self._initial_color)
        self.hide()
    
    def fade_in(self) -> None:
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
        if self._mask:
            self._mask.fade_in()
    
    def fade_out(self) -> None:
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()
        if self._mask:
            self._mask.fade_out()
    
    def exec(self) -> int:
        parent = self.parent()
        if parent:
            self._mask = MaskWidget(parent)
            self._mask.resize(parent.size())
            self._mask.show()
            self._mask.fade_in()
        
        self.adjustSize()
        
        if parent:
            parent_rect = parent.rect()
            global_center = parent.mapToGlobal(parent_rect.center())
            self.move(
                global_center.x() - self.width() // 2,
                global_center.y() - self.height() // 2
            )
        
        self.show()
        self.fade_in()
        
        self._event_loop = QEventLoop()
        self._event_loop.exec()
        
        return self._result
    
    def hide(self) -> None:
        self.fade_out()
        if self._mask:
            self._mask.fade_out()
        
        QTimer.singleShot(150, self._close_all)
    
    def _close_all(self) -> None:
        if self._mask:
            self._mask.hide()
            self._mask.deleteLater()
            self._mask = None
        
        super().hide()
        
        if hasattr(self, '_event_loop') and self._event_loop:
            self._event_loop.quit()
    
    def get_color(self) -> QColor:
        return QColor(self._current_color)
    
    def set_initial_color(self, color: QColor) -> None:
        self._initial_color = QColor(color)
        self._color_preview.set_previous_color(color)
        self._set_color(color)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("ColorDialog cleaned up")
    
    @staticmethod
    def get_color_static(
        parent: Optional[QWidget] = None,
        title: str = "选择颜色",
        initial_color: QColor = None
    ) -> Tuple[int, QColor]:
        """
        Static method to show color dialog and get selected color.
        
        Args:
            parent: Parent widget
            title: Dialog title
            initial_color: Initial color to show
            
        Returns:
            Tuple of (result, color) where result is Accepted or Rejected
        """
        dialog = ColorDialog(parent, title, initial_color)
        result = dialog.exec()
        color = dialog.get_color()
        dialog.cleanup()
        dialog.deleteLater()
        return result, color
