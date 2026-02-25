#!/usr/bin/env python3
"""
Themed Scroll Area Component

Provides a QScrollArea with theme integration that automatically updates
scrollbar colors, background, and styling based on the current application theme.

Features:
- Automatic theme integration with real-time updates
- Theme-consistent scrollbar styling
- Customizable scroll behavior
- Optimized style caching for performance
- Memory-safe with proper cleanup

The scroll area integrates seamlessly with the theme manager and provides
consistent scrolling experience across the application.

Example:
    scroll_area = ThemedScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    scroll_area.setWidget(content_widget)
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QScrollArea, QWidget, QScrollBar
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

# Initialize logger
logger = logging.getLogger(__name__)


class ThemedScrollAreaConfig:
    """Configuration constants for themed scroll area."""
    
    DEFAULT_SCROLLBAR_WIDTH = 8
    DEFAULT_SCROLLBAR_WIDTH_HOVER = 12
    DEFAULT_SCROLLBAR_MIN_LENGTH = 30
    
    MAX_STYLESHEET_CACHE_SIZE = 15


class ThemedScrollArea(QScrollArea):
    """
    Theme-aware scroll area with automatic styling updates.
    
    This component automatically adapts its appearance based on the
    current application theme, providing consistent scrolling experience
    across the user interface.
    
    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets
        _vertical_scrollbar: Custom vertical scrollbar
        _horizontal_scrollbar: Custom horizontal scrollbar
        
    Example:
        scroll_area = ThemedScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the themed scroll area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize theme manager reference
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        
        # Setup custom scrollbars
        self._setup_scrollbars()
        
        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        logger.debug("ThemedScrollArea initialized")
        
    def _setup_scrollbars(self):
        """Setup custom scrollbars with theme support."""
        self._vertical_scrollbar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._vertical_scrollbar)
        
        self._horizontal_scrollbar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        self.setHorizontalScrollBar(self._horizontal_scrollbar)
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.
        
        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ThemedScrollArea: {e}")
            import traceback
            traceback.print_exc()
            
    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to scroll area with caching support.
        
        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        bg_color = theme.get_color('scrollarea.background', QColor(255, 255, 255))
        border_color = theme.get_color('scrollarea.border', QColor(200, 200, 200))
        border_radius = theme.get_value('scrollarea.border_radius', 4)
        border_width = theme.get_value('scrollarea.border_width', 1)
        
        cache_key = (
            bg_color.name(),
            border_color.name(),
            border_radius,
            border_width,
        )
        
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            qss = self._build_stylesheet(bg_color, border_color, border_radius, border_width)
            
            if len(self._stylesheet_cache) < ThemedScrollAreaConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
        
        self.setStyleSheet(qss)
        
        self.style().unpolish(self)
        self.style().polish(self)
        
        logger.debug(f"Theme applied to ThemedScrollArea: {theme.name if hasattr(theme, 'name') else 'unknown'}")
        
    def _build_stylesheet(self, bg_color: QColor, border_color: QColor,
                         border_radius: int, border_width: int) -> str:
        """
        Build QSS stylesheet from theme properties.
        
        Args:
            bg_color: Background color
            border_color: Border color
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            
        Returns:
            Complete QSS stylesheet string
        """
        qss = f"""
        ThemedScrollArea {{
            background-color: {bg_color.name() if bg_color.alpha() > 0 else 'transparent'};
            border: {border_width}px solid {border_color.name() if border_color.alpha() > 0 else 'transparent'};
            border-radius: {border_radius}px;
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
        
    def set_scrollbar_width(self, width: int) -> None:
        """
        Set the scrollbar width.
        
        Args:
            width: Scrollbar width in pixels
        """
        logger.debug(f"Setting scrollbar width: {width}px")
        if self._current_theme:
            self._current_theme.set_value('scrollbar.width', width)
            self._apply_theme(self._current_theme)
            
    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.
        """
        # Unsubscribe from theme manager
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedScrollArea unsubscribed from theme manager")
            
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
        logger.debug("ThemedScrollArea scheduled for deletion")


# Backward compatibility alias
ScrollArea = ThemedScrollArea