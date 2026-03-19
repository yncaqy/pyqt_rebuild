"""
Modern Line Edit Component - WinUI 3 Style

Provides a modern, themed line edit with WinUI 3 Fluent Design:
- Subtle border with low contrast for clear identification
- Light shadow effect for depth
- Theme integration with automatic updates
- Support for normal, focus, disabled, error states
- Placeholder text color customization
- Optimized style caching for performance
- Memory-safe with proper cleanup
- Local style overrides without modifying shared theme
- Automatic resource cleanup
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy, QGraphicsDropShadowEffect
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class LineEditConfig:
    """Configuration constants for line edit behavior and styling."""

    DEFAULT_MIN_WIDTH = 200
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['input']['min_height']
    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['input']['border_radius']
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['input']['padding_v']}px {WINUI3_CONTROL_SIZING['input']['padding_h']}px"
    DEFAULT_PLACEHOLDER_COLOR = QColor(170, 170, 170)


class ModernLineEdit(QLineEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed line edit with WinUI 3 Fluent Design styling.

    Features:
    - Subtle border with low contrast for clear identification
    - Light shadow effect for depth
    - Theme integration with automatic updates
    - Support for normal, focus, disabled, error states
    - Placeholder text color customization
    - Optimized style caching for performance
    - Memory-safe with proper cleanup
    - Local style overrides without modifying shared theme
    - Automatic resource cleanup

    Example:
        lineedit = ModernLineEdit("Enter text here")
        lineedit.setPlaceholderText("Username")
        lineedit.setError(True)  # Show error state
        lineedit.textChanged.connect(lambda text: print(f"Text: {text}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setMinimumSize(
            LineEditConfig.DEFAULT_MIN_WIDTH,
            LineEditConfig.DEFAULT_MIN_HEIGHT
        )

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._border_color: QColor = QColor(200, 200, 200, 40)
        self._border_color_focused: QColor = QColor(0, 120, 212)
        self._border_color_error: QColor = QColor(196, 43, 28)
        self._is_focused: bool = False
        self._has_error: bool = False
        
        self._shadow_effect: Optional[QGraphicsDropShadowEffect] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"ModernLineEdit initialized with text: '{text}'")

    def focusInEvent(self, event):
        self._is_focused = True
        self._update_shadow()
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._is_focused = False
        self._update_shadow()
        self.update()
        super().focusOutEvent(event)

    def _update_shadow(self):
        if self._shadow_effect:
            if self._is_focused or self._has_error:
                self._shadow_effect.setOffset(0, 1)
                self._shadow_effect.setBlurRadius(8)
                if self._has_error:
                    self._shadow_effect.setColor(QColor(196, 43, 28, 40))
                else:
                    self._shadow_effect.setColor(QColor(0, 120, 212, 30))
            else:
                self._shadow_effect.setOffset(0, 1)
                self._shadow_effect.setBlurRadius(4)
                self._shadow_effect.setColor(QColor(0, 0, 0, 15))

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ModernLineEdit: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        bg_normal = self.get_style_color(theme, 'input.background.normal', QColor(255, 255, 255))
        bg_disabled = self.get_style_color(theme, 'input.background.disabled', QColor(245, 245, 245))

        text_color = self.get_style_color(theme, 'input.text.normal', QColor(51, 51, 51))
        text_disabled = self.get_style_color(theme, 'input.text.disabled', QColor(170, 170, 170))
        placeholder_color = self.get_style_color(theme, 'input.text.placeholder', QColor(170, 170, 170))

        self._border_color = self.get_style_color(theme, 'input.border.normal', QColor(200, 200, 200, 40))
        self._border_color_focused = self.get_style_color(theme, 'input.border.focus', QColor(0, 120, 212))
        self._border_color_error = self.get_style_color(theme, 'input.border.error', QColor(196, 43, 28))

        border_radius = self.get_style_value(theme, 'input.border_radius', LineEditConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'input.padding', LineEditConfig.DEFAULT_PADDING)

        is_dark = getattr(theme, 'is_dark', False)
        
        if not self._shadow_effect:
            self._shadow_effect = QGraphicsDropShadowEffect(self)
            self.setGraphicsEffect(self._shadow_effect)
        
        self._update_shadow()

        cache_key = (
            bg_normal.name(),
            bg_disabled.name(),
            text_color.name(),
            text_disabled.name(),
            placeholder_color.name(),
            border_radius,
            padding,
            is_dark,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(bg_normal, bg_disabled, text_color,
                                          text_disabled, placeholder_color,
                                          border_radius, padding, is_dark)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.update()

    def _build_stylesheet(self, bg_normal: QColor, bg_disabled: QColor,
                         text_color: QColor, text_disabled: QColor,
                         placeholder_color: QColor, border_radius: int,
                         padding: str, is_dark: bool) -> str:
        if is_dark:
            border_normal = "rgba(255, 255, 255, 25)"
        else:
            border_normal = "rgba(0, 0, 0, 15)"
        
        qss = f"""
        ModernLineEdit {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 1px solid {border_normal};
            border-radius: {border_radius}px;
            padding: {padding};
        }}
        ModernLineEdit:focus {{
            border: 1px solid {self._border_color_focused.name()};
        }}
        ModernLineEdit:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid rgba(128, 128, 128, 20);
        }}
        ModernLineEdit[error="true"] {{
            border: 1px solid {self._border_color_error.name()};
        }}
        """
        return qss

    def set_theme(self, name: str) -> None:
        logger.info(f"Setting theme to: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        if self._current_theme and hasattr(self._current_theme, 'name'):
            return self._current_theme.name
        return None

    def set_error(self, error: bool) -> None:
        self._has_error = error
        self.setProperty("error", "true" if error else "false")
        self._update_shadow()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        logger.debug(f"Error state set to: {error}")

    def has_error(self) -> bool:
        return self._has_error

    def set_placeholder_text(self, text: str) -> None:
        self.setPlaceholderText(text)

    def set_echo_mode(self, mode) -> None:
        self.setEchoMode(mode)

    def set_border_radius(self, radius: int) -> None:
        logger.debug(f"Setting border radius: {radius}px")
        self.override_style('input.border_radius', radius)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_padding(self, padding: str) -> None:
        logger.debug(f"Setting padding: {padding}")
        self.override_style('input.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_widget_destroyed(self) -> None:
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ModernLineEdit unsubscribed from theme manager")

        self._clear_stylesheet_cache()
        self.clear_overrides()

    def __del__(self):
        try:
            if not self._cleanup_done:
                self.cleanup()
        except Exception as e:
            logger.debug(f"Error in ModernLineEdit.__del__: {e}")
