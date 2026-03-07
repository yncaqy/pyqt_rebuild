"""
分割面板组件

提供可拖动调整尺寸的分割面板，具有以下特性：
- 支持水平和垂直两种分割方向
- 可配置的最小面板尺寸限制
- 平滑的拖动动画效果
- 清晰的视觉反馈（悬停/拖动状态）
- 响应式设计
- 主题集成
"""

import logging
from typing import Optional, List
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QTimer, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QCursor, QLinearGradient
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class SplitterConfig:
    """Splitter 行为和样式的配置常量。"""
    
    DEFAULT_HANDLE_WIDTH = 6
    DEFAULT_MIN_SIZE = 50
    DEFAULT_ANIMATION_DURATION = 150
    COLLAPSE_THRESHOLD = 10


class SplitterHandle(QWidget):
    """分隔条组件，支持拖动调整面板尺寸。"""
    
    positionChanged = pyqtSignal(int)
    dragStarted = pyqtSignal()
    dragFinished = pyqtSignal()
    
    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._orientation = orientation
        self._is_dragging = False
        self._is_hovered = False
        self._start_pos: int = 0
        self._color: Optional[QColor] = None
        self._hover_color: Optional[QColor] = None
        self._drag_color: Optional[QColor] = None
        
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        if orientation == Qt.Orientation.Horizontal:
            self.setCursor(QCursor(Qt.CursorShape.SplitHCursor))
            self.setFixedWidth(SplitterConfig.DEFAULT_HANDLE_WIDTH)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setCursor(QCursor(Qt.CursorShape.SplitVCursor))
            self.setFixedHeight(SplitterConfig.DEFAULT_HANDLE_WIDTH)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
    def set_colors(self, normal: QColor, hover: QColor, drag: QColor):
        self._color = normal
        self._hover_color = hover
        self._drag_color = drag
        self.update()
    
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._start_pos = event.globalPosition().toPoint().x() if self._orientation == Qt.Orientation.Horizontal else event.globalPosition().toPoint().y()
            self.dragStarted.emit()
            self.update()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._is_dragging:
            current_pos = event.globalPosition().toPoint().x() if self._orientation == Qt.Orientation.Horizontal else event.globalPosition().toPoint().y()
            delta = current_pos - self._start_pos
            self._start_pos = current_pos
            self.positionChanged.emit(delta)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._is_dragging:
            self._is_dragging = False
            self.dragFinished.emit()
            self.update()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        if self._is_dragging and self._drag_color:
            color = self._drag_color
        elif self._is_hovered and self._hover_color:
            color = self._hover_color
        elif self._color:
            color = self._color
        else:
            color = QColor(200, 200, 200)
        
        painter.fillRect(rect, color)
        
        if self._is_dragging or self._is_hovered:
            accent_color = color.lighter(120) if color.lightness() < 128 else color.darker(120)
            painter.setPen(QPen(accent_color, 1))
            if self._orientation == Qt.Orientation.Horizontal:
                painter.drawLine(rect.center().x(), rect.top(), rect.center().x(), rect.bottom())
            else:
                painter.drawLine(rect.left(), rect.center().y(), rect.right(), rect.center().y())
        
        painter.end()


class SplitterPanel(QWidget):
    """分割面板中的单个面板。"""
    
    def __init__(self, widget: Optional[QWidget] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._widget: Optional[QWidget] = None
        self._min_size: int = SplitterConfig.DEFAULT_MIN_SIZE
        self._current_size: int = 0
        self._is_collapsed: bool = False
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QHBoxLayout(self) if False else QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        if widget:
            self.set_widget(widget)
    
    def set_widget(self, widget: QWidget):
        if self._widget:
            self._widget.setParent(None)
        
        self._widget = widget
        if widget:
            widget.setParent(self)
            self.layout().addWidget(widget)
    
    def widget(self) -> Optional[QWidget]:
        return self._widget
    
    def minimumSize(self) -> int:
        return self._min_size
    
    def setMinimumSize(self, size: int):
        self._min_size = max(0, size)
    
    def size(self) -> int:
        return self._current_size
    
    def setSize(self, size: int):
        self._current_size = size
    
    def isCollapsed(self) -> bool:
        return self._is_collapsed
    
    def setCollapsed(self, collapsed: bool):
        self._is_collapsed = collapsed


class Splitter(QWidget, StyleOverrideMixin):
    """
    分割面板组件。
    
    特性：
    - 支持水平和垂直两种分割方向
    - 可配置的最小面板尺寸限制
    - 平滑的拖动动画效果
    - 清晰的视觉反馈（悬停/拖动状态）
    - 响应式设计
    - 主题集成
    
    信号：
        splitterMoved: 当分隔条移动时发出
    
    示例：
        splitter = Splitter(Qt.Orientation.Horizontal)
        splitter.addWidget(panel1)
        splitter.addWidget(panel2)
        splitter.setSizes([200, 300])
    """
    
    splitterMoved = pyqtSignal(int, int)
    
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_style_override()
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._orientation = orientation
        self._panels: List[SplitterPanel] = []
        self._handles: List[SplitterHandle] = []
        self._sizes: List[int] = []
        self._min_sizes: List[int] = []
        self._is_resizing: bool = False
        
        self._setup_ui()
        self._apply_initial_theme()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
    
    def _setup_ui(self):
        if self._orientation == Qt.Orientation.Horizontal:
            self._main_layout = QHBoxLayout(self)
        else:
            self._main_layout = QVBoxLayout(self)
        
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
    
    def _apply_initial_theme(self):
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)
    
    def _on_theme_changed(self, theme: Theme):
        if not theme:
            return
        
        self._current_theme = theme
        self._update_style()
    
    def _update_style(self):
        if not self._current_theme:
            return
        
        theme = self._current_theme
        
        bg = self.get_style_color(theme, 'splitter.background', QColor(240, 240, 240))
        handle_color = self.get_style_color(theme, 'splitter.handle', QColor(220, 220, 220))
        handle_hover = self.get_style_color(theme, 'splitter.handle.hover', QColor(200, 200, 200))
        handle_drag = self.get_style_color(theme, 'splitter.handle.drag', QColor(52, 152, 219))
        
        self.setStyleSheet(f"background-color: {bg.name()};")
        
        for handle in self._handles:
            handle.set_colors(handle_color, handle_hover, handle_drag)
    
    def _on_widget_destroyed(self):
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)
    
    def orientation(self) -> Qt.Orientation:
        return self._orientation
    
    def addWidget(self, widget: QWidget, min_size: int = SplitterConfig.DEFAULT_MIN_SIZE):
        panel = SplitterPanel(widget)
        panel.setMinimumSize(min_size)
        
        if self._panels:
            handle = SplitterHandle(self._orientation, self)
            handle.positionChanged.connect(lambda delta, idx=len(self._handles): self._on_handle_moved(idx, delta))
            handle.dragStarted.connect(self._on_drag_started)
            handle.dragFinished.connect(self._on_drag_finished)
            
            self._main_layout.addWidget(handle)
            self._handles.append(handle)
            
            if self._current_theme:
                handle_color = self.get_style_color(self._current_theme, 'splitter.handle', QColor(220, 220, 220))
                handle_hover = self.get_style_color(self._current_theme, 'splitter.handle.hover', QColor(200, 200, 200))
                handle_drag = self.get_style_color(self._current_theme, 'splitter.handle.drag', QColor(52, 152, 219))
                handle.set_colors(handle_color, handle_hover, handle_drag)
        
        self._main_layout.addWidget(panel)
        self._panels.append(panel)
        self._min_sizes.append(min_size)
        
        if len(self._panels) == 1:
            self._sizes = [self.width() if self._orientation == Qt.Orientation.Horizontal else self.height()]
        else:
            self._recalculate_sizes()
    
    def insertWidget(self, index: int, widget: QWidget, min_size: int = SplitterConfig.DEFAULT_MIN_SIZE):
        if index < 0 or index > len(self._panels):
            return
        
        if index == len(self._panels):
            self.addWidget(widget, min_size)
            return
        
        panel = SplitterPanel(widget)
        panel.setMinimumSize(min_size)
        
        if self._panels:
            handle = SplitterHandle(self._orientation, self)
            handle.positionChanged.connect(lambda delta, idx=index - 1: self._on_handle_moved(idx, delta))
            handle.dragStarted.connect(self._on_drag_started)
            handle.dragFinished.connect(self._on_drag_finished)
            
            self._main_layout.insertWidget(index * 2, handle)
            self._handles.insert(index, handle)
        
        self._main_layout.insertWidget(index * 2 if self._handles else index, panel)
        self._panels.insert(index, panel)
        self._min_sizes.insert(index, min_size)
        
        self._recalculate_sizes()
    
    def widget(self, index: int) -> Optional[QWidget]:
        if 0 <= index < len(self._panels):
            return self._panels[index].widget()
        return None
    
    def count(self) -> int:
        return len(self._panels)
    
    def sizes(self) -> List[int]:
        return self._sizes.copy()
    
    def setSizes(self, sizes: List[int]):
        if len(sizes) != len(self._panels):
            return
        
        total = sum(sizes)
        available = self.width() if self._orientation == Qt.Orientation.Horizontal else self.height()
        
        if total > 0 and available > 0:
            scale = available / total
            self._sizes = [int(s * scale) for s in sizes]
        else:
            self._sizes = sizes.copy()
        
        self._apply_sizes()
    
    def setMinimumSize(self, index: int, min_size: int):
        if 0 <= index < len(self._panels):
            self._panels[index].setMinimumSize(min_size)
            self._min_sizes[index] = min_size
    
    def minimumSize(self, index: int) -> int:
        if 0 <= index < len(self._panels):
            return self._panels[index].minimumSize()
        return SplitterConfig.DEFAULT_MIN_SIZE
    
    def _recalculate_sizes(self):
        if not self._panels:
            return
        
        available = self.width() if self._orientation == Qt.Orientation.Horizontal else self.height()
        handle_width = SplitterConfig.DEFAULT_HANDLE_WIDTH * len(self._handles)
        available -= handle_width
        
        if len(self._sizes) < len(self._panels):
            old_count = len(self._sizes)
            new_count = len(self._panels)
            
            if old_count == 0:
                self._sizes = [available // new_count] * new_count
            else:
                old_total = sum(self._sizes)
                if old_total > 0:
                    scale = available / old_total
                    self._sizes = [int(s * scale) for s in self._sizes]
                
                remaining = available - sum(self._sizes)
                self._sizes.append(max(remaining, SplitterConfig.DEFAULT_MIN_SIZE))
        
        self._apply_sizes()
    
    def _apply_sizes(self):
        for i, panel in enumerate(self._panels):
            size = self._sizes[i] if i < len(self._sizes) else SplitterConfig.DEFAULT_MIN_SIZE
            
            if self._orientation == Qt.Orientation.Horizontal:
                panel.setFixedWidth(max(size, self._min_sizes[i]))
            else:
                panel.setFixedHeight(max(size, self._min_sizes[i]))
    
    def _on_handle_moved(self, handle_index: int, delta: int):
        if handle_index < 0 or handle_index >= len(self._panels) - 1:
            return
        
        left_index = handle_index
        right_index = handle_index + 1
        
        new_left_size = self._sizes[left_index] + delta
        new_right_size = self._sizes[right_index] - delta
        
        min_left = self._min_sizes[left_index]
        min_right = self._min_sizes[right_index]
        
        if new_left_size < min_left:
            delta = min_left - self._sizes[left_index]
            new_left_size = min_left
            new_right_size = self._sizes[right_index] - delta
        elif new_right_size < min_right:
            delta = self._sizes[right_index] - min_right
            new_right_size = min_right
            new_left_size = self._sizes[left_index] + delta
        
        self._sizes[left_index] = new_left_size
        self._sizes[right_index] = new_right_size
        
        self._apply_sizes()
        
        self.splitterMoved.emit(handle_index, delta)
    
    def _on_drag_started(self):
        self._is_resizing = True
    
    def _on_drag_finished(self):
        self._is_resizing = False
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if self._panels:
            total = self.width() if self._orientation == Qt.Orientation.Horizontal else self.height()
            handle_width = SplitterConfig.DEFAULT_HANDLE_WIDTH * len(self._handles)
            available = total - handle_width
            
            if available > 0:
                old_total = sum(self._sizes)
                if old_total > 0:
                    scale = available / old_total
                    self._sizes = [max(int(s * scale), self._min_sizes[i]) for i, s in enumerate(self._sizes)]
                else:
                    self._sizes = [available // len(self._panels)] * len(self._panels)
                
                self._apply_sizes()
    
    def saveState(self) -> dict:
        return {
            'sizes': self._sizes.copy(),
            'min_sizes': self._min_sizes.copy()
        }
    
    def restoreState(self, state: dict):
        if 'sizes' in state:
            sizes = state['sizes']
            if len(sizes) == len(self._panels):
                self._sizes = sizes.copy()
                self._apply_sizes()
    
    def cleanup(self):
        if self._cleanup_done:
            return
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)


class AnimatedSplitter(Splitter):
    """带动画效果的分割面板组件。"""
    
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self._animation: Optional[QPropertyAnimation] = None
        self._target_sizes: List[int] = []
    
    def setSizesAnimated(self, sizes: List[int], duration: int = SplitterConfig.DEFAULT_ANIMATION_DURATION):
        if len(sizes) != len(self._panels):
            return
        
        self._target_sizes = sizes.copy()
        
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"animationValue")
        self._animation.setDuration(duration)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation_progress)
        self._animation.start()
    
    def _on_animation_progress(self, progress: float):
        if not self._target_sizes:
            return
        
        current_sizes = self.sizes()
        new_sizes = []
        
        for i, target in enumerate(self._target_sizes):
            if i < len(current_sizes):
                current = current_sizes[i]
                new_size = int(current + (target - current) * progress)
                new_sizes.append(new_size)
        
        if len(new_sizes) == len(self._panels):
            self._sizes = new_sizes
            self._apply_sizes()
    
    def get_animationValue(self):
        return 0.0
    
    def set_animationValue(self, value: float):
        pass
    
    animationValue = property(get_animationValue, set_animationValue)
