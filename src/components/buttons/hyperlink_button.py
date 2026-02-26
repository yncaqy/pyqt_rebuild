"""
HyperlinkButton Component

Provides a button that acts like a hyperlink for URL navigation.

Features:
- Link styling with underline
- Opens URL in default browser when clicked
- Theme integration with automatic updates
- Hover and visited states
- Support for text and icon display
"""

import logging
import webbrowser
from typing import Optional
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QColor, QIcon, QPixmap, QEnterEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class HyperlinkButtonConfig:
    """Configuration constants for hyperlink button."""

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_ICON_SIZE = 16


class HyperlinkButton(QPushButton):
    """
    Button that acts like a hyperlink for URL navigation.

    Features:
    - Link styling with underline
    - Opens URL in default browser when clicked
    - Theme integration with automatic updates
    - Hover and visited states
    - Support for text and icon display

    Example:
        button = HyperlinkButton("Click here", "https://example.com")
        button.clicked.connect(button.open_url)
    """

    def __init__(
        self,
        text: str = "",
        url: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(text, parent)

        self.setSizePolicy(
            HyperlinkButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            HyperlinkButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._url = url
        self._visited = False
        self._icon_size = HyperlinkButtonConfig.DEFAULT_ICON_SIZE
        self._icon_content: Optional[str] = None
        self._colored_pixmap: Optional[QPixmap] = None

        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug(f"HyperlinkButton initialized with text: '{text}', url: '{url}'")

    def _setup_ui(self) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._current_theme = theme
        self._apply_theme(theme)
        self._update_icon()

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        link_color = theme.get_color('link.normal', QColor(0, 120, 212))
        link_hover = theme.get_color('link.hover', QColor(0, 100, 192))

        qss = f"""
        HyperlinkButton {{
            background-color: transparent;
            color: {link_color.name()};
            border: none;
            padding: 0px;
        }}
        HyperlinkButton:hover {{
            color: {link_hover.name()};
        }}
        """

        self.setStyleSheet(qss)

    def _get_icon_color(self) -> QColor:
        """Get the icon color based on current theme."""
        if self._current_theme:
            return self._current_theme.get_color('link.normal', QColor(0, 120, 212))
        return QColor(0, 120, 212)

    def _update_icon(self) -> None:
        """Update the icon with current theme color."""
        if not self._icon_content:
            super().setIcon(QIcon())
            return

        color = self._get_icon_color()
        self._colored_pixmap = self._create_colored_pixmap(self._icon_content, color)

        if self._colored_pixmap:
            icon = QIcon(self._colored_pixmap)
            super().setIcon(icon)
            super().setIconSize(QSize(self._icon_size, self._icon_size))

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
                return None

            if pixmap.width() != self._icon_size or pixmap.height() != self._icon_size:
                pixmap = pixmap.scaled(
                    self._icon_size, self._icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            return pixmap
        except Exception as e:
            logger.error(f"Error creating colored pixmap: {e}")
            return None

    def _on_clicked(self) -> None:
        """Handle button click to open URL."""
        if self._url:
            self.open_url()

    def open_url(self) -> bool:
        """
        Open the URL in the default browser.

        Returns:
            True if URL was opened successfully, False otherwise
        """
        if not self._url:
            logger.warning("No URL set for HyperlinkButton")
            return False

        try:
            result = webbrowser.open(self._url)
            if result:
                logger.debug(f"Opened URL: {self._url}")
            return result
        except Exception as e:
            logger.error(f"Failed to open URL {self._url}: {e}")
            return False

    def setUrl(self, url: str) -> None:
        """
        Set the URL to open when clicked.

        Args:
            url: URL string to open
        """
        self._url = url
        logger.debug(f"URL set to: {url}")

    def url(self) -> str:
        """
        Get the current URL.

        Returns:
            Current URL string
        """
        return self._url

    def setVisited(self, visited: bool) -> None:
        """
        Set the visited state.

        Args:
            visited: Whether the link has been visited
        """
        if self._visited != visited:
            self._visited = visited
            self._apply_theme(self._current_theme)
            self._update_icon()

    def isVisited(self) -> bool:
        """
        Check if the link has been visited.

        Returns:
            True if visited, False otherwise
        """
        return self._visited

    def setIcon(self, icon: QIcon | str) -> None:
        """
        Set the button icon.

        Args:
            icon: QIcon or SVG string
        """
        if isinstance(icon, str):
            self._icon_content = icon
            self._update_icon()

            if self.text():
                original_text = self.text().lstrip()
                super().setText(f" {original_text}")
        else:
            self._icon_content = None
            self._colored_pixmap = None
            super().setIcon(icon)

    def setIconSize(self, size: QSize) -> None:
        """Set the icon size."""
        self._icon_size = size.width()
        self._update_icon()

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
