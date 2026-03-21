#!/usr/bin/env python3
"""
Font Manager for Theme Integration

Provides centralized font management that integrates with the theme system
to enable dynamic font switching based on current theme.

Features:
- Theme-aware font creation and application
- Font family, size, and weight management
- Dynamic font updates when theme changes
- Performance optimization with font caching
- Support for different font categories
- Anti-aliasing and subpixel rendering support
- High DPI scaling support
- Global font application

Example:
    font_mgr = FontManager.instance()
    title_font = font_mgr.get_font('title')
    body_font = font_mgr.get_font('body')
    
    # Or use static method
    font = FontManager.get_body_font()
"""

import logging
from typing import Optional, Dict, Tuple
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import QObject

from .theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class FontConfig:
    """Configuration constants for font management."""
    
    DEFAULT_FAMILY = "Segoe UI Variable"
    DEFAULT_FAMILY_FALLBACK = "Segoe UI"
    
    FONT_SIZES = {
        'display': 68,
        'title_large': 40,
        'title': 28,
        'subtitle': 20,
        'body_large': 18,
        'body_strong': 14,
        'body': 14,
        'header': 14,
        'caption': 12,
        'small': 10,
        'button': 12,
        'menu': 12,
        'tooltip': 11,
    }
    
    FONT_WEIGHTS = {
        'display': 'semibold',
        'title_large': 'semibold',
        'title': 'semibold',
        'subtitle': 'semibold',
        'body_large': 'normal',
        'body_strong': 'semibold',
        'body': 'normal',
        'header': 'semibold',
        'caption': 'normal',
        'small': 'normal',
        'button': 'normal',
        'menu': 'normal',
        'tooltip': 'normal',
    }
    
    WEIGHT_MAP = {
        'normal': QFont.Weight.Normal,
        'bold': QFont.Weight.Bold,
        'light': QFont.Weight.Light,
        'medium': QFont.Weight.Medium,
        'demibold': QFont.Weight.DemiBold,
        'semibold': QFont.Weight.DemiBold,
    }
    
    MAX_FONT_CACHE_SIZE = 100
    
    PREFERRED_FONTS = [
        "Segoe UI Variable",
        "Segoe UI",
        "Microsoft YaHei UI",
        "PingFang SC",
        "Noto Sans CJK SC",
        "Arial",
    ]


class FontManager(QObject):
    """
    Centralized font manager with theme integration.
    
    This class manages application fonts and ensures they stay synchronized
    with the current theme. It provides convenient methods for creating
    fonts based on theme settings.
    """
    
    _instance: Optional['FontManager'] = None
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = self._theme_mgr.current_theme()
        self._font_cache: Dict[Tuple[str, str], QFont] = {}
        self._resolved_family: Optional[str] = None
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("FontManager initialized")
        
    @classmethod
    def instance(cls) -> 'FontManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_body_font(cls) -> QFont:
        """Get body font (static convenience method)."""
        return cls.instance().get_font('body')
    
    @classmethod
    def get_caption_font(cls) -> QFont:
        """Get caption font (static convenience method)."""
        return cls.instance().get_font('caption')
    
    @classmethod
    def get_small_font(cls) -> QFont:
        """Get small font (static convenience method)."""
        return cls.instance().get_font('small')
    
    @classmethod
    def get_button_font(cls) -> QFont:
        """Get button font (static convenience method)."""
        return cls.instance().get_font('button')
    
    @classmethod
    def get_menu_font(cls) -> QFont:
        """Get menu font (static convenience method)."""
        return cls.instance().get_font('menu')
    
    @classmethod
    def get_tooltip_font(cls) -> QFont:
        """Get tooltip font (static convenience method)."""
        return cls.instance().get_font('tooltip')
    
    @classmethod
    def get_header_font(cls) -> QFont:
        """Get header font (static convenience method)."""
        return cls.instance().get_font('header')
    
    @classmethod
    def get_title_font(cls) -> QFont:
        """Get title font (static convenience method)."""
        return cls.instance().get_font('title')
        
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._current_theme = theme
            self._font_cache.clear()
            self._resolved_family = None
            logger.debug(f"Font cache cleared due to theme change")
        except Exception as e:
            logger.error(f"Error handling theme change in FontManager: {e}")
    
    def get_resolved_family(self) -> str:
        """Get the resolved font family name."""
        if self._resolved_family is None:
            self._resolved_family = self._get_best_font_family(FontConfig.DEFAULT_FAMILY)
        return self._resolved_family
            
    def get_font(self, category: str = 'body', theme_override: Optional[Theme] = None) -> QFont:
        """
        Get themed font for specified category.
        
        Args:
            category: Font category (see FontConfig.FONT_SIZES)
            theme_override: Optional theme to use instead of current
            
        Returns:
            QFont configured according to theme settings
        """
        theme = theme_override or self._current_theme or self._theme_mgr.current_theme()
        
        if not theme:
            logger.warning("No theme available, returning default font")
            return self._create_default_font(category)
            
        theme_name = getattr(theme, 'name', 'unnamed')
        cache_key = (category, theme_name)
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
            
        font = self._create_themed_font(theme, category)
        
        if len(self._font_cache) < FontConfig.MAX_FONT_CACHE_SIZE:
            self._font_cache[cache_key] = font
            
        return font
        
    def _create_themed_font(self, theme: Theme, category: str) -> QFont:
        font_family = self.get_resolved_family()
        
        size_key = f'font.size.{category}'
        pixel_size = theme.get_value(size_key, FontConfig.FONT_SIZES.get(category, 12))
        
        if pixel_size is None or (isinstance(pixel_size, (int, float)) and pixel_size <= 0):
            logger.warning(f"Invalid pixel_size for category '{category}': {pixel_size}, using default")
            pixel_size = FontConfig.FONT_SIZES.get(category, 12)
            if not pixel_size or pixel_size <= 0:
                pixel_size = 12
        
        weight_key = f'font.weight.{category}'
        weight_str = theme.get_value(weight_key, FontConfig.FONT_WEIGHTS.get(category, 'normal'))
        weight = FontConfig.WEIGHT_MAP.get(weight_str, QFont.Weight.Normal)
        
        font = QFont(font_family)
        font.setPixelSize(int(pixel_size))
        font.setWeight(weight)
        self._apply_antialiasing(font)
        
        return font
        
    def _create_default_font(self, category: str) -> QFont:
        pixel_size = FontConfig.FONT_SIZES.get(category, 12)
        if not pixel_size or pixel_size <= 0:
            logger.warning(f"Invalid default pixel_size for category '{category}': {pixel_size}, using 12")
            pixel_size = 12
        font_family = self.get_resolved_family()
        font = QFont(font_family)
        font.setPixelSize(int(pixel_size))
        self._apply_antialiasing(font)
        
        return font
    
    def _get_best_font_family(self, preferred: str) -> str:
        available_families = QFontDatabase.families()
        
        if preferred in available_families:
            return preferred
            
        for family in FontConfig.PREFERRED_FONTS:
            if family in available_families:
                logger.debug(f"Using fallback font: {family}")
                return family
                
        return FontConfig.DEFAULT_FAMILY_FALLBACK
    
    def _apply_antialiasing(self, font: QFont) -> None:
        font.setStyleStrategy(
            QFont.StyleStrategy.PreferAntialias |
            QFont.StyleStrategy.PreferQuality
        )
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        
    def apply_font_to_widget(self, widget, category: str = 'body', 
                           theme_override: Optional[Theme] = None) -> None:
        """
        Apply themed font directly to widget.
        
        Args:
            widget: Widget to apply font to
            category: Font category
            theme_override: Optional theme override
        """
        try:
            font = self.get_font(category, theme_override)
            widget.setFont(font)
        except Exception as e:
            logger.error(f"Error applying font to widget: {e}")
            
    def get_available_categories(self) -> list:
        """Get list of available font categories."""
        return list(FontConfig.FONT_SIZES.keys())
        
    def clear_cache(self) -> None:
        """Clear font cache."""
        self._font_cache.clear()
        logger.debug("Font cache cleared")
        
    def cache_size(self) -> int:
        """Get current cache size."""
        return len(self._font_cache)


def get_font(category: str = 'body') -> QFont:
    """Convenience function to get font by category."""
    return FontManager.get_body_font() if category == 'body' else FontManager.instance().get_font(category)


def apply_global_font(app) -> None:
    """
    Apply global font settings to QApplication.
    
    Args:
        app: QApplication instance
    """
    font_mgr = FontManager.instance()
    font = font_mgr.get_font('body')
    app.setFont(font)
    logger.info(f"Global font applied: {font.family()}, pixelSize={font.pixelSize()}")
