"""
IconWidget Component

A reusable icon display widget with comprehensive features:
- Multiple icon sources (SVG, PNG, font icons, raw SVG string)
- Unified size control with standard sizes
- Custom color and style support
- Lazy loading for performance optimization
- Error handling with fallback icons
- Theme integration

Features:
- High-quality rendering at any resolution
- Smooth scaling with anti-aliasing
- Hover and click effects
- Accessible design
- Memory efficient with caching

Reference: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
"""

import logging
from typing import Optional, Union
from enum import Enum
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QEvent
from PyQt6.QtGui import QPainter, QColor, QPixmap, QIcon, QEnterEvent, QMouseEvent

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class IconSize(Enum):
    """Standard icon sizes for consistency across the application."""
    TINY = 12
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    XLARGE = 32
    XXLARGE = 48
    HUGE = 64


class IconSource:
    """Icon source configuration."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        svg_content: Optional[str] = None,
        icon: Optional[QIcon] = None,
        pixmap: Optional[QPixmap] = None
    ):
        self.name = name
        self.svg_content = svg_content
        self.icon = icon
        self.pixmap = pixmap
    
    @classmethod
    def from_name(cls, name: str) -> 'IconSource':
        """Create icon source from icon name."""
        return cls(name=name)
    
    @classmethod
    def from_svg(cls, svg_content: str) -> 'IconSource':
        """Create icon source from SVG content string."""
        return cls(svg_content=svg_content)
    
    @classmethod
    def from_icon(cls, icon: QIcon) -> 'IconSource':
        """Create icon source from QIcon."""
        return cls(icon=icon)
    
    @classmethod
    def from_pixmap(cls, pixmap: QPixmap) -> 'IconSource':
        """Create icon source from QPixmap."""
        return cls(pixmap=pixmap)


class IconWidgetConfig:
    """Configuration constants for IconWidget."""
    
    DEFAULT_SIZE = IconSize.MEDIUM.value
    DEFAULT_BORDER_RADIUS = 4
    PRESSED_SCALE = 0.9
    ANIMATION_DURATION = 100
    LAZY_LOAD_DELAY = 100


class IconWidget(QWidget):
    """
    A reusable icon display widget with comprehensive features.
    
    Features:
    - Multiple icon sources (SVG, PNG, font icons, raw SVG string)
    - Unified size control with standard sizes
    - Custom color and style support
    - Lazy loading for performance optimization
    - Error handling with fallback icons
    - Theme integration
    - Hover and click effects
    
    Signals:
        clicked: Emitted when the icon is clicked
        doubleClicked: Emitted when the icon is double-clicked
    
    Example:
        # From icon name
        icon_widget = IconWidget("Play_white", size=IconSize.LARGE)
        
        # With custom color
        icon_widget = IconWidget("Play_white", color=QColor(255, 0, 0))
        
        # From SVG content
        svg = '<svg viewBox="0 0 24 24">...</svg>'
        icon_widget = IconWidget.from_svg(svg, size=IconSize.MEDIUM)
        
        # From QIcon
        icon = QIcon("path/to/icon.png")
        icon_widget = IconWidget.from_icon(icon)
    """
    
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()
    
    def __init__(
        self,
        source: Optional[Union[str, IconSource]] = None,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None,
        *,
        clickable: bool = False,
        hover_effect: bool = False,
        lazy_load: bool = False,
        theme_aware: bool = True
    ):
        """
        Initialize IconWidget.
        
        Args:
            source: Icon source (name, IconSource, or None for lazy loading)
            size: Icon size (int or IconSize enum)
            color: Optional color to apply to the icon
            parent: Parent widget
            clickable: Whether the icon responds to clicks
            hover_effect: Whether to show hover animation
            lazy_load: Whether to delay icon loading
            theme_aware: Whether to auto-switch icon variant based on theme
        """
        super().__init__(parent)
        
        self._icon_mgr = IconManager.instance()
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self._size = size.value if isinstance(size, IconSize) else size
        self._color = color
        self._source: Optional[IconSource] = None
        self._base_icon_name: Optional[str] = None
        self._pixmap: Optional[QPixmap] = None
        self._fallback_pixmap: Optional[QPixmap] = None
        self._is_loaded = False
        self._load_error = False
        
        self._clickable = clickable
        self._hover_effect = hover_effect
        self._lazy_load = lazy_load
        self._theme_aware = theme_aware
        
        self._is_hovered = False
        self._is_pressed = False
        self._scale = 1.0
        self._opacity = 1.0
        
        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
        if source is not None:
            if isinstance(source, str):
                self._source = IconSource.from_name(source)
            else:
                self._source = source
            
            if lazy_load:
                QTimer.singleShot(IconWidgetConfig.LAZY_LOAD_DELAY, self._load_icon)
            else:
                self._load_icon()
    
    def _setup_ui(self) -> None:
        """Setup UI properties."""
        self._base_size = self._size
        self._max_display_size = self._size
        self.setMinimumSize(self._max_display_size, self._max_display_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        if self._clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle theme change."""
        self._current_theme = theme
        if self._source and self._source.name:
            self._load_icon()
        self.update()
    
    def _load_icon(self) -> None:
        """Load icon from source."""
        if self._source is None:
            return
        
        try:
            self._load_error = False
            
            if self._source.pixmap:
                self._pixmap = self._source.pixmap
            elif self._source.icon:
                self._pixmap = self._source.icon.pixmap(self._size, self._size)
            elif self._source.svg_content:
                self._pixmap = self._icon_mgr.create_pixmap_from_svg(
                    self._source.svg_content, self._size
                )
            elif self._source.name:
                icon_name = self._source.name
                
                if self._theme_aware and self._current_theme:
                    theme_type = self._current_theme.name if hasattr(self._current_theme, 'name') else 'dark'
                    resolved_name = self._icon_mgr.resolve_icon_name(icon_name, theme_type)
                    if resolved_name != icon_name:
                        icon_name = resolved_name
                
                is_colored = self._icon_mgr.is_colored_icon(icon_name)
                color = self._color
                
                if color is None and self._current_theme and not is_colored:
                    color = self._get_theme_color()
                
                if color and not is_colored:
                    icon = self._icon_mgr.get_colored_icon(
                        icon_name, color, self._size
                    )
                else:
                    icon = self._icon_mgr.get_icon(icon_name, self._size)
                
                self._pixmap = icon.pixmap(self._size, self._size)
            
            self._is_loaded = True
            self.update()
            
        except Exception as e:
            logger.error(f"Error loading icon: {e}")
            self._load_error = True
            self._pixmap = self._get_fallback_pixmap()
            self.update()
    
    def _get_theme_color(self) -> Optional[QColor]:
        """Get icon color from current theme."""
        if self._current_theme:
            return self._current_theme.get_color('icon.normal', QColor(255, 255, 255))
        return None
    
    def _get_fallback_pixmap(self) -> QPixmap:
        """Get fallback pixmap for error cases."""
        if self._fallback_pixmap is None:
            self._fallback_pixmap = QPixmap(self._size, self._size)
            self._fallback_pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(self._fallback_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(128, 128, 128))
            painter.drawEllipse(0, 0, self._size, self._size)
            
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(0, 0, self._size, self._size, 
                           Qt.AlignmentFlag.AlignCenter, "?")
            painter.end()
        
        return self._fallback_pixmap
    
    def get_scale(self) -> float:
        return self._scale
    
    def set_scale(self, value: float) -> None:
        self._scale = value
        self.update()
    
    scale = pyqtProperty(float, get_scale, set_scale)
    
    def get_opacity(self) -> float:
        return self._opacity
    
    def set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def _animate_press(self) -> None:
        """Animate press effect - scale down."""
        if not self._hover_effect:
            return
        
        self._press_anim = QPropertyAnimation(self, b"scale")
        self._press_anim.setDuration(IconWidgetConfig.ANIMATION_DURATION)
        self._press_anim.setStartValue(self._scale)
        self._press_anim.setEndValue(IconWidgetConfig.PRESSED_SCALE)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._press_anim.start()
    
    def _animate_release(self) -> None:
        """Animate release effect - restore to normal size."""
        if not self._hover_effect:
            return
        
        self._release_anim = QPropertyAnimation(self, b"scale")
        self._release_anim.setDuration(IconWidgetConfig.ANIMATION_DURATION)
        self._release_anim.setStartValue(self._scale)
        self._release_anim.setEndValue(1.0)
        self._release_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._release_anim.start()
    
    def enterEvent(self, event: QEnterEvent) -> None:
        self._is_hovered = True
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent) -> None:
        self._is_hovered = False
        self._is_pressed = False
        super().leaveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._animate_press()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self._animate_release()
            
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)
        
        pixmap = self._pixmap if self._pixmap else self._get_fallback_pixmap()
        
        widget_size = min(self.width(), self.height())
        icon_display_size = int(self._base_size * self._scale)
        x_offset = (self.width() - icon_display_size) // 2
        y_offset = (self.height() - icon_display_size) // 2
        
        if self._scale != 1.0:
            scaled_pixmap = pixmap.scaled(
                icon_display_size, icon_display_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            painter.drawPixmap(x_offset, y_offset, pixmap)
    
    def sizeHint(self) -> QSize:
        return QSize(self._max_display_size, self._max_display_size)
    
    def minimumSizeHint(self) -> QSize:
        return QSize(self._max_display_size, self._max_display_size)
    
    # ==================== Public API ====================
    
    def setSource(self, source: Union[str, IconSource]) -> None:
        """
        Set icon source.
        
        Args:
            source: Icon name string or IconSource object
        """
        if isinstance(source, str):
            self._source = IconSource.from_name(source)
        else:
            self._source = source
        
        self._is_loaded = False
        self._load_icon()
    
    def source(self) -> Optional[IconSource]:
        """Get current icon source."""
        return self._source
    
    def setSize(self, size: Union[int, IconSize]) -> None:
        """
        Set icon size.
        
        Args:
            size: Icon size (int or IconSize enum)
        """
        new_size = size.value if isinstance(size, IconSize) else size
        if self._base_size != new_size:
            self._base_size = new_size
            self._size = new_size
            self._max_display_size = new_size
            self.setFixedSize(self._max_display_size, self._max_display_size)
            self._fallback_pixmap = None
            
            if self._source and self._is_loaded:
                self._load_icon()
    
    def size(self) -> int:
        """Get current icon size."""
        return self._size
    
    def setColor(self, color: Optional[QColor]) -> None:
        """
        Set icon color.
        
        Args:
            color: Color to apply, or None to use theme default
        """
        if self._color != color:
            self._color = color
            if self._source:
                self._load_icon()
    
    def color(self) -> Optional[QColor]:
        """Get current icon color."""
        return self._color
    
    def setClickable(self, clickable: bool) -> None:
        """
        Set whether the icon responds to clicks.
        
        Args:
            clickable: True to enable click response
        """
        self._clickable = clickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable 
            else Qt.CursorShape.ArrowCursor
        )
    
    def isClickable(self) -> bool:
        """Check if icon is clickable."""
        return self._clickable
    
    def setHoverEffect(self, enabled: bool) -> None:
        """
        Enable or disable hover animation effect.
        
        Args:
            enabled: True to enable hover effect
        """
        self._hover_effect = enabled
    
    def hasHoverEffect(self) -> bool:
        """Check if hover effect is enabled."""
        return self._hover_effect
    
    def isLoaded(self) -> bool:
        """Check if icon is loaded."""
        return self._is_loaded
    
    def hasError(self) -> bool:
        """Check if icon loading failed."""
        return self._load_error
    
    def reload(self) -> None:
        """Force reload the icon."""
        self._is_loaded = False
        self._load_error = False
        self._load_icon()
    
    def clear(self) -> None:
        """Clear the icon."""
        self._source = None
        self._pixmap = None
        self._is_loaded = False
        self._load_error = False
        self.update()
    
    # ==================== Factory Methods ====================
    
    @classmethod
    def from_name(
        cls,
        name: str,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        Create IconWidget from icon name.
        
        Args:
            name: Icon name (without extension)
            size: Icon size
            color: Optional color
            parent: Parent widget
        
        Returns:
            IconWidget instance
        """
        return cls(IconSource.from_name(name), size, color, parent)
    
    @classmethod
    def from_svg(
        cls,
        svg_content: str,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        Create IconWidget from SVG content string.
        
        Args:
            svg_content: SVG content as string
            size: Icon size
            color: Optional color
            parent: Parent widget
        
        Returns:
            IconWidget instance
        """
        return cls(IconSource.from_svg(svg_content), size, color, parent)
    
    @classmethod
    def from_icon(
        cls,
        icon: QIcon,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        Create IconWidget from QIcon.
        
        Args:
            icon: QIcon instance
            size: Icon size
            parent: Parent widget
        
        Returns:
            IconWidget instance
        """
        return cls(IconSource.from_icon(icon), size, None, parent)
    
    @classmethod
    def from_pixmap(
        cls,
        pixmap: QPixmap,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        Create IconWidget from QPixmap.
        
        Args:
            pixmap: QPixmap instance
            parent: Parent widget
        
        Returns:
            IconWidget instance
        """
        size = pixmap.width()
        return cls(IconSource.from_pixmap(pixmap), size, None, parent)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        self._pixmap = None
        self._fallback_pixmap = None
