#!/usr/bin/env python3
"""
主题化分组框组件

提供带主题集成的 QGroupBox，根据当前应用主题自动更新颜色、字体和样式。

功能特性:
- 自动主题集成，实时更新
- 可自定义标题样式
- 主题一致的背景和边框颜色
- 优化的样式缓存，提升性能
- 内存安全，正确清理资源
- 本地样式覆盖，无需修改共享主题

分组框与主题管理器无缝集成，在整个应用程序中提供一致的样式。

使用示例:
    group = ThemedGroupBox("设置")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("选项 1"))
    group.setLayout(layout)
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class ThemedGroupBoxConfig:
    """主题化分组框配置常量。"""
    
    DEFAULT_TITLE_FONT_SIZE = 12
    DEFAULT_TITLE_FONT_WEIGHT = QFont.Weight.Bold
    DEFAULT_SPACING = 15
    
    MAX_STYLESHEET_CACHE_SIZE = 20


class ThemedGroupBox(QGroupBox, StyleOverrideMixin):
    """
    主题感知的分组框，支持自动样式更新。

    该组件根据当前应用主题自动调整外观，在整个用户界面中提供一致的样式。

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
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
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
            import traceback
            traceback.print_exc()
            
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
        
        border_radius = self.get_style_value(theme, 'groupbox.border_radius', 6)
        border_width = self.get_style_value(theme, 'groupbox.border_width', 1)
        
        font_size = self.get_style_value(theme, 'groupbox.title.font_size', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_SIZE)
        font_weight = self.get_style_value(theme, 'groupbox.title.font_weight', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_WEIGHT)
        
        cache_key = (
            bg_color.name(),
            border_color.name(),
            title_color.name(),
            border_radius,
            border_width,
            font_size,
            font_weight,
        )
        
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            qss = self._build_stylesheet(
                theme, bg_color, border_color, title_color,
                border_radius, border_width, font_size, font_weight
            )
            
            if len(self._stylesheet_cache) < ThemedGroupBoxConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                
        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
    def _build_stylesheet(self, theme: Theme, bg_color: QColor, border_color: QColor,
                         title_color: QColor, border_radius: int, border_width: int,
                         font_size: int, font_weight: QFont.Weight) -> str:
        """
        从主题属性构建 QSS 样式表。

        Args:
            theme: 主题对象
            bg_color: 背景颜色
            border_color: 边框颜色
            title_color: 标题文本颜色
            border_radius: 边框圆角（像素）
            border_width: 边框宽度（像素）
            font_size: 标题字体大小
            font_weight: 标题字体粗细

        Returns:
            完整的 QSS 样式表字符串
        """
        qss = f"""
        ThemedGroupBox {{
            background-color: {bg_color.name()};
            border: {border_width}px solid {border_color.name()};
            border-radius: {border_radius}px;
            margin-top: 1ex;
            padding-top: {ThemedGroupBoxConfig.DEFAULT_SPACING}px;
            font-size: {font_size}px;
        }}
        
        ThemedGroupBox:hover {{
            background-color: {bg_color.name()};
        }}
        
        ThemedGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            background-color: transparent;
            color: {title_color.name()};
            font-weight: {font_weight};
            font-size: {font_size}px;
        }}
        
        ThemedGroupBox:disabled {{
            color: {border_color.name()};
        }}
        
        ThemedGroupBox::title:disabled {{
            color: {border_color.name()};
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
            
    def cleanup(self) -> None:
        """清理资源并取消主题管理器订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedGroupBox unsubscribed from theme manager")
            
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")
        
        self.clear_overrides()
            
    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedGroupBox scheduled for deletion")


GroupBox = ThemedGroupBox
