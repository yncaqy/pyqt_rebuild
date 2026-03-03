"""
下拉颜色选择器组件

提供现代 Fluent Design 风格的下拉颜色选择器，具有以下特性：
- 点击按钮显示颜色选择面板
- HSV颜色选择器（饱和度/明度方块 + 色相滑块）
- HEX和RGB颜色值输入
- 最近使用颜色历史记录
- 平滑的下拉/收起动画
- 主题集成
- 颜色选择信号

使用方式:
    picker = DropDownColorPicker()
    picker.setCurrentColor(QColor(255, 0, 0))
    picker.colorChanged.connect(lambda c: print(f"选中颜色: {c.name()}"))
"""

import logging
import time
from typing import Optional, List, Dict
from PyQt6.QtCore import (
    Qt, QSize, QPoint, QRect, QRectF, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QEvent
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QIcon,
    QPaintEvent, QMouseEvent, QLinearGradient, QCursor
)
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QGraphicsOpacityEffect,
    QLabel, QLineEdit, QApplication
)

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


def safe_hsv_color(h: int, s: int, v: int, a: int = 255) -> QColor:
    """安全创建 HSV 颜色，确保参数在有效范围内。"""
    h = max(0, min(359, int(h)))
    s = max(0, min(255, int(s)))
    v = max(0, min(255, int(v)))
    a = max(0, min(255, int(a)))
    return QColor.fromHsv(h, s, v, a)


class ColorPickerConfig:
    """下拉颜色选择器配置常量。"""

    DEFAULT_BUTTON_WIDTH = 120
    DEFAULT_BUTTON_HEIGHT = 32
    DEFAULT_BUTTON_BORDER_RADIUS = 6

    PICKER_SIZE = 180
    HUE_SLIDER_WIDTH = 20

    PANEL_BORDER_RADIUS = 8
    PANEL_PADDING = 16
    PANEL_MARGIN = 4

    ANIMATION_DURATION = 150

    MAX_HISTORY_COLORS = 16
    MAX_STYLESHEET_CACHE_SIZE = 100


class ColorPickerWidget(QWidget):
    """
    颜色选择器控件。

    功能特性:
    - 饱和度/明度选择方块
    - 实时颜色更新
    """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent: Optional[QWidget] = None, size: int = 180):
        super().__init__(parent)

        self._color = QColor(255, 0, 0)
        self._hue = 0
        self._pressed = False
        self._picker_size = size

        self.setFixedSize(size, size)
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

    def set_hue(self, hue: int) -> None:
        self._hue = max(0, min(359, hue))
        self._color = safe_hsv_color(self._hue, self._saturation, self._value)
        self.update()
        self.colorChanged.emit(self._color)

    def _hsv_to_pos(self, s: int, v: int) -> tuple:
        size = self._picker_size - 10
        x = int(s / 255.0 * size) + 5
        y = int((255 - v) / 255.0 * size) + 5
        return x, y

    def _pos_to_hsv(self, x: int, y: int) -> tuple:
        size = self._picker_size - 10
        if size <= 0:
            return 0, 0
        x = max(5, min(self._picker_size - 5, x))
        y = max(5, min(self._picker_size - 5, y))
        s = int(max(0, min(255, (x - 5) / size * 255)))
        v = int(max(0, min(255, 255 - (y - 5) / size * 255)))
        return s, v

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = self._picker_size - 10
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._update_color(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pressed:
            self._update_color(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False

    def _update_color(self, pos: QPoint) -> None:
        s, v = self._pos_to_hsv(pos.x(), pos.y())
        self._color = safe_hsv_color(self._hue, s, v)
        self.update()
        self.colorChanged.emit(self._color)


class HueSliderWidget(QWidget):
    """垂直色相滑块控件。"""

    hueChanged = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None, height: int = 180):
        super().__init__(parent)

        self._hue = 0
        self._pressed = False
        self._slider_height = height

        self.setFixedWidth(ColorPickerConfig.HUE_SLIDER_WIDTH + 10)
        self.setFixedHeight(height)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def get_hue(self) -> int:
        return self._hue

    def set_hue(self, hue: int) -> None:
        hue = max(0, min(359, hue))
        self._hue = hue
        self.update()
        self.hueChanged.emit(self._hue)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = ColorPickerConfig.HUE_SLIDER_WIDTH
        height = self._slider_height - 10

        rect = QRect(5, 5, width, height)

        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        for i in range(13):
            hue = min(359, int(i * 30))
            color = safe_hsv_color(hue, 255, 255)
            gradient.setColorAt(i / 12.0, color)

        painter.fillRect(rect, gradient)

        y = int((359 - self._hue) / 359.0 * height) + 5

        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawLine(0, y, rect.left() - 2, y)
        painter.drawLine(rect.right() + 2, y, self.width(), y)

        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawLine(0, y, rect.left() - 2, y)
        painter.drawLine(rect.right() + 2, y, self.width(), y)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._update_hue(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pressed:
            self._update_hue(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False

    def _update_hue(self, pos: QPoint) -> None:
        height = self._slider_height - 10
        if height <= 0:
            return
        y = max(5, min(self._slider_height - 5, pos.y()))
        hue = int(359 - (y - 5) / height * 359)
        self.set_hue(max(0, min(359, hue)))


class ColorHistoryWidget(QWidget):
    """
    颜色历史记录控件。

    功能特性:
    - 显示最近使用的颜色
    - 点击选择颜色
    """

    colorClicked = pyqtSignal(QColor)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._colors: List[QColor] = []
        self._hovered_index = -1

        self.setMouseTracking(True)
        self.setFixedHeight(30)

    def setColors(self, colors: List[QColor]) -> None:
        self._colors = colors[:ColorPickerConfig.MAX_HISTORY_COLORS]
        self.update()

    def colors(self) -> List[QColor]:
        return self._colors.copy()

    def addColor(self, color: QColor) -> None:
        if color in self._colors:
            self._colors.remove(color)
        self._colors.insert(0, color)
        if len(self._colors) > ColorPickerConfig.MAX_HISTORY_COLORS:
            self._colors = self._colors[:ColorPickerConfig.MAX_HISTORY_COLORS]
        self.update()

    def clearColors(self) -> None:
        self._colors.clear()
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(len(self._colors) * 26 + 10, 30)

    def paintEvent(self, event: QPaintEvent) -> None:
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
                painter.setPen(QPen(QColor(52, 152, 219), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(x, y, size, size, 3, 3)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
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

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered_index = -1
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            index = (x - 5) // 26
            if 0 <= index < len(self._colors):
                self.colorClicked.emit(self._colors[index])


class ColorInputWidget(QWidget):
    """
    颜色值输入控件。

    功能特性:
    - HEX颜色值输入
    - RGB颜色值输入
    """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._color = QColor(255, 255, 255)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._hex_label = QLabel("HEX")
        layout.addWidget(self._hex_label)

        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#RRGGBB")
        self._hex_input.setMaxLength(7)
        self._hex_input.setFixedWidth(80)
        self._hex_input.textChanged.connect(self._on_hex_changed)
        layout.addWidget(self._hex_input)

        layout.addSpacing(10)

        self._mode_label = QLabel("RGB")
        layout.addWidget(self._mode_label)

        self._r_spin = self._create_spin_box()
        self._g_spin = self._create_spin_box()
        self._b_spin = self._create_spin_box()

        layout.addWidget(self._r_spin)
        layout.addWidget(QLabel("R"))
        layout.addWidget(self._g_spin)
        layout.addWidget(QLabel("G"))
        layout.addWidget(self._b_spin)
        layout.addWidget(QLabel("B"))

        layout.addStretch()

        self._r_spin.textChanged.connect(self._on_rgb_changed)
        self._g_spin.textChanged.connect(self._on_rgb_changed)
        self._b_spin.textChanged.connect(self._on_rgb_changed)

    def _create_spin_box(self) -> QLineEdit:
        spin = QLineEdit()
        spin.setFixedWidth(40)
        spin.setMaxLength(3)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setText("0")
        return spin

    def set_color(self, color: QColor) -> None:
        self._color = color

        self._hex_input.blockSignals(True)
        self._hex_input.setText(color.name().upper())
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

    def get_color(self) -> QColor:
        return QColor(self._color)

    def _on_hex_changed(self, text: str) -> None:
        if len(text) == 7 and text.startswith('#'):
            color = QColor(text)
            if color.isValid():
                self._color = color
                self._update_rgb_display()
                self.colorChanged.emit(color)

    def _on_rgb_changed(self) -> None:
        try:
            r = int(self._r_spin.text()) if self._r_spin.text() else 0
            g = int(self._g_spin.text()) if self._g_spin.text() else 0
            b = int(self._b_spin.text()) if self._b_spin.text() else 0

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            self._color = QColor(r, g, b)
            self._update_hex_display()
            self.colorChanged.emit(self._color)
        except ValueError:
            pass

    def _update_rgb_display(self) -> None:
        self._r_spin.blockSignals(True)
        self._g_spin.blockSignals(True)
        self._b_spin.blockSignals(True)
        self._r_spin.setText(str(self._color.red()))
        self._g_spin.setText(str(self._color.green()))
        self._b_spin.setText(str(self._color.blue()))
        self._r_spin.blockSignals(False)
        self._g_spin.blockSignals(False)
        self._b_spin.blockSignals(False)

    def _update_hex_display(self) -> None:
        self._hex_input.blockSignals(True)
        self._hex_input.setText(self._color.name().upper())
        self._hex_input.blockSignals(False)

    def apply_theme(self, text_color: QColor, bg_color: QColor, border_color: QColor) -> None:
        self._hex_label.setStyleSheet(f"color: {text_color.name()};")
        self._mode_label.setStyleSheet(f"color: {text_color.name()};")

        input_style = f"""
            QLineEdit {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                padding: 4px;
            }}
        """
        self._hex_input.setStyleSheet(input_style)
        self._r_spin.setStyleSheet(input_style)
        self._g_spin.setStyleSheet(input_style)
        self._b_spin.setStyleSheet(input_style)


class ColorPickerPanel(QWidget):
    """
    颜色选择面板。

    功能特性:
    - HSV颜色选择器
    - 色相滑块
    - 颜色值输入
    - 颜色历史记录
    - 颜色预览
    """

    colorClicked = pyqtSignal(QColor)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        picker_size: int = 180
    ):
        super().__init__(parent)

        self._picker_size = picker_size
        self._current_color: Optional[QColor] = None
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None
        self._show_animation: Optional[QPropertyAnimation] = None
        self._hide_animation: Optional[QPropertyAnimation] = None

        self.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(
            ColorPickerConfig.PANEL_PADDING,
            ColorPickerConfig.PANEL_PADDING,
            ColorPickerConfig.PANEL_PADDING,
            ColorPickerConfig.PANEL_PADDING
        )
        self._main_layout.setSpacing(16)

        self._container = QWidget()
        self._container.setObjectName("colorPickerContainer")

        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(16)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        self._color_picker = ColorPickerWidget(self, self._picker_size)
        self._color_picker.colorChanged.connect(self._on_picker_color_changed)
        top_layout.addWidget(self._color_picker)

        self._hue_slider = HueSliderWidget(self, self._picker_size)
        self._hue_slider.hueChanged.connect(self._on_hue_changed)
        top_layout.addWidget(self._hue_slider)

        self._color_preview = QWidget()
        self._color_preview.setFixedSize(60, self._picker_size)
        self._color_preview.setStyleSheet("background-color: #FF5722; border-radius: 6px;")
        top_layout.addWidget(self._color_preview)

        container_layout.addLayout(top_layout)

        self._color_input = ColorInputWidget()
        self._color_input.colorChanged.connect(self._on_input_color_changed)
        container_layout.addWidget(self._color_input)

        history_section = QVBoxLayout()
        history_section.setSpacing(8)

        history_label = QLabel("最近使用")
        history_label.setObjectName("historyLabel")
        history_section.addWidget(history_label)

        self._history_widget = ColorHistoryWidget()
        self._history_widget.colorClicked.connect(self._on_history_color_clicked)
        history_section.addWidget(self._history_widget)

        container_layout.addLayout(history_section)

        self._main_layout.addWidget(self._container)

        self._adjust_size()

    def _adjust_size(self) -> None:
        width = self._picker_size + ColorPickerConfig.HUE_SLIDER_WIDTH + 60 + 36 + 24
        width += ColorPickerConfig.PANEL_PADDING * 2

        height = self._picker_size + 120
        height += ColorPickerConfig.PANEL_PADDING * 2

        self.setFixedSize(width, height)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        bg_color = theme.get_color('menu.background', QColor(45, 45, 45))
        border_color = theme.get_color('menu.border', QColor(60, 60, 60))
        text_color = theme.get_color('label.text.normal', QColor(200, 200, 200))
        input_bg = theme.get_color('input.background.normal', QColor(60, 60, 60))
        border_radius = ColorPickerConfig.PANEL_BORDER_RADIUS

        self._container.setStyleSheet(f"""
            #colorPickerContainer {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {border_radius}px;
            }}
        """)

        self._color_input.apply_theme(text_color, input_bg, border_color)

        history_label = self.findChild(QLabel, "historyLabel")
        if history_label:
            history_label.setStyleSheet(f"color: {text_color.name()};")

    def _on_picker_color_changed(self, color: QColor) -> None:
        self._current_color = color
        self._color_input.set_color(color)
        self._update_preview(color)
        self.colorClicked.emit(color)

    def _on_hue_changed(self, hue: int) -> None:
        self._color_picker.set_hue(hue)

    def _on_input_color_changed(self, color: QColor) -> None:
        self._current_color = color

        self._color_picker.blockSignals(True)
        self._color_picker.set_color(color)
        self._color_picker.blockSignals(False)

        self._update_preview(color)

        hue = color.hue()
        if hue >= 0:
            self._hue_slider.blockSignals(True)
            self._hue_slider.set_hue(hue)
            self._hue_slider.blockSignals(False)

        self.colorClicked.emit(color)

    def _on_history_color_clicked(self, color: QColor) -> None:
        self.setCurrentColor(color)
        self.colorClicked.emit(color)

    def _update_preview(self, color: QColor) -> None:
        self._color_preview.setStyleSheet(f"background-color: {color.name()}; border-radius: 6px;")

    def setCurrentColor(self, color: QColor) -> None:
        self._current_color = color

        self._color_picker.blockSignals(True)
        self._color_picker.set_color(color)
        self._color_picker.blockSignals(False)

        hue = color.hue()
        if hue >= 0:
            self._hue_slider.blockSignals(True)
            self._hue_slider.set_hue(hue)
            self._hue_slider.blockSignals(False)

        self._color_input.set_color(color)
        self._update_preview(color)

    def currentColor(self) -> Optional[QColor]:
        return QColor(self._current_color) if self._current_color else None

    def addHistoryColor(self, color: QColor) -> None:
        self._history_widget.addColor(color)

    def getHistoryColors(self) -> List[QColor]:
        return self._history_widget.colors()

    def clearHistory(self) -> None:
        self._history_widget.clearColors()

    def show_panel(self, pos: QPoint) -> None:
        self.move(pos)
        self.show()
        self._animate_show()

    def hide_panel(self) -> None:
        self._animate_hide()

    def _animate_show(self) -> None:
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        self._show_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._show_animation.setDuration(ColorPickerConfig.ANIMATION_DURATION)
        self._show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._show_animation.setStartValue(0.0)
        self._show_animation.setEndValue(1.0)
        self._show_animation.start()

    def _animate_hide(self) -> None:
        if self._opacity_effect:
            self._hide_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
            self._hide_animation.setDuration(ColorPickerConfig.ANIMATION_DURATION)
            self._hide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._hide_animation.setStartValue(1.0)
            self._hide_animation.setEndValue(0.0)
            self._hide_animation.finished.connect(self.hide)
            self._hide_animation.start()
        else:
            self.hide()

    def cleanup(self) -> None:
        if self._show_animation:
            self._show_animation.stop()
            self._show_animation.deleteLater()
            self._show_animation = None

        if self._hide_animation:
            self._hide_animation.stop()
            self._hide_animation.deleteLater()
            self._hide_animation = None

        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class DropDownColorPicker(QPushButton, StyleOverrideMixin):
    """
    下拉颜色选择器组件。

    功能特性:
    - 点击按钮显示颜色选择面板
    - HSV颜色选择器
    - RGB/HSV模式切换
    - HEX和RGB颜色值输入
    - 最近使用颜色历史记录
    - 平滑的下拉/收起动画
    - 主题集成
    - 颜色选择信号

    信号:
        colorChanged: 颜色改变时发出
        currentColorChanged: 当前颜色改变时发出

    示例:
        picker = DropDownColorPicker()
        picker.setCurrentColor(QColor(255, 0, 0))
        picker.colorChanged.connect(lambda c: print(f"选中颜色: {c.name()}"))
    """

    colorChanged = pyqtSignal(QColor)
    currentColorChanged = pyqtSignal(QColor)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        picker_size: int = 180
    ):
        super().__init__(parent)

        self._init_style_override()

        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
        self.setFixedHeight(ColorPickerConfig.DEFAULT_BUTTON_HEIGHT)
        self.setMinimumWidth(ColorPickerConfig.DEFAULT_BUTTON_WIDTH)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self._picker_size = picker_size
        self._current_color: Optional[QColor] = None
        self._panel: Optional[ColorPickerPanel] = None
        self._arrow_icon: Optional[QIcon] = None
        self._is_panel_visible = False

        self._stylesheet_cache: Dict[str, str] = {}

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug("DropDownColorPicker 初始化完成")

    def sizeHint(self) -> QSize:
        return QSize(ColorPickerConfig.DEFAULT_BUTTON_WIDTH, ColorPickerConfig.DEFAULT_BUTTON_HEIGHT)

    def _on_clicked(self) -> None:
        if self._is_panel_visible:
            self._hide_panel()
        else:
            self._show_panel()

    def _show_panel(self) -> None:
        if not self._panel:
            self._panel = ColorPickerPanel(self, self._picker_size)
            self._panel.colorClicked.connect(self._on_color_selected)

        if self._current_color:
            self._panel.setCurrentColor(self._current_color)

        panel_size = self._panel.size()
        screen = QApplication.screenAt(self.mapToGlobal(QPoint(0, 0)))
        if not screen:
            screen = QApplication.primaryScreen()

        screen_rect = screen.availableGeometry()
        button_global_pos = self.mapToGlobal(QPoint(0, 0))

        if button_global_pos.y() + self.height() + ColorPickerConfig.PANEL_MARGIN + panel_size.height() <= screen_rect.bottom():
            global_pos = self.mapToGlobal(QPoint(0, self.height() + ColorPickerConfig.PANEL_MARGIN))
        else:
            global_pos = self.mapToGlobal(QPoint(0, -panel_size.height() - ColorPickerConfig.PANEL_MARGIN))

        if global_pos.x() + panel_size.width() > screen_rect.right():
            global_pos.setX(screen_rect.right() - panel_size.width() - 5)
        if global_pos.x() < screen_rect.left():
            global_pos.setX(screen_rect.left() + 5)

        self._panel.show_panel(global_pos)
        self._is_panel_visible = True

    def _hide_panel(self) -> None:
        if self._panel:
            self._panel.hide_panel()
        self._is_panel_visible = False

    def _on_color_selected(self, color: QColor) -> None:
        self.setCurrentColor(color)
        if self._panel:
            self._panel.addHistoryColor(color)

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 DropDownColorPicker 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        start_time = time.time()

        if not theme:
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')

        if theme_name in self._stylesheet_cache:
            qss = self._stylesheet_cache[theme_name]
        else:
            qss = self._build_stylesheet(theme)
            if len(self._stylesheet_cache) < ColorPickerConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[theme_name] = qss

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        self._update_arrow_icon()

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (缓存大小: {len(self._stylesheet_cache)}, 耗时 {elapsed_time:.3f}s)")

    def _build_stylesheet(self, theme: Theme) -> str:
        bg_normal = self.get_style_color(theme, 'colorpicker.background.normal',
                                         theme.get_color('button.background.normal', QColor(58, 58, 58)))
        bg_hover = self.get_style_color(theme, 'colorpicker.background.hover',
                                        theme.get_color('button.background.hover', QColor(74, 74, 74)))
        bg_pressed = self.get_style_color(theme, 'colorpicker.background.pressed',
                                          theme.get_color('button.background.pressed', QColor(85, 85, 85)))
        bg_disabled = self.get_style_color(theme, 'colorpicker.background.disabled',
                                           theme.get_color('button.background.disabled', QColor(42, 42, 42)))

        border_normal = self.get_style_color(theme, 'colorpicker.border.normal',
                                             theme.get_color('button.border.normal', QColor(68, 68, 68)))
        border_hover = self.get_style_color(theme, 'colorpicker.border.hover',
                                            theme.get_color('button.border.hover', QColor(93, 173, 226)))
        border_pressed = self.get_style_color(theme, 'colorpicker.border.pressed',
                                              theme.get_color('button.border.pressed', QColor(52, 152, 219)))
        border_disabled = self.get_style_color(theme, 'colorpicker.border.disabled',
                                               theme.get_color('button.border.disabled', QColor(51, 51, 51)))

        border_radius = self.get_style_value(theme, 'colorpicker.border_radius',
                                             ColorPickerConfig.DEFAULT_BUTTON_BORDER_RADIUS)

        qss = f"""
        DropDownColorPicker {{
            background-color: {bg_normal.name()};
            border: 1px solid {border_normal.name()};
            border-radius: {border_radius}px;
            padding: 4px 32px 4px 4px;
            text-align: left;
        }}
        DropDownColorPicker:hover {{
            background-color: {bg_hover.name()};
            border: 1px solid {border_hover.name()};
        }}
        DropDownColorPicker:pressed {{
            background-color: {bg_pressed.name()};
            border: 1px solid {border_pressed.name()};
        }}
        DropDownColorPicker:disabled {{
            background-color: {bg_disabled.name()};
            border: 1px solid {border_disabled.name()};
        }}
        """

        return qss

    def _update_arrow_icon(self) -> None:
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color('colorpicker.arrow.normal',
                                                    self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200)))

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, 12)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color_preview_rect = QRect(6, 6, self.height() - 12, self.height() - 12)
        if self._current_color:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self._current_color))
            painter.drawRoundedRect(QRectF(color_preview_rect), 4, 4)
        else:
            painter.setPen(QPen(QColor(128, 128, 128), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(color_preview_rect), 4, 4)

            painter.setPen(QColor(128, 128, 128))
            painter.drawLine(color_preview_rect.topLeft(), color_preview_rect.bottomRight())
            painter.drawLine(color_preview_rect.topRight(), color_preview_rect.bottomLeft())

        if self._arrow_icon and not self._arrow_icon.isNull():
            arrow_size = 12
            arrow_margin = 10

            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2

            self._arrow_icon.paint(painter, x, y, arrow_size, arrow_size)

    def currentColor(self) -> Optional[QColor]:
        return QColor(self._current_color) if self._current_color else None

    def setCurrentColor(self, color: QColor) -> None:
        if self._current_color != color:
            self._current_color = QColor(color)
            self.update()
            self.colorChanged.emit(self._current_color)
            self.currentColorChanged.emit(self._current_color)
            logger.debug(f"颜色已设置: {color.name()}")

    def showPanel(self) -> None:
        self._show_panel()

    def hidePanel(self) -> None:
        self._hide_panel()

    def isPanelVisible(self) -> bool:
        return self._is_panel_visible

    def getHistoryColors(self) -> List[QColor]:
        if self._panel:
            return self._panel.getHistoryColors()
        return []

    def clearHistory(self) -> None:
        if self._panel:
            self._panel.clearHistory()

    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

        if self._panel:
            self._panel.cleanup()
            self._panel.deleteLater()
            self._panel = None

        self._stylesheet_cache.clear()
        self.clear_overrides()

    def __del__(self) -> None:
        try:
            self.cleanup()
        except Exception:
            pass
