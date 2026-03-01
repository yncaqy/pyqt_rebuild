"""
Themed Widget - 主题化基础容器组件

提供主题感知的基础QWidget容器，自动响应主题切换。

Features:
- 自动主题集成与实时更新
- 主题一致的背景色
- 性能优化的样式缓存
- 内存安全的清理机制

Example:
    widget = ThemedWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(ThemedLabel("内容"))
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor

from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class ThemedWidgetConfig:
    """ThemedWidget配置常量"""
    
    DEFAULT_BACKGROUND_KEY = 'window.background'
    MAX_STYLESHEET_CACHE_SIZE = 10


class ThemedWidget(QWidget):
    """
    主题感知的基础容器组件。
    
    自动响应主题切换，提供一致的背景样式。
    用于替代原生QWidget作为布局容器。
    
    Attributes:
        _current_theme: 当前应用的主题
        _stylesheet_cache: 样式表缓存
        _bg_color_key: 主题中背景色的键名
        
    Example:
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(button)
    """
    
    def __init__(self, parent: Optional[QWidget] = None, bg_color_key: str = None):
        """
        初始化主题化容器。
        
        Args:
            parent: 父组件
            bg_color_key: 主题中背景色的键名，默认使用 'window.background'
        """
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        self._bg_color_key = bg_color_key or ThemedWidgetConfig.DEFAULT_BACKGROUND_KEY
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        logger.debug(f"ThemedWidget initialized with bg_key: {self._bg_color_key}")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题变更通知。
        
        Args:
            theme: 新主题
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedWidget: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题样式。
        
        Args:
            theme: 主题对象
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        bg_color = theme.get_color(self._bg_color_key, QColor(30, 30, 30))
        
        cache_key = (bg_color.name(),)
        
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            qss = f"""
            ThemedWidget {{
                background-color: {bg_color.name()};
            }}
            ThemedWidget:hover {{
                background-color: {bg_color.name()};
            }}
            """
            
            if len(self._stylesheet_cache) < ThemedWidgetConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                
        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedWidget: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def set_theme(self, name: str) -> None:
        """
        设置当前主题。
        
        Args:
            name: 主题名称
        """
        self._theme_mgr.set_theme(name)
        
    def get_theme(self) -> Optional[str]:
        """
        获取当前主题名称。
        
        Returns:
            当前主题名称，未设置则返回None
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None
        
    def cleanup(self) -> None:
        """清理资源并取消主题订阅"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedWidget unsubscribed from theme manager")
            
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            
    def deleteLater(self) -> None:
        """调度删除并自动清理"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedWidget scheduled for deletion")
