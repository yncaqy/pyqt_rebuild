"""
Circular Progress Component

Circular progress widget with pluggable painting strategy.

Demonstrates complete separation of rendering logic from component,
using the Strategy Pattern for flexible rendering approaches.

Features:
- Pluggable painting strategies (circular, gradient, etc.)
- Theme-based rendering
- Animated value transitions
- Optimized partial updates
- Memory-safe with proper cleanup
"""

import logging
from typing import Optional, Dict
from PyQt6.QtCore import Qt, QRectF, pyqtProperty, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy

from core.theme_manager import ThemeManager, Theme
from core.animation_controller import AnimationController
from core.painting.widget_painter import WidgetPainter, PaintContext, PainterFactory
from core.painting.circular_progress_painter import (
    CircularProgressPainter,
    CircularProgressGradientPainter
)

# Initialize logger
logger = logging.getLogger(__name__)


class ProgressConfig:
    """Configuration constants for circular progress widget."""

    # Default size
    DEFAULT_MIN_SIZE = 100
    DEFAULT_MIN_WIDTH = 100
    DEFAULT_MIN_HEIGHT = 100

    # Default progress properties
    DEFAULT_MAXIMUM = 100.0
    DEFAULT_MINIMUM = 0.0
    DEFAULT_VALUE = 0.0
    DEFAULT_THICKNESS = 10
    DEFAULT_SHOW_TEXT = True

    # Animation defaults
    DEFAULT_ANIMATION_DURATION = 300  # milliseconds

    # Paint adjustments
    ANTI_ALIASING_MARGIN = 2  # Margin for anti-aliasing
    TEXT_REGION_RATIO = 0.3  # Text size relative to widget height

    # Painter names
    PAINTER_CIRCULAR = 'circular'
    PAINTER_CIRCULAR_GRADIENT = 'circular_gradient'


class CircularProgress(QWidget):
    """
    Circular progress widget with pluggable painting strategy.

    This component demonstrates the Strategy Pattern for complete separation
    of rendering logic from the component implementation. Different painting
    strategies can be plugged in at runtime without modifying the component.

    Features:
    - Pluggable painting strategies (circular, gradient, etc.)
    - Theme-based rendering with automatic updates
    - Animated value transitions with easing curves
    - Optimized partial updates (only redraw what's needed)
    - Memory-safe with proper cleanup

    Architecture:
        The widget uses a "Painter Strategy" where rendering logic is
        delegated to a WidgetPainter implementation. This allows for:
        - Runtime style switching
        - Easy addition of new visual styles
        - Separation of concerns
        - Testable rendering logic

    Attributes:
        _value: Current progress value
        _maximum: Maximum progress value
        _minimum: Minimum progress value
        _show_text: Whether to show percentage text
        _thickness: Progress bar thickness in pixels
        _painter: Current painting strategy
        _animator: Animation controller

    Signals:
        valueChanged: Emitted when the progress value changes

    Example:
        progress = CircularProgress()
        progress.set_value_animated(75, 1000)  # Animate to 75%
        progress.set_painter_by_name('circular_gradient')  # Switch painter
    """

    # Signals for value changes
    valueChanged = pyqtSignal(float)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        painter: Optional[WidgetPainter] = None
    ):
        """
        Initialize the circular progress widget.

        Args:
            parent: Parent widget
            painter: Optional custom painter strategy. If None, uses default circular painter.
        """
        super().__init__(parent)

        # Initialize properties with defaults
        self._value = ProgressConfig.DEFAULT_VALUE
        self._maximum = ProgressConfig.DEFAULT_MAXIMUM
        self._minimum = ProgressConfig.DEFAULT_MINIMUM
        self._show_text = ProgressConfig.DEFAULT_SHOW_TEXT
        self._thickness = ProgressConfig.DEFAULT_THICKNESS

        # Initialize theme manager
        theme_mgr = ThemeManager.instance()

        # Initialize painter (strategy pattern)
        if painter:
            self._painter = painter
            logger.debug(f"Initialized with custom painter: {painter.__class__.__name__}")
        else:
            # Use default painter
            self._painter = CircularProgressPainter(theme_mgr.current_theme())
            logger.debug("Initialized with default circular painter")

        # Register painters with factory (only once)
        if not PainterFactory.list_available():
            PainterFactory.register(ProgressConfig.PAINTER_CIRCULAR, CircularProgressPainter)
            PainterFactory.register(ProgressConfig.PAINTER_CIRCULAR_GRADIENT, CircularProgressGradientPainter)
            logger.debug("Registered painters with factory")

        # Animation controller
        self._animator = AnimationController(self, self)

        # Subscribe to theme changes
        theme_mgr.subscribe(self, self._on_theme_changed)

        # Enable paint events for custom drawing
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set minimum size for circular shape
        self.setMinimumSize(
            ProgressConfig.DEFAULT_MIN_SIZE,
            ProgressConfig.DEFAULT_MIN_SIZE
        )

        # Set size policy to maintain minimum size
        # Use Fixed to prevent layout from compressing the component
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        logger.debug("CircularProgress initialized successfully")

    # Q_PROPERTY declarations
    @pyqtProperty(float)
    def value(self) -> float:
        """Current progress value."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """
        Set progress value.

        The value is clamped to the range [minimum, maximum].

        Args:
            value: New progress value
        """
        # Clamp to range
        value = max(self._minimum, min(self._maximum, value))

        if self._value != value:
            self._value = value
            self.valueChanged.emit(value)
            self.update()
            logger.debug(f"Value changed to: {value}")

    @pyqtProperty(float)
    def maximum(self) -> float:
        """Maximum progress value."""
        return self._maximum

    @maximum.setter
    def maximum(self, value: float) -> None:
        """
        Set maximum progress value.

        Args:
            value: New maximum value
        """
        if self._maximum != value:
            self._maximum = value
            self.update()
            logger.debug(f"Maximum set to: {value}")

    @pyqtProperty(float)
    def minimum(self) -> float:
        """Minimum progress value."""
        return self._minimum

    @minimum.setter
    def minimum(self, value: float) -> None:
        """
        Set minimum progress value.

        Args:
            value: New minimum value
        """
        if self._minimum != value:
            self._minimum = value
            self.update()
            logger.debug(f"Minimum set to: {value}")

    @pyqtProperty(bool)
    def showText(self) -> bool:
        """Whether to show percentage text in the center."""
        return self._show_text

    @showText.setter
    def showText(self, show: bool) -> None:
        """
        Toggle text display in the center of the progress indicator.

        Args:
            show: True to show percentage text, False to hide
        """
        if self._show_text != show:
            self._show_text = show
            self._update_text_region()
            logger.debug(f"Text display: {'enabled' if show else 'disabled'}")

    @pyqtProperty(int)
    def thickness(self) -> int:
        """Progress bar thickness in pixels."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: int) -> None:
        """
        Set the thickness of the progress bar.

        Args:
            thickness: Thickness in pixels
        """
        if self._thickness != thickness:
            self._thickness = thickness
            self.update()
            logger.debug(f"Thickness set to: {thickness}px")

    def set_value_animated(self, value: float, duration: int = 300) -> None:
        """
        Animate to new value with smooth easing.

        Creates a property animation that smoothly transitions from the current
        value to the target value using an OutCubic easing curve.

        Args:
            value: Target progress value
            duration: Animation duration in milliseconds (default: 300ms)

        Example:
            progress.set_value_animated(75, 1000)  # Animate to 75% over 1 second
        """
        anim = QPropertyAnimation(self, b"value")
        anim.setDuration(duration)
        anim.setStartValue(self._value)
        anim.setEndValue(value)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        logger.info(f"Started animation to value {value} over {duration}ms")

    def set_painter(self, painter: WidgetPainter) -> None:
        """
        Replace painting strategy at runtime.

        This enables complete style switching without modifying the component.
        The strategy pattern allows for flexible rendering approaches.

        Args:
            painter: New painter strategy to use

        Example:
            from core.painting.circular_progress_painter import CircularProgressGradientPainter
            progress.set_painter(CircularProgressGradientPainter(theme))
        """
        self._painter = painter
        self.update()
        logger.info(f"Painter changed to: {painter.__class__.__name__}")

    def set_painter_by_name(self, painter_name: str) -> bool:
        """
        Set painter by registered name.

        This is the recommended way to switch between predefined painting styles.

        Args:
            painter_name: Name of registered painter ('circular', 'circular_gradient', etc.)

        Returns:
            True if painter was found and applied, False otherwise

        Example:
            success = progress.set_painter_by_name('circular_gradient')
            if success:
                print("Painter switched successfully")
        """
        theme_mgr = ThemeManager.instance()
        painter = PainterFactory.create(painter_name, theme_mgr.current_theme())

        if painter:
            self._painter = painter
            self.update()
            logger.info(f"Painter switched to: {painter_name}")
            return True

        logger.warning(f"Painter not found: {painter_name}")
        return False

    def get_painter_name(self) -> Optional[str]:
        """
        Get the name of the current painter.

        Returns:
            Painter name if available, None otherwise

        Example:
            painter_name = progress.get_painter_name()
            print(f"Using painter: {painter_name}")
        """
        if hasattr(self._painter, '__class__'):
            return self._painter.__class__.__name__
        return None

    def get_progress_percentage(self) -> float:
        """
        Get progress as a percentage (0-100).

        Returns:
            Progress percentage, independent of min/max values

        Example:
            percentage = progress.get_progress_percentage()
            print(f"Progress: {percentage}%")
        """
        if self._maximum == self._minimum:
            return 0.0
        return ((self._value - self._minimum) / (self._maximum - self._minimum)) * 100

    def is_complete(self) -> bool:
        """
        Check if progress is at maximum value.

        Returns:
            True if value equals maximum, False otherwise

        Example:
            if progress.is_complete():
                print("Task completed!")
        """
        return self._value >= self._maximum

    def reset(self) -> None:
        """
        Reset progress to minimum value.

        This is a convenience method to quickly reset the progress indicator.

        Example:
            progress.reset()  # Reset to 0%
        """
        self.value = self._minimum
        logger.debug("Progress reset to minimum value")

    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme by name.

        This is a convenience method that delegates to the theme manager.

        Args:
            theme_name: Theme name (e.g., 'dark', 'light', 'default')

        Example:
            progress.set_theme('dark')
        """
        logger.info(f"Setting theme to: {theme_name}")
        ThemeManager.instance().set_theme(theme_name)

    def get_theme(self) -> Optional[str]:
        """
        Get the current theme name.

        Returns:
            Current theme name, or None if no theme is set

        Example:
            current_theme = progress.get_theme()
        """
        theme_mgr = ThemeManager.instance()
        theme = theme_mgr.current_theme()
        if theme and hasattr(theme, 'name'):
            return theme.name
        return None

    def _on_theme_changed(self, theme: Optional[Theme]) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            if self._painter:
                self._painter.set_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to CircularProgress: {e}")
            import traceback
            traceback.print_exc()
        self.update()
        logger.debug(f"Theme changed to: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint event - delegates to painter strategy.

        This method is intentionally thin - it only sets up the paint context
        and delegates the actual rendering to the painter strategy. This follows
        the Strategy Pattern for flexible, testable rendering.

        Args:
            event: Paint event
        """
        painter = QPainter(self)

        # Create paint context with adjusted rect for anti-aliasing
        rect = self.rect()
        rect = rect.adjusted(
            ProgressConfig.ANTI_ALIASING_MARGIN,
            ProgressConfig.ANTI_ALIASING_MARGIN,
            -ProgressConfig.ANTI_ALIASING_MARGIN,
            -ProgressConfig.ANTI_ALIASING_MARGIN
        )

        context = PaintContext(
            widget=self,
            painter=painter,
            rect=QRectF(rect),
            theme=ThemeManager.instance().current_theme(),
            value=self._value,
            maximum=self._maximum,
            minimum=self._minimum,
            thickness=self._thickness,
            show_text=self._show_text,
            state={
                'hover': self.underMouse(),
                'enabled': self.isEnabled()
            }
        )

        # Delegate to painter strategy
        self._painter.paint(context)

    def _update_text_region(self) -> None:
        """
        Trigger partial update for center text only.

        This optimization ensures that only the text region is repainted,
        not the entire progress indicator, improving performance.
        """
        # Calculate text region
        rect = self.rect()
        center = rect.center()
        text_size = rect.height() * ProgressConfig.TEXT_REGION_RATIO

        text_region = QRectF(
            center.x() - text_size / 2,
            center.y() - text_size / 2,
            text_size,
            text_size
        )

        self.update(text_region.toRect())
        logger.debug(f"Partial update triggered for text region: {text_region}")

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the widget is destroyed
        to prevent memory leaks.

        Example:
            progress.cleanup()
            progress.deleteLater()
        """
        # Unsubscribe from theme manager
        theme_mgr = ThemeManager.instance()
        theme_mgr.unsubscribe(self)
        logger.debug("CircularProgress unsubscribed from theme manager")

        # Animation controller cleanup is handled by Qt parent-child relationship
        # No explicit cleanup needed for _animator

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.

        Example:
            progress.deleteLater()  # cleanup() is called automatically
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("CircularProgress scheduled for deletion")

    # Backward compatibility methods
    def setValue(self, value: float) -> None:
        """
        Set value directly without animation.

        This is a backward-compatible convenience method that directly
        sets the value property.

        Args:
            value: Progress value to set

        Note:
            For animated transitions, use set_value_animated() instead.
        """
        self.value = value

    def getValue(self) -> float:
        """
        Get current progress value.

        This is a backward-compatible convenience method.

        Returns:
            Current progress value

        Note:
            Consider using the value property directly: progress.value
        """
        return self._value

    def setTheme(self, theme_name: str) -> None:
        """
        Switch theme (backward compatible method).

        Args:
            theme_name: Name of theme to apply

        Note:
            This method is maintained for backward compatibility.
            Consider using set_theme() instead.
        """
        self.set_theme(theme_name)
