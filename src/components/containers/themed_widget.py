"""
Themed Widget - 主题化基础容器组件

提供主题感知的基础QWidget容器，自动响应主题切换。

Features:
- 自动主题集成与实时更新
- 主题一致的背景色
- 性能优化的样式缓存
- 内存安全的清理机制
- 自动资源清理

Example:
    widget = ThemedWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(ThemedLabel("内容"))
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor

from core.theme_manager import ThemeManager, Theme
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class ThemedWidgetConfig:
    """ThemedWidget配置常量"""
    
    DEFAULT_BACKGROUND_KEY = 'window.background'


class ThemedWidget(QWidget, StylesheetCacheMixin):
    """
    主题感知的基础容器组件。
    
    自动响应主题切换，提供一致的背景样式。
    用于替代原生QWidget作为布局容器。
    """
    
    def __init__(self, parent: Optional[QWidget] = None, bg_color_key: str = None):
        super().__init__(parent)
        
        self._init_stylesheet_cache(max_size=10)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        self._bg_color_key = bg_color_key or ThemedWidgetConfig.DEFAULT_BACKGROUND_KEY
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        logger.debug(f"ThemedWidget initialized with bg_key: {self._bg_color_key}")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedWidget: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        bg_color = theme.get_color(self._bg_color_key, QColor(30, 30, 30))
        
        cache_key = (bg_color.name(),)
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: f"""
            ThemedWidget {{
                background-color: {bg_color.name()};
            }}
            ThemedWidget:hover {{
                background-color: {bg_color.name()};
            }}
            """
        )
                
        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedWidget: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def set_theme(self, name: str) -> None:
        self._theme_mgr.set_theme(name)
        
    def get_theme(self) -> Optional[str]:
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()
        
    def cleanup(self) -> None:
        """
        清理资源并取消主题订阅。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedWidget unsubscribed from theme manager")
            
        self._clear_stylesheet_cache()
            
    def deleteLater(self) -> None:
        """调度删除并自动清理"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedWidget scheduled for deletion")
