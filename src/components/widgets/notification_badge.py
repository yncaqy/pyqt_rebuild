"""
NotificationBadge - 徽章组件

提供功能完整的徽章组件，用于显示未读通知数量。

Features:
- 显示未读通知数量
- 支持不同尺寸（小型/中型/大型）
- 提供多种颜色变体（主要/次要/警告/危险/成功）
- 支持自定义文本内容
- 数字变化动画效果
- 可配置最大显示数字
- 支持点击交互事件
- 深色/浅色主题支持

Example:
    badge = NotificationBadge()
    badge.set_count(5)
    badge.set_variant(NotificationBadge.VARIANT_DANGER)
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize, QPropertyAnimation, 
    QEasingCurve, pyqtProperty, QRectF
)
from PyQt6.QtGui import QColor, QPainter, QFont, QPen, QBrush, QFontMetrics

from core.theme_manager import ThemeManager, Theme
from core.font_manager import FontManager

logger = logging.getLogger(__name__)


class BadgeConfig:
    """NotificationBadge配置常量"""
    
    SIZE_SMALL = "small"
    SIZE_MEDIUM = "medium"
    SIZE_LARGE = "large"
    
    SIZE_DIMENSIONS = {
        SIZE_SMALL: {"min_width": 16, "height": 16, "font_size": 10, "padding": 4},
        SIZE_MEDIUM: {"min_width": 20, "height": 20, "font_size": 11, "padding": 6},
        SIZE_LARGE: {"min_width": 24, "height": 24, "font_size": 12, "padding": 8},
    }
    
    BOUNCE_DURATION = 150


class NotificationBadge(QWidget):
    """
    徽章组件。
    
    显示未读通知数量，支持多种样式和动画效果。
    
    Features:
    - 显示未读通知数量
    - 支持不同尺寸（小型/中型/大型）
    - 提供多种颜色变体（主要/次要/警告/危险/成功）
    - 支持自定义文本内容
    - 数字变化动画效果
    - 可配置最大显示数字
    - 支持点击交互事件
    - 深色/浅色主题支持
    
    Signals:
        clicked: 徽章被点击时发出
        
    Example:
        badge = NotificationBadge()
        badge.set_count(5)
        badge.set_variant(NotificationBadge.VARIANT_DANGER)
        badge.clicked.connect(lambda: print("Badge clicked"))
    """
    
    clicked = pyqtSignal()
    
    VARIANT_PRIMARY = "primary"
    VARIANT_SECONDARY = "secondary"
    VARIANT_WARNING = "warning"
    VARIANT_DANGER = "danger"
    VARIANT_SUCCESS = "success"
    VARIANT_INFO = "info"
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self._count: int = 0
        self._max_count: int = 99
        self._text: Optional[str] = None
        self._size: str = BadgeConfig.SIZE_MEDIUM
        self._variant: str = self.VARIANT_DANGER
        self._show_zero: bool = False
        self._dot_mode: bool = False
        
        self._bg_color: QColor = QColor(231, 76, 60)
        self._text_color: QColor = QColor(255, 255, 255)
        self._border_color: Optional[QColor] = None
        
        self._scale: float = 1.0
        self._animation: Optional[QPropertyAnimation] = None
        self._is_pressed: bool = False
        
        self._setup_ui()
        self._apply_initial_theme()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
    def _setup_ui(self) -> None:
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_size()
        
    def _update_size(self) -> None:
        """更新尺寸"""
        dims = BadgeConfig.SIZE_DIMENSIONS[self._size]
        self.setFixedHeight(dims["height"])
        self.setMinimumWidth(dims["min_width"])
        self.update()
        
    def _apply_initial_theme(self) -> None:
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)
            
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to NotificationBadge: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return
            
        self._current_theme = theme
        self._update_colors()
        self.update()
        
    def _update_colors(self) -> None:
        """根据变体更新颜色"""
        is_dark = self._current_theme and self._current_theme.name == 'dark'
        
        color_map = {
            self.VARIANT_PRIMARY: (QColor(0, 120, 215), QColor(30, 144, 255)) if is_dark else (QColor(0, 120, 215), QColor(0, 120, 215)),
            self.VARIANT_SECONDARY: (QColor(108, 117, 125), QColor(130, 138, 145)) if is_dark else (QColor(108, 117, 125), QColor(108, 117, 125)),
            self.VARIANT_WARNING: (QColor(255, 193, 7), QColor(255, 193, 7)),
            self.VARIANT_DANGER: (QColor(220, 53, 69), QColor(231, 76, 60)),
            self.VARIANT_SUCCESS: (QColor(40, 167, 69), QColor(46, 204, 113)),
            self.VARIANT_INFO: (QColor(23, 162, 184), QColor(52, 152, 219)),
        }
        
        colors = color_map.get(self._variant, color_map[self.VARIANT_DANGER])
        self._bg_color = colors[1] if is_dark else colors[0]
        self._text_color = QColor(255, 255, 255)
        
        if self._variant == self.VARIANT_WARNING:
            self._text_color = QColor(50, 50, 50)
            
    def set_count(self, count: int) -> None:
        """
        设置显示数量。
        
        Args:
            count: 数量值
        """
        old_count = self._count
        self._count = max(0, count)
        
        if old_count != self._count:
            self._animate_change()
            
        self.update()
        
    def get_count(self) -> int:
        """获取当前数量"""
        return self._count
        
    def set_max_count(self, max_count: int) -> None:
        """
        设置最大显示数量。
        
        Args:
            max_count: 最大数量，超过显示如 "99+"
        """
        self._max_count = max(1, max_count)
        self.update()
        
    def set_text(self, text: Optional[str]) -> None:
        """
        设置自定义文本。
        
        Args:
            text: 自定义文本，None则显示数量
        """
        self._text = text
        self.update()
        
    def set_size(self, size: str) -> None:
        """
        设置徽章尺寸。
        
        Args:
            size: 尺寸，可选值：small, medium, large
        """
        if size in BadgeConfig.SIZE_DIMENSIONS:
            self._size = size
            self._update_size()
            
    def set_variant(self, variant: str) -> None:
        """
        设置颜色变体。
        
        Args:
            variant: 变体，可选值：primary, secondary, warning, danger, success, info
        """
        self._variant = variant
        self._update_colors()
        self.update()
        
    def set_show_zero(self, show: bool) -> None:
        """
        设置是否显示零值。
        
        Args:
            show: True显示，False隐藏
        """
        self._show_zero = show
        self.update()
        
    def set_dot_mode(self, enabled: bool) -> None:
        """
        设置是否为圆点模式。
        
        Args:
            enabled: True为圆点模式，False为数字模式
        """
        self._dot_mode = enabled
        self.update()
        
    def increment(self, delta: int = 1) -> None:
        """
        增加数量。
        
        Args:
            delta: 增量值
        """
        self.set_count(self._count + delta)
        
    def decrement(self, delta: int = 1) -> None:
        """
        减少数量。
        
        Args:
            delta: 减量值
        """
        self.set_count(max(0, self._count - delta))
        
    def clear(self) -> None:
        """清除数量"""
        self.set_count(0)
        
    def _animate_change(self) -> None:
        """数字变化动画"""
        if self._animation:
            self._animation.stop()
            
        self._animation = QPropertyAnimation(self, b"scale")
        self._animation.setDuration(BadgeConfig.BOUNCE_DURATION)
        self._animation.setStartValue(1.3)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation.start()
        
    @pyqtProperty(float)
    def scale(self) -> float:
        return self._scale
        
    @scale.setter
    def scale(self, scale: float) -> None:
        self._scale = scale
        self.update()
        
    def _get_display_text(self) -> str:
        """获取显示文本"""
        if self._text is not None:
            return self._text
            
        if self._dot_mode:
            return ""
            
        if self._count == 0:
            return "0"
            
        if self._count > self._max_count:
            return f"{self._max_count}+"
            
        return str(self._count)
        
    def _should_show(self) -> bool:
        """判断是否应该显示"""
        if self._text is not None:
            return True
        if self._dot_mode:
            return self._count > 0
        if self._count == 0 and not self._show_zero:
            return False
        return True
        
    def paintEvent(self, event) -> None:
        if not self._should_show():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        dims = BadgeConfig.SIZE_DIMENSIONS[self._size]
        
        cx = self.width() / 2
        cy = self.height() / 2
        
        painter.translate(cx, cy)
        painter.scale(self._scale, self._scale)
        painter.translate(-cx, -cy)
        
        if self._dot_mode:
            radius = dims["height"] / 4
            painter.setBrush(QBrush(self._bg_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                int(self.width() / 2 - radius),
                int(self.height() / 2 - radius),
                int(radius * 2),
                int(radius * 2)
            )
        else:
            text = self._get_display_text()
            font = FontManager.get_small_font()
            font.setBold(True)
            painter.setFont(font)
            
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            
            badge_width = max(dims["min_width"], text_width + dims["padding"] * 2)
            badge_height = dims["height"]
            radius = badge_height / 2
            
            rect_x = (self.width() - badge_width) / 2
            rect_y = (self.height() - badge_height) / 2
            
            painter.setBrush(QBrush(self._bg_color))
            
            if self._is_pressed:
                painter.setOpacity(0.8)
                
            if self._border_color:
                painter.setPen(QPen(self._border_color, 1))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                
            painter.drawRoundedRect(
                QRectF(rect_x, rect_y, badge_width, badge_height),
                radius, radius
            )
            
            painter.setPen(QPen(self._text_color))
            painter.setOpacity(1.0 if not self._is_pressed else 0.8)
            painter.drawText(
                QRectF(rect_x, rect_y, badge_width, badge_height),
                Qt.AlignmentFlag.AlignCenter,
                text
            )
            
        painter.end()
        
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.update()
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)
        
    def sizeHint(self) -> QSize:
        if not self._should_show():
            return QSize(0, 0)
            
        dims = BadgeConfig.SIZE_DIMENSIONS[self._size]
        
        if self._dot_mode:
            size = int(dims["height"] / 2)
            return QSize(size, size)
            
        text = self._get_display_text()
        font = FontManager.get_small_font()
        font.setBold(True)
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        badge_width = max(dims["min_width"], text_width + dims["padding"] * 2)
        
        return QSize(int(badge_width), dims["height"])
        
    def cleanup(self) -> None:
        """清理资源"""
        if self._animation:
            self._animation.stop()
        self._theme_mgr.unsubscribe(self)
