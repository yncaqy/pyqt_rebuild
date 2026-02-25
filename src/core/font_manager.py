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
- Support for different font categories (title, header, body, small)

The font manager works closely with ThemeManager to provide consistent
typography across the application.

Example:
    font_mgr = FontManager.instance()
    title_font = font_mgr.get_font('title')
    header_font = font_mgr.get_font('header', theme_override=some_theme)
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QObject

from .theme_manager import ThemeManager, Theme

# Initialize logger
logger = logging.getLogger(__name__)


class FontConfig:
    """Configuration constants for font management."""
    
    # Default font settings (fallback values)
    DEFAULT_FAMILY = "Segoe UI"
    DEFAULT_TITLE_SIZE = 16
    DEFAULT_HEADER_SIZE = 14
    DEFAULT_BODY_SIZE = 12
    DEFAULT_SMALL_SIZE = 10
    
    # Font weights
    WEIGHT_MAP = {
        'normal': QFont.Weight.Normal,
        'bold': QFont.Weight.Bold,
        'light': QFont.Weight.Light,
        'medium': QFont.Weight.Medium
    }
    
    # Performance
    MAX_FONT_CACHE_SIZE = 50


class FontManager(QObject):
    """
    Centralized font manager with theme integration.
    
    This class manages application fonts and ensures they stay synchronized
    with the current theme. It provides convenient methods for creating
    fonts based on theme settings.
    
    Attributes:
        _instance: Singleton instance
        _theme_mgr: Reference to theme manager
        _font_cache: Cache for created fonts
        _current_theme: Currently active theme
        
    Example:
        # Get themed font
        font_mgr = FontManager.instance()
        title_font = font_mgr.get_font('title')
        
        # Apply to widget
        label.setFont(title_font)
    """
    
    _instance: Optional['FontManager'] = None
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize font manager.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Initialize theme manager reference
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        # Font cache for performance optimization
        self._font_cache: Dict[Tuple[str, str], QFont] = {}
        
        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("FontManager initialized")
        
    @classmethod
    def instance(cls) -> 'FontManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification.
        
        Args:
            theme: New theme
        """
        try:
            self._current_theme = theme
            # Clear cache when theme changes to ensure fresh fonts
            self._font_cache.clear()
            logger.debug(f"Font cache cleared due to theme change: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        except Exception as e:
            logger.error(f"Error handling theme change in FontManager: {e}")
            
    def get_font(self, category: str = 'body', theme_override: Optional[Theme] = None) -> QFont:
        """
        Get themed font for specified category.
        
        Args:
            category: Font category ('title', 'header', 'body', 'small')
            theme_override: Optional theme to use instead of current
            
        Returns:
            QFont configured according to theme settings
            
        Example:
            title_font = font_mgr.get_font('title')
            body_font = font_mgr.get_font('body')
        """
        theme = theme_override or self._current_theme or self._theme_mgr.current_theme()
        
        if not theme:
            logger.warning("No theme available, returning default font")
            return self._create_default_font(category)
            
        # Create cache key
        theme_name = getattr(theme, 'name', 'unnamed')
        cache_key = (category, theme_name)
        
        # Check cache
        if cache_key in self._font_cache:
            logger.debug(f"Using cached font for {category}")
            return self._font_cache[cache_key]
            
        # Create new font
        font = self._create_themed_font(theme, category)
        
        # Cache the font (with size limit)
        if len(self._font_cache) < FontConfig.MAX_FONT_CACHE_SIZE:
            self._font_cache[cache_key] = font
            logger.debug(f"Font cached for {category} (cache size: {len(self._font_cache)})")
            
        return font
        
    def _create_themed_font(self, theme: Theme, category: str) -> QFont:
        """
        Create font based on theme settings.
        
        Args:
            theme: Theme to use for font configuration
            category: Font category
            
        Returns:
            Configured QFont instance
        """
        # Get font settings from theme
        font_family = theme.get_value('font.family', FontConfig.DEFAULT_FAMILY)
        
        # Get size for category
        size_key = f'font.size.{category}'
        default_sizes = {
            'title': FontConfig.DEFAULT_TITLE_SIZE,
            'header': FontConfig.DEFAULT_HEADER_SIZE,
            'body': FontConfig.DEFAULT_BODY_SIZE,
            'small': FontConfig.DEFAULT_SMALL_SIZE
        }
        size = theme.get_value(size_key, default_sizes.get(category, FontConfig.DEFAULT_BODY_SIZE))
        
        # Get weight for category
        weight_key = f'font.weight.{category}'
        weight_str = theme.get_value(weight_key, 'normal')
        weight = FontConfig.WEIGHT_MAP.get(weight_str, QFont.Weight.Normal)
        
        # Create font
        font = QFont(font_family, size, weight)
        
        logger.debug(f"Created themed font: {font_family}, size={size}, weight={weight_str}")
        return font
        
    def _create_default_font(self, category: str) -> QFont:
        """
        Create default font when no theme is available.
        
        Args:
            category: Font category
            
        Returns:
            Default QFont instance
        """
        default_sizes = {
            'title': FontConfig.DEFAULT_TITLE_SIZE,
            'header': FontConfig.DEFAULT_HEADER_SIZE,
            'body': FontConfig.DEFAULT_BODY_SIZE,
            'small': FontConfig.DEFAULT_SMALL_SIZE
        }
        
        size = default_sizes.get(category, FontConfig.DEFAULT_BODY_SIZE)
        font = QFont(FontConfig.DEFAULT_FAMILY, size)
        
        logger.debug(f"Created default font: {FontConfig.DEFAULT_FAMILY}, size={size}")
        return font
        
    def apply_font_to_widget(self, widget, category: str = 'body', 
                           theme_override: Optional[Theme] = None) -> None:
        """
        Apply themed font directly to widget.
        
        Args:
            widget: Widget to apply font to
            category: Font category
            theme_override: Optional theme override
            
        Example:
            font_mgr.apply_font_to_widget(label, 'title')
            font_mgr.apply_font_to_widget(button, 'body')
        """
        try:
            font = self.get_font(category, theme_override)
            widget.setFont(font)
            logger.debug(f"Applied {category} font to {widget.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error applying font to widget: {e}")
            
    def get_available_categories(self) -> list:
        """
        Get list of available font categories.
        
        Returns:
            List of supported font categories
        """
        return ['title', 'header', 'body', 'small']
        
    def clear_cache(self) -> None:
        """Clear font cache."""
        self._font_cache.clear()
        logger.debug("Font cache cleared")
        
    def cache_size(self) -> int:
        """Get current cache size."""
        return len(self._font_cache)