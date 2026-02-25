#!/usr/bin/env python3
"""
Themed Group Box Component

Provides a QGroupBox with theme integration that automatically updates
colors, fonts, and styling based on the current application theme.

Features:
- Automatic theme integration with real-time updates
- Customizable title styling
- Theme-consistent background and border colors
- Optimized style caching for performance
- Memory-safe with proper cleanup

The group box integrates seamlessly with the theme manager and provides
consistent styling across the application.

Example:
    group = ThemedGroupBox("Settings")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Option 1"))
    group.setLayout(layout)
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager, Theme

# Initialize logger
logger = logging.getLogger(__name__)


class ThemedGroupBoxConfig:
    """Configuration constants for themed group box."""
    
    # Default styling
    DEFAULT_TITLE_FONT_SIZE = 12
    DEFAULT_TITLE_FONT_WEIGHT = QFont.Weight.Bold
    DEFAULT_SPACING = 15
    
    # Performance
    MAX_STYLESHEET_CACHE_SIZE = 20


class ThemedGroupBox(QGroupBox):
    """
    Theme-aware group box with automatic styling updates.
    
    This component automatically adapts its appearance based on the
    current application theme, providing consistent styling across
    the user interface.
    
    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets
        
    Example:
        group = ThemedGroupBox("User Settings")
        group.setLayout(QVBoxLayout())
    """
    
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        """
        Initialize the themed group box.
        
        Args:
            title: Group box title text
            parent: Parent widget
        """
        super().__init__(title, parent)
        
        # Initialize theme manager reference
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        
        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        logger.debug(f"ThemedGroupBox initialized with title: '{title}'")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.
        
        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedGroupBox: {e}")
            import traceback
            traceback.print_exc()
            
    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to group box with caching support.
        
        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        # Get colors with fallback defaults
        bg_color = theme.get_color('groupbox.background', QColor(255, 255, 255))
        border_color = theme.get_color('groupbox.border', QColor(200, 200, 200))
        title_color = theme.get_color('groupbox.title.color', QColor(50, 50, 50))
        
        border_radius = theme.get_value('groupbox.border_radius', 6)
        border_width = theme.get_value('groupbox.border_width', 1)
        
        font_size = theme.get_value('groupbox.title.font_size', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_SIZE)
        font_weight = theme.get_value('groupbox.title.font_weight', ThemedGroupBoxConfig.DEFAULT_TITLE_FONT_WEIGHT)
        
        # Create cache key
        cache_key = (
            bg_color.name(),
            border_color.name(),
            title_color.name(),
            border_radius,
            border_width,
            font_size,
            font_weight,
        )
        
        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for ThemedGroupBox")
        else:
            # Build stylesheet
            qss = self._build_stylesheet(
                theme, bg_color, border_color, title_color,
                border_radius, border_width, font_size, font_weight
            )
            
            # Cache the stylesheet
            if len(self._stylesheet_cache) < ThemedGroupBoxConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")
                
        # Apply stylesheet
        self.setStyleSheet(qss)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedGroupBox: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def _build_stylesheet(self, theme: Theme, bg_color: QColor, border_color: QColor,
                         title_color: QColor, border_radius: int, border_width: int,
                         font_size: int, font_weight: QFont.Weight) -> str:
        """
        Build QSS stylesheet from theme properties.
        
        Args:
            theme: Theme object
            bg_color: Background color
            border_color: Border color
            title_color: Title text color
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            font_size: Title font size
            font_weight: Title font weight
            
        Returns:
            Complete QSS stylesheet string
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
        
    def set_title_font_size(self, size: int) -> None:
        """
        Set the title font size.
        
        Args:
            size: Font size in pixels
        """
        logger.debug(f"Setting title font size: {size}px")
        if self._current_theme:
            self._current_theme.set_value('groupbox.title_font_size', size)
            self._apply_theme(self._current_theme)
            
    def set_border_radius(self, radius: int) -> None:
        """
        Set the border radius.
        
        Args:
            radius: Border radius in pixels
        """
        logger.debug(f"Setting border radius: {radius}px")
        if self._current_theme:
            self._current_theme.set_value('groupbox.border_radius', radius)
            self._apply_theme(self._current_theme)
            
    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.
        """
        # Unsubscribe from theme manager
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedGroupBox unsubscribed from theme manager")
            
        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")
            
    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("ThemedGroupBox scheduled for deletion")


# Backward compatibility alias
GroupBox = ThemedGroupBox