"""
WinUI3 风格 ComboBox 下拉菜单

实现符合 WinUI3 设计规范的下拉菜单组件。
特性：
- 平滑的弹出动画
- 选中项指示器
- 悬停高亮效果
- 键盘导航支持
"""

import logging
from typing import Optional, List, Dict, Any, Callable
from PyQt6.QtCore import (
    Qt, QSize, QPoint, QRect, QPropertyAnimation, 
    QEasingCurve, pyqtProperty, pyqtSignal, QTimer
)
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QFont, QCursor, QPainterPath
from PyQt6.QtWidgets import QWidget, QFrame, QScrollArea, QVBoxLayout, QSizePolicy, QApplication

try:
    from core.theme_manager import ThemeManager, Theme
    from core.icon_manager import IconManager
    from themes.colors import FONT_CONFIG
    from .config import ComboBoxMenuConfig, ComboBoxAnimationConfig
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.icon_manager import IconManager
    from ...themes.colors import FONT_CONFIG
    from .config import ComboBoxMenuConfig, ComboBoxAnimationConfig

logger = logging.getLogger(__name__)


class ComboBoxMenuItem(QWidget):
    """ComboBox 下拉菜单项组件。"""
    
    clicked = pyqtSignal(int)
    
    def __init__(self, text: str, index: int, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._text = text
        self._index = index
        self._icon: Optional[QIcon] = None
        self._user_data: Any = None
        self._is_selected = False
        self._is_hovered = False
        self._is_enabled = True
        
        self._theme: Optional[Theme] = None
        self._colors: Dict[str, QColor] = {}
        
        self._hover_progress = 0.0
        self._hover_animation: Optional[QPropertyAnimation] = None
        
        self.setFixedHeight(ComboBoxMenuConfig.ITEM_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        
        self._init_theme()
    
    def _init_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True
        self._colors = ComboBoxMenuConfig.get_colors(is_dark)
        self.update()
    
    def text(self) -> str:
        return self._text
    
    def setText(self, text: str) -> None:
        self._text = text
        self.update()
    
    def icon(self) -> Optional[QIcon]:
        return self._icon
    
    def setIcon(self, icon: Optional[QIcon]) -> None:
        self._icon = icon
        self.update()
    
    def index(self) -> int:
        return self._index
    
    def userData(self) -> Any:
        return self._user_data
    
    def setUserData(self, data: Any) -> None:
        self._user_data = data
    
    def isSelected(self) -> bool:
        return self._is_selected
    
    def setSelected(self, selected: bool) -> None:
        self._is_selected = selected
        self.update()
    
    def isEnabled(self) -> bool:
        return self._is_enabled
    
    def setEnabled(self, enabled: bool) -> None:
        self._is_enabled = enabled
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if enabled 
            else Qt.CursorShape.ForbiddenCursor
        )
        self.update()
    
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
        self._hover_animation.setDuration(ComboBoxAnimationConfig.HOVER_DURATION)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.start()
    
    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        if self._is_enabled:
            self._is_hovered = True
            self._start_hover_animation(1.0)
    
    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._is_hovered = False
        self._start_hover_animation(0.0)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self.clicked.emit(self._index)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        rect = self.rect()
        
        if not self._colors:
            return
        
        if not self._is_enabled:
            bg_color = self._colors['item_background_normal']
            text_color = self._colors['item_text_disabled']
        elif self._is_selected:
            bg_color = self._colors['item_background_selected']
            text_color = self._colors['item_text_selected']
        elif self._is_hovered or self._hover_progress > 0:
            normal_bg = self._colors['item_background_normal']
            hover_bg = self._colors['item_background_hover']
            bg_color = self._lerp_color(normal_bg, hover_bg, self._hover_progress)
            text_color = self._colors['item_text_hover']
        else:
            bg_color = self._colors['item_background_normal']
            text_color = self._colors['item_text_normal']
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, ComboBoxMenuConfig.ITEM_BORDER_RADIUS, ComboBoxMenuConfig.ITEM_BORDER_RADIUS)
        
        text_left = ComboBoxMenuConfig.ITEM_PADDING_H
        
        if self._is_selected:
            if self._theme:
                indicator_color = self._theme.get_color('primary.background.normal', self._colors['checkmark'])
            else:
                indicator_color = self._colors['checkmark']
            indicator_height = rect.height() - 16
            indicator_x = ComboBoxMenuConfig.INDICATOR_MARGIN
            indicator_y = 8
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(indicator_color))
            painter.drawRoundedRect(
                QRect(indicator_x, indicator_y, ComboBoxMenuConfig.INDICATOR_WIDTH, indicator_height),
                1.5, 1.5
            )
            
            text_left = ComboBoxMenuConfig.ITEM_PADDING_H + 4
        
        icon_size = 16
        if self._icon and not self._icon.isNull():
            icon_x = text_left
            icon_y = (rect.height() - icon_size) // 2
            self._icon.paint(painter, icon_x, icon_y, icon_size, icon_size)
            text_left = icon_x + icon_size + 8
        
        text_rect = rect.adjusted(text_left, 0, -ComboBoxMenuConfig.ITEM_PADDING_H, 0)
        
        font = QFont()
        font.setFamily(FONT_CONFIG['family'])
        font.setFamilies([FONT_CONFIG['family'], FONT_CONFIG['fallback']])
        font.setPixelSize(FONT_CONFIG['size']['body'])
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._text)
    
    def _lerp_color(self, c1: QColor, c2: QColor, t: float) -> QColor:
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        return QColor(r, g, b, a)


class ComboBoxMenu(QWidget):
    """ComboBox 下拉菜单组件。"""
    
    itemClicked = pyqtSignal(int)
    aboutToHide = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items: List[ComboBoxMenuItem] = []
        self._current_index: int = -1
        self._theme: Optional[Theme] = None
        self._colors: Dict[str, QColor] = {}
        
        self._opacity = 0.0
        self._opacity_animation: Optional[QPropertyAnimation] = None
        
        self.setWindowFlags(
            Qt.WindowType.Popup | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self._setup_ui()
        self._init_theme()
    
    def _setup_ui(self) -> None:
        self._container = QFrame(self)
        self._container.setObjectName("comboBoxMenuContainer")
        
        self._scroll_area = QScrollArea(self._container)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setStyleSheet("background: transparent;")
        
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        
        self._layout = QVBoxLayout(self._content_widget)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(2)
        
        self._scroll_area.setWidget(self._content_widget)
        
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self._scroll_area)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(self._container)
    
    def _init_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
        for item in self._items:
            item._on_theme_changed(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True
        self._colors = ComboBoxMenuConfig.get_colors(is_dark)
        self.update()
    
    def get_opacity(self) -> float:
        return self._opacity
    
    def set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def addItem(self, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        item = ComboBoxMenuItem(text, len(self._items), self._content_widget)
        item.setIcon(icon)
        item.setUserData(userData)
        item.clicked.connect(self._on_item_clicked)
        
        if self._theme:
            item._apply_theme(self._theme)
        
        self._items.append(item)
        self._layout.addWidget(item)
        self._update_size()
    
    def addItems(self, texts: List[str]) -> None:
        for text in texts:
            self.addItem(text)
    
    def clear(self) -> None:
        for item in self._items:
            self._layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()
        self._current_index = -1
        self._update_size()
    
    def setCurrentIndex(self, index: int) -> None:
        if 0 <= index < len(self._items):
            for i, item in enumerate(self._items):
                item.setSelected(i == index)
            self._current_index = index
    
    def currentIndex(self) -> int:
        return self._current_index
    
    def itemText(self, index: int) -> str:
        if 0 <= index < len(self._items):
            return self._items[index].text()
        return ""
    
    def itemData(self, index: int) -> Any:
        if 0 <= index < len(self._items):
            return self._items[index].userData()
        return None
    
    def count(self) -> int:
        return len(self._items)
    
    def _on_item_clicked(self, index: int) -> None:
        self.setCurrentIndex(index)
        self.itemClicked.emit(index)
        self.hide()
    
    def _update_size(self) -> None:
        item_count = min(len(self._items), ComboBoxMenuConfig.MAX_VISIBLE_ITEMS)
        spacing = 2
        margins = 8
        content_height = item_count * ComboBoxMenuConfig.ITEM_HEIGHT + (item_count - 1) * spacing + margins
        
        self._content_widget.setFixedHeight(content_height)
        self._scroll_area.setFixedHeight(content_height)
        
        self.setMinimumWidth(120)
        self.setMinimumHeight(content_height + 16)
    
    def show_at(self, pos: QPoint, width: int) -> None:
        self.setFixedWidth(width)
        self.move(pos)
        self._animate_show()
        self.show()
    
    def _animate_show(self) -> None:
        if self._opacity_animation:
            self._opacity_animation.stop()
        
        self._opacity_animation = QPropertyAnimation(self, b"opacity")
        self._opacity_animation.setDuration(ComboBoxAnimationConfig.MENU_OPEN_DURATION)
        self._opacity_animation.setStartValue(0.0)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._opacity_animation.start()
    
    def hide(self) -> None:
        self._animate_hide()
    
    def _animate_hide(self) -> None:
        if self._opacity_animation:
            self._opacity_animation.stop()
        
        self._opacity_animation = QPropertyAnimation(self, b"opacity")
        self._opacity_animation.setDuration(ComboBoxAnimationConfig.MENU_CLOSE_DURATION)
        self._opacity_animation.setStartValue(self._opacity)
        self._opacity_animation.setEndValue(0.0)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self._opacity_animation.finished.connect(super().hide)
        self._opacity_animation.start()
    
    def hideEvent(self, event) -> None:
        self.aboutToHide.emit()
        super().hideEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)
        
        if not self._colors:
            return
        
        is_dark = self._theme.is_dark if self._theme and hasattr(self._theme, 'is_dark') else True
        shadow_color = ComboBoxMenuConfig.SHADOW_COLOR_DARK if is_dark else ComboBoxMenuConfig.SHADOW_COLOR_LIGHT
        
        shadow_rect = self.rect().adjusted(4, 4, -4, -4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.setOpacity(self._opacity * 0.3)
        painter.drawRoundedRect(shadow_rect, ComboBoxMenuConfig.BORDER_RADIUS, ComboBoxMenuConfig.BORDER_RADIUS)
        
        painter.setOpacity(self._opacity)
        
        container_rect = self._container.geometry()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._colors['background']))
        painter.drawRoundedRect(container_rect, ComboBoxMenuConfig.BORDER_RADIUS, ComboBoxMenuConfig.BORDER_RADIUS)
        
        if self._colors['border'].alpha() > 0:
            painter.setPen(QPen(self._colors['border'], ComboBoxMenuConfig.BORDER_WIDTH))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(container_rect, ComboBoxMenuConfig.BORDER_RADIUS, ComboBoxMenuConfig.BORDER_RADIUS)
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        
        if event.key() == Qt.Key.Key_Up:
            new_index = max(0, self._current_index - 1)
            self.setCurrentIndex(new_index)
            return
        
        if event.key() == Qt.Key.Key_Down:
            new_index = min(len(self._items) - 1, self._current_index + 1)
            self.setCurrentIndex(new_index)
            return
        
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._current_index >= 0:
                self._on_item_clicked(self._current_index)
            return
        
        super().keyPressEvent(event)
