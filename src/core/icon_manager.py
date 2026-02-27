"""
Icon Manager Module

Provides centralized icon management with:
- SVG icon loading and caching
- Theme-based icon colorization
- Default icons for common UI elements
- Vector icon support for all scales
"""

import logging
import os
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt6.QtWidgets import QWidget

# Initialize logger
logger = logging.getLogger(__name__)


class IconManager(QObject):
    """
    Centralized icon manager with caching and theme support.

    Provides a unified interface for loading and managing icons
    throughout the application. Supports SVG icons with loading
    and theme-based colorization.

    Features:
    - Icon caching for performance
    - SVG icon support with scaling
    - Theme-aware icon rendering
    - Default icons for common UI elements
    - Memory-safe with proper cleanup

    Attributes:
        _icon_cache: Cache for loaded icons
        _icon_dir: Directory containing icon resources

    Example:
        icon_mgr = IconManager.instance()
        icon = icon_mgr.get_icon('window_default')
        window.setWindowIcon(icon)
    """

    # Singleton instance
    _instance: Optional['IconManager'] = None

    # Signal emitted when icons change (e.g., theme change)
    iconsChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._icon_cache: Dict[str, QIcon] = {}

        # Get icon directory relative to this module
        module_dir = os.path.dirname(os.path.abspath(__file__))
        self._icon_dir = os.path.join(module_dir, '..', 'resources', 'icons')

        logger.debug(f"IconManager initialized with icon directory: {self._icon_dir}")

    @classmethod
    def instance(cls) -> 'IconManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_icon(self, icon_name: str, size: int = 24) -> QIcon:
        """
        Get icon by name with specified size.

        Loads and caches icons for performance. Supports SVG icons
        which scale properly at any size.

        Args:
            icon_name: Name of the icon (without extension)
            size: Desired icon size in pixels (default: 24)

        Returns:
            QIcon instance, or default icon if not found

        Example:
            icon = icon_mgr.get_icon('window_default', 24)
        """
        # Create cache key
        cache_key = f"{icon_name}_{size}"

        # Check cache
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Try to load SVG first
        svg_path = os.path.join(self._icon_dir, f"{icon_name}.svg")
        if os.path.exists(svg_path):
            icon = self._load_svg_icon(svg_path, size)
            self._icon_cache[cache_key] = icon
            logger.debug(f"Loaded SVG icon: {icon_name} at {size}px")
            return icon

        # Try PNG as fallback
        png_path = os.path.join(self._icon_dir, f"{icon_name}.png")
        if os.path.exists(png_path):
            icon = QIcon(png_path)
            self._icon_cache[cache_key] = icon
            logger.debug(f"Loaded PNG icon: {icon_name} at {size}px")
            return icon

        # Return default icon
        logger.warning(f"Icon not found: {icon_name}, using default")
        return self._get_default_icon(size)

    def _load_svg_icon(self, svg_path: str, size: int) -> QIcon:
        """
        Load SVG icon and render at specified size.

        Args:
            svg_path: Path to SVG file
            size: Desired icon size in pixels

        Returns:
            QIcon rendered at specified size
        """
        try:
            # Load SVG as QIcon (Qt6 supports SVG natively)
            icon = QIcon(svg_path)

            # Pre-render at specified size for better performance
            pixmap = icon.pixmap(size, size)
            if not pixmap.isNull():
                # Re-render with anti-aliasing for smooth edges
                smooth_pixmap = QPixmap(size, size)
                smooth_pixmap.fill(Qt.GlobalColor.transparent)

                painter = QPainter(smooth_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()

                return QIcon(smooth_pixmap)

            return icon
        except Exception as e:
            logger.error(f"Error loading SVG icon {svg_path}: {e}")
            return self._get_default_icon(size)

    def _get_default_icon(self, size: int = 24) -> QIcon:
        """
        Get a default/fallback icon.

        Creates a simple default icon programmatically.

        Args:
            size: Icon size in pixels

        Returns:
            Default QIcon
        """
        # Create a simple default icon
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(74, 144, 226))  # Default blue

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))

        # Draw a simple window icon
        margin = size // 8
        box_size = size - 2 * margin

        # Draw rounded rectangle
        painter.setBrush(QColor(52, 152, 219))
        from PyQt6.QtCore import QRectF
        painter.drawRoundedRect(
            QRectF(margin, margin, box_size, box_size * 0.6), 4.0, 4.0
        )

        # Draw inner content
        inner_size = box_size // 2
        inner_margin = (box_size - inner_size) // 2
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.drawRect(
            margin + inner_margin,
            margin + int(box_size * 0.3),
            inner_size,
            inner_size
        )

        painter.end()
        return QIcon(pixmap)

    def get_colored_icon(
        self,
        icon_name: str,
        color: QColor,
        size: int = 24
    ) -> QIcon:
        """
        Get icon with custom color overlay.

        Useful for creating theme-aware colored icons from monochrome
        or grayscale icons.

        Args:
            icon_name: Name of the icon
            color: Color to apply to the icon
            size: Desired icon size in pixels

        Returns:
            QIcon with color overlay applied

        Example:
            from PyQt6.QtGui import QColor
            red_icon = icon_mgr.get_colored_icon('close', QColor(231, 76, 60))
        """
        # Get base icon
        base_icon = self.get_icon(icon_name, size)

        # Create pixmap from base icon
        pixmap = base_icon.pixmap(size, size)
        if pixmap.isNull():
            return base_icon

        # Create colored version with anti-aliasing
        colored_pixmap = QPixmap(size, size)
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)

        # Enable anti-aliasing for smooth edges
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # First draw the original icon
        painter.drawPixmap(0, 0, pixmap)

        # Then apply color using SourceIn (keeps alpha, replaces color)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)

        painter.end()

        return QIcon(colored_pixmap)

    def clear_cache(self) -> None:
        """
        Clear icon cache.

        Forces reload of all icons on next access.
        Useful when resources change or memory needs to be freed.

        Example:
            icon_mgr.clear_cache()
        """
        self._icon_cache.clear()
        logger.debug("Icon cache cleared")
        self.iconsChanged.emit()

    def get_icon_path(self, icon_name: str, icon_type: str = 'svg') -> Optional[str]:
        """
        Get the file path for an icon.

        Args:
            icon_name: Name of the icon (without extension)
            icon_type: File extension (default: 'svg')

        Returns:
            Full path to icon file, or None if not found

        Example:
            path = icon_mgr.get.get_icon_path('window_default', 'svg')
        """
        icon_path = os.path.join(self._icon_dir, f"{icon_name}.{icon_type}")
        if os.path.exists(icon_path):
            return icon_path
        return None

    def has_icon(self, icon_name: str) -> bool:
        """
        Check if an icon exists.

        Args:
            icon_name: Name of the icon (without extension)

        Returns:
            True if icon exists, False otherwise

        Example:
            if icon_mgr.has_icon('window_default'):
                print("Icon is available")
        """
        return (
            os.path.exists(os.path.join(self._icon_dir, f"{icon_name}.svg")) or
            os.path.exists(os.path.join(self._icon_dir, f"{icon_name}.png"))
        )

    def cleanup(self) -> None:
        """
        Clean up resources and clear cache.

        Example:
            icon_mgr.cleanup()
        """
        self.clear_cache()
        logger.debug("IconManager cleaned up")

    @staticmethod
    def create_pixmap_from_svg(svg_content: str, size: int = 24) -> Optional[QPixmap]:
        """
        Create QPixmap from SVG content string.

        Useful for dynamically generating icons from SVG data.

        Args:
            svg_content: SVG content as string
            size: Desired size in pixels

        Returns:
            QPixmap rendered from SVG, or None if failed

        Example:
            svg = '<svg width="32" height="32">...</svg>'
            pixmap = IconManager.create_pixmap_from_svg(svg, 32)
        """
        try:
            # Create temporary SVG data
            from PyQt6.QtCore import QByteArray
            svg_bytes = QByteArray(svg_content.encode('utf-8'))
            pixmap = QPixmap()
            pixmap.loadFromData(svg_bytes)

            if pixmap.isNull():
                logger.warning("Failed to create pixmap from SVG content")
                return None

            # Scale to desired size
            if pixmap.width() != size or pixmap.height() != size:
                pixmap = pixmap.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            return pixmap
        except Exception as e:
            logger.error(f"Error creating pixmap from SVG: {e}")
            return None

    def get_icon_from_svg(self, svg_content: str, size: int = 24) -> QIcon:
        """
        Create QIcon from SVG content string.

        Args:
            svg_content: SVG content as string
            size: Desired size in pixels

        Returns:
            QIcon rendered from SVG

        Example:
            svg = '<svg width="32" height="32">...</svg>'
            icon = icon_mgr.get_icon_from_svg(svg, 32)
        """
        pixmap = self.create_pixmap_from_svg(svg_content, size)
        if pixmap:
            return QIcon(pixmap)
        return self._get_default_icon(size)
