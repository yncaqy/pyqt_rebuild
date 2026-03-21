"""
TabViewItem 组件

严格遵循 WinUI3 TabViewItem 设计规范。
参考: https://learn.microsoft.com/zh-cn/windows/apps/design/controls/tab-view
"""

import logging
from typing import Optional, Union
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QSizePolicy, QPushButton
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPoint, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QSize, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPainterPath, QIcon, QFont,
    QFocusEvent, QMouseEvent, QEnterEvent
)

from .config import TabViewConfig, TabViewVisualStates
from .styles import TabViewStyle
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class TabViewItemCloseButton(QPushButton):
    """
    TabViewItem 关闭按钮。
    
    WinUI3 设计规范:
    - 尺寸: 16x16 像素
    - 圆角: 8px（完全圆形）
    - 悬停时显示背景
    - 按下时背景加深
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._hovered = False
        self._pressed = False
        
        self.setFixedSize(TabViewConfig.CLOSE_BUTTON_SIZE, TabViewConfig.CLOSE_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = TabViewConfig.CLOSE_BUTTON_RADIUS
        
        if self._pressed:
            bg_color = TabViewStyle.get_close_background(hovered=False, pressed=True)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, radius, radius)
        elif self._hovered:
            bg_color = TabViewStyle.get_close_background(hovered=True)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, radius, radius)
        
        icon_color = TabViewStyle.get_close_icon_color(hovered=self._hovered)
        pen = QPen(icon_color, 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        padding = 4
        painter.drawLine(
            rect.left() + padding, rect.top() + padding,
            rect.right() - padding, rect.bottom() - padding
        )
        painter.drawLine(
            rect.right() - padding, rect.top() + padding,
            rect.left() + padding, rect.bottom() - padding
        )
        
    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)


class TabViewItem(QWidget):
    """
    单个标签项控件。
    
    WinUI3 TabViewItem 设计规范:
    - Header: 标签文本
    - IconSource: 图标
    - IsClosable: 是否可关闭
    - 关闭按钮在悬停或选中时显示
    - 选中时背景高亮，与内容区域无缝连接
    - 支持拖拽重排
    - 支持键盘导航
    
    视觉状态:
    - Normal: 默认状态
    - PointerOver: 鼠标悬停
    - Pressed: 按下状态
    - Selected: 选中状态
    - PointerOverSelected: 选中时悬停
    - PressedSelected: 选中时按下
    - Focused: 焦点状态
    """
    
    clicked = pyqtSignal()
    closeRequested = pyqtSignal()
    dragStarted = pyqtSignal()
    dragEntered = pyqtSignal(object)
    
    def __init__(
        self, 
        header: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ):
        self._header = header
        self._key = item_key or header
        self._is_closable = closable
        self._icon_source = icon
        self._is_selected = False
        self._hovered = False
        self._pressed = False
        self._focused = False
        self._focus_visible = False
        self._hover_opacity = 0.0
        self._close_button: Optional[TabViewItemCloseButton] = None
        self._drag_start_pos: Optional[QPoint] = None
        self._is_dragging = False
        self._visual_state = TabViewVisualStates.NORMAL
        self._theme_mgr = ThemeManager.instance()
        self._cleanup_done = False
        
        super().__init__(parent)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setFixedHeight(TabViewConfig.TAB_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        self._update_visual_state()
        self._subscribe_theme()
        
    def _subscribe_theme(self) -> None:
        """订阅主题变化。"""
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_destroyed)
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化。"""
        self.update()
        if hasattr(self, '_close_button') and self._close_button:
            self._close_button.update()
        
    def _on_destroyed(self) -> None:
        """组件销毁时取消订阅。"""
        if not self._cleanup_done:
            try:
                self._theme_mgr.unsubscribe(self)
            except Exception:
                pass
            self._cleanup_done = True
        
    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            TabViewConfig.TAB_PADDING_H,
            TabViewConfig.TAB_PADDING_V,
            TabViewConfig.TAB_PADDING_H,
            TabViewConfig.TAB_PADDING_V
        )
        layout.setSpacing(TabViewConfig.ICON_TEXT_SPACING)
        
        if self._icon_source:
            self._icon_label = QLabel()
            self._icon_label.setFixedSize(TabViewConfig.ICON_SIZE, TabViewConfig.ICON_SIZE)
            self._icon_label.setPixmap(
                self._icon_source.pixmap(TabViewConfig.ICON_SIZE, TabViewConfig.ICON_SIZE)
            )
            layout.addWidget(self._icon_label)
        
        self._header_label = QLabel(self._header)
        font = QFont()
        font.setPixelSize(TabViewConfig.FONT_SIZE)
        self._header_label.setFont(font)
        layout.addWidget(self._header_label, 1)
        
        if self._is_closable:
            self._close_button = TabViewItemCloseButton(self)
            self._close_button.clicked.connect(self.closeRequested.emit)
            self._close_button.hide()
            layout.addWidget(self._close_button)
            
    def _update_visual_state(self) -> None:
        if self._is_selected:
            if self._pressed:
                self._visual_state = TabViewVisualStates.PRESSED_SELECTED
            elif self._hovered:
                self._visual_state = TabViewVisualStates.POINTER_OVER_SELECTED
            elif self._focused:
                self._visual_state = TabViewVisualStates.FOCUSED
            else:
                self._visual_state = TabViewVisualStates.SELECTED
        else:
            if self._pressed:
                self._visual_state = TabViewVisualStates.PRESSED
            elif self._hovered:
                self._visual_state = TabViewVisualStates.POINTER_OVER
            else:
                self._visual_state = TabViewVisualStates.NORMAL
                
        self.update()
        
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = TabViewConfig.TAB_RADIUS
        
        if self._is_selected:
            bg_color = TabViewStyle.get_tab_background_selected()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.top() + radius)
            path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
            path.lineTo(rect.right() - radius, rect.top())
            path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()
            painter.drawPath(path)
            
        elif self._hovered:
            hover_color = TabViewStyle.get_tab_background_hover()
            hover_color = QColor(hover_color)
            hover_color.setAlphaF(hover_color.alphaF() * self._hover_opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover_color)
            painter.drawRoundedRect(rect, radius, radius)
            
        elif self._pressed:
            pressed_color = TabViewStyle.get_tab_background_pressed()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(pressed_color)
            painter.drawRoundedRect(rect, radius, radius)
            
        if self._focused and self._focus_visible:
            focus_color = TabViewStyle.get_focus_border_color()
            pen = QPen(focus_color, TabViewConfig.FOCUS_BORDER_WIDTH)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            focus_rect = rect.adjusted(
                TabViewConfig.FOCUS_BORDER_OFFSET,
                TabViewConfig.FOCUS_BORDER_OFFSET,
                -TabViewConfig.FOCUS_BORDER_OFFSET,
                -TabViewConfig.FOCUS_BORDER_OFFSET
            )
            painter.drawRoundedRect(focus_rect, radius - 2, radius - 2)
            
        text_color = TabViewStyle.get_tab_text(
            selected=self._is_selected,
            hovered=self._hovered
        )
        self._header_label.setStyleSheet(
            f"color: {text_color.name()}; background: transparent;"
        )
        
        if self._icon_source and hasattr(self, '_icon_label'):
            self._icon_label.setStyleSheet("background: transparent;")
            
    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self._animate_hover_opacity(1.0)
        self._update_close_button_visibility()
        self._update_visual_state()
        super().enterEvent(event)
        
    def leaveEvent(self, event) -> None:
        self._hovered = False
        self._pressed = False
        self._animate_hover_opacity(0.0)
        self._update_close_button_visibility()
        self._update_visual_state()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._drag_start_pos = event.pos()
            self._update_visual_state()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            if not self._is_dragging:
                self.clicked.emit()
            self._is_dragging = False
            self._drag_start_pos = None
            self._update_visual_state()
        super().mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_start_pos and not self._is_dragging:
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance > TabViewConfig.DRAG_THRESHOLD:
                self._is_dragging = True
                self.dragStarted.emit()
        super().mouseMoveEvent(event)
        
    def focusInEvent(self, event: QFocusEvent) -> None:
        self._focused = True
        self._focus_visible = event.reason() != Qt.FocusReason.MouseFocusReason
        self._update_visual_state()
        super().focusInEvent(event)
        
    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._focused = False
        self._focus_visible = False
        self._update_visual_state()
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clicked.emit()
        elif event.key() == Qt.Key.Key_Delete and self._is_closable:
            self.closeRequested.emit()
        super().keyPressEvent(event)
        
    def _animate_hover_opacity(self, target: float) -> None:
        if not hasattr(self, '_hover_animation'):
            self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
            self._hover_animation.setDuration(TabViewConfig.ANIMATION_DURATION)
            self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()
        
    def get_hover_opacity(self) -> float:
        return self._hover_opacity
        
    def set_hover_opacity(self, value: float) -> None:
        self._hover_opacity = value
        self.update()
        
    hoverOpacity = pyqtProperty(float, get_hover_opacity, set_hover_opacity)
    
    def _update_close_button_visibility(self) -> None:
        if self._close_button:
            if self._is_selected or self._hovered:
                self._close_button.show()
            else:
                self._close_button.hide()
                
    def setSelected(self, selected: bool) -> None:
        if self._is_selected != selected:
            self._is_selected = selected
            self._update_close_button_visibility()
            self._update_visual_state()
            
            font = QFont()
            font.setPixelSize(TabViewConfig.FONT_SIZE)
            if selected:
                font.setWeight(TabViewConfig.FONT_WEIGHT_SELECTED)
            self._header_label.setFont(font)
            
    def isSelected(self) -> bool:
        return self._is_selected
        
    def setHeader(self, header: str) -> None:
        self._header = header
        self._header_label.setText(header)
        
    def header(self) -> str:
        return self._header
        
    def text(self) -> str:
        return self._header
        
    def key(self) -> str:
        return self._key
        
    def setKey(self, key: str) -> None:
        self._key = key
        
    def isClosable(self) -> bool:
        return self._is_closable
        
    def setClosable(self, closable: bool) -> None:
        self._is_closable = closable
        if self._close_button:
            self._close_button.setVisible(closable and (self._is_selected or self._hovered))
            
    def setIcon(self, icon: QIcon) -> None:
        self._icon_source = icon
        if hasattr(self, '_icon_label'):
            self._icon_label.setPixmap(
                icon.pixmap(TabViewConfig.ICON_SIZE, TabViewConfig.ICON_SIZE)
            )
            
    def icon(self) -> Optional[QIcon]:
        return self._icon_source
        
    def sizeHint(self) -> QSize:
        from PyQt6.QtGui import QFontMetrics
        
        font = QFont()
        font.setPixelSize(TabViewConfig.FONT_SIZE)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self._header)
        
        width = text_width + TabViewConfig.TAB_PADDING_H * 2
        
        if self._icon_source:
            width += TabViewConfig.ICON_SIZE + TabViewConfig.ICON_TEXT_SPACING
            
        if self._is_closable:
            width += TabViewConfig.CLOSE_BUTTON_SIZE + TabViewConfig.CLOSE_BUTTON_MARGIN
            
        return QSize(width, TabViewConfig.TAB_HEIGHT)
        
    def minimumSizeHint(self) -> QSize:
        return QSize(TabViewConfig.TAB_MIN_WIDTH, TabViewConfig.TAB_HEIGHT)


TabItem = TabViewItem
