"""
Custom Check Box Component

Provides a modern, themed check box with:
- Theme integration with automatic updates
- Custom checkmark drawing with smooth rendering
- Support for normal, hover, checked, disabled states
- Optimized style caching for performance
- Local style overrides without modifying shared theme
- Automatic resource cleanup
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtCore import Qt, QRectF, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QPaintEvent
from PyQt6.QtWidgets import QCheckBox, QWidget, QStyle, QStyleOptionButton, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class CheckBoxConfig:
    """Configuration constants for checkbox behavior and styling."""

    DEFAULT_BORDER_RADIUS = 3
    DEFAULT_SIZE = 18
    DEFAULT_CHECKMARK_COLOR = QColor(52, 152, 219)

    CHECKMARK_START_X_RATIO = 0.2
    CHECKMARK_START_Y_RATIO = 0.5
    CHECKMARK_MID_X_RATIO = 0.4
    CHECKMARK_MID_Y_OFFSET = 0.15
    CHECKMARK_END_X_OFFSET = 0.15
    CHECKMARK_END_Y_RATIO = 0.25

    CHECKMARK_PEN_WIDTH = 2
    INDICATOR_MARGIN = 2


class CustomCheckBox(QCheckBox, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed check box with custom checkmark drawing and automatic theme updates.

    Features:
    - Theme integration with automatic updates
    - Custom smooth checkmark drawing (not default Qt style)
    - Support for normal, hover, checked, disabled states
    - Optimized style caching for performance
    - Memory-safe with proper cleanup
    - Local style overrides without modifying shared theme
    - Automatic resource cleanup

    The checkmark is drawn with smooth curves using QPainterPath for
    a modern appearance that differs from the traditional Qt checkbox.

    Example:
        checkbox = CustomCheckBox("Accept Terms")
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda state: print(f"Checked: {state}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._checkmark_color = CheckBoxConfig.DEFAULT_CHECKMARK_COLOR
        self._checkmark_disabled = QColor(176, 176, 176)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

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
        if not theme:
            return

        self._current_theme = theme

        bg_normal = self.get_style_color(theme, 'checkbox.background.normal', QColor(255, 255, 255))
        bg_hover = self.get_style_color(theme, 'checkbox.background.hover', QColor(245, 245, 245))

        border_color = self.get_style_color(theme, 'checkbox.border.normal', QColor(176, 176, 176))
        border_focus = self.get_style_color(theme, 'checkbox.border.focus', QColor(52, 152, 219))
        border_checked = self.get_style_color(theme, 'checkbox.border.checked', QColor(52, 152, 219))
        border_disabled = self.get_style_color(theme, 'checkbox.border.disabled', QColor(224, 224, 224))

        checkmark_color = self.get_style_color(theme, 'checkbox.checkmark', CheckBoxConfig.DEFAULT_CHECKMARK_COLOR)
        checkmark_disabled = self.get_style_color(theme, 'checkbox.checkmark.disabled', QColor(176, 176, 176))
        
        text_color = self.get_style_color(theme, 'checkbox.text.normal', QColor(50, 50, 50))
        text_disabled = self.get_style_color(theme, 'checkbox.text.disabled', QColor(150, 150, 150))

        self._checkmark_color = checkmark_color
        self._checkmark_disabled = checkmark_disabled

        border_radius = self.get_style_value(theme, 'checkbox.border_radius', CheckBoxConfig.DEFAULT_BORDER_RADIUS)
        size = self.get_style_value(theme, 'checkbox.size', CheckBoxConfig.DEFAULT_SIZE)

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

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, bg_normal, bg_hover, border_color,
                                          border_focus, border_checked, border_disabled,
                                          text_color, text_disabled, border_radius, size)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

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
        logger.debug(f"Setting border radius: {radius}px")
        self.override_style('checkbox.border_radius', radius)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_indicator_size(self, size: int) -> None:
        logger.debug(f"Setting indicator size: {size}px")
        self.override_style('checkbox.size', size)
        if self._current_theme:
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
            logger.debug("CustomCheckBox unsubscribed from theme manager")

        self._clear_stylesheet_cache()
        self.clear_overrides()

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("CustomCheckBox scheduled for deletion")
