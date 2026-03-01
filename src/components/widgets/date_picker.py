"""
日期选择器组件

提供现代化的日期选择器，具有以下特性：
- 主题集成，自动更新样式
- 点击弹出日历面板
- 支持年、月快速切换
- 支持键盘导航
- 日期改变时发送 dateChanged 信号
"""

import logging
from typing import Optional, List
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal, QDate
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class DatePickerConfig:
    """
    日期选择器行为和样式的配置常量。

    Attributes:
        DEFAULT_WIDTH: 默认宽度
        DEFAULT_HEIGHT: 默认高度
        DEFAULT_DATE_FORMAT: 默认日期格式
    """

    DEFAULT_WIDTH = 120
    DEFAULT_HEIGHT = 32
    DEFAULT_DATE_FORMAT = "yyyy-MM-dd"


class CalendarPanel(QWidget):
    """
    自定义日历面板组件，完全自绘制。

    特性：
    - 完全自定义绘制，完美主题适配
    - 支持月份切换
    - 支持年份切换
    - 高亮当前日期和选中日期
    - 悬停效果
    """

    dateSelected = pyqtSignal(QDate)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._current_date = QDate.currentDate()
        self._selected_date = QDate.currentDate()
        self._hovered_date: Optional[QDate] = None

        self._weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]

        self.setWindowFlags(
            Qt.WindowType.Popup | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setMouseTracking(True)
        self.setFixedSize(280, 320)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self._apply_theme()

    def _apply_theme(self) -> None:
        """应用主题样式。"""
        theme = self._theme_mgr.current_theme()
        if not theme:
            return

        self._current_theme = theme
        self.update()

    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化。"""
        self._apply_theme()

    def setSelectedDate(self, date: QDate) -> None:
        """设置选中的日期。"""
        self._selected_date = date
        self._current_date = QDate(date.year(), date.month(), 1)
        self.update()

    def _get_theme_color(self, key: str, default: QColor) -> QColor:
        """获取主题颜色。"""
        if not self._current_theme:
            return default
        return self._current_theme.get_color(key, default)

    def _get_theme_value(self, key: str, default) -> any:
        """获取主题值。"""
        if not self._current_theme:
            return default
        return self._current_theme.get_value(key, default)

    def _get_cell_size(self) -> tuple:
        """获取单元格尺寸。"""
        cell_width = (self.width() - 20) // 7
        cell_height = 32
        return cell_width, cell_height

    def _get_calendar_start(self) -> tuple:
        """获取日历起始位置。"""
        start_x = 10
        start_y = 80
        return start_x, start_y

    def _date_to_rect(self, date: QDate) -> QRect:
        """将日期转换为绘制区域。"""
        if not date.isValid():
            return QRect()

        cell_width, cell_height = self._get_cell_size()
        start_x, start_y = self._get_calendar_start()

        first_day = QDate(date.year(), date.month(), 1)
        day_of_week = first_day.dayOfWeek()

        day_index = date.day() - 1
        col = (day_index + day_of_week - 1) % 7
        row = (day_index + day_of_week - 1) // 7

        x = start_x + col * cell_width
        y = start_y + row * cell_height

        return QRect(x, y, cell_width, cell_height)

    def _pos_to_date(self, pos: QPoint) -> Optional[QDate]:
        """将鼠标位置转换为日期。"""
        cell_width, cell_height = self._get_cell_size()
        start_x, start_y = self._get_calendar_start()

        col = (pos.x() - start_x) // cell_width
        row = (pos.y() - start_y) // cell_height

        if col < 0 or col > 6 or row < 0 or row > 5:
            return None

        first_day = QDate(self._current_date.year(), self._current_date.month(), 1)
        day_of_week = first_day.dayOfWeek()

        day = row * 7 + col - day_of_week + 2

        if day < 1 or day > first_day.daysInMonth():
            return None

        return QDate(self._current_date.year(), self._current_date.month(), day)

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制日历面板。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        bg_color = self._get_theme_color('calendar.background', QColor(42, 42, 42))
        header_bg = self._get_theme_color('calendar.header.background', QColor(51, 51, 51))
        text_color = self._get_theme_color('calendar.header.text', QColor(224, 224, 224))
        accent_color = self._get_theme_color('calendar.selection', QColor(93, 173, 226))
        border_color = self._get_theme_color('calendar.border', QColor(51, 51, 51))
        item_normal = self._get_theme_color('calendar.item.normal', QColor(224, 224, 224))
        item_selected = self._get_theme_color('calendar.item.selected', QColor(255, 255, 255))
        item_disabled = self._get_theme_color('calendar.item.disabled', QColor(102, 102, 102))
        border_radius = self._get_theme_value('calendar.border_radius', 8)

        is_dark = theme.is_dark if hasattr(theme, 'is_dark') else bg_color.lightness() < 128
        hover_bg = QColor(255, 255, 255, 25) if is_dark else QColor(0, 0, 0, 12)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), border_radius, border_radius)

        header_rect = QRect(8, 8, self.width() - 16, 40)
        painter.setBrush(QBrush(header_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(header_rect, 6, 6)

        month_names = [
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ]
        header_text = f"{self._current_date.year()}年 {month_names[self._current_date.month() - 1]}"
        painter.setPen(QPen(text_color))
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignCenter, header_text)

        nav_btn_size = 28
        nav_y = 14

        prev_year_rect = QRect(12, nav_y, nav_btn_size, nav_btn_size)
        prev_month_rect = QRect(44, nav_y, nav_btn_size, nav_btn_size)
        next_month_rect = QRect(self.width() - 44 - nav_btn_size, nav_y, nav_btn_size, nav_btn_size)
        next_year_rect = QRect(self.width() - 12 - nav_btn_size, nav_y, nav_btn_size, nav_btn_size)

        painter.setPen(QPen(text_color, 2))
        painter.drawLine(prev_year_rect.center() - QPoint(6, 0), prev_year_rect.center() + QPoint(6, 0))
        painter.drawLine(prev_year_rect.center() - QPoint(2, -4), prev_year_rect.center() - QPoint(6, 0))
        painter.drawLine(prev_year_rect.center() - QPoint(2, 4), prev_year_rect.center() - QPoint(6, 0))

        painter.drawLine(prev_month_rect.center() - QPoint(4, 0), prev_month_rect.center() + QPoint(4, 0))
        painter.drawLine(prev_month_rect.center() - QPoint(0, -4), prev_month_rect.center() - QPoint(4, 0))
        painter.drawLine(prev_month_rect.center() - QPoint(0, 4), prev_month_rect.center() - QPoint(4, 0))

        painter.drawLine(next_month_rect.center() - QPoint(4, 0), next_month_rect.center() + QPoint(4, 0))
        painter.drawLine(next_month_rect.center() + QPoint(0, -4), next_month_rect.center() + QPoint(4, 0))
        painter.drawLine(next_month_rect.center() + QPoint(0, 4), next_month_rect.center() + QPoint(4, 0))

        painter.drawLine(next_year_rect.center() - QPoint(6, 0), next_year_rect.center() + QPoint(6, 0))
        painter.drawLine(next_year_rect.center() + QPoint(2, -4), next_year_rect.center() + QPoint(6, 0))
        painter.drawLine(next_year_rect.center() + QPoint(2, 4), next_year_rect.center() + QPoint(6, 0))

        font.setBold(False)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QPen(item_disabled))

        cell_width, cell_height = self._get_cell_size()
        start_x, start_y = self._get_calendar_start()

        for i, label in enumerate(self._weekday_labels):
            painter.drawText(QRect(start_x + i * cell_width, 56, cell_width, 20),
                           Qt.AlignmentFlag.AlignCenter, label)

        first_day = QDate(self._current_date.year(), self._current_date.month(), 1)
        day_of_week = first_day.dayOfWeek()
        days_in_month = first_day.daysInMonth()

        today = QDate.currentDate()

        for day in range(1, days_in_month + 1):
            date = QDate(self._current_date.year(), self._current_date.month(), day)
            rect = self._date_to_rect(date)

            is_selected = date == self._selected_date
            is_today = date == today
            is_hovered = date == self._hovered_date

            if is_selected:
                painter.setBrush(QBrush(accent_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 4, 4)
                painter.setPen(QPen(item_selected))
            elif is_today:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(accent_color, 2))
                painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 4, 4)
                painter.setPen(QPen(accent_color))
            elif is_hovered:
                painter.setBrush(QBrush(hover_bg))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 4, 4)
                painter.setPen(QPen(item_normal))
            else:
                painter.setPen(QPen(item_normal))

            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(day))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """处理鼠标移动事件。"""
        date = self._pos_to_date(event.pos())
        if date != self._hovered_date:
            self._hovered_date = date
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标点击事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            date = self._pos_to_date(event.pos())
            if date and date.isValid():
                self._selected_date = date
                self.dateSelected.emit(date)
                self.hide()
                return

            cell_width = (self.width() - 20) // 7
            nav_y = 14
            nav_btn_size = 28

            prev_year_rect = QRect(12, nav_y, nav_btn_size, nav_btn_size)
            prev_month_rect = QRect(44, nav_y, nav_btn_size, nav_btn_size)
            next_month_rect = QRect(self.width() - 44 - nav_btn_size, nav_y, nav_btn_size, nav_btn_size)
            next_year_rect = QRect(self.width() - 12 - nav_btn_size, nav_y, nav_btn_size, nav_btn_size)

            if prev_year_rect.contains(event.pos()):
                self._current_date = self._current_date.addYears(-1)
                self.update()
            elif prev_month_rect.contains(event.pos()):
                self._current_date = self._current_date.addMonths(-1)
                self.update()
            elif next_month_rect.contains(event.pos()):
                self._current_date = self._current_date.addMonths(1)
                self.update()
            elif next_year_rect.contains(event.pos()):
                self._current_date = self._current_date.addYears(1)
                self.update()

        super().mousePressEvent(event)

    def leaveEvent(self, event) -> None:
        """处理鼠标离开事件。"""
        self._hovered_date = None
        self.update()
        super().leaveEvent(event)

    def show_at(self, global_pos: QPoint) -> None:
        """在指定位置显示日历面板。"""
        self.move(global_pos)
        self.show()
        self.setFocus()


class DatePicker(QWidget, StyleOverrideMixin):
    """
    日期选择器组件，用于选择日期。

    特性：
    - 主题集成，自动响应主题切换
    - 点击弹出日历面板
    - 支持键盘导航
    - 日期改变时发送 dateChanged 信号
    - 内存安全，支持正确的清理机制

    信号:
        dateChanged: 日期改变时发出，参数为新的日期 (QDate)

    示例:
        picker = DatePicker()
        picker.setDate(QDate.currentDate())
        picker.dateChanged.connect(lambda date: print(f"选择日期: {date.toString()}"))
    """

    dateChanged = pyqtSignal(QDate)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化日期选择器。

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._init_style_override()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setMinimumSize(DatePickerConfig.DEFAULT_WIDTH, DatePickerConfig.DEFAULT_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._date: QDate = QDate.currentDate()
        self._format: str = DatePickerConfig.DEFAULT_DATE_FORMAT

        self._calendar_panel: Optional[CalendarPanel] = None

        self._is_hover: bool = False
        self._is_pressed: bool = False

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        logger.debug("DatePicker 初始化完成")

    def date(self) -> QDate:
        """
        返回当前选择的日期。

        Returns:
            当前日期
        """
        return self._date

    def setDate(self, date: QDate) -> None:
        """
        设置日期。

        Args:
            date: 要设置的日期
        """
        if self._date == date:
            return

        self._date = date
        self.update()
        self.dateChanged.emit(date)
        logger.debug(f"DatePicker 日期改变: {date.toString(self._format)}")

    def setFormat(self, format_str: str) -> None:
        """
        设置日期显示格式。

        Args:
            format_str: 日期格式字符串
        """
        self._format = format_str
        self.update()

    def format(self) -> str:
        """
        返回日期显示格式。

        Returns:
            日期格式字符串
        """
        return self._format

    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化。"""
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        if not theme:
            return

        self._current_theme = theme
        self.update()

    def _show_calendar(self) -> None:
        """显示日历面板。"""
        if self._calendar_panel is None:
            self._calendar_panel = CalendarPanel()
            self._calendar_panel.dateSelected.connect(self._on_date_selected)

        self._calendar_panel.setSelectedDate(self._date)

        global_pos = self.mapToGlobal(
            QPoint(0, self.height() + 4)
        )

        screen = self.screen().availableGeometry()
        panel_width = self._calendar_panel.width()
        panel_height = self._calendar_panel.height()

        if global_pos.x() + panel_width > screen.right():
            global_pos.setX(screen.right() - panel_width - 4)

        if global_pos.y() + panel_height > screen.bottom():
            global_pos.setY(self.mapToGlobal(QPoint(0, 0)).y() - panel_height - 4)

        self._calendar_panel.show_at(global_pos)

    def _on_date_selected(self, date: QDate) -> None:
        """处理日期选择。"""
        self.setDate(date)

    def paintEvent(self, event) -> None:
        """绘制日期选择器。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        bg_color = self.get_style_color(theme, 'datepicker.background', QColor(42, 42, 42))
        border_color = self.get_style_color(theme, 'datepicker.border', QColor(68, 68, 68))
        border_focus = self.get_style_color(theme, 'datepicker.border_focus', QColor(93, 173, 226))
        text_color = self.get_style_color(theme, 'datepicker.text', QColor(224, 224, 224))
        border_radius = self.get_style_value(theme, 'datepicker.border_radius', 4)

        is_enabled = self.isEnabled()

        if not is_enabled:
            bg_color = self.get_style_color(theme, 'datepicker.background_disabled', QColor(37, 37, 37))
            border_color = self.get_style_color(theme, 'datepicker.border', QColor(51, 51, 51))
            text_color = self.get_style_color(theme, 'datepicker.text_disabled', QColor(102, 102, 102))

        rect = QRect(0, 0, self.width(), self.height())

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, border_radius, border_radius)

        text = self._date.toString(self._format)
        text_rect = rect.adjusted(10, 0, -30, 0)

        painter.setPen(QPen(text_color))
        painter.setFont(self.font())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        arrow_x = self.width() - 20
        arrow_y = self.height() // 2

        painter.setPen(QPen(text_color, 2))
        painter.drawLine(arrow_x - 4, arrow_y - 2, arrow_x, arrow_y + 2)
        painter.drawLine(arrow_x, arrow_y + 2, arrow_x + 4, arrow_y - 2)

    def mousePressEvent(self, event) -> None:
        """处理鼠标按下事件。"""
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._is_pressed = True
            self._show_calendar()
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """处理鼠标释放事件。"""
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:
        """处理鼠标进入事件。"""
        self._is_hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """处理鼠标离开事件。"""
        self._is_hover = False
        self._is_pressed = False
        self.update()
        super().leaveEvent(event)

    def sizeHint(self) -> QSize:
        """返回建议尺寸。"""
        return QSize(DatePickerConfig.DEFAULT_WIDTH, DatePickerConfig.DEFAULT_HEIGHT)

    def cleanup(self) -> None:
        """清理资源。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("DatePicker 已取消主题订阅")

        if self._calendar_panel:
            self._calendar_panel.hide()
            self._calendar_panel.deleteLater()
            self._calendar_panel = None

        self.clear_overrides()

    def __del__(self) -> None:
        """析构函数。"""
        try:
            self.cleanup()
        except Exception:
            pass
