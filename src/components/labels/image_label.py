"""
ImageLabel Component

Provides a label widget for displaying images and GIFs with high DPI support.

Features:
- High DPI screen support
- Smooth image scaling without aliasing
- Support for static images and animated GIFs
- Aspect ratio preservation
- Border radius support
"""

import logging
from typing import Optional
from pathlib import Path
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF, QPoint, QTimer,
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QMovie, QTransform,
    QPaintEvent, QPainterPath, QPen, QBrush
)
from PyQt6.QtWidgets import QLabel, QWidget
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class ImageConfig:
    """Configuration constants for image label."""
    
    DEFAULT_BORDER_RADIUS = 0
    SMOOTH_TRANSFORM = Qt.TransformationMode.SmoothTransformation


class ImageLabel(QWidget):
    """
    Image label widget with high DPI support.
    
    Features:
    - High DPI screen support
    - Smooth image scaling without aliasing
    - Support for static images and animated GIFs
    - Aspect ratio preservation
    - Border radius support
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._border_radius = ImageConfig.DEFAULT_BORDER_RADIUS
        self._pixmap: Optional[QPixmap] = None
        self._original_pixmap: Optional[QPixmap] = None
        self._movie: Optional[QMovie] = None
        self._image_path: Optional[str] = None
        self._aspect_ratio_mode = Qt.AspectRatioMode.KeepAspectRatio
        
        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("ImageLabel initialized")
    
    def _setup_ui(self) -> None:
        self.setMinimumSize(1, 1)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()
    
    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = radius
        self.update()
    
    def borderRadius(self) -> int:
        return self._border_radius
    
    def setAspectRatioMode(self, mode: Qt.AspectRatioMode) -> None:
        self._aspect_ratio_mode = mode
        self.update()
    
    def aspectRatioMode(self) -> Qt.AspectRatioMode:
        return self._aspect_ratio_mode
    
    def setImage(self, image: QPixmap | QImage | str) -> None:
        """
        Set the image to display.
        
        Args:
            image: QPixmap, QImage, or file path string
        """
        if isinstance(image, str):
            self._load_from_path(image)
        elif isinstance(image, QPixmap):
            self._set_pixmap(image)
        elif isinstance(image, QImage):
            self._set_pixmap(QPixmap.fromImage(image))
    
    def _load_from_path(self, path: str) -> None:
        """Load image from file path."""
        self._image_path = path
        
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        path_obj = Path(path)
        suffix = path_obj.suffix.lower()
        
        if suffix == '.gif':
            self._load_gif(path)
        else:
            self._load_static_image(path)
    
    def _load_static_image(self, path: str) -> None:
        """Load static image from path."""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            logger.warning(f"Failed to load image: {path}")
            return
        
        self._set_pixmap(pixmap)
    
    def _load_gif(self, path: str) -> None:
        """Load animated GIF from path."""
        self._movie = QMovie(path)
        if not self._movie.isValid():
            logger.warning(f"Failed to load GIF: {path}")
            self._movie.deleteLater()
            self._movie = None
            return
        
        self._movie.frameChanged.connect(self._on_frame_changed)
        self._movie.start()
    
    def _on_frame_changed(self) -> None:
        """Handle GIF frame change."""
        if self._movie:
            pixmap = self._movie.currentPixmap()
            if not pixmap.isNull():
                self._set_pixmap(pixmap, from_movie=True)
    
    def _set_pixmap(self, pixmap: QPixmap, from_movie: bool = False) -> None:
        """Set the pixmap with high DPI support."""
        if not from_movie:
            self._original_pixmap = pixmap
        
        self._pixmap = pixmap
        self.update()
    
    def _get_scaled_pixmap(self) -> Optional[QPixmap]:
        """Get the scaled pixmap for current widget size."""
        if self._pixmap is None:
            return None
        
        source_pixmap = self._original_pixmap if self._original_pixmap and not self._movie else self._pixmap
        if source_pixmap.isNull():
            return None
        
        device_pixel_ratio = self.devicePixelRatioF()
        
        target_size = self.size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return None
        
        actual_size = QSize(
            int(target_size.width() * device_pixel_ratio),
            int(target_size.height() * device_pixel_ratio)
        )
        
        scaled_size = source_pixmap.size().scaled(actual_size, self._aspect_ratio_mode)
        
        scaled_pixmap = source_pixmap.scaled(
            scaled_size,
            self._aspect_ratio_mode,
            Qt.TransformationMode.SmoothTransformation
        )
        
        scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
        
        return scaled_pixmap
    
    def _get_image_rect(self) -> QRect:
        """Get the rectangle where the image should be drawn (centered)."""
        if self._pixmap is None:
            return QRect()
        
        source_pixmap = self._original_pixmap if self._original_pixmap and not self._movie else self._pixmap
        widget_size = self.size()
        
        scaled_size = source_pixmap.size().scaled(widget_size, self._aspect_ratio_mode)
        
        x = (widget_size.width() - scaled_size.width()) // 2
        y = (widget_size.height() - scaled_size.height()) // 2
        
        return QRect(x, y, scaled_size.width(), scaled_size.height())
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle paint event with border radius support."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        if self._pixmap is None:
            return
        
        scaled_pixmap = self._get_scaled_pixmap()
        if scaled_pixmap is None:
            return
        
        image_rect = self._get_image_rect()
        
        if self._border_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(QRectF(image_rect), self._border_radius, self._border_radius)
            painter.setClipPath(path)
        
        painter.drawPixmap(image_rect, scaled_pixmap)
    
    def sizeHint(self) -> QSize:
        """Return the size hint based on the pixmap."""
        if self._original_pixmap:
            return self._original_pixmap.size()
        if self._pixmap:
            return self._pixmap.size()
        return super().sizeHint()
    
    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint."""
        return QSize(1, 1)
    
    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        super().resizeEvent(event)
        self.update()
    
    def clear(self) -> None:
        """Clear the image."""
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        self._pixmap = None
        self._original_pixmap = None
        self._image_path = None
        self.update()
    
    def isAnimated(self) -> bool:
        """Check if the image is animated (GIF)."""
        return self._movie is not None
    
    def pause(self) -> None:
        """Pause GIF animation."""
        if self._movie:
            self._movie.setPaused(True)
    
    def resume(self) -> None:
        """Resume GIF animation."""
        if self._movie:
            self._movie.setPaused(False)
    
    def setSpeed(self, speed: int) -> None:
        """
        Set GIF animation speed.
        
        Args:
            speed: Speed percentage (100 = normal speed)
        """
        if self._movie:
            self._movie.setSpeed(speed)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        
        logger.debug("ImageLabel cleaned up")
