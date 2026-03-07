"""
StatusBar - 状态栏组件

提供功能完整、视觉美观的状态栏组件，显示系统级信息。

Features:
- 显示当前系统时间
- 电池电量状态显示
- 网络连接状态显示
- 通知图标显示
- 深色/浅色主题支持
- 响应式布局
- 性能优化

Example:
    status_bar = StatusBar()
    status_bar.show_time(True)
    status_bar.show_battery(True)
"""

import logging
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QSize
)
from PyQt6.QtGui import QColor, QPainter, QFont, QPixmap

from core.theme_manager import ThemeManager, Theme
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class StatusBarConfig:
    """StatusBar配置常量"""
    
    DEFAULT_HEIGHT = 32
    DEFAULT_SPACING = 12
    DEFAULT_PADDING = 8
    UPDATE_INTERVAL = 1000
    
    TIME_FORMAT = "%H:%M"
    DATE_FORMAT = "%Y-%m-%d"


class StatusItem(QWidget, StyleOverrideMixin):
    """
    状态项基类。
    
    所有状态栏项的基础组件，提供统一的接口和样式。
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_style_override()
        
        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._visible: bool = True
        self._enabled: bool = True
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def set_item_visible(self, visible: bool) -> None:
        self._visible = visible
        self.setVisible(visible)
        
    def is_item_visible(self) -> bool:
        return self._visible
        
    def set_item_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.setEnabled(enabled)
        
    def is_item_enabled(self) -> bool:
        return self._enabled
        
    def apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()
        
    def sizeHint(self) -> QSize:
        return QSize(70, StatusBarConfig.DEFAULT_HEIGHT)
        
    def minimumSizeHint(self) -> QSize:
        return QSize(50, StatusBarConfig.DEFAULT_HEIGHT)


class TimeStatusItem(StatusItem):
    """
    时间状态项。
    
    显示当前系统时间，支持自定义格式。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._time_format = StatusBarConfig.TIME_FORMAT
        self._show_seconds = False
        self._text_color: QColor = QColor(200, 200, 200)
        self._is_dark_theme: bool = True
        
        self._setup_ui()
        self._start_timer()
        
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        layout.addWidget(self._icon_label)
        
        self._time_label = QLabel()
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._time_label)
        
    def _start_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(StatusBarConfig.UPDATE_INTERVAL)
        self._update_time()
        
    def _update_time(self) -> None:
        from datetime import datetime
        now = datetime.now()
        if self._show_seconds:
            time_str = now.strftime("%H:%M:%S")
        else:
            time_str = now.strftime(self._time_format)
        self._time_label.setText(time_str)
        
    def _load_icon(self) -> None:
        icon_name = "DateTime_white" if self._is_dark_theme else "DateTime_black"
        icon = self._icon_mgr.get_icon(icon_name, 32)
        pixmap = icon.pixmap(32, 32)
        scaled = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._icon_label.setPixmap(scaled)
        
    def set_time_format(self, fmt: str) -> None:
        self._time_format = fmt
        self._update_time()
        
    def set_show_seconds(self, show: bool) -> None:
        self._show_seconds = show
        self._update_time()
        
    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        self._text_color = theme.get_color('statusbar.text', QColor(200, 200, 200))
        self._is_dark_theme = theme.name == 'dark'
        self._time_label.setStyleSheet(f"""
            QLabel {{
                color: {self._text_color.name()};
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        self._load_icon()
        
    def sizeHint(self) -> QSize:
        return QSize(70, StatusBarConfig.DEFAULT_HEIGHT)


class BatteryStatusItem(StatusItem):
    """
    电池状态项。
    
    显示电池电量和充电状态。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._battery_level: int = 100
        self._is_charging: bool = False
        self._text_color: QColor = QColor(200, 200, 200)
        self._is_dark_theme: bool = True
        
        self._setup_ui()
        self._start_timer()
        
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        layout.addWidget(self._icon_label)
        
        self._level_label = QLabel()
        self._level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._level_label)
        
    def _start_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_battery)
        self._timer.start(5000)
        self._update_battery()
        
    def _update_battery(self) -> None:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                self._battery_level = int(battery.percent)
                self._is_charging = battery.power_plugged
        except Exception:
            self._battery_level = 100
            self._is_charging = True
            
        self._update_display()
        
    def _update_display(self) -> None:
        self._level_label.setText(f"{self._battery_level}%")
        self._load_icon()
        
    def _load_icon(self) -> None:
        icon_name = "PowerButton_white" if self._is_dark_theme else "PowerButton_black"
        icon = self._icon_mgr.get_icon(icon_name, 32)
        pixmap = icon.pixmap(32, 32)
        scaled = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._icon_label.setPixmap(scaled)
        
    def set_battery_level(self, level: int) -> None:
        self._battery_level = max(0, min(100, level))
        self._update_display()
        
    def set_charging(self, charging: bool) -> None:
        self._is_charging = charging
        self._update_display()
        
    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        self._text_color = theme.get_color('statusbar.text', QColor(200, 200, 200))
        self._is_dark_theme = theme.name == 'dark'
        
        self._level_label.setStyleSheet(f"""
            QLabel {{
                color: {self._text_color.name()};
                font-size: 11px;
            }}
        """)
        self._load_icon()
        
    def sizeHint(self) -> QSize:
        return QSize(75, StatusBarConfig.DEFAULT_HEIGHT)


class NetworkStatusItem(StatusItem):
    """
    网络状态项。
    
    显示网络连接状态和类型。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._is_connected: bool = True
        self._signal_strength: int = 4
        self._connection_type: str = "WiFi"
        self._text_color: QColor = QColor(200, 200, 200)
        self._is_dark_theme: bool = True
        
        self._setup_ui()
        self._start_timer()
        
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        layout.addWidget(self._icon_label)
        
        self._type_label = QLabel()
        self._type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._type_label)
        
    def _start_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_network)
        self._timer.start(10000)
        self._update_network()
        
    def _update_network(self) -> None:
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            self._is_connected = True
        except Exception:
            self._is_connected = False
            
        self._update_display()
        
    def _update_display(self) -> None:
        if self._is_connected:
            self._type_label.setText(self._connection_type)
        else:
            self._type_label.setText("离线")
        self._load_icon()
        
    def _load_icon(self) -> None:
        icon_name = "Wifi_white" if self._is_dark_theme else "Wifi_black"
        icon = self._icon_mgr.get_icon(icon_name, 32)
        pixmap = icon.pixmap(32, 32)
        scaled = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._icon_label.setPixmap(scaled)
        
    def set_connected(self, connected: bool) -> None:
        self._is_connected = connected
        self._update_display()
        
    def set_connection_type(self, conn_type: str) -> None:
        self._connection_type = conn_type
        self._update_display()
        
    def set_signal_strength(self, strength: int) -> None:
        self._signal_strength = max(0, min(4, strength))
        self._load_icon()
        
    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        self._text_color = theme.get_color('statusbar.text', QColor(200, 200, 200))
        self._is_dark_theme = theme.name == 'dark'
        
        self._type_label.setStyleSheet(f"""
            QLabel {{
                color: {self._text_color.name()};
                font-size: 11px;
            }}
        """)
        self._load_icon()
        
    def sizeHint(self) -> QSize:
        return QSize(70, StatusBarConfig.DEFAULT_HEIGHT)


class NotificationStatusItem(StatusItem):
    """
    通知状态项。
    
    显示通知图标和未读数量。
    """
    
    notification_clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._notification_count: int = 0
        self._badge_color: QColor = QColor(231, 76, 60)
        self._badge_text_color: QColor = QColor(255, 255, 255)
        self._is_dark_theme: bool = True
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        self.setFixedSize(40, StatusBarConfig.DEFAULT_HEIGHT)
        
    def _load_icon(self):
        icon_name = "Message_white" if self._is_dark_theme else "Message_black"
        icon = self._icon_mgr.get_icon(icon_name, 32)
        pixmap = icon.pixmap(32, 32)
        scaled = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return scaled
        
    def set_notification_count(self, count: int) -> None:
        self._notification_count = max(0, count)
        self.update()
        
    def clear_notifications(self) -> None:
        self._notification_count = 0
        self.update()
        
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        icon_pixmap = self._load_icon()
        icon_size = 16
        x = (self.width() - icon_size) // 2
        y = (self.height() - icon_size) // 2
        
        painter.drawPixmap(x, y, icon_pixmap)
            
        if self._notification_count > 0:
            badge_radius = 8
            badge_x = x + icon_size - badge_radius
            badge_y = y - badge_radius // 2
            
            painter.setBrush(self._badge_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_x, badge_y, badge_radius * 2, badge_radius * 2)
            
            count_text = str(self._notification_count) if self._notification_count < 100 else "99+"
            painter.setPen(self._badge_text_color)
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                badge_x, badge_y, badge_radius * 2, badge_radius * 2,
                Qt.AlignmentFlag.AlignCenter, count_text
            )
            
        painter.end()
        
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.notification_clicked.emit()
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        self._is_dark_theme = theme.name == 'dark'
        self._badge_color = theme.get_color('statusbar.badge', QColor(231, 76, 60))
        self.update()
        
    def sizeHint(self) -> QSize:
        return QSize(36, StatusBarConfig.DEFAULT_HEIGHT)


class StatusBar(QWidget, StylesheetCacheMixin):
    """
    状态栏组件。
    
    显示系统级信息，包括时间、电池、网络、通知等。
    
    Features:
    - 显示当前系统时间
    - 电池电量状态显示
    - 网络连接状态显示
    - 通知图标显示
    - 深色/浅色主题支持
    - 响应式布局
    - 性能优化
    
    Signals:
        notification_clicked: 通知图标被点击时发出
        
    Example:
        status_bar = StatusBar()
        status_bar.show_time(True)
        status_bar.show_battery(True)
        status_bar.set_notification_count(5)
    """
    
    notification_clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_stylesheet_cache(max_size=10)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._items: Dict[str, StatusItem] = {}
        self._compact_mode: bool = False
        self._compact_width: int = 400
        
        self._setup_ui()
        self._setup_items()
        self._apply_initial_theme()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        logger.debug("StatusBar initialized")
        
    def _setup_ui(self) -> None:
        self.setFixedHeight(StatusBarConfig.DEFAULT_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(
            StatusBarConfig.DEFAULT_PADDING, 2,
            StatusBarConfig.DEFAULT_PADDING, 2
        )
        self._layout.setSpacing(StatusBarConfig.DEFAULT_SPACING)
        
        self._left_spacer = QWidget()
        self._left_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._layout.addWidget(self._left_spacer)
        
    def _setup_items(self) -> None:
        self._time_item = TimeStatusItem()
        self._battery_item = BatteryStatusItem()
        self._network_item = NetworkStatusItem()
        self._notification_item = NotificationStatusItem()
        
        self._notification_item.notification_clicked.connect(self.notification_clicked.emit)
        
        self._items = {
            'time': self._time_item,
            'battery': self._battery_item,
            'network': self._network_item,
            'notification': self._notification_item,
        }
        
        for item in self._items.values():
            item.setVisible(False)
            self._layout.addWidget(item)
            
    def _apply_initial_theme(self) -> None:
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)
            
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to StatusBar: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return
            
        self._current_theme = theme
        
        bg_color = theme.get_color('statusbar.background', QColor(40, 40, 40))
        border_color = theme.get_color('statusbar.border', QColor(60, 60, 60))
        
        cache_key = (bg_color.name(), border_color.name())
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: f"""
                StatusBar {{
                    background-color: {bg_color.name()};
                    border-top: 1px solid {border_color.name()};
                }}
            """
        )
        
        self.setStyleSheet(qss)
        
        for item in self._items.values():
            item.apply_theme(theme)
            
    def _on_widget_destroyed(self) -> None:
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)
        
    def show_time(self, show: bool) -> None:
        self._time_item.set_item_visible(show)
        
    def show_battery(self, show: bool) -> None:
        self._battery_item.set_item_visible(show)
        
    def show_network(self, show: bool) -> None:
        self._network_item.set_item_visible(show)
        
    def show_notification(self, show: bool) -> None:
        self._notification_item.set_item_visible(show)
        
    def set_time_format(self, fmt: str) -> None:
        self._time_item.set_time_format(fmt)
        
    def set_show_seconds(self, show: bool) -> None:
        self._time_item.set_show_seconds(show)
        
    def set_battery_level(self, level: int) -> None:
        self._battery_item.set_battery_level(level)
        
    def set_charging(self, charging: bool) -> None:
        self._battery_item.set_charging(charging)
        
    def set_network_connected(self, connected: bool) -> None:
        self._network_item.set_connected(connected)
        
    def set_connection_type(self, conn_type: str) -> None:
        self._network_item.set_connection_type(conn_type)
        
    def set_notification_count(self, count: int) -> None:
        self._notification_item.set_notification_count(count)
        
    def clear_notifications(self) -> None:
        self._notification_item.clear_notifications()
        
    def set_compact_mode(self, compact: bool) -> None:
        self._compact_mode = compact
        self._update_layout()
        
    def set_compact_width(self, width: int) -> None:
        self._compact_width = width
        
    def _update_layout(self) -> None:
        if self._compact_mode:
            self._network_item.set_item_visible(False)
            self._battery_item.set_item_visible(False)
        else:
            self._network_item.set_item_visible(True)
            self._battery_item.set_item_visible(True)
            
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        
        if self.width() < self._compact_width and not self._compact_mode:
            self._compact_mode = True
            self._update_layout()
        elif self.width() >= self._compact_width and self._compact_mode:
            self._compact_mode = False
            self._update_layout()
            
    def get_item(self, name: str) -> Optional[StatusItem]:
        return self._items.get(name)
        
    def add_custom_item(self, name: str, item: StatusItem) -> None:
        if name in self._items:
            logger.warning(f"Item '{name}' already exists, replacing")
            self._items[name].deleteLater()
            
        self._items[name] = item
        if self._current_theme:
            item.apply_theme(self._current_theme)
        self._layout.insertWidget(self._layout.count() - 1, item)
        
    def remove_item(self, name: str) -> None:
        if name in self._items:
            self._items[name].deleteLater()
            del self._items[name]
            
    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        self._cleanup_done = True
        
        for item in self._items.values():
            if hasattr(item, 'cleanup'):
                item.cleanup()
                
        self._theme_mgr.unsubscribe(self)
        self.clear_overrides()
        
    def __del__(self) -> None:
        try:
            self.cleanup()
        except Exception:
            pass
