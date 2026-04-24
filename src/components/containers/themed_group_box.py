#!/usr/bin/env python3
"""
主题化分组框组件

遵循 Microsoft WinUI 3 Expander/GroupBox 设计规范实现。
提供带主题集成的 QGroupBox，根据当前应用主题自动更新颜色、字体和样式。

WinUI 3 设计规范:
- 简洁扁平的视觉风格
- 淡边框或无边框
- 标题使用次要文本颜色
- 微妙的悬停效果
- 适当的圆角和间距

功能特性:
- 自动主题集成，实时更新
- 可自定义标题样式
- 主题一致的背景和边框颜色
- 优化的样式缓存，提升性能
- 内存安全，正确清理资源
- 本地样式覆盖，无需修改共享主题
- 自动资源清理机制

分组框与主题管理器无缝集成，在整个应用程序中提供一致的样式。

使用示例:
    group = ThemedGroupBox("设置")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("选项 1"))
    group.setLayout(layout)
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from src.core.theme_manager import ThemeManager, Theme
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG

logger = logging.getLogger(__name__)


class ThemedGroupBoxConfig:
    """主题化分组框配置常量，遵循 WinUI 3 设计规范。"""

    DEFAULT_TITLE_FONT_SIZE = FONT_CONFIG['size']['caption']
    DEFAULT_TITLE_FONT_WEIGHT = QFont.Weight.Normal
    DEFAULT_SPACING = WINUI3_CONTROL_SIZING['spacing']['small']
    DEFAULT_PADDING_H = WINUI3_CONTROL_SIZING['card']['padding']
    DEFAULT_BORDER_RADIUS = 8
    DEFAULT_MARGIN_TOP = 20


class ThemedGroupBox(QGroupBox, StyleOverrideMixin, StylesheetCacheMixin):
    """
    主题感知的分组框，支持自动样式更新。

    该组件根据当前应用主题自动调整外观，在整个用户界面中提供一致的样式。
    支持自动资源清理机制。

    使用示例:
        group = ThemedGroupBox("用户设置")
        group.setLayout(QVBoxLayout())
    """

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        """
        初始化主题化分组框。

        Args:
            title: 分组框标题
            parent: 父控件
        """
        super().__init__(title, parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=20)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"ThemedGroupBox initialized with title: '{title}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器的主题变化通知。

        Args:
            theme: 要应用的新主题
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedGroupBox: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到分组框，支持缓存。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        if not theme:
            return

        self._current_theme = theme

        bg_color = self.get_style_color(theme, 'groupbox.background', QColor(255, 255, 255))
        border_color = self.get_style_color(theme, 'groupbox.border', QColor(200, 200, 200))
        title_color = self.get_style_color(theme, 'groupbox.title.color', QColor(50, 50, 50))

        bg_hover = self.get_style_color(theme, 'groupbox.background_hover', bg_color)

        border_radius = self.get_style_value(theme, 'groupbox.border_radius', 4)
        border_width = self.get_style_value(theme, 'groupbox.border_width', 1)
        margin_top = self.get_style_value(theme, 'groupbox.margin_top', 24)

        font_size = self.get_style_value(theme, 'groupbox.title.font_size', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_SIZE)
        font_weight = self.get_style_value(theme, 'groupbox.title.font_weight', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_WEIGHT)

        cache_key = (
            bg_color.name(),
            bg_hover.name(),
            border_color.name(),
            title_color.name(),
            border_radius,
            border_width,
            margin_top,
            font_size,
            font_weight,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(
                theme, bg_color, bg_hover, border_color, title_color,
                border_radius, border_width, margin_top, font_size, font_weight
            )
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

    def _build_stylesheet(self, theme: Theme, bg_color: QColor, bg_hover: QColor,
                         border_color: QColor, title_color: QColor, border_radius: int,
                         border_width: int, margin_top: int, font_size: int,
                         font_weight: QFont.Weight) -> str:
        """
        从主题属性构建 QSS 样式表，遵循 WinUI 3 设计规范。

        Args:
            theme: 主题对象
            bg_color: 背景颜色
            bg_hover: 悬停背景颜色
            border_color: 边框颜色
            title_color: 标题文本颜色
            border_radius: 边框圆角（像素）
            border_width: 边框宽度（像素）
            margin_top: 标题区域上边距（像素）
            font_size: 标题字体大小
            font_weight: 标题字体粗细

        Returns:
            完整的 QSS 样式表字符串
        """
        padding_h = ThemedGroupBoxConfig.DEFAULT_PADDING_H
        padding_v = ThemedGroupBoxConfig.DEFAULT_SPACING

        qss = f"""
        ThemedGroupBox {{
            background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
            border: {border_width}px solid {border_color.name(QColor.NameFormat.HexArgb)};
            border-radius: {border_radius}px;
            margin-top: {margin_top}px;
            padding: {padding_v}px {padding_h}px {padding_v}px {padding_h}px;
            font-size: {font_size}px;
        }}
        
        ThemedGroupBox:hover {{
            background-color: {bg_hover.name(QColor.NameFormat.HexArgb)};
        }}
        
        ThemedGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px;
            background-color: transparent;
            color: {title_color.name(QColor.NameFormat.HexArgb)};
            font-weight: {font_weight};
            font-size: {font_size}px;
            left: {padding_h}px;
        }}
        
        ThemedGroupBox:disabled {{
            color: {border_color.name(QColor.NameFormat.HexArgb)};
        }}
        
        ThemedGroupBox::title:disabled {{
            color: {border_color.name(QColor.NameFormat.HexArgb)};
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

    def set_title_font_size(self, size: int) -> None:
        """
        设置标题字体大小。

        Args:
            size: 字体大小（像素）
        """
        logger.debug(f"Setting title font size: {size}px")
        self.override_style('groupbox.title.font_size', size)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_border_radius(self, radius: int) -> None:
        """
        设置边框圆角。

        Args:
            radius: 圆角半径（像素）
        """
        logger.debug(f"Setting border radius: {radius}px")
        self.override_style('groupbox.border_radius', radius)
        if self._current_theme:
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
            logger.debug("ThemedGroupBox unsubscribed from theme manager")

        self._clear_stylesheet_cache()
        self.clear_overrides()

    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedGroupBox scheduled for deletion")


GroupBox = ThemedGroupBox
