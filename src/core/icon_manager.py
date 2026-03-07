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

    def resolve_icon_name(self, icon_name: str, theme_type: str = "dark") -> str:
        """
        Resolve icon name based on theme type.
        
        For icons with _black/_white suffixes, returns the appropriate variant
        based on the theme type. Icons without suffixes are returned unchanged.
        
        Args:
            icon_name: Base icon name (without extension)
            theme_type: Theme type - "dark" or "light"
        
        Returns:
            Resolved icon name with appropriate suffix
        
        Example:
            resolve_icon_name("Play", "dark") -> "Play_white"
            resolve_icon_name("Play", "light") -> "Play_black"
            resolve_icon_name("error", "dark") -> "error" (no suffix variant)
        """
        if icon_name.endswith('_white') or icon_name.endswith('_black'):
            base_name = icon_name[:-6]
        else:
            base_name = icon_name
        
        white_icon = f"{base_name}_white"
        black_icon = f"{base_name}_black"
        
        has_white = os.path.exists(os.path.join(self._icon_dir, f"{white_icon}.svg")) or \
                    os.path.exists(os.path.join(self._icon_dir, f"{white_icon}.png"))
        has_black = os.path.exists(os.path.join(self._icon_dir, f"{black_icon}.svg")) or \
                    os.path.exists(os.path.join(self._icon_dir, f"{black_icon}.png"))
        
        if not has_white and not has_black:
            return icon_name
        
        if theme_type == "dark":
            if has_white:
                return white_icon
            elif has_black:
                return black_icon
        else:
            if has_black:
                return black_icon
            elif has_white:
                return white_icon
        
        return icon_name

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
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtCore import QRectF
            
            renderer = QSvgRenderer(svg_path)
            if not renderer.isValid():
                return self._get_default_icon(size)
            
            scale_factor = 2
            render_size = size * scale_factor
            
            pixmap = QPixmap(render_size, render_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            
            renderer.render(painter, QRectF(0, 0, render_size, render_size))
            painter.end()
            
            if scale_factor > 1:
                final_pixmap = pixmap.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                return QIcon(final_pixmap)
            
            return QIcon(pixmap)
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
        scale_factor = 2
        render_size = size * scale_factor
        
        base_icon = self.get_icon(icon_name, render_size)

        pixmap = base_icon.pixmap(render_size, render_size)
        if pixmap.isNull():
            return base_icon

        colored_pixmap = QPixmap(render_size, render_size)
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        painter.drawPixmap(0, 0, pixmap)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)

        painter.end()

        if scale_factor > 1:
            final_pixmap = colored_pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            return QIcon(final_pixmap)

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
    
    def list_icons(self, pattern: str = "", color_variant: str = "auto") -> list:
        """
        List available icon names.
        
        By default, returns icons without duplicates:
        - Icons without suffix (e.g., error.svg) are always shown
        - Icons with _black/_white suffix are grouped, only one variant is shown
        
        Args:
            pattern: Optional pattern to filter icons
            color_variant: Which color variant to show for suffixed icons:
                - "auto": Prefer _white, fallback to _black (default)
                - "white": Only show _white variants
                - "black": Only show _black variants
                - "all": Show all icons including duplicates
        
        Returns:
            List of icon names (without extension)
        
        Example:
            icons = icon_mgr.list_icons()  # Returns unique icons
            white_only = icon_mgr.list_icons(color_variant="white")
            all_icons = icon_mgr.list_icons(color_variant="all")
        """
        if not os.path.exists(self._icon_dir):
            logger.warning(f"Icon directory not found: {self._icon_dir}")
            return []
        
        if color_variant == "all":
            icons = set()
            for filename in os.listdir(self._icon_dir):
                if filename.endswith('.svg') or filename.endswith('.png'):
                    name = filename.rsplit('.', 1)[0]
                    if pattern in name:
                        icons.add(name)
            return sorted(icons)
        
        if color_variant in ("white", "black"):
            icons = set()
            suffix = f"_{color_variant}"
            for filename in os.listdir(self._icon_dir):
                if filename.endswith('.svg') or filename.endswith('.png'):
                    name = filename.rsplit('.', 1)[0]
                    if pattern in name and name.endswith(suffix):
                        icons.add(name)
            return sorted(icons)
        
        base_icons = set()
        suffixed_icons = {}
        
        for filename in os.listdir(self._icon_dir):
            if filename.endswith('.svg') or filename.endswith('.png'):
                name = filename.rsplit('.', 1)[0]
                if pattern in name:
                    if name.endswith('_white'):
                        base = name[:-6]
                        suffixed_icons[base] = name
                    elif name.endswith('_black'):
                        base = name[:-6]
                        if base not in suffixed_icons:
                            suffixed_icons[base] = name
                    else:
                        base_icons.add(name)
        
        result = sorted(base_icons | set(suffixed_icons.values()))
        return result
    
    def get_icon_categories(self) -> Dict[str, list]:
        """
        Get icons grouped by category (base name).
        
        Groups icons by their base name (without _black/_white suffix).
        
        Returns:
            Dict mapping base name to list of variants
        
        Example:
            categories = icon_mgr.get_icon_categories()
            # {'Play': ['Play_black', 'Play_white'], ...}
        """
        icons = self.list_icons()
        categories: Dict[str, list] = {}
        
        for icon_name in icons:
            if icon_name.endswith('_white'):
                base = icon_name[:-6]
            elif icon_name.endswith('_black'):
                base = icon_name[:-6]
            else:
                base = icon_name
            
            if base not in categories:
                categories[base] = []
            categories[base].append(icon_name)
        
        return categories

    def is_colored_icon(self, icon_name: str) -> bool:
        """
        Check if an icon is a colored icon (should not be colorized).
        
        Colored icons have their own colors in the SVG and should not 
        be overridden by theme colors. This method detects colored icons
        by checking if the SVG contains fill attributes with actual colors
        (not just "currentColor" or "none").
        
        Note: 
        - Icons with _black/_white suffixes are considered monochrome
        - Grayscale colors (R=G=B) are considered monochrome
        - Only truly colored icons (with non-grayscale colors) return True
        
        Args:
            icon_name: Name of the icon
        
        Returns:
            True if the icon is a colored icon
        """
        known_colored = {
            'error', 'info', 'success', 'warning',
            'Error', 'Info', 'Success', 'Warning',
        }
        if icon_name in known_colored:
            return True
        
        if icon_name.endswith('_black') or icon_name.endswith('_white'):
            return False
        
        svg_path = os.path.join(self._icon_dir, f"{icon_name}.svg")
        if not os.path.exists(svg_path):
            return False
        
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            color_pattern = r'fill\s*=\s*["\']#([0-9a-fA-F]{3,8})["\']'
            matches = re.findall(color_pattern, content)
            
            if matches:
                for match in matches:
                    hex_lower = match.lower()
                    if not self._is_grayscale_color(hex_lower):
                        return True
                return False
            
            rgba_pattern = r'fill\s*=\s*["\']rgba?\([^"\']+["\']'
            if re.search(rgba_pattern, content):
                rgba_matches = re.findall(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', content)
                for r, g, b in rgba_matches:
                    if not (r == g == b):
                        return True
                return False
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking if icon is colored: {e}")
            return False
    
    def _is_grayscale_color(self, hex_color: str) -> bool:
        """
        Check if a hex color is grayscale (R=G=B).
        
        Args:
            hex_color: Hex color string (3, 4, 6, or 8 characters)
        
        Returns:
            True if the color is grayscale
        """
        hex_lower = hex_color.lower()
        
        if len(hex_lower) == 3:
            return hex_lower[0] == hex_lower[1] == hex_lower[2]
        elif len(hex_lower) == 4:
            return hex_lower[0] == hex_lower[1] == hex_lower[2]
        elif len(hex_lower) >= 6:
            r = hex_lower[0:2]
            g = hex_lower[2:4]
            b = hex_lower[4:6]
            return r == g == b
        
        return False

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
