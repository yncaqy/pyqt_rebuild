#!/usr/bin/env python3
"""
WinUI3 风格主题化标签组件

遵循 WinUI3 设计规范，提供自动主题适配的文本标签。
支持 WinUI3 的字体层级系统（Type Ramp）和颜色系统。

字体层级:
- caption: 12px, 用于辅助说明文字
- body: 14px, 用于正文内容
- body_strong: 14px semibold, 用于强调正文
- body_large: 18px, 用于大号正文
- subtitle: 20px semibold, 用于副标题
- title: 28px semibold, 用于标题
- title_large: 40px semibold, 用于大标题
- display: 68px semibold, 用于展示文字

Example:
    label = ThemedLabel("Hello World")
    label.set_category('title')
    label.set_alignment(Qt.AlignmentFlag.AlignCenter)
"""

from typing import Optional, Any
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import logging

try:
    from core.theme_manager import ThemeManager, Theme
    from core.stylesheet_cache_mixin import StylesheetCacheMixin
    from core.font_manager import FontManager
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.stylesheet_cache_mixin import StylesheetCacheMixin
    from ...core.font_manager import FontManager

logger = logging.getLogger(__name__)


class ThemedLabelConfig:
    """ThemedLabel 配置常量，遵循 WinUI3 设计规范。"""
    
    DEFAULT_ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    DEFAULT_WORD_WRAP = False
    DEFAULT_OPEN_EXTERNAL_LINKS = False
    
    FONT_CATEGORIES = ['caption', 'body', 'body_strong', 'body_large', 'subtitle', 'title', 'title_large', 'display']


class ThemedLabel(QLabel, StylesheetCacheMixin):
    """
    WinUI3 风格主题化标签。
    
    自动适配主题，支持 WinUI3 字体层级系统。
    
    Example:
        label = ThemedLabel("Status: Ready")
        label.set_category('body')
        label.set_alignment(Qt.AlignmentFlag.AlignCenter)
    """
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None, 
                 font_role: str = 'body'):
        super().__init__(text, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._init_stylesheet_cache(max_size=50)
        
        self._font_category = font_role if font_role in ThemedLabelConfig.FONT_CATEGORIES else 'body'
        self._text_color_role = f'label.text.{self._font_category}'
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
            
        logger.debug(f"ThemedLabel initialized with text: '{text}', font_role: '{font_role}'")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedLabel: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        text_color = theme.get_color(self._text_color_role)
        if text_color is None:
            is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True
            text_color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0, 228)
        
        bg_color = theme.get_color('label.background', QColor(0, 0, 0, 0))
        
        disabled_color = theme.get_color('label.text.disabled')
        if disabled_color is None:
            is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True
            disabled_color = QColor(255, 255, 255, 92) if is_dark else QColor(0, 0, 0, 92)
        
        cache_key = (
            text_color.name() if hasattr(text_color, 'name') else str(text_color),
            bg_color.name() if hasattr(bg_color, 'name') else str(bg_color),
            self._font_category,
        )
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(text_color, bg_color, disabled_color)
        )
                
        self.setStyleSheet(qss)
        self._apply_font()
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedLabel: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def _build_stylesheet(self, text_color: QColor, bg_color: QColor, disabled_color: QColor) -> str:
        if bg_color.alpha() == 0:
            bg_css = "transparent"
        else:
            bg_css = bg_color.name()
            
        return f"""
        ThemedLabel {{
            color: {text_color.name()};
            background-color: {bg_css};
        }}
        
        ThemedLabel:disabled {{
            color: {disabled_color.name()};
            background-color: {bg_css};
        }}
        """
        
    def _apply_font(self) -> None:
        """应用 WinUI3 字体样式。"""
        font = FontManager.instance().get_font(self._font_category)
        self.setFont(font)
        logger.debug(f"Applied {self._font_category} font to ThemedLabel")
            
    def set_category(self, category: str) -> None:
        """
        设置字体类别。
        
        Args:
            category: 字体类别 ('caption', 'body', 'body_strong', 'body_large', 
                      'subtitle', 'title', 'title_large', 'display')
        """
        if category in ThemedLabelConfig.FONT_CATEGORIES:
            self._font_category = category
            self._text_color_role = f'label.text.{category}'
            self._apply_font()
            self._apply_theme(self._current_theme or self._theme_mgr.current_theme())
            logger.debug(f"Font category set to: {category}")
        else:
            logger.warning(f"Invalid font category: {category}, valid options: {ThemedLabelConfig.FONT_CATEGORIES}")
            
    def get_category(self) -> str:
        return self._font_category
        
    def set_text_color_role(self, role: str) -> None:
        self._text_color_role = role
        if self._current_theme:
            self._apply_theme(self._current_theme)
            
    def get_text_color_role(self) -> str:
        return self._text_color_role
        
    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._alignment = alignment
        self.setAlignment(alignment)
        
    def get_alignment(self) -> Qt.AlignmentFlag:
        return self._alignment
        
    def set_word_wrap(self, wrap: bool) -> None:
        self._word_wrap = wrap
        self.setWordWrap(wrap)
        
    def get_word_wrap(self) -> bool:
        return self._word_wrap
        
    def set_theme(self, name: str) -> None:
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)
        
    def get_theme(self) -> Optional[str]:
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None
        
    def _on_widget_destroyed(self) -> None:
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedLabel unsubscribed from theme manager")
            
        self._clear_stylesheet_cache()
            
    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedLabel scheduled for deletion")
