"""
Widget Painting Strategy Module

Provides pluggable painting strategies using the Strategy Pattern.
Decouples painting logic from widget implementation.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type, List
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget


class PaintContext:
    """
    Context object passed to painters containing all necessary information.

    This decouples painters from widget implementation details, allowing
    painters to work without knowing the widget's internal structure.
    """

    def __init__(
        self,
        widget: Optional[QWidget],
        painter: QPainter,
        rect: QRectF,
        theme: Optional['Theme'] = None,
        **kwargs
    ):
        self.widget = widget
        self.painter = painter
        self.rect = rect
        self.theme = theme
        self.state = kwargs.get('state', {})
        self.options = kwargs

    def get_color(self, key: str, default: QColor = None) -> QColor:
        """
        Convenience method to get color from theme.

        Args:
            key: Dot-separated theme key path
            default: Default color if not found

        Returns:
            QColor value
        """
        if default is None:
            default = QColor()

        if self.theme:
            return self.theme.get_color(key, default)
        return default

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Convenience method to get any value from theme or options.

        Checks options first, then falls back to theme.

        Args:
            key: Value key
            default: Default if not found

        Returns:
            Value or default
        """
        # Check options first (passed directly to paint())
        if key in self.options:
            return self.options[key]
        # Fall back to theme
        if self.theme:
            return self.theme.get_value(key, default)
        return default


class WidgetPainter(ABC):
    """
    Abstract base class for all painting strategies.

    Implements the Strategy Pattern for pluggable painting logic.
    Subclasses implement the paint() method to define custom rendering.

    Usage:
        painter = CircularProgressPainter(theme)
        context = PaintContext(widget, painter, rect, theme, value=75)
        painter.paint(context)
    """

    def __init__(self, theme: Optional['Theme'] = None):
        self._theme = theme

    @abstractmethod
    def paint(self, context: PaintContext) -> None:
        """
        Main painting method.

        Args:
            context: PaintContext containing widget, painter, rect, theme, etc.
        """
        pass

    def set_theme(self, theme: 'Theme') -> None:
        """
        Update theme used by this painter.

        Args:
            theme: New theme to use
        """
        self._theme = theme

    def theme(self) -> Optional['Theme']:
        """Get current theme."""
        return self._theme

    def prepare_painter(self, context: PaintContext) -> None:
        """
        Common painter setup (called before paint()).

        Subclasses can override but should call super().prepare_painter().
        """
        painter = context.painter
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    def cleanup_painter(self, context: PaintContext) -> None:
        """
        Common painter cleanup (called after paint()).

        Subclasses can override but should call super().cleanup_painter().
        """
        pass


class PainterFactory:
    """
    Factory for creating painter instances.

    Implements Factory Pattern with theme awareness.
    Allows runtime painter selection by name.
    """

    _painter_classes: Dict[str, Type[WidgetPainter]] = {}

    @classmethod
    def register(cls, name: str, painter_class: Type[WidgetPainter]) -> None:
        """
        Register a painter class.

        Args:
            name: Name to identify the painter
            painter_class: WidgetPainter subclass
        """
        if not issubclass(painter_class, WidgetPainter):
            raise TypeError(f"{painter_class} must be a subclass of WidgetPainter")
        cls._painter_classes[name] = painter_class

    @classmethod
    def create(
        cls,
        name: str,
        theme: Optional['Theme'] = None,
        **kwargs
    ) -> Optional[WidgetPainter]:
        """
        Create painter instance by name.

        Args:
            name: Registered painter name
            theme: Theme to pass to painter
            **kwargs: Additional arguments passed to painter constructor

        Returns:
            Painter instance or None if name not found
        """
        painter_class = cls._painter_classes.get(name)
        if painter_class:
            return painter_class(theme, **kwargs)
        return None

    @classmethod
    def list_available(cls) -> List[str]:
        """List all registered painter types."""
        return list(cls._painter_classes.keys())

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a painter from the registry."""
        cls._painter_classes.pop(name, None)
