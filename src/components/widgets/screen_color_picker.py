"""
屏幕颜色拾取器组件

提供现代 Fluent Design 风格的屏幕颜色拾取器，具有以下特性：
- 点击按钮进入拾取模式
- 放大镜效果显示拾取区域
- 实时颜色预览
- 多种颜色格式显示（RGB、HEX、HSV）
- 颜色历史记录
- 一键复制颜色值
- 主题集成
- 自动资源清理

使用方式:
    picker = ScreenColorPicker()
    picker.colorPicked.connect(lambda c: print(f"拾取颜色: {c.name()}"))
"""

import logging
from typing import Optional, List
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF,
    pyqtSignal, QEvent, QTimer
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont,
    QPaintEvent, QMouseEvent, QCursor,
    QScreen, QPixmap, QGuiApplication
)
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QLabel, QApplication
)

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class ScreenColorPickerConfig:
    """屏幕颜色拾取器配置常量。"""

    DEFAULT_BUTTON_WIDTH = 120
    DEFAULT_BUTTON_HEIGHT = 32
    DEFAULT_BUTTON_BORDER_RADIUS = 6
    MAGNIFIER_SIZE = 150
    MAGNIFIER_ZOOM = 8
    MAGNIFIER_BORDER_RADIUS = 8
    PANEL_WIDTH = 280
    PANEL_HEIGHT = 200
    PANEL_BORDER_RADIUS = 8
    PANEL_PADDING = 12
    ANIMATION_DURATION = 150
    MAX_HISTORY_COLORS = 16
    DEFAULT_COLOR = '#5dade2'


class ColorPickerOverlay(QWidget):
    """
    透明全屏覆盖窗口 - 用于捕获窗口外的鼠标事件。
    """

    colorPicked = pyqtSignal(QColor)
    cancelled = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        self.setMouseTracking(True)

        self._current_color = QColor()
        self._screen_pixmap: Optional[QPixmap] = None
        self._zoom = ScreenColorPickerConfig.MAGNIFIER_ZOOM
        self._magnifier_size = ScreenColorPickerConfig.MAGNIFIER_SIZE

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_capture)

    def start(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen:
            virtual_geometry = screen.virtualGeometry()
            self.setGeometry(virtual_geometry)

        self._timer.start(16)
        self.show()
        self.grabMouse()
        self.setFocus()
        self.setCursor(Qt.CursorShape.CrossCursor)

    def stop(self) -> None:
        self._timer.stop()
        self.releaseMouse()
        self.hide()

    def _update_capture(self) -> None:
        cursor_pos = QCursor.pos()

        screen = QGuiApplication.screenAt(cursor_pos)
        if not screen:
            screen = QGuiApplication.primaryScreen()

        dpr = screen.devicePixelRatio()
        screen_geometry = screen.geometry()

        grab_size_logical = max(1, self._magnifier_size // self._zoom)
        half_logical = grab_size_logical // 2

        local_x = cursor_pos.x() - screen_geometry.x()
        local_y = cursor_pos.y() - screen_geometry.y()

        grab_x = local_x - half_logical
        grab_y = local_y - half_logical

        self._screen_pixmap = screen.grabWindow(0, grab_x, grab_y, grab_size_logical, grab_size_logical)

        if self._screen_pixmap:
            self._screen_pixmap.setDevicePixelRatio(dpr)

        pixel = screen.grabWindow(0, local_x, local_y, 1, 1)
        self._current_color = pixel.toImage().pixelColor(0, 0)

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        cursor_pos = self.mapFromGlobal(QCursor.pos())

        magnifier_x = cursor_pos.x() + 20
        magnifier_y = cursor_pos.y() + 20

        screen = QGuiApplication.screenAt(QCursor.pos())
        if screen:
            screen_rect = screen.availableGeometry()
            global_cursor = QCursor.pos()
            if global_cursor.x() + self._magnifier_size + 40 > screen_rect.right():
                magnifier_x = cursor_pos.x() - self._magnifier_size - 20
            if global_cursor.y() + self._magnifier_size + 100 > screen_rect.bottom():
                magnifier_y = cursor_pos.y() - self._magnifier_size - 100

        painter.setPen(QPen(QColor(30, 30, 30), 1))
        painter.setBrush(QColor(35, 35, 35, 240))
        painter.drawRoundedRect(
            QRectF(magnifier_x, magnifier_y, self._magnifier_size + 20, self._magnifier_size + 80),
            8, 8
        )

        if self._screen_pixmap and not self._screen_pixmap.isNull():
            painter.save()
            target_rect = QRectF(magnifier_x + 10, magnifier_y + 10, self._magnifier_size, self._magnifier_size)
            source_rect = QRectF(self._screen_pixmap.rect())
            painter.drawPixmap(target_rect, self._screen_pixmap, source_rect)
            painter.restore()

        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            magnifier_x + 10, magnifier_y + 10,
            self._magnifier_size, self._magnifier_size, 4, 4
        )

        center_x = magnifier_x + 10 + self._magnifier_size // 2
        center_y = magnifier_y + 10 + self._magnifier_size // 2

        painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
        painter.drawLine(center_x - 12, center_y, center_x - 4, center_y)
        painter.drawLine(center_x + 4, center_y, center_x + 12, center_y)
        painter.drawLine(center_x, center_y - 12, center_x, center_y - 4)
        painter.drawLine(center_x, center_y + 4, center_x, center_y + 12)

        painter.setPen(QPen(QColor(0, 0, 0, 220), 1))
        painter.drawLine(center_x - 11, center_y, center_x - 5, center_y)
        painter.drawLine(center_x + 5, center_y, center_x + 11, center_y)
        painter.drawLine(center_x, center_y - 11, center_x, center_y - 5)
        painter.drawLine(center_x, center_y + 5, center_x, center_y + 11)

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(
            center_x - self._zoom // 2, center_y - self._zoom // 2,
            self._zoom, self._zoom
        )

        info_y = magnifier_y + self._magnifier_size + 20

        color_preview_rect = QRectF(magnifier_x + 10, info_y, 24, 20)
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(self._current_color)
        painter.drawRoundedRect(color_preview_rect, 3, 3)

        painter.setPen(QColor(230, 230, 230))
        font = QFont("Microsoft YaHei", 9, QFont.Weight.Bold)
        painter.setFont(font)
        hex_text = self._current_color.name().upper()
        painter.drawText(
            QRectF(magnifier_x + 40, info_y - 2, 80, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            hex_text
        )

        r, g, b = self._current_color.red(), self._current_color.green(), self._current_color.blue()
        rgb_text = f"RGB({r},{g},{b})"
        painter.drawText(
            QRectF(magnifier_x + 110, info_y - 2, 100, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            rgb_text
        )

        info_y2 = info_y + 24
        h, s, v = self._current_color.hue(), self._current_color.saturation(), self._current_color.value()
        if h < 0:
            h = 0
        hsv_text = f"HSV({h}°,{s}%,{v}%)"
        painter.drawText(
            QRectF(magnifier_x + 10, info_y2 - 2, 200, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            hsv_text
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.colorPicked.emit(QColor(self._current_color))
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()

    def get_current_color(self) -> QColor:
        return QColor(self._current_color)


class ColorHistoryWidget(QWidget):
    """
    颜色历史记录控件。

    功能特性:
    - 显示最近拾取的颜色
    - 点击选择颜色
    """

    colorClicked = pyqtSignal(QColor)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._colors: List[QColor] = []
        self._hovered_index = -1

        self.setMouseTracking(True)
        self.setFixedHeight(30)

    def addColor(self, color: QColor) -> None:
        if color in self._colors:
            self._colors.remove(color)
        self._colors.insert(0, color)
        if len(self._colors) > ScreenColorPickerConfig.MAX_HISTORY_COLORS:
            self._colors = self._colors[:ScreenColorPickerConfig.MAX_HISTORY_COLORS]
        self.update()

    def colors(self) -> List[QColor]:
        return self._colors.copy()

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


class ScreenColorPickerButton(QPushButton, StyleOverrideMixin, StylesheetCacheMixin):
    """
    屏幕颜色拾取按钮。

    功能特性:
    - 点击进入拾取模式
    - 显示当前颜色预览
    - 主题集成
    - 自动资源清理
    """

    colorPicked = pyqtSignal(QColor)
    pickStarted = pyqtSignal()
    pickCancelled = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
        self.setFixedHeight(ScreenColorPickerConfig.DEFAULT_BUTTON_HEIGHT)
        self.setMinimumWidth(ScreenColorPickerConfig.DEFAULT_BUTTON_WIDTH)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._current_color: QColor = QColor(ScreenColorPickerConfig.DEFAULT_COLOR)
        self._is_picking = False
        self._overlay: Optional[ColorPickerOverlay] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug("ScreenColorPickerButton 初始化完成")

    def sizeHint(self) -> QSize:
        return QSize(
            ScreenColorPickerConfig.DEFAULT_BUTTON_WIDTH,
            ScreenColorPickerConfig.DEFAULT_BUTTON_HEIGHT
        )

    def _on_clicked(self) -> None:
        if self._is_picking:
            self._cancel_pick()
        else:
            self._start_pick()

    def _start_pick(self) -> None:
        self._is_picking = True

        self._overlay = ColorPickerOverlay()
        self._overlay.colorPicked.connect(self._on_color_picked)
        self._overlay.cancelled.connect(self._cancel_pick)
        self._overlay.start()

        self.pickStarted.emit()
        logger.debug("开始屏幕颜色拾取")

    def _on_color_picked(self, color: QColor) -> None:
        self._current_color = QColor(color)
        self.colorPicked.emit(color)
        self.update()
        self._cancel_pick()

    def _cancel_pick(self) -> None:
        self._is_picking = False

        if self._overlay:
            self._overlay.stop()
            self._overlay.deleteLater()
            self._overlay = None

        self.pickCancelled.emit()
        logger.debug("取消屏幕颜色拾取")

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 ScreenColorPickerButton 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')

        qss = self._get_cached_stylesheet(
            (theme_name,),
            lambda: self._build_stylesheet(theme)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"主题已应用: {theme_name}")

    def _build_stylesheet(self, theme: Theme) -> str:
        bg_normal = self.get_style_color(theme, 'screencolorpicker.background.normal',
                                         theme.get_color('button.background.normal', QColor(58, 58, 58)))
        bg_hover = self.get_style_color(theme, 'screencolorpicker.background.hover',
                                        theme.get_color('button.background.hover', QColor(74, 74, 74)))
        bg_pressed = self.get_style_color(theme, 'screencolorpicker.background.pressed',
                                          theme.get_color('button.background.pressed', QColor(85, 85, 85)))

        border_normal = self.get_style_color(theme, 'screencolorpicker.border.normal',
                                             theme.get_color('button.border.normal', QColor(68, 68, 68)))
        border_hover = self.get_style_color(theme, 'screencolorpicker.border.hover',
                                            theme.get_color('button.border.hover', QColor(93, 173, 226)))
        border_pressed = self.get_style_color(theme, 'screencolorpicker.border.pressed',
                                              theme.get_color('button.border.pressed', QColor(52, 152, 219)))

        border_radius = self.get_style_value(theme, 'screencolorpicker.border_radius',
                                             ScreenColorPickerConfig.DEFAULT_BUTTON_BORDER_RADIUS)

        qss = f"""
        ScreenColorPickerButton {{
            background-color: {bg_normal.name()};
            border: 1px solid {border_normal.name()};
            border-radius: {border_radius}px;
            padding: 4px 32px 4px 4px;
            text-align: left;
        }}
        ScreenColorPickerButton:hover {{
            background-color: {bg_hover.name()};
            border: 1px solid {border_hover.name()};
        }}
        ScreenColorPickerButton:pressed {{
            background-color: {bg_pressed.name()};
            border: 1px solid {border_pressed.name()};
        }}
        """

        return qss

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        color_preview_rect = QRect(6, 6, self.height() - 12, self.height() - 12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._current_color))
        painter.drawRoundedRect(QRectF(color_preview_rect), 4, 4)

        if self._current_theme:
            icon_color = self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200))
            theme_type = "dark" if self._current_theme.is_dark else "light"
            icon_name = self._icon_mgr.resolve_icon_name("Palette", theme_type)
            icon = self._icon_mgr.get_colored_icon(icon_name, icon_color, 12)

            icon_size = 12
            icon_margin = 10
            x = self.width() - icon_size - icon_margin
            y = (self.height() - icon_size) // 2
            self.draw_icon(painter, icon, x, y, icon_size)

    def currentColor(self) -> QColor:
        return QColor(self._current_color)

    def isPicking(self) -> bool:
        return self._is_picking

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

        if self._overlay:
            self._overlay.stop()
            self._overlay.deleteLater()
            self._overlay = None

        self._clear_stylesheet_cache()
        self.clear_overrides()


class ScreenColorPicker(QWidget):
    """
    屏幕颜色拾取器组件。

    功能特性:
    - 点击按钮进入拾取模式
    - 放大镜效果显示拾取区域
    - 实时颜色预览
    - 多种颜色格式显示（RGB、HEX、HSV）
    - 颜色历史记录
    - 一键复制颜色值
    - 主题集成
    - 自动资源清理

    信号:
        colorPicked: 颜色拾取完成时发出
        pickStarted: 开始拾取时发出
        pickCancelled: 取消拾取时发出
    """

    colorPicked = pyqtSignal(QColor)
    pickStarted = pyqtSignal()
    pickCancelled = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._init_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(12)

        self._pick_button = ScreenColorPickerButton()
        self._pick_button.colorPicked.connect(self._on_color_picked)
        self._pick_button.pickStarted.connect(self.pickStarted.emit)
        self._pick_button.pickCancelled.connect(self.pickCancelled.emit)
        picker_layout.addWidget(self._pick_button)

        self._current_color_preview = QWidget()
        self._current_color_preview.setFixedSize(32, 32)
        self._current_color_preview.setStyleSheet("background-color: #FFFFFF; border-radius: 4px;")
        picker_layout.addWidget(self._current_color_preview)

        self._current_color_label = QLabel("#FFFFFF")
        picker_layout.addWidget(self._current_color_label)

        picker_layout.addStretch()
        layout.addLayout(picker_layout)

        history_section = QVBoxLayout()
        history_section.setSpacing(8)

        history_label = QLabel("最近拾取")
        history_section.addWidget(history_label)

        self._history_widget = ColorHistoryWidget()
        self._history_widget.colorClicked.connect(self._on_history_color_clicked)
        history_section.addWidget(self._history_widget)

        layout.addLayout(history_section)

    def _on_color_picked(self, color: QColor) -> None:
        self._current_color_preview.setStyleSheet(
            f"background-color: {color.name()}; border-radius: 4px;"
        )
        self._current_color_label.setText(color.name().upper())
        self._history_widget.addColor(color)
        self.colorPicked.emit(color)

    def _on_history_color_clicked(self, color: QColor) -> None:
        self._current_color_preview.setStyleSheet(
            f"background-color: {color.name()}; border-radius: 4px;"
        )
        self._current_color_label.setText(color.name().upper())
        self.colorPicked.emit(color)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        text_color = theme.get_color('label.text.normal', QColor(200, 200, 200))

        self._current_color_label.setStyleSheet(f"color: {text_color.name()};")

        for label in self.findChildren(QLabel):
            if label != self._current_color_label:
                label.setStyleSheet(f"color: {text_color.name()};")

    def startPick(self) -> None:
        self._pick_button._start_pick()

    def cancelPick(self) -> None:
        self._pick_button._cancel_pick()

    def isPicking(self) -> bool:
        return self._pick_button.isPicking()

    def currentColor(self) -> Optional[QColor]:
        return self._pick_button.currentColor()

    def getHistoryColors(self) -> List[QColor]:
        return self._history_widget.colors()

    def clearHistory(self) -> None:
        self._history_widget.clearColors()

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        self._pick_button.cleanup()
