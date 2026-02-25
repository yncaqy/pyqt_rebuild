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
- Support for all QLabel features plus theme awareness

Example:
    label = ThemedLabel("Hello World")
    label.set_category('title')  # Apply title font styling
    label.set_alignment(Qt.AlignmentFlag.AlignCenter)
"""

from typing import Optional, Dict, Tuple, Any
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
import logging

# Absolute imports with fallback
try:
    from core.theme_manager import ThemeManager, Theme
    from core.font_manager import FontManager
except ImportError:
    # Fallback for relative imports
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.font_manager import FontManager

logger = logging.getLogger(__name__)


class ThemedLabelConfig:
    """Configuration constants for ThemedLabel."""
    
    # Default styling
    DEFAULT_ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    DEFAULT_WORD_WRAP = False
    DEFAULT_OPEN_EXTERNAL_LINKS = False
    
    # Performance
    MAX_STYLESHEET_CACHE_SIZE = 50


class ThemedLabel(QLabel):
    """
    Theme-aware label with automatic styling updates.
    
    This component automatically adapts its appearance based on the
    current application theme, providing consistent text styling across
    the user interface.
    
    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets
        _font_category: Font category for styling ('title', 'header', 'body', 'small')
        _text_color_role: Theme color role for text color
        _alignment: Text alignment
        _word_wrap: Word wrap setting
        
    Example:
        label = ThemedLabel("Status: Ready")
        label.set_category('body')
        label.set_alignment(Qt.AlignmentFlag.AlignCenter)
    """
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None, 
                 font_role: str = 'body'):
        """
        Initialize the themed label.
        
        Args:
            text: Label text content
            parent: Parent widget
            font_role: Font category ('title', 'header', 'body', 'small')
        """
        super().__init__(text, parent)
        
        # Initialize managers
        self._theme_mgr = ThemeManager.instance()
        self._font_mgr = FontManager.instance()
        self._current_theme: Optional[Theme] = None
        
        # Set font role
        self._font_category = font_role
        
        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        
        # Label properties - text color role based on font_role
        self._text_color_role = f'label.text.{font_role}'
        self._alignment = ThemedLabelConfig.DEFAULT_ALIGNMENT
        self._word_wrap = ThemedLabelConfig.DEFAULT_WORD_WRAP
        
        # Set default properties
        self.setAlignment(self._alignment)
        self.setWordWrap(self._word_wrap)
        self.setOpenExternalLinks(ThemedLabelConfig.DEFAULT_OPEN_EXTERNAL_LINKS)
        
        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
            
        # Apply font from font manager
        self._apply_font()
            
        logger.debug(f"ThemedLabel initialized with text: '{text}', font_role: '{font_role}'")
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.
        
        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
            self._apply_font()
        except Exception as e:
            logger.error(f"Error applying theme to ThemedLabel: {e}")
            import traceback
            traceback.print_exc()
            
    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to label with caching support.
        
        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return
            
        self._current_theme = theme
        
        text_color = theme.get_color(self._text_color_role, QColor(50, 50, 50))
        bg_color = theme.get_color('label.background', QColor(0, 0, 0, 0))
        
        # Create cache key
        cache_key = (
            text_color.name(),
            bg_color.name(),
            self._font_category,
        )
        
        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for ThemedLabel")
        else:
            # Build stylesheet
            qss = self._build_stylesheet(theme, text_color, bg_color)
            
            # Cache the stylesheet
            if len(self._stylesheet_cache) < ThemedLabelConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")
                
        # Apply stylesheet
        self.setStyleSheet(qss)
        
        # Force style refresh
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
        
    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.
        """
        # Unsubscribe from theme manager
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ThemedLabel unsubscribed from theme manager")
            
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
        logger.debug("ThemedLabel scheduled for deletion")