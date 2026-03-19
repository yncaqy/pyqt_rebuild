#!/usr/bin/env python3
"""
Themed Label Component

Provides QLabel with automatic theme integration and styling updates.
This component automatically adapts its appearance based on the current
application theme, ensuring consistent text presentation across the UI.

Features:
- Automatic theme synchronization
- Configurable text styling (color, font, alignment)
- Performance-optimized stylesheet caching
- Memory-safe with proper cleanup
- Automatic resource cleanup

Example:
    label = ThemedLabel("Hello World")
    label.set_category('title')  # Apply title font styling
    label.set_alignment(Qt.AlignmentFlag.AlignCenter)
"""

from typing import Optional, Tuple, Any
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import logging

try:
    from core.theme_manager import ThemeManager, Theme
    from core.font_manager import FontManager
    from core.stylesheet_cache_mixin import StylesheetCacheMixin
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.font_manager import FontManager
    from ...core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class ThemedLabelConfig:
    """Configuration constants for ThemedLabel."""
    
    DEFAULT_ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    DEFAULT_WORD_WRAP = False
    DEFAULT_OPEN_EXTERNAL_LINKS = False


class ThemedLabel(QLabel, StylesheetCacheMixin):
    """
    Theme-aware label with automatic styling updates.
    
    This component automatically adapts its appearance based on the
    current application theme, providing consistent text styling across
    the user interface.
    
    Example:
        label = ThemedLabel("Status: Ready")
        label.set_category('body')
        label.set_alignment(Qt.AlignmentFlag.AlignCenter)
    """
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None, 
                 font_role: str = 'body'):
        super().__init__(text, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._font_mgr = FontManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._init_stylesheet_cache(max_size=50)
        
        self._font_category = font_role
        self._text_color_role = f'label.text.{font_role}'
        self._alignment = ThemedLabelConfig.DEFAULT_ALIGNMENT
        self._word_wrap = ThemedLabelConfig.DEFAULT_WORD_WRAP
        
        self.setAlignment(self._alignment)
        self.setWordWrap(self._word_wrap)
        self.setOpenExternalLinks(ThemedLabelConfig.DEFAULT_OPEN_EXTERNAL_LINKS)
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        self._apply_font()
            
        logger.debug(f"ThemedLabel initialized with text: '{text}', font_role: '{font_role}'")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
            self._apply_font()
        except Exception as e:
            logger.error(f"Error applying theme to ThemedLabel: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        text_color = theme.get_color(self._text_color_role, QColor(50, 50, 50))
        bg_color = theme.get_color('label.background', QColor(0, 0, 0, 0))
        
        cache_key = (
            text_color.name(),
            bg_color.name(),
            self._font_category,
        )
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, text_color, bg_color)
        )
                
        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedLabel: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def _build_stylesheet(self, theme: Theme, text_color: QColor, bg_color: QColor) -> str:
        """
        Build QSS stylesheet from theme properties.
        
        Args:
            theme: Theme object
            text_color: Text color
            bg_color: Background color
            
        Returns:
            Complete QSS stylesheet string
        """
        if bg_color.alpha() == 0:
            bg_css = "transparent"
        else:
            bg_css = bg_color.name()
            
        qss = f"""
        ThemedLabel {{
            color: {text_color.name()};
            background-color: {bg_css};
        }}
        
        ThemedLabel:disabled {{
            color: {theme.get_color('label.text.disabled', QColor(150, 150, 150)).name()};
            background-color: {bg_css};
        }}
        """
        return qss
        
    def _apply_font(self) -> None:
        """Apply themed font to label."""
        try:
            font = self._font_mgr.get_font(self._font_category, self._current_theme)
            self.setFont(font)
            logger.debug(f"Applied {self._font_category} font to ThemedLabel")
        except Exception as e:
            logger.error(f"Error applying font to ThemedLabel: {e}")
            
    def set_category(self, category: str) -> None:
        """
        Set font category for styling.
        
        Args:
            category: Font category ('title', 'header', 'body', 'small')
        """
        if category in ['title', 'header', 'body', 'small']:
            self._font_category = category
            self._text_color_role = f'label.text.{category}'
            self._apply_font()
            self._apply_theme(self._current_theme or self._theme_mgr.current_theme())
            logger.debug(f"Font category set to: {category}")
        else:
            logger.warning(f"Invalid font category: {category}")
            
    def get_category(self) -> str:
        """
        Get current font category.
        
        Returns:
            Current font category
        """
        return self._font_category
        
    def set_text_color_role(self, role: str) -> None:
        """
        Set theme color role for text color.
        
        Args:
            role: Theme color role (e.g., 'label.text', 'button.text')
        """
        self._text_color_role = role
        if self._current_theme:
            self._apply_theme(self._current_theme)
            
    def get_text_color_role(self) -> str:
        """
        Get current text color role.
        
        Returns:
            Current text color role
        """
        return self._text_color_role
        
    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        """
        Set text alignment.
        
        Args:
            alignment: Text alignment flags
        """
        self._alignment = alignment
        self.setAlignment(alignment)
        
    def get_alignment(self) -> Qt.AlignmentFlag:
        """
        Get current text alignment.
        
        Returns:
            Current alignment flags
        """
        return self._alignment
        
    def set_word_wrap(self, wrap: bool) -> None:
        """
        Set word wrap behavior.
        
        Args:
            wrap: Enable/disable word wrapping
        """
        self._word_wrap = wrap
        self.setWordWrap(wrap)
        
    def get_word_wrap(self) -> bool:
        """
        Get word wrap setting.
        
        Returns:
            Current word wrap setting
        """
        return self._word_wrap
        
    def set_theme(self, name: str) -> None:
        """
        Set the current theme by name.
        
        Args:
            name: Theme name (e.g., 'dark', 'light', 'default')
        """
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)
        
    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name.
        
        Returns:
            Current theme name, or None if no theme is set
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None
        
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
            logger.debug("ThemedLabel unsubscribed from theme manager")
            
        self._clear_stylesheet_cache()
            
    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedLabel scheduled for deletion")