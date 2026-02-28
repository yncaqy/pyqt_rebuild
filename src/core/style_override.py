"""
Style Override Mixin

Provides a mechanism for components to override theme values locally
without modifying the shared Theme object.

This ensures theme immutability while allowing per-component customization.
"""

from typing import Dict, Any, Optional, Callable
from PyQt6.QtGui import QColor

from core.theme_manager import Theme


class StyleOverrideMixin:
    """
    Mixin that provides local style override capability for themed components.
    
    This mixin allows components to customize their appearance without
    modifying the shared Theme object, preserving theme immutability.
    
    Usage:
        class MyButton(QPushButton, StyleOverrideMixin):
            def __init__(self):
                super().__init__()
                self._init_style_override()
            
            def set_custom_radius(self, radius: int):
                self.override_style('button.border_radius', radius)
            
            def _build_stylesheet(self, theme: Theme) -> str:
                # Use get_style_value to get merged value
                bg = self.get_style_value(theme, 'button.background.normal', QColor(60, 60, 60))
                radius = self.get_style_value(theme, 'button.border_radius', 6)
                # ...
    
    Attributes:
        _style_overrides: Dictionary of local style overrides
    """
    
    def _init_style_override(self) -> None:
        """Initialize style override system. Must be called in __init__."""
        self._style_overrides: Dict[str, Any] = {}
    
    def override_style(self, key: str, value: Any) -> None:
        """
        Set a local style override.
        
        This override takes precedence over theme values but does not
        modify the theme itself.
        
        Args:
            key: Style key (e.g., 'button.border_radius')
            value: Override value
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        self._style_overrides[key] = value
    
    def remove_override(self, key: str) -> None:
        """
        Remove a local style override.
        
        Args:
            key: Style key to remove
        """
        if hasattr(self, '_style_overrides') and key in self._style_overrides:
            del self._style_overrides[key]
    
    def clear_overrides(self) -> None:
        """Clear all local style overrides."""
        if hasattr(self, '_style_overrides'):
            self._style_overrides.clear()
    
    def get_style_value(self, theme: Optional[Theme], key: str, default: Any = None) -> Any:
        """
        Get style value with override precedence.
        
        Returns the override value if set, otherwise returns the theme value.
        
        Args:
            theme: Theme to get value from
            key: Style key
            default: Default value if not found
            
        Returns:
            Style value (override > theme > default)
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        
        if key in self._style_overrides:
            return self._style_overrides[key]
        
        if theme:
            return theme.get_value(key, default)
        
        return default
    
    def get_style_color(self, theme: Optional[Theme], key: str, default: QColor = None) -> QColor:
        """
        Get color value with override precedence.
        
        Args:
            theme: Theme to get color from
            key: Style key
            default: Default color if not found
            
        Returns:
            QColor value (override > theme > default)
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        
        if key in self._style_overrides:
            value = self._style_overrides[key]
            if isinstance(value, QColor):
                return value
            elif isinstance(value, str):
                return QColor(value)
            return default if default else QColor()
        
        if theme:
            return theme.get_color(key, default)
        
        return default if default else QColor()
    
    def has_override(self, key: str) -> bool:
        """
        Check if a style override exists.
        
        Args:
            key: Style key to check
            
        Returns:
            True if override exists
        """
        return hasattr(self, '_style_overrides') and key in self._style_overrides
    
    def get_all_overrides(self) -> Dict[str, Any]:
        """
        Get all local style overrides.
        
        Returns:
            Copy of overrides dictionary
        """
        if hasattr(self, '_style_overrides'):
            return self._style_overrides.copy()
        return {}
    
    def apply_overrides_to_theme(self, theme: Theme) -> Theme:
        """
        Create a new theme with all overrides applied.
        
        This is useful when you need a complete Theme object with overrides.
        
        Args:
            theme: Base theme to apply overrides to
            
        Returns:
            New Theme instance with overrides applied
        """
        result_theme = theme
        for key, value in self._style_overrides.items():
            result_theme = result_theme.with_override(key, value)
        return result_theme
