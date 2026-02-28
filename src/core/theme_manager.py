"""
Theme Management Module

Provides global theme registry and dynamic theme switching for PyQt components.
"""
import weakref
from typing import Dict, Any, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget


class Theme:
    """
    Immutable theme data container.

    Stores style parameters (colors, fonts, borders, etc.) with support
    for nested key access (e.g., 'button.hover.background').
    """

    def __init__(self, name: str, style_data: Dict[str, Any]):
        super().__init__()
        self._name = name
        self._style_data = style_data.copy() if style_data else {}

    @property
    def name(self) -> str:
        """Theme name/identifier."""
        return self._name
    
    @property
    def is_dark(self) -> bool:
        """
        Check if this is a dark theme.
        
        First checks for explicit 'is_dark' key in theme data.
        If not found, determines based on background color luminance.
        
        Returns:
            True if dark theme, False otherwise
        """
        explicit = self._get_nested_value('is_dark')
        if explicit is not None:
            return bool(explicit)
        
        bg_color = self.get_color('window.background', QColor(255, 255, 255))
        luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255
        return luminance < 0.5

    def get_color(self, key: str, default: QColor = None) -> QColor:
        """
        Get color value by key path.

        Args:
            key: Dot-separated path (e.g., 'button.background.hover')
            default: Default color if key not found

        Returns:
            QColor value or default
        """
        if default is None:
            default = QColor()

        value = self._get_nested_value(key)
        if isinstance(value, QColor):
            return value

        # Convert to QColor from various formats
        return self._to_color(value, default)

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get any theme value by key path.

        Args:
            key: Dot-separated path
            default: Default value if key not found

        Returns:
            Theme value or default
        """
        value = self._get_nested_value(key)
        return value if value is not None else default

    def _get_nested_value(self, key: str) -> Any:
        """Get value using dot notation."""
        parts = key.split('.')
        value = self._style_data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None
        return value

    def _to_color(self, value: Any, default: QColor) -> QColor:
        """Convert various color formats to QColor."""
        if isinstance(value, QColor):
            return value
        elif isinstance(value, str):
            # Hex color or named color
            color = QColor(value)
            return color if color.isValid() else default
        elif isinstance(value, (tuple, list)) and len(value) >= 3:
            # RGB or RGBA tuple
            if len(value) == 3:
                return QColor(int(value[0]), int(value[1]), int(value[2]))
            elif len(value) == 4:
                return QColor(int(value[0]), int(value[1]), int(value[2]), int(value[3]))
        return default

    def to_dict(self) -> Dict[str, Any]:
        """Return complete theme data."""
        return self._style_data.copy()

    def with_override(self, key: str, value: Any) -> 'Theme':
        """
        Create a new Theme with a single value override.
        
        This method returns a new Theme instance with the specified override,
        preserving the immutability of the original theme.
        
        Args:
            key: Dot-separated path (e.g., 'button.border_radius')
            value: Value to set
            
        Returns:
            New Theme instance with the override applied
        """
        new_data = self._copy_with_override(self._style_data, key.split('.'), value)
        return Theme(f"{self._name}_override", new_data)
    
    def _copy_with_override(self, data: Dict, keys: list, value: Any) -> Dict:
        """Recursively copy data structure with override applied."""
        result = data.copy()
        if len(keys) == 1:
            result[keys[0]] = value
        else:
            if keys[0] in result and isinstance(result[keys[0]], dict):
                result[keys[0]] = self._copy_with_override(result[keys[0]], keys[1:], value)
            else:
                result[keys[0]] = {}
                self._set_nested(result[keys[0]], keys[1:], value)
        return result
    
    def _set_nested(self, data: Dict, keys: list, value: Any) -> None:
        """Set nested value in dictionary."""
        if len(keys) == 1:
            data[keys[0]] = value
        else:
            if keys[0] not in data:
                data[keys[0]] = {}
            self._set_nested(data[keys[0]], keys[1:], value)

    def __repr__(self) -> str:
        return f"Theme(name='{self._name}')"


class ThemeManager(QObject):
    """
    Global theme registry and manager (Singleton).

    Responsibilities:
    - Register and retrieve themes by name
    - Apply theme to widgets
    - Notify theme changes to all subscribers
    - Provide QSS expansion support
    """

    # Singleton instance
    _instance: Optional['ThemeManager'] = None

    # Signal emitted when theme changes
    themeChanged = pyqtSignal(str)  # New theme name

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._subscribers: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    @classmethod
    def instance(cls) -> 'ThemeManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_theme(self, theme: Theme) -> None:
        """
        Register a theme object.

        Args:
            theme: Theme instance to register
        """
        self._themes[theme.name] = theme

    def register_theme_dict(self, name: str, style_data: Dict[str, Any]) -> Theme:
        """
        Create and register theme from dictionary.

        Args:
            name: Theme name
            style_data: Dictionary of style values

        Returns:
            Created Theme instance
        """
        theme = Theme(name, style_data)
        self.register_theme(theme)
        return theme

    def register_theme_file(self, name: str, file_path: str) -> Theme:
        """
        Load and register theme from Python file.

        The file should contain a THEME_DATA dictionary.

        Args:
            name: Theme name
            file_path: Path to theme file

        Returns:
            Created Theme instance
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(f"theme_{name}", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"theme_{name}"] = module
        spec.loader.exec_module(module)

        if hasattr(module, 'THEME_DATA'):
            return self.register_theme_dict(name, module.THEME_DATA)
        else:
            raise ValueError(f"Theme file '{file_path}' must contain THEME_DATA dictionary")

    def get_theme(self, name: str) -> Optional[Theme]:
        """Retrieve theme by name."""
        return self._themes.get(name)

    def set_theme(self, theme_name: str) -> None:
        """
        Set active theme and notify all subscribers.

        Args:
            theme_name: Name of theme to activate

        Raises:
            ValueError: If theme not registered

        Example:
            ThemeManager.instance().set_theme('dark')
        """
        print(f"[ThemeManager] set_theme called with: {theme_name}")
        theme = self._themes.get(theme_name)
        if not theme:
            raise ValueError(f"Theme '{theme_name}' not registered")

        print(f"[ThemeManager] Theme found: {theme.name if hasattr(theme, 'name') else 'Unknown'}")
        self._current_theme = theme
        self.themeChanged.emit(theme_name)

        print(f"[ThemeManager] Notifying {len(self._subscribers)} subscribers")
        # Notify all subscribed widgets
        self._notify_subscribers()

    def set_current_theme(self, theme_name: str) -> None:
        """
        Set active theme (convenience method).

        This is a convenience alias for set_theme().
        Use this method for backward compatibility.

        Args:
            theme_name: Name of theme to activate

        Raises:
            ValueError: If theme not registered
        """
        self.set_theme(theme_name)

    def _notify_subscribers(self) -> None:
        """
        Notify all subscribed widgets of theme change.
        
        Note: WeakKeyDictionary automatically removes deleted widgets,
        so we don't need manual cleanup for garbage-collected widgets.
        """
        if not self._current_theme:
            return

        for widget, callback in list(self._subscribers.items()):
            try:
                callback(self._current_theme)
            except RuntimeError:
                pass
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f"Theme callback error in {widget.__class__.__name__}: {e}"
                )

    def current_theme(self) -> Optional[Theme]:
        """Get currently active theme."""
        return self._current_theme

    def subscribe(self, widget: QWidget, callback: Callable[[Theme], None]) -> None:
        """
        Subscribe widget to theme changes.

        Args:
            widget: Widget to subscribe
            callback: Function called when theme changes
        """
        self._subscribers[widget] = callback
        # Immediately apply current theme
        if self._current_theme:
            callback(self._current_theme)

    def unsubscribe(self, widget: QWidget) -> None:
        """Unsubscribe widget from theme changes."""
        self._subscribers.pop(widget, None)

    def apply_to_widget(self, widget: QWidget, theme_name: Optional[str] = None) -> None:
        """
        Apply theme to widget.

        This is a base implementation. Subclasses should override
        _generate_qss to provide theme-specific QSS generation.

        Args:
            widget: Widget to apply theme to
            theme_name: Theme name (uses current if None)
        """
        theme = self._themes.get(theme_name) if theme_name else self._current_theme
        if not theme:
            return

        # Generate QSS from theme (override in subclass for custom behavior)
        qss = self._generate_qss(theme, widget)

        # Store theme name in widget property
        widget.setProperty("_theme", theme.name)

        # Apply stylesheet
        widget.setStyleSheet(qss)

        # Force style refresh (CRITICAL for dynamic styling)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _generate_qss(self, theme: Theme, widget: QWidget) -> str:
        """
        Generate QSS string from theme data.

        This is a template method that can be overridden for custom QSS generation.
        Base implementation returns empty string.

        Args:
            theme: Theme to generate QSS from
            widget: Target widget

        Returns:
            QSS string
        """
        return ""
