"""
Animated Slider Component

Provides a modern, themed slider following WinUI3 design guidelines.

Features:
- Theme integration with automatic updates
- Smooth animated value transitions
- Support for horizontal and vertical orientations
- WinUI3 style: thin groove, circular handle with proper touch target
- Optimized style caching for performance
- Memory-safe with proper cleanup
- Automatic resource cleanup

Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/slider

WinUI3 Slider Design Specifications:
- Handle: 20px diameter circular, white (dark) / #595959 (light)
- Groove: 4px height, #292929 (dark) / #CACACA (light)
- Progress: #595959 accent color
- Touch target: Large enough for easy interaction
- States: Normal, Hover (scale 1.1), Pressed (scale 0.95), Disabled
"""

import logging
from typing import Optional, Tuple, Any
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import QSlider, QWidget, QSizePolicy, QStyleOptionSlider
from PyQt6.QtWidgets import QStyle
from src.core.theme_manager import ThemeManager, Theme
from src.core.animation_controller import AnimationController
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.core.style_override import StyleOverrideMixin
from src.themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class SliderConfig:
    """Configuration constants for slider behavior and styling, following WinUI3 design."""

    DEFAULT_MIN_WIDTH_HORIZONTAL = 120
    DEFAULT_MIN_HEIGHT_HORIZONTAL = 32
    DEFAULT_MIN_WIDTH_VERTICAL = 32
    DEFAULT_MIN_HEIGHT_VERTICAL = 120
    DEFAULT_HANDLE_SIZE = WINUI3_CONTROL_SIZING['slider']['handle_size']
    DEFAULT_HANDLE_RADIUS = WINUI3_CONTROL_SIZING['slider']['handle_radius']
    DEFAULT_GROOVE_HEIGHT = WINUI3_CONTROL_SIZING['slider']['groove_height']
    DEFAULT_GROOVE_BORDER_RADIUS = WINUI3_CONTROL_SIZING['slider']['groove_radius']
    DEFAULT_ANIMATION_DURATION = 300
    DEFAULT_HANDLE_SCALE = 1.0
    DEFAULT_TOUCH_TARGET_SIZE = 44


class AnimatedSlider(QSlider, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed slider with smooth animated value transitions, following WinUI3 design.

    Features:
    - Theme integration with automatic updates
    - Smooth animated value transitions with easing curves
    - Support for horizontal and vertical orientations
    - WinUI3 style: thin groove, circular handle with proper touch target
    - Optimized style caching for performance
    - Memory-safe with proper cleanup
    - Automatic resource cleanup
    - Custom painting for precise WinUI3 appearance

    Design Guidelines (from Microsoft):
    - Use natural orientation based on context
    - Ensure touch target is large enough for easy interaction
    - Provide immediate feedback during value changes
    - Use labels to show value range
    - Disable all related labels when slider is disabled

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

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self._orientation = orientation

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
        self._is_hovered: bool = False
        self._is_pressed: bool = False

        self._groove_color = QColor(200, 200, 200)
        self._progress_color = QColor(89, 89, 89)
        self._handle_color = QColor(255, 255, 255)
        self._handle_hover_color = QColor(245, 245, 245)
        self._handle_pressed_color = QColor(89, 89, 89)
        self._handle_disabled_color = QColor(200, 200, 200)
        self._groove_disabled_color = QColor(220, 220, 220)

        theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"AnimatedSlider initialized with orientation: {'horizontal' if orientation == Qt.Orientation.Horizontal else 'vertical'}")

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to AnimatedSlider: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme
        is_dark = getattr(theme, 'is_dark', False)

        if is_dark:
            self._groove_color = QColor(41, 41, 41)
            self._groove_disabled_color = QColor(40, 40, 40)
            self._progress_color = QColor(89, 89, 89)
            self._handle_color = QColor(255, 255, 255)
            self._handle_hover_color = QColor(240, 240, 240)
            self._handle_pressed_color = QColor(128, 128, 128)
            self._handle_disabled_color = QColor(102, 102, 102)
        else:
            self._groove_color = QColor(202, 202, 202)
            self._groove_disabled_color = QColor(249, 249, 249)
            self._progress_color = QColor(89, 89, 89)
            self._handle_color = QColor(89, 89, 89)
            self._handle_hover_color = QColor(16, 110, 190)
            self._handle_pressed_color = QColor(64, 64, 64)
            self._handle_disabled_color = QColor(202, 202, 202)

        self._groove_color = self.get_style_color(theme, 'slider.groove.background', self._groove_color)
        self._groove_disabled_color = self.get_style_color(theme, 'slider.groove.disabled', self._groove_disabled_color)
        self._progress_color = self.get_style_color(theme, 'slider.progress', self._progress_color)
        self._handle_color = self.get_style_color(theme, 'slider.handle.background', self._handle_color)
        self._handle_hover_color = self.get_style_color(theme, 'slider.handle.hover', self._handle_hover_color)
        self._handle_pressed_color = self.get_style_color(theme, 'slider.handle.pressed', self._handle_pressed_color)
        self._handle_disabled_color = self.get_style_color(theme, 'slider.handle.disabled', self._handle_disabled_color)
        border_radius = self.get_style_value(theme, 'slider.border_radius', SliderConfig.DEFAULT_GROOVE_BORDER_RADIUS)

        is_horizontal = self._orientation == Qt.Orientation.Horizontal
        cache_key = (
            self._groove_color.name(QColor.NameFormat.HexArgb),
            self._groove_disabled_color.name(QColor.NameFormat.HexArgb),
            self._progress_color.name(QColor.NameFormat.HexArgb),
            self._handle_color.name(QColor.NameFormat.HexArgb),
            self._handle_hover_color.name(QColor.NameFormat.HexArgb),
            self._handle_pressed_color.name(QColor.NameFormat.HexArgb),
            self._handle_disabled_color.name(QColor.NameFormat.HexArgb),
            border_radius,
            is_horizontal,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, border_radius)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        logger.debug(f"Theme applied to AnimatedSlider: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _build_stylesheet(self, theme: Theme, border_radius: int) -> str:
        """
        Build QSS stylesheet from theme properties, following WinUI3 design.

        Args:
            theme: Theme object
            border_radius: Border radius in pixels

        Returns:
            Complete QSS stylesheet string
        """
        handle_size = SliderConfig.DEFAULT_HANDLE_SIZE
        handle_radius = SliderConfig.DEFAULT_HANDLE_RADIUS
        groove_thickness = SliderConfig.DEFAULT_GROOVE_HEIGHT

        groove_hex = self._groove_color.name(QColor.NameFormat.HexArgb)
        groove_disabled_hex = self._groove_disabled_color.name(QColor.NameFormat.HexArgb)
        progress_hex = self._progress_color.name(QColor.NameFormat.HexArgb)
        handle_hex = self._handle_color.name(QColor.NameFormat.HexArgb)
        handle_hover_hex = self._handle_hover_color.name(QColor.NameFormat.HexArgb)
        handle_pressed_hex = self._handle_pressed_color.name(QColor.NameFormat.HexArgb)
        handle_disabled_hex = self._handle_disabled_color.name(QColor.NameFormat.HexArgb)

        handle_margin = (handle_size - groove_thickness) // 2

        qss = f"""
        AnimatedSlider {{
            background: transparent;
        }}
        """

        if self._orientation == Qt.Orientation.Horizontal:
            qss += f"""
            AnimatedSlider::groove:horizontal {{
                height: {groove_thickness}px;
                background: {groove_hex};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::groove:horizontal:disabled {{
                background: {groove_disabled_hex};
            }}
            AnimatedSlider::sub-page:horizontal {{
                background: {progress_hex};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::sub-page:horizontal:disabled {{
                background: {groove_disabled_hex};
            }}
            AnimatedSlider::add-page:horizontal {{
                background: transparent;
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::handle:horizontal {{
                background: {handle_hex};
                border: none;
                width: {handle_size}px;
                height: {handle_size}px;
                margin: -{handle_margin}px 0;
                border-radius: {handle_radius}px;
            }}
            AnimatedSlider::handle:horizontal:hover {{
                background: {handle_hover_hex};
            }}
            AnimatedSlider::handle:horizontal:pressed {{
                background: {handle_pressed_hex};
            }}
            AnimatedSlider::handle:horizontal:disabled {{
                background: {handle_disabled_hex};
            }}
            """
        else:
            qss += f"""
            AnimatedSlider::groove:vertical {{
                width: {groove_thickness}px;
                background: {groove_hex};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::groove:vertical:disabled {{
                background: {groove_disabled_hex};
            }}
            AnimatedSlider::sub-page:vertical {{
                background: {progress_hex};
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::sub-page:vertical:disabled {{
                background: {groove_disabled_hex};
            }}
            AnimatedSlider::add-page:vertical {{
                background: transparent;
                border-radius: {border_radius}px;
            }}
            AnimatedSlider::handle:vertical {{
                background: {handle_hex};
                border: none;
                width: {handle_size}px;
                height: {handle_size}px;
                margin: 0 -{handle_margin}px;
                border-radius: {handle_radius}px;
            }}
            AnimatedSlider::handle:vertical:hover {{
                background: {handle_hover_hex};
            }}
            AnimatedSlider::handle:vertical:pressed {{
                background: {handle_pressed_hex};
            }}
            AnimatedSlider::handle:vertical:disabled {{
                background: {handle_disabled_hex};
            }}
            """

        return qss

    def enterEvent(self, event) -> None:
        """Handle mouse enter event for hover state."""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave event for hover state."""
        self._is_hovered = False
        self._is_pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press event for pressed state."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release event for pressed state."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        """Custom paint event for precise WinUI3 slider appearance."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        rect = self.rect()
        handle_size = SliderConfig.DEFAULT_HANDLE_SIZE
        groove_thickness = SliderConfig.DEFAULT_GROOVE_HEIGHT
        handle_radius = SliderConfig.DEFAULT_HANDLE_RADIUS
        groove_radius = SliderConfig.DEFAULT_GROOVE_BORDER_RADIUS

        is_enabled = self.isEnabled()
        is_horizontal = self._orientation == Qt.Orientation.Horizontal

        if is_horizontal:
            groove_y = (rect.height() - groove_thickness) // 2
            groove_rect = QRectF(
                handle_radius,
                groove_y,
                rect.width() - handle_radius * 2,
                groove_thickness
            )
        else:
            groove_x = (rect.width() - groove_thickness) // 2
            groove_rect = QRectF(
                groove_x,
                handle_radius,
                groove_thickness,
                rect.height() - handle_radius * 2
            )

        groove_color = self._groove_color if is_enabled else self._groove_disabled_color
        painter.setBrush(QBrush(groove_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(groove_rect, groove_radius, groove_radius)

        value_range = self.maximum() - self.minimum()
        if value_range > 0:
            progress = (self.value() - self.minimum()) / value_range
        else:
            progress = 0

        if is_horizontal:
            progress_width = groove_rect.width() * progress
            progress_rect = QRectF(
                groove_rect.x(),
                groove_rect.y(),
                progress_width,
                groove_rect.height()
            )
        else:
            progress_height = groove_rect.height() * (1 - progress)
            progress_rect = QRectF(
                groove_rect.x(),
                groove_rect.y() + progress_height,
                groove_rect.width(),
                groove_rect.height() - progress_height
            )

        if progress > 0:
            progress_color = self._progress_color if is_enabled else self._groove_disabled_color
            painter.setBrush(QBrush(progress_color))
            painter.drawRoundedRect(progress_rect, groove_radius, groove_radius)

        if is_horizontal:
            handle_x = groove_rect.x() + groove_rect.width() * progress - handle_size / 2
            handle_y = (rect.height() - handle_size) // 2
        else:
            handle_x = (rect.width() - handle_size) // 2
            handle_y = groove_rect.y() + groove_rect.height() * (1 - progress) - handle_size / 2

        handle_center = QPointF(handle_x + handle_size / 2, handle_y + handle_size / 2)

        if is_enabled:
            if self._is_pressed:
                handle_color = self._handle_pressed_color
            elif self._is_hovered:
                handle_color = self._handle_hover_color
            else:
                handle_color = self._handle_color
        else:
            handle_color = self._handle_disabled_color

        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(handle_center, handle_radius, handle_radius)

        if is_enabled and self._is_hovered and not self._is_pressed:
            hover_ring_color = QColor(handle_color)
            hover_ring_color.setAlpha(30)
            painter.setBrush(QBrush(hover_ring_color))
            painter.drawEllipse(handle_center, handle_radius + 3, handle_radius + 3)
            painter.setBrush(QBrush(handle_color))
            painter.drawEllipse(handle_center, handle_radius, handle_radius)

        painter.end()

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
        self.clear_overrides()

    def deleteLater(self) -> None:
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
        logger.debug("AnimatedSlider scheduled for deletion")

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
