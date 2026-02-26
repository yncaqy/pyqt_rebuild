"""
Toast Notification Component

Provides modern toast notification widgets with:
- Theme integration with automatic updates
- Smooth fade in/out animations
- Multiple toast types (info, success, warning, error)
- Flexible positioning
- Auto-hide with hover pause
- Optimized style caching for performance
- Memory-safe with proper cleanup
"""

import logging
from typing import Optional, Dict, Tuple, Any
from enum import Enum
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QRectF, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFrame, QGraphicsOpacityEffect, QSizePolicy
from core.theme_manager import ThemeManager, Theme

# Initialize logger
logger = logging.getLogger(__name__)


class ToastPosition(Enum):
    """
    Toast display positions.

    Positions are relative to the parent widget or window.
    """
    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_CENTER = 5
    BOTTOM_RIGHT = 6
    CENTER = 7


class ToastType(Enum):
    """
    Toast message types with semantic meaning.

    Each type has its own color scheme in the theme.
    """
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ToastConfig:
    """Configuration constants for toast behavior and styling."""
    
    # Size constraints
    ICON_SIZE = 18
    CLOSE_BUTTON_SIZE = 16
    
    # Spacing
    MARGIN = 20  # Margin from parent edges
    CONTENT_MARGIN_H = 12  # Horizontal content margin
    CONTENT_MARGIN_V = 8   # Vertical content margin
    SPACING = 8  # Spacing between elements
    
    # Animation
    FADE_DURATION = 300  # milliseconds
    HOVER_DELAY = 500  # milliseconds to wait after mouse leaves
    
    # Icon characters
    ICONS = {
        ToastType.INFO: "ℹ",
        ToastType.SUCCESS: "✓",
        ToastType.WARNING: "⚠",
        ToastType.ERROR: "✕"
    }
    
    # Icon styling
    ICON_FONT_SIZE = 14
    CLOSE_BUTTON_FONT_SIZE = 14
    
    # Message styling
    MESSAGE_FONT_SIZE = 12
    
    # Default duration
    DEFAULT_DURATION = 3000  # milliseconds
    
    # Cache size limit
    MAX_STYLESHEET_CACHE_SIZE = 50
    
    # Close button visibility
    DEFAULT_SHOW_CLOSE_BUTTON = False


class Toast(QFrame):
    """
    Modern toast notification widget with theme support and smooth animations.

    Features:
    - Theme integration with automatic updates
    - Smooth fade in/out animations using QPropertyAnimation
    - Multiple toast types (info, success, warning, error)
    - Flexible positioning (9 predefined positions)
    - Auto-hide with configurable duration
    - Hover pause (auto-hide pauses when mouse is over toast)
    - Click-to-close functionality
    - Memory-safe with proper cleanup

    Architecture:
        The toast uses Qt's opacity effect and property animation system
        for smooth fade transitions. It integrates with the theme manager
        for consistent styling across the application.

    Attributes:
        _message: Toast message text
        _toast_type: ToastType enum value
        _duration: Auto-hide duration in milliseconds
        _opacity: Current opacity value (0.0 to 1.0)
        _fade_animation: QPropertyAnimation for fade effects
        _current_theme: Currently applied theme
        _stylesheet_cache: Cache for generated stylesheets

    Signals:
        No custom signals (uses QProperty notifications instead)

    Example:
        toast = Toast("Operation completed successfully", ToastType.SUCCESS)
        toast.show(ToastPosition.TOP_CENTER, parent_widget)
    """

    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = ToastConfig.DEFAULT_DURATION,
        show_close_button: bool = ToastConfig.DEFAULT_SHOW_CLOSE_BUTTON,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the toast notification.
        
        Args:
            message: Toast message text
            toast_type: Type of toast (info, success, warning, error)
            duration: Auto-hide duration in milliseconds (0 for no auto-hide)
            show_close_button: Whether to show the close button
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        self._show_close_button = show_close_button
        self._opacity = 0.0

        # Set size policy to prevent compression
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Initialize theme manager reference
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        # Stylesheet cache for performance optimization
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Setup opacity effect for fade animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Setup UI
        self._setup_ui()

        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        # Apply initial theme
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        # Setup animations
        self._setup_animations()

        # Setup auto-hide timer
        if duration > 0:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._hide)
            self._timer.setSingleShot(True)

        # Pre-warm animation system to prevent first-click lag
        self._prewarm_animations()

        logger.debug(f"Toast created: {message} (type: {toast_type.value}, duration: {duration}ms)")

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            ToastConfig.CONTENT_MARGIN_H,
            ToastConfig.CONTENT_MARGIN_V,
            ToastConfig.CONTENT_MARGIN_H,
            ToastConfig.CONTENT_MARGIN_V
        )
        layout.setSpacing(ToastConfig.SPACING)
        
        # Icon label
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(ToastConfig.ICON_SIZE, ToastConfig.ICON_SIZE)
        layout.addWidget(self._icon_label)
        
        # Message label
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(False)
        self._message_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self._message_label, 1)
        
        # Close button (only if enabled)
        self._close_button = None
        if self._show_close_button:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(ToastConfig.CLOSE_BUTTON_SIZE, ToastConfig.CLOSE_BUTTON_SIZE)
            self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_button.clicked.connect(self._hide)
            layout.addWidget(self._close_button)
        
        # Note: Don't adjustSize here - it will be done after theme application

    def _setup_animations(self) -> None:
        """Setup fade in/out animations."""
        self._fade_animation = QPropertyAnimation(self, b"opacity")
        self._fade_animation.setDuration(ToastConfig.FADE_DURATION)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Pre-connect the finish signal to avoid first-click lag
        # Use a flag to track if we're in fade-out mode
        self._is_closing = False
        self._fade_animation.finished.connect(self._on_animation_finished)

    def _prewarm_animations(self) -> None:
        """Pre-warm the animation system to prevent first-use lag.

        This runs a minimal animation cycle to initialize Qt's animation
        system and graphics effect pipeline, eliminating the lag on first use.
        """
        try:
            # Trigger a minimal opacity update to initialize graphics pipeline
            self._opacity_effect.setOpacity(0.01)
            self._opacity_effect.setOpacity(0.0)

            # Force update to ensure graphics effect is initialized
            self.update()

            # Pre-size the toast to avoid layout recalculation on first show
            self.adjustSize()

            logger.debug("Animation system pre-warmed")
        except Exception as e:
            logger.warning(f"Error pre-warming animations: {e}")

    def _on_animation_finished(self) -> None:
        """Handle animation finished event."""
        if self._is_closing:
            self._close()
            self._is_closing = False

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change notification from theme manager.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to Toast: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        Apply theme to toast with caching support.

        Args:
            theme: Theme object containing color and style definitions
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        # Get colors based on toast type
        type_key = f'toast.{self._toast_type.value}'

        bg_color = theme.get_color(f'{type_key}.background', QColor(50, 50, 50))
        text_color = theme.get_color(f'{type_key}.text', QColor(255, 255, 255))
        border_color = theme.get_color(f'{type_key}.border', QColor(100, 100, 100))
        icon_color = theme.get_color(f'{type_key}.icon', QColor(255, 255, 255))

        border_radius = theme.get_value('toast.border_radius', 8)
        shadow_blur = theme.get_value('toast.shadow_blur', 10)

        # Create cache key
        cache_key = (
            bg_color.name(),
            text_color.name(),
            border_color.name(),
            icon_color.name(),
            border_radius,
            shadow_blur,
            self._toast_type.value,
        )

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for Toast")
        else:
            # Build stylesheet
            qss = f"""
            Toast {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {border_radius}px;
                padding: 0px;
            }}
            Toast QLabel {{
                color: {text_color.name()};
                background: transparent;
                border: none;
                font-size: {ToastConfig.MESSAGE_FONT_SIZE}px;
            }}
            Toast QPushButton {{
                color: {text_color.name()};
                background: transparent;
                border: none;
                font-size: {ToastConfig.CLOSE_BUTTON_FONT_SIZE}px;
                font-weight: bold;
            }}
            Toast QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: {border_radius}px;
            }}
            """

            # Cache the stylesheet
            if len(self._stylesheet_cache) < ToastConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")

        # Apply stylesheet
        self.setStyleSheet(qss)

        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

        # Update icon
        self._update_icon(icon_color)

        logger.debug(f"Theme applied to Toast: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _update_icon(self, color: QColor) -> None:
        """
        Update icon based on toast type.

        Args:
            color: Icon color
        """
        icon_text = ToastConfig.ICONS.get(self._toast_type, ToastConfig.ICONS[ToastType.INFO])
        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(
            f"color: {color.name()}; "
            f"font-size: {ToastConfig.ICON_FONT_SIZE}px; "
            f"font-weight: bold;"
        )

    @pyqtProperty(float)
    def opacity(self) -> float:
        """
        Opacity property for animations.

        Returns:
            Current opacity value (0.0 to 1.0)
        """
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        """
        Opacity property setter.

        Args:
            value: New opacity value (0.0 to 1.0)
        """
        self._opacity = value
        self._opacity_effect.setOpacity(value)
        self.update()
        logger.debug(f"Opacity set to: {value}")

    def show(self, position: ToastPosition = ToastPosition.TOP_CENTER, parent: Optional[QWidget] = None, show_close_button: bool = None) -> None:
        """
        Show toast at specified position.
        
        Args:
            position: Where to position the toast relative to parent
            parent: Parent widget (uses window() if None)
            show_close_button: Whether to show the close button (uses instance default if None)
        
        Example:
            toast.show(ToastPosition.TOP_CENTER, main_window)
            toast.show(ToastPosition.TOP_CENTER, main_window, show_close_button=True)
        """
        if show_close_button is not None:
            self._show_close_button = show_close_button
        if parent:
            # Reparent to the top-level window
            top_level = parent.window() if parent.window() else parent
            self.setParent(top_level)

        # Ensure proper sizing before positioning
        self.adjustSize()

        # Calculate position
        parent_widget = self.parent()
        if parent_widget:
            self._position_at(parent_widget, position)

        # Show as widget (not window)
        self.raise_()
        super().show()

        # Start fade in animation
        self._fade_in()

        # Start auto-hide timer
        if self._duration > 0 and hasattr(self, '_timer'):
            self._timer.start(self._duration)

        logger.info(f"Toast shown at {position.name}: {self._message}")

    def _position_at(self, parent: QWidget, position: ToastPosition) -> None:
        """
        Position toast relative to parent.

        Args:
            parent: Parent widget to position against
            position: Desired toast position
        """
        # Get parent's geometry (excluding window frame)
        rect = parent.rect()

        # Ensure toast has has been sized
        if self.width() == 0 or self.height() == 0:
            self.adjustSize()

        toast_width = self.width()
        toast_height = self.height()

        x, y = 0, 0
        margin = ToastConfig.MARGIN

        # Check if parent has a title bar (FramelessWindow)
        titlebar_height = 0
        if hasattr(parent, 'title_bar') and parent.title_bar:
            titlebar_height = parent.title_bar.height()

        # For TOP positions, add titlebar height to margin
        top_margin = margin + titlebar_height

        if position == ToastPosition.TOP_LEFT:
            x = margin
            y = top_margin
        elif position == ToastPosition.TOP_CENTER:
            x = (rect.width() - toast_width) // 2
            y = top_margin
        elif position == ToastPosition.TOP_RIGHT:
            x = rect.width() - toast_width - margin
            y = top_margin
        elif position == ToastPosition.BOTTOM_LEFT:
            x = margin
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.BOTTOM_CENTER:
            x = (rect.width() - toast_width) // 2
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.BOTTOM_RIGHT:
            x = rect.width() - toast_width - margin
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.CENTER:
            x = (rect.width() - toast_width) // 2
            y = (rect.height() - toast_height) // 2

        self.move(x, y)
        logger.debug(f"Positioned at ({x}, {y})")

    def _fade_in(self) -> None:
        """Start fade in animation."""
        self._fade_animation.stop()
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._is_closing = False
        self._fade_animation.start()
        logger.debug("Fade in animation started")

    def _hide(self) -> None:
        """Hide toast with fade out animation."""
        self._fade_animation.stop()
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._is_closing = True
        self._fade_animation.start()
        logger.debug("Fade out animation started")

    def _close(self) -> None:
        """Close toast and clean up resources."""
        self.timer_stop()
        super().close()
        logger.debug("Toast closed")

    def timer_stop(self) -> None:
        """
        Stop auto-hide timer.

        This pauses the auto-hide timer without canceling it.
        """
        if hasattr(self, '_timer') and self._timer.isActive():
            self._timer.stop()
            logger.debug("Auto-hide timer stopped")

    def close(self) -> None:
        """
        Close toast with fade out animation.

        This initiates a smooth fade out before closing the toast.

        Example:
            toast.close()  # Fade out and close
        """
        self._hide()

    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press for click-to-close functionality.

        Clicking anywhere on the toast will close it.

        Args:
            event: Mouse press event
        """
        self._hide()
        logger.debug("Toast closed by mouse click")

    def enterEvent(self, event: QEvent) -> None:
        """
        Pause auto-hide timer when mouse enters toast area.

        This allows users to read the message without it disappearing.

        Args:
            event: Enter event
        """
        if hasattr(self, '_timer') and self._timer.isActive():
            self._timer.stop()
            logger.debug("Auto-hide paused (mouse entered)")

    def leaveEvent(self, event: QEvent) -> None:
        """
        Resume auto-hide timer when mouse leaves toast area.

        Restarts the timer with a short delay to allow for smooth
        mouse movement.

        Args:
            event: Leave event
        """
        if hasattr(self, '_timer') and self._duration > 0:
            self._timer.start(ToastConfig.HOVER_DELAY)
            logger.debug(f"Auto-hide resumed (mouse left, delay: {ToastConfig.HOVER_DELAY}ms)")

    def set_message(self, message: str) -> None:
        """
        Update the toast message.

        Args:
            message: New message text

        Example:
            toast.set_message("Updated message")
        """
        self._message = message
        self._message_label.setText(message)
        self.adjustSize()
        logger.debug(f"Message updated: {message}")

    def get_message(self) -> str:
        """
        Get the current toast message.

        Returns:
            Current message text

        Example:
            message = toast.get_message()
        """
        return self._message

    def get_type(self) -> ToastType:
        """
        Get the toast type.

        Returns:
            ToastType enum value

        Example:
            toast_type = toast.get_type()
        """
        return self._toast_type

    def is_visible(self) -> bool:
        """
        Check if toast is currently visible.

        Returns:
            True if visible, False otherwise

        Example:
            if toast.is_visible():
                print("Toast is showing")
        """
        return super().isVisible()

    def cleanup(self) -> None:
        """
        Clean up resources and unsubscribe from theme manager.

        This method should be called before the toast is destroyed
        to prevent memory leaks.

        Example:
            toast.cleanup()
            toast.deleteLater()
        """
        # Stop timer
        if hasattr(self, '_timer'):
            self._timer.stop()

        # Unsubscribe from theme manager
        self._theme_mgr.unsubscribe(self)
        logger.debug("Toast unsubscribed from theme manager")

        # Clear cache
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")

    def deleteLater(self) -> None:
        """
        Schedule the widget for deletion with automatic cleanup.

        Overrides Qt's deleteLater to ensure proper cleanup.

        Example:
            toast.deleteLater()  # cleanup() is called automatically
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("Toast scheduled for deletion")
