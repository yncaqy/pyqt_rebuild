"""
Modern Line Edit Component

Provides a modern, themed line edit with:
- Theme integration with automatic updates
- Support for normal, focus, disabled, error states
- Placeholder text color customization
- Optimized style caching for performance
- Memory-safe with proper cleanup
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme

# Initialize logger
logger = logging.getLogger(__name__)


class LineEditConfig:
    """Configuration constants for line edit behavior and styling."""

    # Default size policy
    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Preferred
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed

    # Default size constraints
    DEFAULT_MIN_WIDTH = 200
    DEFAULT_MIN_HEIGHT = 36

    # Default style values (used as fallbacks)
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_PADDING = '8px 12px'
    DEFAULT_PLACEHOLDER_COLOR = QColor(170, 170, 170)

    # Cache size limit
    MAX_STYLESHEET_CACHE_SIZE = 100


class ModernLineEdit(QLineEdit):
    """
    Themed line edit with modern styling and automatic theme updates.

    Features:
    - Theme integration with automatic updates
    - Support for normal, focus, disabled, error states
    - Placeholder text color customization
    - Optimized style caching for performance
    - Memory-safe with proper cleanup

    The line edit supports error state visualization and provides
    convenient methods for validation feedback.

    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets

    Example:
        lineedit = ModernLineEdit("Enter text here")
        lineedit.setPlaceholderText("Username")
        lineedit.setError(True)  # Show error state
        lineedit.textChanged.connect(lambda text: print(f"Text: {text}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        """
        Initialize the themed line edit.

        Args:
            text: Initial text content
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set size hint to ensure proper minimum size based on content
        self.setMinimumSize(
            LineEditConfig.DEFAULT_MIN_WIDTH,
            LineEditConfig.DEFAULT_MIN_HEIGHT
        )

        # Set size policy: Preferred horizontal means widget will use its sizeHint
        self.setSizePolicy(
            LineEditConfig.DEFAULT_HORIZONTAL_POLICY,
            LineEditConfig.DEFAULT_VERTICAL_POLICY
        )

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

        logger.debug(f"ModernLineEdit initialized with text: '{text}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ModernLineEdit: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to line edit with caching support.

        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        # Get colors with fallback defaults
        bg_normal = theme.get_color('input.background.normal', QColor(255, 255, 255))
        bg_disabled = theme.get_color('input.background.disabled', QColor(245, 245, 245))

        text_color = theme.get_color('input.text.normal', QColor(51, 51, 51))
        text_disabled = theme.get_color('input.text.disabled', QColor(170, 170, 170))

        border_color = theme.get_color('input.border.normal', QColor(204, 204, 204))
        border_focus = theme.get_color('input.border.focus', QColor(52, 152, 219))
        border_error = theme.get_color('input.border.error', QColor(231, 76, 60))

        border_radius = theme.get_value('input.border_radius', LineEditConfig.DEFAULT_BORDER_RADIUS)
        padding = theme.get_value('input.padding', LineEditConfig.DEFAULT_PADDING)

        # Get current error state
        error_state = self.property("error")

        # Create cache key
        cache_key = (
            bg_normal.name(),
            bg_disabled.name(),
            text_color.name(),
            text_disabled.name(),
            border_color.name(),
            border_focus.name(),
            border_error.name(),
            border_radius,
            padding,
            error_state,
        )

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for ModernLineEdit")
        else:
            # Build stylesheet
            qss = self._build_stylesheet(theme, bg_normal, bg_disabled, text_color,
                                        text_disabled, border_color, border_focus,
                                        border_error, border_radius, padding)

            # Cache the stylesheet
            if len(self._stylesheet_cache) < LineEditConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")

        # Apply stylesheet
        self.setStyleSheet(qss)

        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"Theme applied to ModernLineEdit: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _build_stylesheet(self, theme: Theme, bg_normal: QColor, bg_disabled: QColor,
                         text_color: QColor, text_disabled: QColor, border_color: QColor,
                         border_focus: QColor, border_error: QColor, border_radius: int,
                         padding: str) -> str:
        """
        Build QSS stylesheet from theme properties.

        Args:
            theme: Theme object
            bg_normal: Normal background color
            bg_disabled: Disabled background color
            text_color: Normal text color
            text_disabled: Disabled text color
            border_color: Normal border color
            border_focus: Focus border color
            border_error: Error border color
            border_radius: Border radius in pixels
            padding: CSS padding value

        Returns:
            Complete QSS stylesheet string
        """
        qss = f"""
        ModernLineEdit {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 2px solid {border_color.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            selection-background-color: {border_focus.name()};
        }}
        ModernLineEdit:focus {{
            border: 2px solid {border_focus.name()};
        }}
        ModernLineEdit:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 2px solid {border_color.name()};
        }}
        ModernLineEdit[error="true"] {{
            border: 2px solid {border_error.name()};
        }}
        """
        return qss

    def set_theme(self, name: str) -> None:
        """
        Set the current theme by name.

        This is a convenience method that delegates to the theme manager.

        Args:
            name: Theme name (e.g., 'dark', 'light', 'default')

        Example:
            lineedit.set_theme('dark')
        """
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name.

        Returns:
            Current theme name, or None if no theme is set

        Example:
            current_theme = lineedit.get_theme()
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def set_error(self, error: bool) -> None:
        """
        Set the error state for visual feedback.

        When error is True, the border will be displayed in the error color.

        Args:
            error: True to show error state, False to clear

        Example:
            lineedit.set_error(True)   # Show error
            lineedit.set_error(False)  # Clear error
        """
        self.setProperty("error", "true" if error else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        logger.debug(f"Error state set to: {error}")

    def has_error(self) -> bool:
        """
        Check if the line edit is in error state.

        Returns:
            True if error state is active, False otherwise
        """
        return self.property("error") == "true"

    def set_border_radius(self, radius: int) -> None:
        """
        Set the line edit border radius.

        Args:
            radius: Border radius in pixels

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        logger.debug(f"Setting border radius: {radius}px")
        if self._current_theme:
            self._current_theme.set_value('lineedit.border_radius', radius)
            self._apply_theme(self._current_theme)

    def set_padding(self, padding: str) -> None:
        """
        Set the line edit padding.

        Args:
            padding: CSS padding value (e.g., '8px 12px', '10px')

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        logger.debug(f"Setting padding: {padding}")
        if self._current_theme:
            self._current_theme.set_value('lineedit.padding', padding)
            self._apply_theme(self._current_theme)

    def set_placeholder_color(self, color: QColor) -> None:
        """
        Set the placeholder text color.

        This uses QPalette to change the placeholder text color
        for the line edit.

        Args:
            color: Color for placeholder text

        Example:
            from PyQt6.QtGui import QColor
            lineedit.set_placeholder_color(QColor(150, 150, 150))

        Note:
            This overrides the theme color. Changes will be lost if theme changes.
        """
        logger.debug(f"Setting placeholder color: {color.name()}")

        # Get current palette
        palette = self.palette()

        # Set placeholder text color using PlaceholderText color role
        palette.setColor(QPalette.ColorRole.PlaceholderText, color)

        # Apply the modified palette
        self.setPalette(palette)

    def set_min_size(self, width: int, height: int) -> None:
        """
        Set the minimum size for the line edit.

        Args:
            width: Minimum width in pixels
            height: Minimum height in pixels

        Example:
            lineedit.set_min_size(250, 40)
        """
        logger.debug(f"Setting minimum size: {width}x{height}")
        self.setMinimumSize(width, height)

    def clear_with_focus(self) -> None:
        """
        Clear text and set focus to the line edit.

        This is a convenience method that combines clearing the text
        and setting focus, useful for "Clear" buttons or similar actions.

        Example:
            clear_button.clicked.connect(lineedit.clear_with_focus)
        """
        self.clear()
        self.setFocus()
        logger.debug("Cleared text and set focus")

    def validate_not_empty(self) -> bool:
        """
        Validate that the line edit is not empty.

        If empty, sets error state and returns False.
        If not empty, clears error state and returns True.

        Returns:
            True if validation passed, False otherwise

        Example:
            if not lineedit.validate_not_empty():
                print("Field cannot be empty!")
        """
        if not self.text().strip():
            self.set_error(True)
            return False

        self.set_error(False)
        return True

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the line edit is destroyed
        to prevent memory leaks.

        Example:
            lineedit.cleanup()
            lineedit.deleteLater()
        """
        # Unsubscribe from theme manager to prevent memory leaks
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ModernLineEdit unsubscribed from theme manager")

        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")

    # Convenience methods (snake_case aliases for Qt methods)
    def set_placeholder_text(self, text: str) -> None:
        """
        Set placeholder text (snake_case alias).

        This is a convenience alias for setPlaceholderText().

        Args:
            text: Placeholder text to display

        Example:
            lineedit.set_placeholder_text("Enter your name...")
        """
        self.setPlaceholderText(text)

    def get_placeholder_text(self) -> str:
        """
        Get placeholder text (snake_case alias).

        This is a convenience alias for placeholderText().

        Returns:
            Current placeholder text
        """
        return self.placeholderText()

    def set_echo_mode(self, mode) -> None:
        """
        Set echo mode (snake_case alias).

        This is a convenience alias for setEchoMode().

        Args:
            mode: EchoMode enum value
        """
        self.setEchoMode(mode)

    def get_echo_mode(self):
        """
        Get echo mode (snake_case alias).

        Returns:
            Current echo mode
        """
        return self.echoMode()

    def set_read_only(self, read_only: bool) -> None:
        """
        Set read-only state (snake_case alias).

        This is a convenience alias for setReadOnly().

        Args:
            read_only: True for read-only, False for editable
        """
        self.setReadOnly(read_only)

    def is_read_only(self) -> bool:
        """
        Check if read-only (snake_case alias).

        Returns:
            True if read-only, False otherwise
        """
        return self.isReadOnly()

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("ModernLineEdit scheduled for deletion")
