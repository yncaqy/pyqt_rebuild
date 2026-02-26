"""
Custom Push Button Component

Provides a modern, themed push button with:
- Theme integration with automatic updates
- Support for normal, hover, pressed, disabled states
- Customizable border radius and padding
- Optimized style caching for performance
"""

import logging
import time
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

# Initialize logger
logger = logging.getLogger(__name__)


class ButtonConfig:
    """Configuration constants for button behavior and styling."""

    # Default size policy
    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed

    # Default style values (used as fallbacks)
    DEFAULT_BORDER_RADIUS = 6
    DEFAULT_PADDING = '8px 16px'

    # Cache size limit
    MAX_STYLESHEET_CACHE_SIZE = 100


class CustomPushButton(QPushButton):
    """
    Themed push button with modern styling and automatic theme updates.

    Features:
    - Theme integration with automatic updates
    - Support for normal, hover, pressed, disabled states
    - Customizable border radius and padding
    - Optimized style caching for performance
    - Memory-safe with proper cleanup

    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets

    Example:
        button = CustomPushButton("Click Me")
        button.set_theme('dark')
        button.clicked.connect(lambda: print("Clicked!"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, icon_name: str = ""):
        """
        Initialize the themed push button.

        Args:
            text: Button text label
            parent: Parent widget
            icon_name: Name of the icon (without extension)
        """
        super().__init__(text, parent)

        # Set size policy to maintain minimum size when layout stretches
        # Policy.Minimum: widget won't shrink below minimumSize hint
        self.setSizePolicy(
            ButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            ButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        # Initialize managers
        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        # Icon properties
        self._icon_name = icon_name
        self._icon_size = QSize(16, 16)
        self._icon_color_role = 'button.icon.normal'

        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
        else:
            # Apply default icon if no theme
            if icon_name:
                self._update_icon()

        logger.info(f"CustomPushButton initialized with text: '{text}', icon: '{icon_name}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
            self._update_icon()
        except Exception as e:
            logger.error(f"Error applying theme to CustomPushButton: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to button with caching support and performance monitoring.

        Args:
            theme: Theme object containing color and style definitions
        """
        start_time = time.time()
        
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        # Create optimized cache key
        theme_name = getattr(theme, 'name', 'unnamed')
        cache_key = (
            theme_name,
            theme.get_color('button.background.normal', QColor(230, 230, 230)).name(),
            theme.get_color('button.background.hover', QColor(200, 200, 200)).name(),
            theme.get_color('button.background.pressed', QColor(180, 180, 180)).name(),
            theme.get_color('button.background.disabled', QColor(240, 240, 240)).name(),
            theme.get_color('button.text.normal', QColor(50, 50, 50)).name(),
            theme.get_color('button.text.disabled', QColor(150, 150, 150)).name(),
            theme.get_color('button.border.normal', QColor(150, 150, 150)).name(),
            theme.get_color('button.border.hover', QColor(100, 100, 100)).name(),
            theme.get_color('button.border.pressed', QColor(80, 80, 80)).name(),
            theme.get_color('button.border.disabled', QColor(200, 200, 200)).name(),
            theme.get_value('button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS),
            theme.get_value('button.padding', ButtonConfig.DEFAULT_PADDING),
        )

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            # Using cached stylesheet - performance optimization
        else:
            # Build stylesheet
            qss = self._build_stylesheet(theme)

            # Cache the stylesheet (with size limit)
            if len(self._stylesheet_cache) < ButtonConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                # Stylesheet cached successfully

        # Apply stylesheet with smart refresh
        current_stylesheet = self.styleSheet()
        if current_stylesheet != qss:
            self.setStyleSheet(qss)
            # Only refresh style if stylesheet actually changed
            self.style().unpolish(self)
            self.style().polish(self)
            logger.debug("Stylesheet updated and refreshed")
        else:
            logger.debug("Stylesheet unchanged, skipping refresh")

        elapsed_time = time.time() - start_time
        logger.info(f"Theme applied: {getattr(theme, 'name', 'unnamed')} (cache size: {len(self._stylesheet_cache)}, took {elapsed_time:.3f}s)")

    def _needs_style_refresh(self, new_qss: str) -> bool:
        """
        Determine if style refresh is needed.
        
        Args:
            new_qss: New stylesheet to apply
            

        Returns:
            True if refresh is needed, False otherwise
        """
        current_qss = self.styleSheet()
        return current_qss != new_qss
    def _build_stylesheet(self, theme: Theme) -> str:
        """
        Build QSS stylesheet from theme properties.

        Args:
            theme: Theme object containing color and style definitions

        Returns:
            Complete QSS stylesheet string
        """
        # Get colors with fallback defaults
        bg_normal = theme.get_color('button.background.normal', QColor(230, 230, 230))
        bg_hover = theme.get_color('button.background.hover', QColor(200, 200, 200))
        bg_pressed = theme.get_color('button.background.pressed', QColor(180, 180, 180))
        bg_disabled = theme.get_color('button.background.disabled', QColor(240, 240, 240))

        text_color = theme.get_color('button.text.normal', QColor(50, 50, 50))
        text_disabled = theme.get_color('button.text.disabled', QColor(150, 150, 150))

        border_color = theme.get_color('button.border.normal', QColor(150, 150, 150))
        border_hover = theme.get_color('button.border.hover', QColor(100, 100, 100))
        border_pressed = theme.get_color('button.border.pressed', QColor(80, 80, 80))
        border_disabled = theme.get_color('button.border.disabled', QColor(200, 200, 200))

        border_radius = theme.get_value('button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS)
        padding = theme.get_value('button.padding', ButtonConfig.DEFAULT_PADDING)

        # Build QSS with all states
        qss = f"""
        CustomPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 2px solid {border_color.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            font-weight: bold;
            text-align: center;
        }}
        CustomPushButton:hover {{
            background-color: {bg_hover.name()};
            border: 2px solid {border_hover.name()};
        }}
        CustomPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: 2px solid {border_pressed.name()};
        }}
        CustomPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 2px solid {border_disabled.name()};
        }}
        """

        # For buttons with icon, add spacing between icon and text
        if self._icon_name:
            qss += ""
            # PyQt doesn't support icon-text-spacing, so we'll handle it in _update_icon

        return qss

    def set_theme(self, name: str) -> None:
        """
        Set the current theme by name.

        This is a convenience method that delegates to the theme manager.

        Args:
            name: Theme name (e.g., 'dark', 'light', 'default')

        Example:
            button.set_theme('dark')
        """
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name with enhanced error handling.

        Returns:
            Current theme name, or None if no theme is set

        Example:
            current_theme = button.get_theme()
        """
        try:
            if self._current_theme is not None:
                # More robust attribute access
                theme_name = getattr(self._current_theme, 'name', None)
                if theme_name is not None:
                    return str(theme_name)
            return None
        except Exception as e:
            logger.warning(f"Error getting theme name: {e}")
            return None

    def set_border_radius(self, radius: int) -> None:
        """
        Set the button border radius with improved error handling.

        Args:
            radius: Border radius in pixels

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        try:
            if not isinstance(radius, int) or radius < 0:
                logger.warning(f"Invalid border radius value: {radius}")
                return
                
            logger.debug(f"Setting border radius: {radius}px")
            if self._current_theme:
                # Temporarily override theme value
                self._current_theme.set_value('button.border_radius', radius)
                self._apply_theme(self._current_theme)
        except Exception as e:
            logger.error(f"Error setting border radius: {e}")

    def set_padding(self, padding: str) -> None:
        """
        Set the button padding with improved validation.

        Args:
            padding: CSS padding value (e.g., '8px 16px', '10px')

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        try:
            if not isinstance(padding, str) or not padding.strip():
                logger.warning(f"Invalid padding value: {padding}")
                return
                
            logger.debug(f"Setting padding: {padding}")
            if self._current_theme:
                # Temporarily override theme value
                self._current_theme.set_value('button.padding', padding)
                self._apply_theme(self._current_theme)
        except Exception as e:
            logger.error(f"Error setting padding: {e}")

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the button is destroyed
        to prevent memory leaks.

        Example:
            button.cleanup()
            button.deleteLater()
        """
        # Unsubscribe from theme manager to prevent memory leaks
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("CustomPushButton unsubscribed from theme manager")

        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")

    def _update_icon(self) -> None:
        """
        Update the button icon based on current settings.
        """
        if not self._icon_name:
            # Clear icon if no name provided
            self.setIcon(QIcon())
            # Reset stylesheet to remove any icon-specific padding
            if self._current_theme:
                qss = self._build_stylesheet(self._current_theme)
                self.setStyleSheet(qss)
            return
        
        # Get icon from IconManager
        icon_size = self._icon_size.width()
        if self._current_theme:
            # Get color from theme
            color = self._current_theme.get_color(self._icon_color_role, QColor(50, 50, 50))
            icon = self._icon_mgr.get_colored_icon(self._icon_name, color, icon_size)
        else:
            # Use default icon without color
            icon = self._icon_mgr.get_icon(self._icon_name, icon_size)
        
        # Apply icon to button
        self.setIcon(icon)
        self.setIconSize(self._icon_size)
        
        logger.debug(f"Icon size set to: {icon_size}x{icon_size}")
        
        # Add spacing between icon and text
        if self.text():
            # Remove any existing leading spaces
            original_text = self.text().lstrip()
            # Add a single space before the text to create spacing after icon
            self.setText(f" {original_text}")
        
        # Set the base stylesheet
        if self._current_theme:
            base_qss = self._build_stylesheet(self._current_theme)
            self.setStyleSheet(base_qss)
        
        logger.debug(f"Icon updated: {self._icon_name}, size: {self._icon_size.width()}x{self._icon_size.height()}")
    
    def set_icon(self, icon_name: str) -> None:
        """
        Set the button icon.

        Args:
            icon_name: Name of the icon (without extension)
        """
        if self._icon_name != icon_name:
            self._icon_name = icon_name
            self._update_icon()
            logger.debug(f"Icon set to: {icon_name}")
            
    def get_icon(self) -> str:
        """
        Get current icon name.

        Returns:
            Current icon name
        """
        return self._icon_name
        
    def set_icon_size(self, size: QSize) -> None:
        """
        Set icon size.

        Args:
            size: Icon size as QSize
        """
        if self._icon_size != size:
            self._icon_size = size
            self._update_icon()
            logger.debug(f"Icon size set to: {size.width()}x{size.height()}")
            
    def get_icon_size(self) -> QSize:
        """
        Get current icon size.

        Returns:
            Current icon size
        """
        return self._icon_size
        
    def set_icon_color_role(self, role: str) -> None:
        """
        Set theme color role for icon color.

        Args:
            role: Theme color role (e.g., 'button.icon.normal')
        """
        if self._icon_color_role != role:
            self._icon_color_role = role
            if self._current_theme:
                self._update_icon()
            logger.debug(f"Icon color role set to: {role}")
            
    def get_icon_color_role(self) -> str:
        """
        Get current icon color role.

        Returns:
            Current icon color role
        """
        return self._icon_color_role

    def set_tooltip(self, tooltip: str) -> None:
        """
        Set the button tooltip text.

        Args:
            tooltip: Tooltip text to display on hover
        """
        from components.tooltips.tooltip_manager import install_tooltip
        install_tooltip(self, tooltip)
        logger.debug(f"Tooltip set to: {tooltip}")

    def get_tooltip(self) -> str:
        """
        Get the current tooltip text.

        Returns:
            Current tooltip text
        """
        return self.toolTip()

    def remove_tooltip(self) -> None:
        """
        Remove the tooltip from the button.
        """
        from components.tooltips.tooltip_manager import remove_tooltip
        remove_tooltip(self)
        logger.debug("Tooltip removed")

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.
        """
        self.remove_tooltip()
        self.cleanup()
        super().deleteLater()
        logger.debug("CustomPushButton scheduled for deletion")
