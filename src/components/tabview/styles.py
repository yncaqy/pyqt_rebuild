"""
TabView 样式定义

严格遵循 WinUI3 TabView 设计规范。
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject

from .config import TabViewColors
from src.core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class TabViewStyle:
    """
    TabView 样式管理类。

    提供统一的样式获取接口，支持主题切换。
    与 ThemeManager 集成，自动响应主题变化。
    """

    _dark_mode: bool = True

    @classmethod
    def is_dark_mode(cls) -> bool:
        """检查是否为暗色模式。"""
        theme = ThemeManager.instance().current_theme()
        if theme is not None and hasattr(theme, 'is_dark'):
            return theme.is_dark
        return cls._dark_mode

    @classmethod
    def get_colors(cls) -> Dict[str, Any]:
        """获取当前主题的颜色配置。"""
        return TabViewColors.DARK if cls.is_dark_mode() else TabViewColors.LIGHT

    @classmethod
    def get_color(cls, key: str) -> QColor:
        """
        获取指定键的颜色。

        Args:
            key: 颜色键名

        Returns:
            QColor 对象
        """
        colors = cls.get_colors()
        value = colors.get(key)

        if value is None:
            return QColor(128, 128, 128)

        if isinstance(value, tuple):
            if len(value) == 3:
                return QColor(*value)
            elif len(value) == 4:
                return QColor(*value)
        elif isinstance(value, str):
            return QColor(value)

        return QColor(128, 128, 128)

    @classmethod
    def get_tabstrip_background(cls) -> QColor:
        """获取标签条背景颜色。"""
        return cls.get_color('tabstrip_background')

    @classmethod
    def get_tab_background_selected(cls) -> QColor:
        """获取选中标签背景颜色。"""
        return cls.get_color('tab_background_selected')

    @classmethod
    def get_tab_background_hover(cls) -> QColor:
        """获取悬停标签背景颜色。"""
        return cls.get_color('tab_background_hover')

    @classmethod
    def get_tab_background_pressed(cls) -> QColor:
        """获取按下标签背景颜色。"""
        return cls.get_color('tab_background_pressed')

    @classmethod
    def get_tab_text(cls, selected: bool = False, hovered: bool = False) -> QColor:
        """
        获取标签文本颜色。

        Args:
            selected: 是否选中
            hovered: 是否悬停

        Returns:
            QColor 对象
        """
        if selected:
            return cls.get_color('tab_text_selected')
        elif hovered:
            return cls.get_color('tab_text_hover')
        else:
            return cls.get_color('tab_text')

    @classmethod
    def get_close_icon_color(cls, hovered: bool = False) -> QColor:
        """获取关闭图标颜色。"""
        return cls.get_color('close_icon_hover' if hovered else 'close_icon')

    @classmethod
    def get_close_background(cls, hovered: bool = False, pressed: bool = False) -> QColor:
        """获取关闭按钮背景颜色。"""
        if pressed:
            return cls.get_color('close_background_pressed')
        elif hovered:
            return cls.get_color('close_background_hover')
        return QColor(0, 0, 0, 0)

    @classmethod
    def get_add_icon_color(cls, hovered: bool = False) -> QColor:
        """获取添加按钮图标颜色。"""
        return cls.get_color('add_icon_hover' if hovered else 'add_icon')

    @classmethod
    def get_scroll_icon_color(cls) -> QColor:
        """获取滚动按钮图标颜色。"""
        return cls.get_color('scroll_icon')

    @classmethod
    def get_focus_border_color(cls) -> QColor:
        """获取焦点边框颜色。"""
        return cls.get_color('focus_border')
