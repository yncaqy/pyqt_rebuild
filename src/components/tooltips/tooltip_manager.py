"""
Custom Tooltip Component

Provides a simple, theme-aware tooltip that can be installed on any widget.

Features:
- Single line display (no wrapping)
- Compact size
- Theme integration
- Easy installation on any widget
- Memory-safe with proper cleanup
"""

import logging
from typing import Optional, Dict
from PyQt6.QtCore import Qt, QTimer, QPoint, QObject, QEvent
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget, QApplication
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class TooltipConfig:
    """Configuration constants for tooltip behavior."""
    
    DEFAULT_DELAY = 800
    DEFAULT_DURATION = 2000
    DEFAULT_PADDING = 4
    DEFAULT_BORDER_RADIUS = 2
    DEFAULT_FONT_SIZE = 10


class CustomTooltip(QWidget):
    """Custom tooltip widget with theme support."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self._text = ""
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        logger.debug("CustomTooltip initialized")
    
    def set_text(self, text: str) -> None:
        self._text = text
        self._resize_to_fit()
        
    def _resize_to_fit(self) -> None:
        if not self._text:
            self.resize(0, 0)
            return
        
        font = QFont()
        font.setPointSize(TooltipConfig.DEFAULT_FONT_SIZE)
        metrics = QFontMetrics(font)
        
        text_width = metrics.horizontalAdvance(self._text)
        text_height = metrics.height()
        
        width = text_width + (TooltipConfig.DEFAULT_PADDING * 2)
        height = text_height + (TooltipConfig.DEFAULT_PADDING * 2)
        
        self.resize(width, height)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._theme:
            bg_color = self._theme.get_color('tooltip.background', QColor(60, 60, 60))
            text_color = self._theme.get_color('tooltip.text', QColor(255, 255, 255))
            border_color = self._theme.get_color('tooltip.border', QColor(100, 100, 100))
        else:
            bg_color = QColor(60, 60, 60)
            text_color = QColor(255, 255, 255)
            border_color = QColor(100, 100, 100)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(
            0, 0, self.width() - 1, self.height() - 1,
            TooltipConfig.DEFAULT_BORDER_RADIUS, TooltipConfig.DEFAULT_BORDER_RADIUS
        )
        
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Arial", TooltipConfig.DEFAULT_FONT_SIZE))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            self._text
        )
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("CustomTooltip cleaned up")


class TooltipManager(QObject):
    """Manages tooltips for multiple widgets with theme support."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not TooltipManager._initialized:
            super().__init__()
            self._initialize()
            TooltipManager._initialized = True
    
    def _initialize(self) -> None:
        self._widget_tooltip: Dict[QWidget, str] = {}
        self._widget_timer: Dict[QWidget, QTimer] = {}
        self._widget_show_timer: Dict[QWidget, QTimer] = {}
        self._active_tooltip: Optional[CustomTooltip] = None
        
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        
        logger.debug("TooltipManager initialized")
    
    def install_tooltip(self, widget: QWidget, text: str) -> None:
        self._widget_tooltip[widget] = text
        logger.debug(f"Tooltip installed: '{text}'")
    
    def remove_tooltip(self, widget: QWidget) -> None:
        if widget in self._widget_tooltip:
            del self._widget_tooltip[widget]
        
        if widget in self._widget_timer:
            self._widget_timer[widget].stop()
            del self._widget_timer[widget]
        
        if widget in self._widget_show_timer:
            self._widget_show_timer[widget].stop()
            del self._widget_show_timer[widget]
        
        logger.debug("Tooltip removed")
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj in self._widget_tooltip:
            if event.type() == QEvent.Type.Enter:
                self._start_delay_timer(obj)
            elif event.type() == QEvent.Type.Leave:
                self._cancel_timer(obj)
                self._hide_tooltip()
            elif event.type() == QEvent.Type.MouseButtonPress:
                self._hide_tooltip()
        
        return False
    
    def _start_delay_timer(self, widget: QWidget) -> None:
        self._cancel_timer(widget)
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._show_tooltip(widget))
        timer.start(TooltipConfig.DEFAULT_DELAY)
        
        self._widget_timer[widget] = timer
    
    def _cancel_timer(self, widget: QWidget) -> None:
        if widget in self._widget_timer:
            self._widget_timer[widget].stop()
            del self._widget_timer[widget]
    
    def _show_tooltip(self, widget: QWidget) -> None:
        if widget not in self._widget_tooltip:
            return
        
        self._hide_tooltip()
        
        self._active_tooltip = CustomTooltip()
        self._active_tooltip.set_text(self._widget_tooltip[widget])
        
        global_pos = widget.mapToGlobal(QPoint(0, 0))
        tooltip_pos = QPoint(
            global_pos.x() + (widget.width() // 2) - (self._active_tooltip.width() // 2),
            global_pos.y() - self._active_tooltip.height() - 5
        )
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.geometry()
            if tooltip_pos.x() < 0:
                tooltip_pos.setX(5)
            elif tooltip_pos.x() + self._active_tooltip.width() > screen_rect.width():
                tooltip_pos.setX(screen_rect.width() - self._active_tooltip.width() - 5)
            
            if tooltip_pos.y() < 0:
                tooltip_pos.setY(global_pos.y() + widget.height() + 5)
        
        self._active_tooltip.move(tooltip_pos)
        self._active_tooltip.show()
        
        show_timer = QTimer()
        show_timer.setSingleShot(True)
        show_timer.timeout.connect(self._hide_tooltip)
        show_timer.start(TooltipConfig.DEFAULT_DURATION)
        
        self._widget_show_timer[widget] = show_timer
        
        logger.debug(f"Tooltip shown: '{self._widget_tooltip[widget]}'")
    
    def _hide_tooltip(self) -> None:
        if self._active_tooltip:
            self._active_tooltip.hide()
            self._active_tooltip.cleanup()
            self._active_tooltip.deleteLater()
            self._active_tooltip = None
            logger.debug("Tooltip hidden")
    
    def cleanup(self) -> None:
        self._hide_tooltip()
        
        for widget, timer in self._widget_timer.items():
            timer.stop()
        
        for widget, timer in self._widget_show_timer.items():
            timer.stop()
        
        self._widget_tooltip.clear()
        self._widget_timer.clear()
        self._widget_show_timer.clear()
        
        logger.debug("TooltipManager cleaned up")


tooltip_manager = TooltipManager()


def install_tooltip(widget: QWidget, text: str) -> None:
    tooltip_manager.install_tooltip(widget, text)


def remove_tooltip(widget: QWidget) -> None:
    tooltip_manager.remove_tooltip(widget)
