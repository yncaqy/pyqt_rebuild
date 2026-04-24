"""
Modern Line Edit Component - WinUI 3 Style

Provides a modern, themed line edit with WinUI 3 Fluent Design:
- Transparent/subtle background with low contrast border
- Theme integration with automatic updates
- Support for normal, focus, disabled, error states
- Placeholder text color customization
- Optimized style caching for performance
- Memory-safe with proper cleanup
- Local style overrides without modifying shared theme
- Automatic resource cleanup

WinUI 3 Design Guidelines:
- Background: Very subtle (9% white on dark, 6% black on light)
- Border: Low contrast (24% opacity)
- Focus: Accent color border
- Height: 28px compact
- No shadow effects
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy
from src.core.theme_manager import ThemeManager, Theme
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.core.font_manager import FontManager
from src.themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class LineEditConfig:
    """Configuration constants for line edit behavior and styling, following WinUI 3 design."""

    DEFAULT_MIN_WIDTH = 200
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['input']['min_height']
    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['input']['border_radius']
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['input']['padding_v']}px {WINUI3_CONTROL_SIZING['input']['padding_h']}px"
    DEFAULT_PLACEHOLDER_COLOR = QColor(170, 170, 170)


class ModernLineEdit(QLineEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Themed line edit with WinUI 3 Fluent Design styling.

    Features:
    - Transparent/subtle background with low contrast border
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

        self._border_color_focused: QColor = QColor(0, 120, 212)
        self._border_color_error: QColor = QColor(196, 43, 28)
        self._is_focused: bool = False
        self._has_error: bool = False

        self._setup_font()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"ModernLineEdit initialized with text: '{text}'")

    def _setup_font(self) -> None:
        """设置字体，遵循 WinUI 3 设计规范。"""
        font = FontManager.get_body_font()
        self.setFont(font)

    def focusInEvent(self, event):
        self._is_focused = True
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._is_focused = False
        self.update()
        super().focusOutEvent(event)

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to ModernLineEdit: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        is_dark = getattr(theme, 'is_dark', True)

        bg_normal = self.get_style_color(theme, 'input.background.normal', QColor(255, 255, 255, 9) if is_dark else QColor(0, 0, 0, 6))
        bg_disabled = self.get_style_color(theme, 'input.background.disabled', QColor(255, 255, 255, 4) if is_dark else QColor(0, 0, 0, 3))

        text_color = self.get_style_color(theme, 'input.text.normal', QColor(255, 255, 255) if is_dark else QColor(0, 0, 0, 228))
        text_disabled = self.get_style_color(theme, 'input.text.disabled', QColor(255, 255, 255, 92) if is_dark else QColor(0, 0, 0, 92))
        placeholder_color = self.get_style_color(theme, 'input.text.placeholder', QColor(255, 255, 255, 135) if is_dark else QColor(0, 0, 0, 114))

        border_normal = self.get_style_color(theme, 'input.border.normal', QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24))
        self._border_color_focused = self.get_style_color(theme, 'input.border.focus', QColor('#60CDFF') if is_dark else QColor('#595959'))
        self._border_color_error = self.get_style_color(theme, 'input.border.error', QColor(196, 43, 28))

        border_radius = self.get_style_value(theme, 'input.border_radius', LineEditConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'input.padding', LineEditConfig.DEFAULT_PADDING)

        cache_key = (
            bg_normal.name(QColor.NameFormat.HexArgb),
            bg_disabled.name(QColor.NameFormat.HexArgb),
            text_color.name(QColor.NameFormat.HexArgb),
            text_disabled.name(QColor.NameFormat.HexArgb),
            placeholder_color.name(QColor.NameFormat.HexArgb),
            border_normal.name(QColor.NameFormat.HexArgb),
            self._border_color_focused.name(QColor.NameFormat.HexArgb),
            self._border_color_error.name(QColor.NameFormat.HexArgb),
            border_radius,
            padding,
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(bg_normal, bg_disabled, text_color,
                                          text_disabled, placeholder_color,
                                          border_normal, border_radius, padding)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        self.update()

    def _build_stylesheet(self, bg_normal: QColor, bg_disabled: QColor,
                         text_color: QColor, text_disabled: QColor,
                         placeholder_color: QColor, border_normal: QColor,
                         border_radius: int, padding: str) -> str:
        qss = f"""
        ModernLineEdit {{
            background-color: {bg_normal.name(QColor.NameFormat.HexArgb)};
            color: {text_color.name(QColor.NameFormat.HexArgb)};
            border: 1px solid {border_normal.name(QColor.NameFormat.HexArgb)};
            border-radius: {border_radius}px;
            padding: {padding};
        }}
        ModernLineEdit:focus {{
            border: 1px solid {self._border_color_focused.name(QColor.NameFormat.HexArgb)};
        }}
        ModernLineEdit:disabled {{
            background-color: {bg_disabled.name(QColor.NameFormat.HexArgb)};
            color: {text_disabled.name(QColor.NameFormat.HexArgb)};
            border: 1px solid rgba(128, 128, 128, 20);
        }}
        ModernLineEdit[error="true"] {{
            border: 1px solid {self._border_color_error.name(QColor.NameFormat.HexArgb)};
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
