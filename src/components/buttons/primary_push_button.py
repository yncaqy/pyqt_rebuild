"""
Primary Push Button Component

Provides a prominent push button for highlighting important actions.

Features:
- Prominent styling with accent color background
- Theme integration with automatic updates
- Support for normal, hover, pressed, disabled states
- Support for text and icon display
- Customizable border radius and padding
- Support for icon name loading via IconManager
- Local style overrides without modifying shared theme
- Automatic resource cleanup
"""

import logging
import time
from typing import Optional, Union
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class PrimaryButtonConfig:
    """Configuration constants for primary button behavior and styling."""

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_BORDER_RADIUS = 6
    DEFAULT_PADDING = '8px 16px'
    DEFAULT_ICON_SIZE = 16


class PrimaryPushButton(QPushButton, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Prominent push button for highlighting important actions.

    Features:
    - Prominent styling with accent color background
    - Theme integration with automatic updates
    - Support for normal, hover, pressed, disabled states
    - Support for text and icon display
    - Customizable border radius and padding
    - Support for icon name, SVG string, or QIcon
    - Local style overrides without modifying shared theme
    - Automatic resource cleanup

    Example:
        button = PrimaryPushButton("Submit", icon_name="Check_white")
        button.clicked.connect(lambda: print("Submitted!"))
    """

    def __init__(
        self, 
        text: str = "", 
        parent: Optional[QWidget] = None, 
        icon_name: str = "",
        icon: str = ""
    ):
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(
            PrimaryButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            PrimaryButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._icon_name: str = ""
        self._icon_content: Optional[str] = None
        self._icon_size = QSize(PrimaryButtonConfig.DEFAULT_ICON_SIZE, PrimaryButtonConfig.DEFAULT_ICON_SIZE)
        self._colored_pixmap: Optional[QPixmap] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        if icon_name:
            self.setIconName(icon_name)
        elif icon:
            self._icon_content = icon
            self._update_icon()
        
        if self._icon_name or self._icon_content:
            if self.text():
                original_text = self.text().lstrip()
                super().setText(f" {original_text}")

        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"PrimaryPushButton initialized with text: '{text}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
            self._update_icon()
        except Exception as e:
            logger.error(f"Error applying theme to PrimaryPushButton: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        start_time = time.time()
        
        if not theme:
            return

        self._current_theme = theme

        theme_name = getattr(theme, 'name', 'unnamed')
        cache_key = (
            theme_name,
            theme.get_color('primary.background.normal', QColor(0, 120, 212)).name(),
            theme.get_color('primary.background.hover', QColor(0, 100, 192)).name(),
            theme.get_color('primary.background.pressed', QColor(0, 80, 172)).name(),
            theme.get_color('primary.background.disabled', QColor(100, 100, 100)).name(),
            theme.get_color('primary.text.normal', QColor(255, 255, 255)).name(),
            theme.get_color('primary.text.disabled', QColor(180, 180, 180)).name(),
            theme.get_value('primary.border_radius', PrimaryButtonConfig.DEFAULT_BORDER_RADIUS),
            theme.get_value('primary.padding', PrimaryButtonConfig.DEFAULT_PADDING),
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme),
            theme_name
        )

        current_stylesheet = self.styleSheet()
        if current_stylesheet != qss:
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)

        elapsed_time = time.time() - start_time
        logger.debug(f"PrimaryPushButton theme applied in {elapsed_time:.3f}s")

    def _build_stylesheet(self, theme: Theme) -> str:
        bg_normal = self.get_style_color(theme, 'primary.background.normal', QColor(0, 120, 212))
        bg_hover = self.get_style_color(theme, 'primary.background.hover', QColor(0, 100, 192))
        bg_pressed = self.get_style_color(theme, 'primary.background.pressed', QColor(0, 80, 172))
        bg_disabled = self.get_style_color(theme, 'primary.background.disabled', QColor(100, 100, 100))

        text_color = self.get_style_color(theme, 'primary.text.normal', QColor(255, 255, 255))
        text_disabled = self.get_style_color(theme, 'primary.text.disabled', QColor(180, 180, 180))

        border_radius = self.get_style_value(theme, 'primary.border_radius', PrimaryButtonConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'primary.padding', PrimaryButtonConfig.DEFAULT_PADDING)

        qss = f"""
        PrimaryPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: none;
            border-radius: {border_radius}px;
            padding: {padding};
            font-weight: bold;
        }}
        PrimaryPushButton:hover {{
            background-color: {bg_hover.name()};
        }}
        PrimaryPushButton:pressed {{
            background-color: {bg_pressed.name()};
        }}
        PrimaryPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
        }}
        """

        return qss

    def _get_icon_color(self) -> QColor:
        """Get the icon color based on current theme."""
        if self._current_theme:
            return self._current_theme.get_color('primary.text.normal', QColor(255, 255, 255))
        return QColor(255, 255, 255)

    def _update_icon(self) -> None:
        """Update the icon with current theme color."""
        if self._icon_name:
            icon = self._icon_mgr.get_icon(self._icon_name, self._icon_size.width())
            super().setIcon(icon)
            super().setIconSize(self._icon_size)
        elif self._icon_content:
            color = self._get_icon_color()
            self._colored_pixmap = self._create_colored_pixmap(self._icon_content, color)
            
            if self._colored_pixmap:
                icon = QIcon(self._colored_pixmap)
                super().setIcon(icon)
                super().setIconSize(self._icon_size)
        else:
            super().setIcon(QIcon())

    def _create_colored_pixmap(self, svg_content: str, color: QColor) -> Optional[QPixmap]:
        """Create a colored pixmap from SVG content."""
        try:
            color_hex = color.name(QColor.NameFormat.HexRgb)
            svg_colored = svg_content.replace('currentColor', color_hex)
            
            if 'stroke="currentColor"' in svg_colored:
                svg_colored = svg_colored.replace('stroke="currentColor"', f'stroke="{color_hex}"')
            if 'fill="currentColor"' in svg_colored:
                svg_colored = svg_colored.replace('fill="currentColor"', f'fill="{color_hex}"')
            
            svg_bytes = QByteArray(svg_colored.encode('utf-8'))
            pixmap = QPixmap()
            pixmap.loadFromData(svg_bytes)
            
            if pixmap.isNull():
                logger.warning(f"Failed to load SVG pixmap")
                return None
            
            icon_size = self._icon_size.width()
            if pixmap.width() != icon_size or pixmap.height() != icon_size:
                pixmap = pixmap.scaled(
                    icon_size, icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            return pixmap
        except Exception as e:
            logger.error(f"Error creating colored pixmap: {e}")
            return None

    def setIconName(self, name: str) -> None:
        """
        Set icon by name.
        
        Args:
            name: Icon name (without extension, e.g., 'Play_white')
        """
        self._icon_name = name
        self._icon_content = None
        self._colored_pixmap = None
        self._update_icon()
        
        if self.text():
            original_text = self.text().lstrip()
            super().setText(f" {original_text}")
    
    def iconName(self) -> str:
        """Get current icon name."""
        return self._icon_name
    
    def setIcon(self, icon: Union[QIcon, str]) -> None:
        """
        Set the button icon.

        Args:
            icon: QIcon, icon name, or SVG string
        """
        logger.debug(f"setIcon called with type: {type(icon)}")
        if isinstance(icon, str):
            if icon.endswith('.svg') or icon.startswith('<svg'):
                self._icon_content = icon
                self._icon_name = ""
            else:
                self._icon_name = icon
                self._icon_content = None
            
            if not self._current_theme:
                initial_theme = self._theme_mgr.current_theme()
                if initial_theme:
                    self._current_theme = initial_theme
            self._update_icon()
            
            if self.text():
                original_text = self.text().lstrip()
                super().setText(f" {original_text}")
        else:
            self._icon_name = ""
            self._icon_content = None
            self._colored_pixmap = None
            super().setIcon(icon)

    def setIconSize(self, size: QSize) -> None:
        """Set the icon size."""
        self._icon_size = size
        self._update_icon()

    def set_border_radius(self, radius: int) -> None:
        if not isinstance(radius, int) or radius < 0:
            return
        self.override_style('primary.border_radius', radius)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_padding(self, padding: str) -> None:
        if not isinstance(padding, str) or not padding.strip():
            return
        self.override_style('primary.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        
        self._clear_stylesheet_cache()
        self.clear_overrides()

    def deleteLater(self) -> None:
        """Schedule the widget for deletion with automatic cleanup."""
        self.cleanup()
        super().deleteLater()
