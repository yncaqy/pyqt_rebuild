"""
WinUI3 风格图片标签组件

遵循 WinUI3 设计规范，提供高 DPI 支持的图片显示组件。
支持静态图片和 GIF 动画，支持圆角和阴影效果。

Features:
- High DPI screen support
- Smooth image scaling without aliasing
- Support for static images and animated GIFs
- Aspect ratio preservation
- Border radius support
- Theme-aware styling
"""

import logging
from typing import Optional
from pathlib import Path
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF, QTimer,
    QPropertyAnimation, QEasingCurve, pyqtProperty, QPointF
)
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QMovie, QTransform,
    QPaintEvent, QPainterPath, QPen, QBrush, QColor, QLinearGradient
)
from PyQt6.QtWidgets import QWidget
try:
    from core.theme_manager import ThemeManager, Theme
    from themes.colors import WINUI3_DARK_COLORS, WINUI3_LIGHT_COLORS
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...themes.colors import WINUI3_DARK_COLORS, WINUI3_LIGHT_COLORS

logger = logging.getLogger(__name__)


class ImageLabelConfig:
    """ImageLabel 配置常量，遵循 WinUI3 设计规范。"""
    
    DEFAULT_BORDER_RADIUS = 4
    SMOOTH_TRANSFORM = Qt.TransformationMode.SmoothTransformation
    
    SHADOW_OFFSET = 2.0
    SHADOW_BLUR = 8.0
    SHADOW_COLOR_DARK = QColor(0, 0, 0, 60)
    SHADOW_COLOR_LIGHT = QColor(0, 0, 0, 30)


class ImageLabel(QWidget):
    """
    WinUI3 风格图片标签组件。
    
    Features:
    - High DPI screen support
    - Smooth image scaling without aliasing
    - Support for static images and animated GIFs
    - Aspect ratio preservation
    - Border radius support
    - Theme-aware styling
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._border_radius = ImageLabelConfig.DEFAULT_BORDER_RADIUS
        self._pixmap: Optional[QPixmap] = None
        self._original_pixmap: Optional[QPixmap] = None
        self._movie: Optional[QMovie] = None
        self._image_path: Optional[str] = None
        self._aspect_ratio_mode = Qt.AspectRatioMode.KeepAspectRatio
        
        self._shadow_enabled = False
        self._shadow_offset = ImageLabelConfig.SHADOW_OFFSET
        self._shadow_blur = ImageLabelConfig.SHADOW_BLUR
        
        self._hover_progress = 0.0
        self._hover_animation: Optional[QPropertyAnimation] = None
        
        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setMouseTracking(True)
        
        logger.debug("ImageLabel initialized")
    
    def _setup_ui(self) -> None:
        self.setMinimumSize(1, 1)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
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
    
    def setShadowEnabled(self, enabled: bool) -> None:
        self._shadow_enabled = enabled
        self.update()
    
    def isShadowEnabled(self) -> bool:
        return self._shadow_enabled
    
    def setImage(self, image: QPixmap | QImage | str) -> None:
        if isinstance(image, str):
            self._load_from_path(image)
        elif isinstance(image, QPixmap):
            self._set_pixmap(image)
        elif isinstance(image, QImage):
            self._set_pixmap(QPixmap.fromImage(image))
    
    def _load_from_path(self, path: str) -> None:
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
        pixmap = QPixmap(path)
        if pixmap.isNull():
            logger.warning(f"Failed to load image: {path}")
            return
        
        self._set_pixmap(pixmap)
    
    def _load_gif(self, path: str) -> None:
        self._movie = QMovie(path)
        if not self._movie.isValid():
            logger.warning(f"Failed to load GIF: {path}")
            self._movie.deleteLater()
            self._movie = None
            return
        
        self._movie.frameChanged.connect(self._on_frame_changed)
        self._movie.start()
    
    def _on_frame_changed(self) -> None:
        if self._movie:
            pixmap = self._movie.currentPixmap()
            if not pixmap.isNull():
                self._set_pixmap(pixmap, from_movie=True)
    
    def _set_pixmap(self, pixmap: QPixmap, from_movie: bool = False) -> None:
        if not from_movie:
            self._original_pixmap = pixmap
        
        self._pixmap = pixmap
        self.update()
    
    def _get_scaled_pixmap(self) -> Optional[QPixmap]:
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
        if self._pixmap is None:
            return QRect()
        
        source_pixmap = self._original_pixmap if self._original_pixmap and not self._movie else self._pixmap
        widget_size = self.size()
        
        scaled_size = source_pixmap.size().scaled(widget_size, self._aspect_ratio_mode)
        
        x = (widget_size.width() - scaled_size.width()) // 2
        y = (widget_size.height() - scaled_size.height()) // 2
        
        return QRect(x, y, scaled_size.width(), scaled_size.height())
    
    def get_hover_progress(self) -> float:
        return self._hover_progress
    
    def set_hover_progress(self, value: float) -> None:
        self._hover_progress = value
        self.update()
    
    hoverProgress = pyqtProperty(float, get_hover_progress, set_hover_progress)
    
    def _start_hover_animation(self, target: float) -> None:
        if self._hover_animation:
            self._hover_animation.stop()
        
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress")
        self._hover_animation.setDuration(167)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.start()
    
    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._start_hover_animation(1.0)
    
    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._start_hover_animation(0.0)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        if self._pixmap is None:
            return
        
        scaled_pixmap = self._get_scaled_pixmap()
        if scaled_pixmap is None:
            return
        
        image_rect = self._get_image_rect()
        
        if self._shadow_enabled:
            self._draw_shadow(painter, image_rect)
        
        if self._border_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(QRectF(image_rect), self._border_radius, self._border_radius)
            painter.setClipPath(path)
        
        if self._hover_progress > 0:
            overlay_color = QColor(255, 255, 255, int(20 * self._hover_progress))
            painter.setOpacity(1.0 - self._hover_progress * 0.1)
        
        painter.drawPixmap(image_rect, scaled_pixmap)
        
        painter.setOpacity(1.0)
    
    def _draw_shadow(self, painter: QPainter, rect: QRect) -> None:
        is_dark = self._theme.is_dark if self._theme and hasattr(self._theme, 'is_dark') else True
        shadow_color = ImageLabelConfig.SHADOW_COLOR_DARK if is_dark else ImageLabelConfig.SHADOW_COLOR_LIGHT
        
        shadow_rect = QRectF(rect)
        shadow_rect.translate(self._shadow_offset, self._shadow_offset)
        
        path = QPainterPath()
        path.addRoundedRect(shadow_rect, self._border_radius, self._border_radius)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.setOpacity(0.5)
        painter.drawPath(path)
        painter.setOpacity(1.0)
    
    def sizeHint(self) -> QSize:
        if self._original_pixmap:
            return self._original_pixmap.size()
        if self._pixmap:
            return self._pixmap.size()
        return super().sizeHint()
    
    def minimumSizeHint(self) -> QSize:
        return QSize(1, 1)
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update()
    
    def clear(self) -> None:
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        self._pixmap = None
        self._original_pixmap = None
        self._image_path = None
        self.update()
    
    def isAnimated(self) -> bool:
        return self._movie is not None
    
    def pause(self) -> None:
        if self._movie:
            self._movie.setPaused(True)
    
    def resume(self) -> None:
        if self._movie:
            self._movie.setPaused(False)
    
    def setSpeed(self, speed: int) -> None:
        if self._movie:
            self._movie.setSpeed(speed)
    
    def cleanup(self) -> None:
        if self._movie:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None
        
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.deleteLater()
            self._hover_animation = None
        
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        
        logger.debug("ImageLabel cleaned up")
    
    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
