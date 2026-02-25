"""
Animated Slider Component

Provides a modern, themed slider with:
- Theme integration with automatic updates
- Smooth animated value transitions
- Support for horizontal and vertical orientations
- Customizable handle animations
- Optimized style caching for performance
- Memory-safe with proper cleanup
"""

import logging
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSlider, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.animation_controller import AnimationController

# Initialize logger
logger = logging.getLogger(__name__)


class SliderConfig:
    """Configuration constants for slider behavior and styling."""

    # Default size constraints
    DEFAULT_MIN_WIDTH_HORIZONTAL = 150
    DEFAULT_MIN_HEIGHT_HORIZONTAL = 30
    DEFAULT_MIN_WIDTH_VERTICAL = 30
    DEFAULT_MIN_HEIGHT_VERTICAL = 150

    # Handle styling
    DEFAULT_HANDLE_SIZE = 18
    DEFAULT_HANDLE_RADIUS = 9
    DEFAULT_HANDLE_MARGIN = -9

    # Groove styling
    DEFAULT_GROOVE_HEIGHT = 6
    DEFAULT_GROOVE_WIDTH = 6
    DEFAULT_GROOVE_BORDER_RADIUS = 2

    # Spacing
    DEFAULT_PADDING = 9

    # Animation defaults
    DEFAULT_ANIMATION_DURATION = 300  # milliseconds
    DEFAULT_HANDLE_SCALE = 1.0

    # Cache size limit
    MAX_STYLESHEET_CACHE_SIZE = 100


class AnimatedSlider(QSlider):
    """
    Themed slider with smooth animated value transitions.

    Features:
    - Theme integration with automatic updates
    - Smooth animated value transitions with easing curves
    - Support for horizontal and vertical orientations
    - Customizable handle scale animations
    - Optimized style caching for performance
    - Memory-safe with proper cleanup

    The slider provides smooth value transitions using Qt's property
    animation system, creating a more polished user experience compared
    to standard sliders.

    Attributes:
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets
        _handle_scale: Scale factor for handle animations
        _orientation: Slider orientation (horizontal/vertical)

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
        """
        Initialize the themed slider.

        Args:
            orientation: Slider orientation (Horizontal or Vertical)
            parent: Parent widget
        """
        super().__init__(orientation, parent)

        # Store orientation
        self._orientation = orientation

        # Set size policy based on orientation
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

        # Initialize theme manager reference
        theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Animation properties
        self._handle_scale = SliderConfig.DEFAULT_HANDLE_SCALE

        # Subscribe to theme changes
        theme_mgr.subscribe(self, self._on_theme_changed)

        # Apply initial theme
        initial_theme = theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"AnimatedSlider initialized with orientation: {'horizontal' if orientation == Qt.Orientation.Horizontal else 'vertical'}")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to AnimatedSlider: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to slider with caching support.

        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        # Get colors with fallback defaults
        groove_color = theme.get_color('slider.groove.background', QColor(224, 224, 224))
        groove_disabled = theme.get_color('slider.groove.disabled', QColor(240, 240, 240))

        handle_color = theme.get_color('slider.handle.background', QColor(52, 152, 219))
        handle_hover = theme.get_color('slider.handle.hover', QColor(41, 128, 185))
        handle_pressed = theme.get_color('slider.handle.pressed', QColor(26, 82, 118))
        handle_disabled = theme.get_color('slider.handle.disabled', QColor(176, 176, 176))

        border_radius = theme.get_value('slider.border_radius', SliderConfig.DEFAULT_GROOVE_BORDER_RADIUS)

        # Create cache key (orientation-specific)
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

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for AnimatedSlider")
        else:
            # Build stylesheet
            qss = self._build_stylesheet(theme, groove_color, groove_disabled,
                                        handle_color, handle_hover, handle_pressed,
                                        handle_disabled, border_radius)

            # Cache the stylesheet
            if len(self._stylesheet_cache) < SliderConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")

        # Apply stylesheet
        self.setStyleSheet(qss)

        # Force style refresh
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

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the slider is destroyed
        to prevent memory leaks.

        Example:
            slider.cleanup()
            slider.deleteLater()
        """
        # Unsubscribe from theme manager to prevent memory leaks
        theme_mgr = ThemeManager.instance()
        theme_mgr.unsubscribe(self)
        logger.debug("AnimatedSlider unsubscribed from theme manager")

        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.

        Example:
            slider.deleteLater()  # cleanup() is called automatically
        """
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
