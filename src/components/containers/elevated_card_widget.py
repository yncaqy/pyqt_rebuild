"""
ElevatedCardWidget Component

Provides a card widget with hover lift animation effect.

Features:
- Lift animation when mouse enters
- Theme integration
- Customizable border radius
- Smooth animations
"""

import logging
from typing import Optional
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QPoint
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class CardConfig:
    """Configuration constants for elevated card."""
    
    DEFAULT_BORDER_RADIUS = 8
    HOVER_LIFT_DISTANCE = 4
    ANIMATION_DURATION = 200


class ElevatedCardWidget(QWidget):
    """
    Elevated card widget with hover lift animation effect.
    
    Features:
    - Lift animation when mouse enters
    - Theme integration
    - Customizable border radius
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._border_radius = CardConfig.DEFAULT_BORDER_RADIUS
        self._lift_distance = 0
        self._is_hovered = False
        
        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
        logger.debug("ElevatedCardWidget initialized")
    
    def _setup_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(16, 16, 16, 16)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()
    
    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = radius
        self.update()
    
    def borderRadius(self) -> int:
        return self._border_radius
    
    def get_lift_distance(self) -> float:
        return self._lift_distance
    
    def set_lift_distance(self, value: float) -> None:
        self._lift_distance = value
        self.update()
    
    lift_distance = pyqtProperty(float, get_lift_distance, set_lift_distance)
    
    def _animate_hover_in(self) -> None:
        self._lift_anim = QPropertyAnimation(self, b"lift_distance")
        self._lift_anim.setDuration(CardConfig.ANIMATION_DURATION)
        self._lift_anim.setStartValue(self._lift_distance)
        self._lift_anim.setEndValue(CardConfig.HOVER_LIFT_DISTANCE)
        self._lift_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._lift_anim.start()
    
    def _animate_hover_out(self) -> None:
        self._lift_anim = QPropertyAnimation(self, b"lift_distance")
        self._lift_anim.setDuration(CardConfig.ANIMATION_DURATION)
        self._lift_anim.setStartValue(self._lift_distance)
        self._lift_anim.setEndValue(0)
        self._lift_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._lift_anim.start()
    
    def enterEvent(self, event) -> None:
        self._is_hovered = True
        self._animate_hover_in()
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        self._is_hovered = False
        self._animate_hover_out()
        super().leaveEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._theme:
            bg_color = self._theme.get_color('card.background', QColor(50, 50, 50))
            border_color = self._theme.get_color('card.border', QColor(60, 60, 60))
        else:
            bg_color = QColor(50, 50, 50)
            border_color = QColor(60, 60, 60)
        
        lift = int(self._lift_distance)
        rect = QRectF(self.rect())
        card_rect = rect.translated(0, -lift)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(card_rect, self._border_radius, self._border_radius)
    
    def setContentWidget(self, widget: QWidget) -> None:
        if self._main_layout.count() > 0:
            old_widget = self._main_layout.takeAt(0).widget()
            if old_widget:
                old_widget.deleteLater()
        
        self._main_layout.addWidget(widget)
    
    def contentWidget(self) -> Optional[QWidget]:
        if self._main_layout.count() > 0:
            return self._main_layout.itemAt(0).widget()
        return None
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("ElevatedCardWidget cleaned up")
