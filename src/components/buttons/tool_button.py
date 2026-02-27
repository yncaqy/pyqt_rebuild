"""
ToolButton Component

Provides a tool button widget for displaying icons only.

Features:
- Icon-only display
- Theme integration with icon color adaptation
- Hover and pressed states
- Customizable icon size
- Support for SVG and pixmap icons
"""

import logging
from typing import Optional
from pathlib import Path
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF, QPoint, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QByteArray
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QBrush,
    QEnterEvent, QMouseEvent, QPainterPath
)
from PyQt6.QtWidgets import QToolButton, QWidget
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class ToolButtonConfig:
    """Configuration constants for tool button."""
    
    DEFAULT_SIZE = 36
    DEFAULT_ICON_SIZE = 16
    BORDER_RADIUS = 4


class ToolButton(QToolButton):
    """
    Tool button widget for displaying icons only.
    
    Features:
    - Icon-only display
    - Theme integration with icon color adaptation
    - Hover and pressed states
    - Customizable icon size
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._icon_size = ToolButtonConfig.DEFAULT_ICON_SIZE
        self._border_radius = ToolButtonConfig.BORDER_RADIUS
        self._is_hovered = False
        self._is_pressed = False
        self._hover_opacity = 0.0
        self._svg_content: Optional[str] = None
        self._colored_pixmap: Optional[QPixmap] = None
        
        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("ToolButton initialized")
    
    def _setup_ui(self) -> None:
        self.setFixedSize(ToolButtonConfig.DEFAULT_SIZE, ToolButtonConfig.DEFAULT_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._update_colored_icon()
        self.update()
    
    def _get_icon_color(self) -> QColor:
        """Get the icon color based on current theme."""
        if self._theme:
            return self._theme.get_color('button.text.normal', QColor(255, 255, 255))
        return QColor(255, 255, 255)
    
    def _update_colored_icon(self) -> None:
        """Update the colored icon based on current theme."""
        if self._svg_content:
            color = self._get_icon_color()
            self._colored_pixmap = self._create_colored_pixmap(self._svg_content, color)
    
    def _create_colored_pixmap(self, svg_content: str, color: QColor) -> Optional[QPixmap]:
        """
        Create a colored pixmap from SVG content.
        
        Args:
            svg_content: SVG content string
            color: Color to apply
            
        Returns:
            Colored QPixmap or None
        """
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
    
    def setIconSize(self, size: QSize) -> None:
        """Set the icon size."""
        self._icon_size = size.width()
        super().setIconSize(size)
        self._update_colored_icon()
        self.update()
    
    def setBorderRadius(self, radius: int) -> None:
        """Set the border radius."""
        self._border_radius = radius
        self.update()
    
    def borderRadius(self) -> int:
        return self._border_radius
    
    def setIcon(self, icon: QIcon | str) -> None:
        """
        Set the icon.
        
        Args:
            icon: QIcon or SVG string
        """
        if isinstance(icon, str):
            self._svg_content = icon
            self._update_colored_icon()
        else:
            self._svg_content = None
            self._colored_pixmap = None
            super().setIcon(icon)
    
    def get_hover_opacity(self) -> float:
        return self._hover_opacity
    
    def set_hover_opacity(self, value: float) -> None:
        self._hover_opacity = value
        self.update()
    
    hover_opacity = pyqtProperty(float, get_hover_opacity, set_hover_opacity)
    
    def _animate_hover_in(self) -> None:
        self._hover_anim = QPropertyAnimation(self, b"hover_opacity")
        self._hover_anim.setDuration(150)
        self._hover_anim.setStartValue(self._hover_opacity)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._hover_anim.start()
    
    def _animate_hover_out(self) -> None:
        self._hover_anim = QPropertyAnimation(self, b"hover_opacity")
        self._hover_anim.setDuration(150)
        self._hover_anim.setStartValue(self._hover_opacity)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._hover_anim.start()
    
    def enterEvent(self, event: QEnterEvent) -> None:
        self._is_hovered = True
        self._animate_hover_in()
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        self._is_hovered = False
        self._animate_hover_out()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        rect = QRectF(self.rect())
        
        if self._theme:
            if self._is_pressed:
                bg_color = self._theme.get_color('button.background.pressed', QColor(60, 60, 60))
            elif self._is_hovered:
                bg_color = self._theme.get_color('button.background.hover', QColor(50, 50, 50))
            else:
                bg_color = QColor(0, 0, 0, 0)
        else:
            if self._is_pressed:
                bg_color = QColor(60, 60, 60)
            elif self._is_hovered:
                bg_color = QColor(50, 50, 50)
            else:
                bg_color = QColor(0, 0, 0, 0)
        
        if self._hover_opacity > 0 and bg_color.alpha() > 0:
            bg_color.setAlpha(int(bg_color.alpha() * self._hover_opacity))
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)
        
        if self._colored_pixmap:
            icon_size = QSize(self._icon_size, self._icon_size)
            x = (self.width() - icon_size.width()) // 2
            y = (self.height() - icon_size.height()) // 2
            icon_rect = QRect(QPoint(x, y), icon_size)
            painter.drawPixmap(icon_rect, self._colored_pixmap)
        else:
            icon = self.icon()
            if not icon.isNull():
                icon_size = QSize(self._icon_size, self._icon_size)
                pixmap = icon.pixmap(icon_size)
                
                x = (self.width() - icon_size.width()) // 2
                y = (self.height() - icon_size.height()) // 2
                
                icon_rect = QRect(QPoint(x, y), icon_size)
                painter.drawPixmap(icon_rect, pixmap)
    
    def sizeHint(self) -> QSize:
        return QSize(ToolButtonConfig.DEFAULT_SIZE, ToolButtonConfig.DEFAULT_SIZE)
    
    def minimumSizeHint(self) -> QSize:
        return QSize(ToolButtonConfig.DEFAULT_SIZE, ToolButtonConfig.DEFAULT_SIZE)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("ToolButton cleaned up")
