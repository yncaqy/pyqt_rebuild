"""
Animated Slider Component

Provides a modern, themed slider with:
- Theme integration with automatic updates
- Smooth animated value transitions
- Support for horizontal and vertical orientations
- Customizable handle animations
- Optimized style caching for performance
- Memory-safe with proper cleanup
- Automatic resource cleanup
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSlider, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.animation_controller import AnimationController
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class SliderConfig:
    """Configuration constants for slider behavior and styling."""

    DEFAULT_MIN_WIDTH_HORIZONTAL = 150
    DEFAULT_MIN_HEIGHT_HORIZONTAL = 30
    DEFAULT_MIN_WIDTH_VERTICAL = 30
    DEFAULT_MIN_HEIGHT_VERTICAL = 150
    DEFAULT_HANDLE_SIZE = 18
    DEFAULT_HANDLE_RADIUS = 9
    DEFAULT_HANDLE_MARGIN = -9
    DEFAULT_GROOVE_HEIGHT = 6
    DEFAULT_GROOVE_WIDTH = 6
    DEFAULT_GROOVE_BORDER_RADIUS = 2
    DEFAULT_PADDING = 9
    DEFAULT_ANIMATION_DURATION = 300
    DEFAULT_HANDLE_SCALE = 1.0


class AnimatedSlider(QSlider, StylesheetCacheMixin):
    """
    Themed slider with smooth animated value transitions.

    Features:
    - Theme integration with automatic updates
    - Smooth animated value transitions with easing curves
    - Support for horizontal and vertical orientations
    - Customizable handle scale animations
    - Optimized style caching for performance
    - Memory-safe with proper cleanup
    - Automatic resource cleanup

    Example:
        slider = AnimatedSlider(Qt.Orientation.Horizontal)
        slider.set_value_animated(75, 500)  # Animate to 75% over 500ms
        slider.valueChanged.connect(lambda value: print(f"Value: {value}"))
    """

    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        parent: Optional[QWidget] = None
    ):
        super().__init__(orientation, parent)

        self._orientation = orientation
        self._init_stylesheet_cache(max_size=100)

        if orientation == Qt.Orientation.Horizontal:
            self.setMinimumSize(
                SliderConfig.DEFAULT_MIN_WIDTH_HORIZONTAL,
                SliderConfig.DEFAULT_MIN_HEIGHT_HORIZONTAL
            )
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setMinimumSize(
                SliderConfig.DEFAULT_MIN_WIDTH_VERTICAL,
                SliderConfig.DEFAULT_MIN_HEIGHT_VERTICAL
            )
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        self._handle_scale = SliderConfig.DEFAULT_HANDLE_SCALE

        theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"AnimatedSlider initialized with orientation: {'horizontal' if orientation == Qt.Orientation.Horizontal else'vertical'}")

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to AnimatedSlider: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        groove_color = theme.get_color('slider.groove.background', QColor(224, 224, 224))
        groove_disabled = theme.get_color('slider.groove.disabled', QColor(240, 240, 240))
        handle_color = theme.get_color('slider.handle.background', QColor(52, 152, 219))
        handle_hover = theme.get_color('slider.handle.hover', QColor(41, 128, 185))
        handle_pressed = theme.get_color('slider.handle.pressed', QColor(26, 82, 118))
        handle_disabled = theme.get_color('slider.handle.disabled', QColor(176, 176, 176))
        border_radius = theme.get_value('slider.border_radius', SliderConfig.DEFAULT_GROOVE_BORDER_RADIUS)

        is_horizontal = self._orientation == Qt.Orientation.Horizontal
        cache_key = (
            groove_color.name(),
            groove_disabled.name(),
            handle_color.name(),
            handle_hover.name(),
            handle_pressed.name(),
            handle_disabled.name(),
            border_radius,
            is_horizontal,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, groove_color, groove_disabled,
                                          handle_color, handle_hover, handle_pressed,
                                          handle_disabled, border_radius)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"Theme applied to AnimatedSlider: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _build_stylesheet(self, theme: Theme, groove_color: QColor, groove_disabled: QColor,
                         handle_color: QColor, handle_hover: QColor, handle_pressed: QColor,
                         handle_disabled: QColor, border_radius: int) -> str:
        """
        Build QSS stylesheet from theme properties.

        Args:
            theme: Theme object
            groove_color: Normal groove color
            groove_disabled: Disabled groove color
            handle_color: Normal handle color
            handle_hover: Hover handle color
            handle_pressed: Pressed handle color
            handle_disabled: Disabled handle color
            border_radius: Border radius in pixels

        Returns:
            Complete QSS stylesheet string
        """
        handle_size = SliderConfig.DEFAULT_HANDLE_SIZE
        handle_radius = SliderConfig.DEFAULT_HANDLE_RADIUS
        handle_margin = SliderConfig.DEFAULT_HANDLE_MARGIN
        groove_thickness = SliderConfig.DEFAULT_GROOVE_HEIGHT if self._orientation == Qt.Orientation.Horizontal else SliderConfig.DEFAULT_GROOVE_WIDTH
        padding = SliderConfig.DEFAULT_PADDING

        qss = f"""
        AnimatedSlider {{
            padding: {padding}px 0;
            background: transparent;
        }}
        """

        if self._orientation == Qt.Orientation.Horizontal:
            qss += f"""
            AnimatedSlider::groove:horizontal {{
                height: {groove_thickness}px;
                background: {groove_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::groove:horizontal:disabled {{
                background: {groove_disabled.name()};
            }}
            AnimatedSlider::sub-page:horizontal {{
                background: {handle_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::add-page:horizontal {{
                background: {groove_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::handle:horizontal {{
                background: {handle_color.name()};
                border: none;
                width: {handle_size}px;
                height: {handle_size}px;
                margin: {handle_margin}px 0;
                border-radius: {handle_radius}px;
            }}
            AnimatedSlider::handle:horizontal:hover {{
                background: {handle_hover.name()};
            }}
            AnimatedSlider::handle:horizontal:pressed {{
                background: {handle_pressed.name()};
            }}
            AnimatedSlider::handle:horizontal:disabled {{
                background: {handle_disabled.name()};
            }}
            """
        else:  # Vertical
            qss += f"""
            AnimatedSlider::groove:vertical {{
                width: {groove_thickness}px;
                background: {groove_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::groove:vertical:disabled {{
                background: {groove_disabled.name()};
            }}
            AnimatedSlider::sub-page:vertical {{
                background: {handle_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::add-page:vertical {{
                background: {groove_color.name()};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::handle:vertical {{
                background: {handle_color.name()};
                border: none;
                width: {handle_size}px;
                height: {handle_size}px;
                margin: 0 {handle_margin}px;
                border-radius: {handle_radius}px;
            }}
            AnimatedSlider::handle:vertical:hover {{
                background: {handle_hover.name()};
            }}
            AnimatedSlider::handle:vertical:pressed {{
                background: {handle_pressed.name()};
            }}
            AnimatedSlider::handle:vertical:disabled {{
                background: {handle_disabled.name()};
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
            slider.set_theme('dark')
        """
        logger.info(f"Setting theme to: {name}")
        ThemeManager.instance().set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name.

        Returns:
            Current theme name, or None if no theme is set

        Example:
            current_theme = slider.get_theme()
        """
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def set_value_animated(self, value: int, duration: int = 300) -> None:
        """
        Set slider value with smooth animation.

        Creates a property animation that smoothly transitions from the current
        value to the target value using an OutCubic easing curve.

        Args:
            value: Target slider value (will be clamped to min/max range)
            duration: Animation duration in milliseconds (default: 300ms)

        Example:
            slider.set_value_animated(75, 500)  # Animate to 75 over 500ms
        """
        # Clamp value to valid range
        if value < self.minimum():
            value = self.minimum()
            logger.debug(f"Value clamped to minimum: {value}")
        if value > self.maximum():
            value = self.maximum()
            logger.debug(f"Value clamped to maximum: {value}")

        animation = QPropertyAnimation(self, b"value")
        animation.setDuration(duration)
        animation.setStartValue(self.value())
        animation.setEndValue(value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        logger.info(f"Started animation to value {value} over {duration}ms")

    def set_value_directly(self, value: int) -> None:
        """
        Set value directly without animation.

        This is a convenience method that sets the value immediately.

        Args:
            value: Slider value to set

        Example:
            slider.set_value_directly(50)  # Jump to 50 immediately
        """
        self.setValue(value)

    def get_percentage(self) -> float:
        """
        Get current value as a percentage (0-100).

        Returns:
            Value percentage, independent of min/max values

        Example:
            percentage = slider.get_percentage()
            print(f"Progress: {percentage}%")
        """
        if self.maximum() == self.minimum():
            return 0.0
        return ((self.value() - self.minimum()) / (self.maximum() - self.minimum())) * 100

    @pyqtProperty(float)
    def handleScale(self) -> float:
        """
        Handle scale property for animations.

        This property can be animated to create scale effects on the handle.

        Returns:
            Current handle scale factor

        Example:
            # Animate handle scale (pulsing effect)
            slider.handleScale = 1.2
        """
        return self._handle_scale

    @handleScale.setter
    def handleScale(self, value: float) -> None:
        """
        Handle scale property setter.

        Args:
            value: New scale factor (1.0 = normal size)
        """
        if self._handle_scale != value:
            self._handle_scale = value
            self.update()
            logger.debug(f"Handle scale set to: {value}")

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源并取消主题管理器订阅。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        theme_mgr = ThemeManager.instance()
        theme_mgr.unsubscribe(self)
        logger.debug("AnimatedSlider unsubscribed from theme manager")

        self._clear_stylesheet_cache()

    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("AnimatedSlider scheduled for deletion")

    # Backward compatibility methods
    def setValueAnimated(self, value: int, duration: int = 300) -> None:
        """
        Set value with smooth animation (backward compatible).

        Args:
            value: Target slider value
            duration: Animation duration in milliseconds

        Note:
            This method is maintained for backward compatibility.
            Consider using set_value_animated() instead.
        """
        self.set_value_animated(value, duration)

    def setTheme(self, name: str) -> None:
        """
        Set theme by name (backward compatible).

        Args:
            name: Theme name

        Note:
            This method is maintained for backward compatibility.
            Consider using set_theme() instead.
        """
        self.set_theme(name)

    def getTheme(self) -> Optional[str]:
        """
        Get current theme name (backward compatible).

        Returns:
            Current theme name, or None if no theme is set

        Note:
            This method is maintained for backward compatibility.
            Consider using get_theme() instead.
        """
        return self.get_theme()
