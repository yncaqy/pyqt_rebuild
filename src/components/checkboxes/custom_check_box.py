"""
Custom Check Box Component

Provides a modern, themed check box with:
- Theme integration with automatic updates
- Custom checkmark drawing with smooth rendering
- Support for normal, hover, checked, disabled states
- Optimized style caching for performance
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QRectF, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QPaintEvent
from PyQt6.QtWidgets import QCheckBox, QWidget, QStyle, QStyleOptionButton, QSizePolicy
from core.theme_manager import ThemeManager, Theme

# Initialize logger
logger = logging.getLogger(__name__)


class CheckBoxConfig:
    """Configuration constants for checkbox behavior and styling."""

    # Default size policy
    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed

    # Default style values (used as fallbacks)
    DEFAULT_BORDER_RADIUS = 3
    DEFAULT_SIZE = 18
    DEFAULT_CHECKMARK_COLOR = QColor(52, 152, 219)  # Nice blue

    # Checkmark drawing proportions (relative to indicator size)
    CHECKMARK_START_X_RATIO = 0.2
    CHECKMARK_START_Y_RATIO = 0.5
    CHECKMARK_MID_X_RATIO = 0.4
    CHECKMARK_MID_Y_OFFSET = 0.15  # From bottom
    CHECKMARK_END_X_OFFSET = 0.15  # From right
    CHECKMARK_END_Y_RATIO = 0.25

    # Checkmark styling
    CHECKMARK_PEN_WIDTH = 2
    INDICATOR_MARGIN = 2  # Margin inside indicator

    # Cache size limit
    MAX_STYLESHEET_CACHE_SIZE = 100


class CustomCheckBox(QCheckBox):
    """
    Themed check box with custom checkmark drawing and automatic theme updates.

    Features:
    - Theme integration with automatic updates
    - Custom smooth checkmark drawing (not default Qt style)
    - Support for normal, hover, checked, disabled states
    - Optimized style caching for performance
    - Memory-safe with proper cleanup

    The checkmark is drawn with smooth curves using QPainterPath for
    a modern appearance that differs from the traditional Qt checkbox.

    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets
        _checkmark_color: Color for enabled checkmark
        _checkmark_disabled: Color for disabled checkmark

    Example:
        checkbox = CustomCheckBox("Accept Terms")
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda state: print(f"Checked: {state}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        """
        Initialize the themed check box.

        Args:
            text: Checkbox label text
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Set size policy to prevent compression
        self.setSizePolicy(
            CheckBoxConfig.DEFAULT_HORIZONTAL_POLICY,
            CheckBoxConfig.DEFAULT_VERTICAL_POLICY
        )

        # Initialize theme manager reference
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Store checkmark colors for custom painting
        self._checkmark_color = CheckBoxConfig.DEFAULT_CHECKMARK_COLOR
        self._checkmark_disabled = QColor(176, 176, 176)

        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"CustomCheckBox initialized with text: '{text}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to CustomCheckBox: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to checkbox with caching support.

        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        # Get colors with fallback defaults
        bg_normal = theme.get_color('checkbox.background.normal', QColor(255, 255, 255))
        bg_hover = theme.get_color('checkbox.background.hover', QColor(245, 245, 245))

        border_color = theme.get_color('checkbox.border.normal', QColor(176, 176, 176))
        border_focus = theme.get_color('checkbox.border.focus', QColor(52, 152, 219))
        border_checked = theme.get_color('checkbox.border.checked', QColor(52, 152, 219))
        border_disabled = theme.get_color('checkbox.border.disabled', QColor(224, 224, 224))

        checkmark_color = theme.get_color('checkbox.checkmark', CheckBoxConfig.DEFAULT_CHECKMARK_COLOR)
        checkmark_disabled = theme.get_color('checkbox.checkmark.disabled', QColor(176, 176, 176))
        
        text_color = theme.get_color('checkbox.text.normal', QColor(50, 50, 50))
        text_disabled = theme.get_color('checkbox.text.disabled', QColor(150, 150, 150))

        # Store checkmark colors for custom painting
        self._checkmark_color = checkmark_color
        self._checkmark_disabled = checkmark_disabled

        border_radius = theme.get_value('checkbox.border_radius', CheckBoxConfig.DEFAULT_BORDER_RADIUS)
        size = theme.get_value('checkbox.size', CheckBoxConfig.DEFAULT_SIZE)

        # Create cache key
        cache_key = (
            bg_normal.name(),
            bg_hover.name(),
            border_color.name(),
            border_focus.name(),
            border_checked.name(),
            border_disabled.name(),
            checkmark_color.name(),
            checkmark_disabled.name(),
            text_color.name(),
            text_disabled.name(),
            border_radius,
            size,
        )

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for CustomCheckBox")
        else:
            # Build stylesheet
            qss = self._build_stylesheet(theme, bg_normal, bg_hover, border_color,
                                        border_focus, border_checked, border_disabled,
                                        text_color, text_disabled, border_radius, size)

            # Cache the stylesheet
            if len(self._stylesheet_cache) < CheckBoxConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")

        # Apply stylesheet
        self.setStyleSheet(qss)

        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"Theme applied to CustomCheckBox: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _build_stylesheet(self, theme: Theme, bg_normal: QColor, bg_hover: QColor,
                         border_color: QColor, border_focus: QColor, border_checked: QColor,
                         border_disabled: QColor, text_color: QColor, text_disabled: QColor,
                         border_radius: int, size: int) -> str:
        """
        Build QSS stylesheet from theme properties.

        Args:
            theme: Theme object
            bg_normal: Normal background color
            bg_hover: Hover background color
            border_color: Normal border color
            border_focus: Focus border color
            border_checked: Checked border color
            border_disabled: Disabled border color
            text_color: Normal text color
            text_disabled: Disabled text color
            border_radius: Border radius in pixels
            size: Indicator size in pixels

        Returns:
            Complete QSS stylesheet string
        """
        bg_normal_css = bg_normal.name() if bg_normal.alpha() > 0 else 'transparent'
        bg_hover_css = bg_hover.name() if bg_hover.alpha() > 0 else 'transparent'
        
        qss = f"""
        CustomCheckBox {{
            spacing: 8px;
            color: {text_color.name()};
            background: transparent;
        }}
        CustomCheckBox::indicator {{
            width: {size}px;
            height: {size}px;
            border-radius: {border_radius}px;
            border: 2px solid {border_color.name()};
            background: {bg_normal_css};
        }}
        CustomCheckBox::indicator:hover {{
            border: 2px solid {border_focus.name()};
            background: {bg_hover_css};
        }}
        CustomCheckBox::indicator:checked {{
            background: {bg_normal_css};
            border: 2px solid {border_checked.name()};
        }}
        CustomCheckBox::indicator:checked:hover {{
            background: {bg_hover_css};
            border: 2px solid {border_checked.name()};
        }}
        CustomCheckBox::indicator:disabled {{
            background: {bg_normal_css};
            border: 2px solid {border_disabled.name()};
        }}
        CustomCheckBox::indicator:checked:disabled {{
            background: {bg_normal_css};
            border: 2px solid {border_disabled.name()};
        }}
        CustomCheckBox:disabled {{
            color: {text_disabled.name()};
            background: transparent;
        }}
        CustomCheckBox:focus {{
            border: none;
            outline: none;
        }}
        """
        return qss

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Override paintEvent to draw custom checkmark.

        Args:
            event: Paint event
        """
        # Call parent to draw checkbox background and indicator
        super().paintEvent(event)

        # Only draw checkmark if checked
        if not self.isChecked():
            return

        # Get indicator rect
        style = self.style()
        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        indicator_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, opt, self
        )

        # Draw custom checkmark
        self._draw_checkmark(indicator_rect)

    def _draw_checkmark(self, indicator_rect: QRectF) -> None:
        """
        Draw custom smooth checkmark in the indicator.

        Args:
            indicator_rect: Rectangle for the indicator area
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine color based on enabled state
        color = self._checkmark_disabled if not self.isEnabled() else self._checkmark_color

        # Configure pen for smooth drawing
        pen = QPen(color, CheckBoxConfig.CHECKMARK_PEN_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # Calculate checkmark path using configured proportions
        rect = indicator_rect.adjusted(
            CheckBoxConfig.INDICATOR_MARGIN,
            CheckBoxConfig.INDICATOR_MARGIN,
            -CheckBoxConfig.INDICATOR_MARGIN,
            -CheckBoxConfig.INDICATOR_MARGIN
        )

        # Calculate checkmark coordinates
        start_x = rect.left() + rect.width() * CheckBoxConfig.CHECKMARK_START_X_RATIO
        start_y = rect.top() + rect.height() * CheckBoxConfig.CHECKMARK_START_Y_RATIO

        mid_x = rect.left() + rect.width() * CheckBoxConfig.CHECKMARK_MID_X_RATIO
        mid_y = rect.bottom() - rect.height() * CheckBoxConfig.CHECKMARK_MID_Y_OFFSET

        end_x = rect.right() - rect.width() * CheckBoxConfig.CHECKMARK_END_X_OFFSET
        end_y = rect.top() + rect.height() * CheckBoxConfig.CHECKMARK_END_Y_RATIO

        # Draw checkmark path
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        path.lineTo(mid_x, mid_y)
        path.lineTo(end_x, end_y)

        painter.drawPath(path)
        painter.end()

        logger.debug(f"Custom checkmark drawn at {indicator_rect}")

    def set_theme(self, name: str) -> None:
        """
        Set the current theme by name.

        This is a convenience method that delegates to the theme manager.

        Args:
            name: Theme name (e.g., 'dark', 'light', 'default')

        Example:
            checkbox.set_theme('dark')
        """
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name.

        Returns:
            Current theme name, or None if no theme is set

        Example:
            current_theme = checkbox.get_theme()
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def set_border_radius(self, radius: int) -> None:
        """
        Set the checkbox border radius.

        Args:
            radius: Border radius in pixels

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        logger.debug(f"Setting border radius: {radius}px")
        if self._current_theme:
            self._current_theme.set_value('checkbox.border_radius', radius)
            self._apply_theme(self._current_theme)

    def set_indicator_size(self, size: int) -> None:
        """
        Set the checkbox indicator size.

        Args:
            size: Indicator size in pixels

        Note:
            This applies to the current theme. If theme changes,
            this customization will be lost.
        """
        logger.debug(f"Setting indicator size: {size}px")
        if self._current_theme:
            self._current_theme.set_value('checkbox.size', size)
            self._apply_theme(self._current_theme)

    def set_checkmark_color(self, color: QColor) -> None:
        """
        Set the checkmark color directly.

        Args:
            color: Color for the checkmark

        Note:
            This overrides the theme color. Changes will be lost if theme changes.
        """
        logger.debug(f"Setting checkmark color: {color.name()}")
        self._checkmark_color = color
        self.update()  # Trigger repaint

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the checkbox is destroyed
        to prevent memory leaks.

        Example:
            checkbox.cleanup()
            checkbox.deleteLater()
        """
        # Unsubscribe from theme manager to prevent memory leaks
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("CustomCheckBox unsubscribed from theme manager")

        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("CustomCheckBox scheduled for deletion")
