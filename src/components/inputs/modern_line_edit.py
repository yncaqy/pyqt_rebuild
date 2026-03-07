"""
Modern Line Edit Component

Provides a modern, themed line edit with:
- Theme integration with automatic updates
- Support for normal, focus, disabled, error states
- Placeholder text color customization
- Optimized style caching for performance
- Memory-safe with proper cleanup
- Local style overrides without modifying shared theme
- Automatic resource cleanup
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class LineEditConfig:
    """Configuration constants for line edit behavior and styling."""

    DEFAULT_MIN_WIDTH = 200
    DEFAULT_MIN_HEIGHT = 36
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_PADDING = '8px 12px'
    DEFAULT_PLACEHOLDER_COLOR = QColor(170, 170, 170)


class ModernLineEdit(QLineEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed line edit with modern styling and automatic theme updates.

    Features:
    - Theme integration with automatic updates
    - Support for normal, focus, disabled, error states
    - Placeholder text color customization
    - Optimized style caching for performance
    - Memory-safe with proper cleanup
    - Local style overrides without modifying shared theme
    - Automatic resource cleanup

    The line edit supports error state visualization and provides
    convenient methods for validation feedback.

    Example:
        lineedit = ModernLineEdit("Enter text here")
        lineedit.setPlaceholderText("Username")
        lineedit.setError(True)  # Show error state
        lineedit.textChanged.connect(lambda text: print(f"Text: {text}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setMinimumSize(
            LineEditConfig.DEFAULT_MIN_WIDTH,
            LineEditConfig.DEFAULT_MIN_HEIGHT
        )

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

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
        if not theme:
            return

        self._current_theme = theme

        bg_normal = self.get_style_color(theme, 'input.background.normal', QColor(255, 255, 255))
        bg_disabled = self.get_style_color(theme, 'input.background.disabled', QColor(245, 245, 245))

        text_color = self.get_style_color(theme, 'input.text.normal', QColor(51, 51, 51))
        text_disabled = self.get_style_color(theme, 'input.text.disabled', QColor(170, 170, 170))

        border_color = self.get_style_color(theme, 'input.border.normal', QColor(204, 204, 204))
        border_focus = self.get_style_color(theme, 'input.border.focus', QColor(52, 152, 219))
        border_error = self.get_style_color(theme, 'input.border.error', QColor(231, 76, 60))

        border_radius = self.get_style_value(theme, 'input.border_radius', LineEditConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'input.padding', LineEditConfig.DEFAULT_PADDING)

        error_state = self.property("error")

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

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, bg_normal, bg_disabled, text_color,
                                          text_disabled, border_color, border_focus,
                                          border_error, border_radius, padding)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

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
        logger.debug(f"Setting border radius: {radius}px")
        self.override_style('input.border_radius', radius)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_padding(self, padding: str) -> None:
        logger.debug(f"Setting padding: {padding}")
        self.override_style('input.padding', padding)
        if self._current_theme:
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

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ModernLineEdit unsubscribed from theme manager")

        self._clear_stylesheet_cache()
        self.clear_overrides()

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
