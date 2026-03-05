"""
时间选择器组件

提供现代化的时间选择器，具有以下特性：
- 主题集成，自动更新样式
- 点击弹出时间选择面板
- 24小时制时间选择
- 滚轮式小时和分钟选择
- 时间改变时发送 timeChanged 信号
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal, QTime, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QMouseEvent, QPaintEvent, QFont, QWheelEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class TimePickerConfig:
    """时间选择器配置常量。"""

    DEFAULT_WIDTH = 100
    DEFAULT_HEIGHT = 32
    DEFAULT_TIME_FORMAT = "HH:mm"

    PANEL_WIDTH = 200
    PANEL_HEIGHT = 240
    PANEL_BORDER_RADIUS = 8
    PANEL_MARGIN = 4

    WHEEL_ITEM_HEIGHT = 32
    WHEEL_VISIBLE_ITEMS = 5

    ANIMATION_DURATION = 150


class TimeWheelWidget(QWidget):
    """
    时间滚轮选择器控件。

    功能特性:
    - 滚轮式数字选择
    - 平滑滚动动画
    - 循环/非循环模式
    """

    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        min_value: int = 0,
        max_value: int = 23,
        is_cyclic: bool = False
    ):
        super().__init__(parent)

        self._min_value = min_value
        self._max_value = max_value
        self._is_cyclic = is_cyclic
        self._current_value = min_value
        self._scroll_offset = 0.0
        self._target_offset = 0.0
        self._is_dragging = False
        self._last_mouse_y = 0
        self._velocity = 0.0
        self._click_offset: Optional[float] = None
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._scroll_timer = QTimer(self)
        self._scroll_timer.timeout.connect(self._animate_scroll)

        self.setFixedHeight(
            TimePickerConfig.WHEEL_ITEM_HEIGHT * TimePickerConfig.WHEEL_VISIBLE_ITEMS
        )
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def value(self) -> int:
        return self._current_value

    def setValue(self, value: int) -> None:
        value = max(self._min_value, min(self._max_value, value))
        if self._current_value != value:
            self._current_value = value
            self._scroll_offset = -value * TimePickerConfig.WHEEL_ITEM_HEIGHT
            self._target_offset = self._scroll_offset
            self.update()
            self.valueChanged.emit(value)

    def _get_visible_range(self) -> tuple:
        center_offset = -self._scroll_offset / TimePickerConfig.WHEEL_ITEM_HEIGHT
        half_visible = TimePickerConfig.WHEEL_VISIBLE_ITEMS / 2

        start = int(center_offset - half_visible) - 1
        end = int(center_offset + half_visible) + 1

        return start, end

    def _value_to_y(self, value: int) -> float:
        center_y = self.height() / 2
        offset = value + self._scroll_offset / TimePickerConfig.WHEEL_ITEM_HEIGHT
        return center_y + offset * TimePickerConfig.WHEEL_ITEM_HEIGHT

    def _animate_scroll(self) -> None:
        diff = self._target_offset - self._scroll_offset
        if abs(diff) < 0.5:
            self._scroll_offset = self._target_offset
            self._scroll_timer.stop()
            self._update_value_from_offset()
        else:
            self._scroll_offset += diff * 0.3
        self.update()

    def _update_value_from_offset(self) -> None:
        item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT
        index = int(round(-self._scroll_offset / item_height))

        if self._is_cyclic:
            range_size = self._max_value - self._min_value + 1
            index = index % range_size

        index = max(0, min(self._max_value - self._min_value, index))
        new_value = self._min_value + index

        if new_value != self._current_value:
            self._current_value = new_value
            self.valueChanged.emit(new_value)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        text_color = theme.get_color('timewheel.text.normal', QColor(200, 200, 200))
        selected_color = theme.get_color('timewheel.text.selected', QColor(255, 255, 255))
        disabled_color = theme.get_color('timewheel.text.disabled', QColor(100, 100, 100))

        center_y = self.height() / 2
        item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT

        selection_rect = QRect(
            0,
            int(center_y - item_height / 2),
            self.width(),
            int(item_height)
        )

        selection_bg = theme.get_color('timewheel.selection.background', QColor(60, 60, 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(selection_bg))
        painter.drawRoundedRect(selection_rect, 6, 6)

        start, end = self._get_visible_range()
        range_size = self._max_value - self._min_value + 1

        for i in range(start, end + 1):
            if self._is_cyclic:
                display_index = i % range_size
                if display_index < 0:
                    display_index += range_size
            else:
                if i < 0 or i >= range_size:
                    continue
                display_index = i

            value = self._min_value + display_index
            y = self._value_to_y(i)

            if abs(y - center_y) < item_height / 2:
                color = selected_color
                font_size = 14
            elif abs(y - center_y) < item_height * 1.5:
                color = text_color
                font_size = 13
            else:
                color = disabled_color
                font_size = 12

            painter.setPen(QPen(color))
            font = QFont("Arial", font_size)
            font.setBold(abs(y - center_y) < item_height / 2)
            painter.setFont(font)

            text = f"{value:02d}"
            text_rect = QRect(0, int(y - item_height / 2), self.width(), int(item_height))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        step = TimePickerConfig.WHEEL_ITEM_HEIGHT

        if delta > 0:
            self._target_offset = self._scroll_offset + step
        else:
            self._target_offset = self._scroll_offset - step

        range_size = self._max_value - self._min_value + 1
        max_offset = 0
        min_offset = -(range_size - 1) * step

        if not self._is_cyclic:
            self._target_offset = max(min_offset, min(max_offset, self._target_offset))

        self._scroll_timer.start(16)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._last_mouse_y = event.pos().y()
            self._velocity = 0.0
            self._scroll_timer.stop()
            
            clicked_y = event.pos().y()
            center_y = self.height() / 2
            item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT
            
            self._click_offset = (clicked_y - center_y) / item_height
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_dragging:
            current_y = event.pos().y()
            delta = current_y - self._last_mouse_y
            
            if abs(delta) > 3:
                self._click_offset = None
            
            self._last_mouse_y = current_y

            self._scroll_offset += delta
            self._velocity = delta

            range_size = self._max_value - self._min_value + 1
            item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT

            if not self._is_cyclic:
                max_offset = 0
                min_offset = -(range_size - 1) * item_height
                self._scroll_offset = max(min_offset, min(max_offset, self._scroll_offset))

            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False

            if abs(self._velocity) > 2:
                self._target_offset = self._scroll_offset + self._velocity * 5
                range_size = self._max_value - self._min_value + 1
                item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT

                if not self._is_cyclic:
                    max_offset = 0
                    min_offset = -(range_size - 1) * item_height
                    self._target_offset = max(min_offset, min(max_offset, self._target_offset))
                
                self._scroll_timer.start(16)
            elif self._click_offset is not None:
                item_height = TimePickerConfig.WHEEL_ITEM_HEIGHT
                current_index = -self._scroll_offset / item_height
                target_index = round(current_index + self._click_offset)

                range_size = self._max_value - self._min_value + 1
                if not self._is_cyclic:
                    target_index = max(0, min(range_size - 1, target_index))

                self._target_offset = -target_index * item_height
                self._scroll_timer.start(16)
            
            self._click_offset = None

        super().mouseReleaseEvent(event)

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._scroll_timer.stop()


class TimePickerPanel(QWidget):
    """
    时间选择面板。

    功能特性:
    - 小时滚轮选择器 (0-23)
    - 分钟滚轮选择器 (0-59)
    - 点击外部自动关闭
    """

    timeSelected = pyqtSignal(QTime)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(TimePickerConfig.PANEL_WIDTH, TimePickerConfig.PANEL_HEIGHT)

        self._init_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(12, 12, 12, 12)
        self._main_layout.setSpacing(0)

        self._hour_wheel = TimeWheelWidget(self, 0, 23, is_cyclic=False)
        self._hour_wheel.valueChanged.connect(self._on_time_changed)
        self._main_layout.addWidget(self._hour_wheel, 1)

        separator = QLabel(":")
        separator.setObjectName("timeSeparator")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setFixedWidth(20)
        self._main_layout.addWidget(separator)

        self._minute_wheel = TimeWheelWidget(self, 0, 59, is_cyclic=False)
        self._minute_wheel.valueChanged.connect(self._on_time_changed)
        self._main_layout.addWidget(self._minute_wheel, 1)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        
        text_color = theme.get_color('timepicker.text', QColor(200, 200, 200))
        separator = self.findChild(QLabel, "timeSeparator")
        if separator:
            separator.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-size: 18px;
                    font-weight: bold;
                }}
            """)
        
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        bg_color = theme.get_color('timepicker.background', QColor(45, 45, 45))
        border_color = theme.get_color('timepicker.border', QColor(60, 60, 60))
        border_radius = TimePickerConfig.PANEL_BORDER_RADIUS

        rect = QRect(0, 0, self.width(), self.height())

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, border_radius, border_radius)

    def _on_time_changed(self) -> None:
        hour = self._hour_wheel.value()
        minute = self._minute_wheel.value()
        self.timeSelected.emit(QTime(hour, minute))

    def setTime(self, time: QTime) -> None:
        self._hour_wheel.setValue(time.hour())
        self._minute_wheel.setValue(time.minute())

    def time(self) -> QTime:
        return QTime(self._hour_wheel.value(), self._minute_wheel.value())

    def show_at(self, global_pos: QPoint) -> None:
        self.move(global_pos)
        self.show()
        self.setFocus()

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._hour_wheel.cleanup()
        self._minute_wheel.cleanup()


class TimePicker(QWidget, StyleOverrideMixin):
    """
    时间选择器组件，用于选择24小时制时间。

    功能特性:
    - 主题集成，自动响应主题切换
    - 点击弹出时间选择面板
    - 滚轮式小时和分钟选择
    - 时间改变时发送 timeChanged 信号
    - 内存安全，支持正确的清理机制

    信号:
        timeChanged: 时间改变时发出，参数为新的时间 (QTime)

    示例:
        picker = TimePicker()
        picker.setTime(QTime.currentTime())
        picker.timeChanged.connect(lambda time: print(f"选择时间: {time.toString()}"))
    """

    timeChanged = pyqtSignal(QTime)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_style_override()

        self.setMinimumSize(TimePickerConfig.DEFAULT_WIDTH, TimePickerConfig.DEFAULT_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self._time: QTime = QTime.currentTime()
        self._format: str = TimePickerConfig.DEFAULT_TIME_FORMAT

        self._panel: Optional[TimePickerPanel] = None
        self._arrow_icon: Optional[QIcon] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        logger.debug("TimePicker 初始化完成")

    def time(self) -> QTime:
        return QTime(self._time)

    def setTime(self, time: QTime) -> None:
        if self._time == time:
            return

        self._time = time
        self.update()
        self.timeChanged.emit(time)
        logger.debug(f"TimePicker 时间改变: {time.toString(self._format)}")

    def setFormat(self, format_str: str) -> None:
        self._format = format_str
        self.update()

    def format(self) -> str:
        return self._format

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        self._update_arrow_icon()
        self.update()

    def _update_arrow_icon(self) -> None:
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color(
            'timepicker.icon.normal',
            self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200))
        )

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)
        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, 12)
        self.update()

    def _show_panel(self) -> None:
        if self._panel is None:
            self._panel = TimePickerPanel()
            self._panel.timeSelected.connect(self._on_time_selected)

        self._panel.setTime(self._time)

        global_pos = self.mapToGlobal(
            QPoint(0, self.height() + TimePickerConfig.PANEL_MARGIN)
        )

        screen = self.screen().availableGeometry()
        panel_width = self._panel.width()
        panel_height = self._panel.height()

        if global_pos.x() + panel_width > screen.right():
            global_pos.setX(screen.right() - panel_width - 4)

        if global_pos.y() + panel_height > screen.bottom():
            global_pos.setY(self.mapToGlobal(QPoint(0, 0)).y() - panel_height - TimePickerConfig.PANEL_MARGIN)

        self._panel.show_at(global_pos)

    def _on_time_selected(self, time: QTime) -> None:
        self.setTime(time)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        bg_color = self.get_style_color(theme, 'timepicker.background', QColor(42, 42, 42))
        border_color = self.get_style_color(theme, 'timepicker.border', QColor(68, 68, 68))
        text_color = self.get_style_color(theme, 'timepicker.text', QColor(224, 224, 224))
        border_radius = self.get_style_value(theme, 'timepicker.border_radius', 4)

        is_enabled = self.isEnabled()

        if not is_enabled:
            bg_color = self.get_style_color(theme, 'timepicker.background_disabled', QColor(37, 37, 37))
            border_color = self.get_style_color(theme, 'timepicker.border_disabled', QColor(51, 51, 51))
            text_color = self.get_style_color(theme, 'timepicker.text_disabled', QColor(102, 102, 102))

        rect = QRect(0, 0, self.width(), self.height())

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, border_radius, border_radius)

        text = self._time.toString(self._format)
        text_rect = rect.adjusted(10, 0, -24, 0)

        painter.setPen(QPen(text_color))
        painter.setFont(self.font())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        if self._arrow_icon and not self._arrow_icon.isNull():
            arrow_size = 12
            arrow_margin = 8

            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2

            self._arrow_icon.paint(painter, x, y, arrow_size, arrow_size)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._show_panel()
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(TimePickerConfig.DEFAULT_WIDTH, TimePickerConfig.DEFAULT_HEIGHT)

    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("TimePicker 已取消主题订阅")

        if self._panel:
            self._panel.cleanup()
            self._panel.hide()
            self._panel.deleteLater()
            self._panel = None

        self.clear_overrides()

    def __del__(self) -> None:
        try:
            self.cleanup()
        except Exception:
            pass
