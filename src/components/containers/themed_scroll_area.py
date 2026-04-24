#!/usr/bin/env python3
"""
主题化滚动区域组件

提供带主题集成的 QScrollArea，根据当前应用主题自动更新滚动条颜色、背景和样式。

功能特性:
- 自动主题集成，实时更新
- 主题一致的滚动条样式
- 可自定义滚动行为
- 优化的样式缓存，提升性能
- 内存安全，正确清理资源
- 自动资源清理机制

滚动区域与主题管理器无缝集成，在整个应用程序中提供一致的滚动体验。

使用示例:
    scroll_area = ThemedScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    scroll_area.setWidget(content_widget)
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtWidgets import QScrollArea, QWidget, QScrollBar
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from src.core.theme_manager import ThemeManager, Theme
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class ThemedScrollAreaConfig:
    """主题化滚动区域配置常量。"""

    DEFAULT_SCROLLBAR_WIDTH = 8
    DEFAULT_SCROLLBAR_WIDTH_HOVER = 12
    DEFAULT_SCROLLBAR_MIN_LENGTH = 30


class ThemedScrollArea(QScrollArea, StylesheetCacheMixin):
    """
    主题感知的滚动区域，支持自动样式更新。

    该组件根据当前应用主题自动调整外观，在整个用户界面中提供一致的滚动体验。
    支持自动资源清理机制。

    使用示例:
        scroll_area = ThemedScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化主题化滚动区域。

        Args:
            parent: 父控件
        """
        super().__init__(parent)

        self._init_stylesheet_cache(max_size=15)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._setup_scrollbars()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug("ThemedScrollArea initialized")

    def _setup_scrollbars(self):
        """初始化自定义滚动条，支持主题。"""
        self._vertical_scrollbar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._vertical_scrollbar)

        self._horizontal_scrollbar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        self.setHorizontalScrollBar(self._horizontal_scrollbar)

        corner = QWidget()
        corner.setStyleSheet("background: transparent;")
        corner.setFixedSize(1, 1)
        self.setCornerWidget(corner)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器的主题变化通知。

        Args:
            theme: 要应用的新主题
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedScrollArea: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到滚动区域，支持缓存。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        bg_color = theme.get_color('scrollarea.background', QColor(255, 255, 255))
        border_color = theme.get_color('scrollarea.border', QColor(200, 200, 200))
        border_radius = theme.get_value('scrollarea.border_radius', 4)
        border_width = theme.get_value('scrollarea.border_width', 1)

        cache_key = (
            bg_color.name(),
            border_color.name(),
            border_radius,
            border_width,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(bg_color, border_color, border_radius, border_width)
        )

        self.setStyleSheet(qss)

        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"Theme applied to ThemedScrollArea: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _build_stylesheet(self, bg_color: QColor, border_color: QColor,
                         border_radius: int, border_width: int) -> str:
        """
        从主题属性构建 QSS 样式表。

        Args:
            bg_color: 背景颜色
            border_color: 边框颜色
            border_radius: 边框圆角（像素）
            border_width: 边框宽度（像素）

        Returns:
            完整的 QSS 样式表字符串
        """
        qss = f"""
        ThemedScrollArea {{
            background-color: {bg_color.name() if bg_color.alpha() > 0 else 'transparent'};
            border: {border_width}px solid {border_color.name() if border_color.alpha() > 0 else 'transparent'};
            border-radius: {border_radius}px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
        }}
        """
        return qss

    def set_theme(self, name: str) -> None:
        """
        通过名称设置当前主题。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）
        """
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        获取当前主题名称。

        Returns:
            当前主题名称，如果未设置主题则返回 None
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def set_scrollbar_width(self, width: int) -> None:
        """
        设置滚动条宽度。

        Args:
            width: 滚动条宽度（像素）
        """
        logger.debug(f"Setting scrollbar width: {width}px")
        if self._current_theme:
            self._current_theme.set_value('scrollbar.width', width)
            self._apply_theme(self._current_theme)

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源并取消主题管理器订阅。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return

        self._cleanup_done = True

        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedScrollArea unsubscribed from theme manager")

        self._clear_stylesheet_cache()

    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedScrollArea scheduled for deletion")


ScrollArea = ThemedScrollArea
