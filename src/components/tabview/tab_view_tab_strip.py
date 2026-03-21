"""
TabStrip 组件

严格遵循 WinUI3 TabView TabStrip 设计规范。
参考: https://learn.microsoft.com/zh-cn/windows/apps/design/controls/tab-view
"""

import logging
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QPushButton, QFrame
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPoint, QMimeData, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QDrag, QDropEvent, QDragEnterEvent,
    QDragMoveEvent, QDragLeaveEvent, QIcon, QMouseEvent, QEnterEvent
)

from .config import TabViewConfig, TabViewWidthMode
from .styles import TabViewStyle
from .tab_view_item import TabViewItem
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class TabViewAddButton(QPushButton):
    """
    TabView 添加按钮。
    
    WinUI3 设计规范:
    - 尺寸: 36x36 像素
    - 圆角: 8px
    - 悬停时背景变化
    - 图标: 加号 (+)
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._hovered = False
        self._pressed = False
        
        self.setFixedSize(TabViewConfig.ADD_BUTTON_SIZE, TabViewConfig.ADD_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setToolTip("添加新标签页 (Ctrl+T)")
        
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = TabViewConfig.TAB_RADIUS
        
        if self._pressed:
            bg_color = QColor(255, 255, 255, 30) if TabViewStyle.is_dark_mode() else QColor(0, 0, 0, 30)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, radius, radius)
        elif self._hovered:
            bg_color = QColor(255, 255, 255, 20) if TabViewStyle.is_dark_mode() else QColor(0, 0, 0, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, radius, radius)
            
        icon_color = TabViewStyle.get_add_icon_color(hovered=self._hovered)
        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        center = rect.center()
        size = 10
        
        painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
        painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)
        
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


class TabViewScrollButton(QPushButton):
    """
    TabView 滚动按钮。
    
    WinUI3 设计规范:
    - 尺寸: 24x24 像素
    - 圆角: 4px
    - 悬停时背景变化
    - 图标: 左/右箭头
    """
    
    def __init__(self, direction: str = 'left', parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._direction = direction
        self._hovered = False
        
        self.setFixedSize(TabViewConfig.SCROLL_BUTTON_SIZE, TabViewConfig.SCROLL_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        radius = 4
        
        if self._hovered:
            bg_color = QColor(255, 255, 255, 20) if TabViewStyle.is_dark_mode() else QColor(0, 0, 0, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, radius, radius)
            
        icon_color = TabViewStyle.get_scroll_icon_color()
        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        center = rect.center()
        size = 5
        
        if self._direction == 'left':
            painter.drawLine(center.x() + size, center.y() - size, center.x() - size, center.y())
            painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y() + size)
        else:
            painter.drawLine(center.x() - size, center.y() - size, center.x() + size, center.y())
            painter.drawLine(center.x() + size, center.y(), center.x() - size, center.y() + size)
            
    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)


class TabViewTabStrip(QWidget):
    """
    TabView 标签条。
    
    WinUI3 设计规范:
    - 包含所有 TabViewItem
    - 支持拖拽重排
    - 支持滚动（标签过多时）
    - 左侧可放置自定义控件
    - 右侧可放置添加按钮
    - 键盘导航支持
    """
    
    tabClicked = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)
    tabReordered = pyqtSignal(int, int)
    addTabClicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._tabs: List[TabViewItem] = []
        self._selected_index = -1
        self._drag_index = -1
        self._drop_index = -1
        self._show_add_button = True
        self._can_reorder = True
        self._tab_width_mode = TabViewWidthMode.EQUAL
        self._left_header: Optional[QWidget] = None
        self._right_header: Optional[QWidget] = None
        self._theme_mgr = ThemeManager.instance()
        self._cleanup_done = False
        
        super().__init__(parent)
        
        self.setAcceptDrops(True)
        self.setFixedHeight(TabViewConfig.TAB_HEIGHT)
        self.setMouseTracking(True)
        
        self._init_ui()
        self._subscribe_theme()
        
    def _subscribe_theme(self) -> None:
        """订阅主题变化。"""
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_destroyed)
        
    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化。"""
        self.update()
        if hasattr(self, '_add_button') and self._add_button:
            self._add_button.update()
        if hasattr(self, '_left_scroll_btn') and self._left_scroll_btn:
            self._left_scroll_btn.update()
        if hasattr(self, '_right_scroll_btn') and self._right_scroll_btn:
            self._right_scroll_btn.update()
        for tab in self._tabs:
            tab.update()
        
    def _on_destroyed(self) -> None:
        """组件销毁时取消订阅。"""
        if not self._cleanup_done:
            try:
                self._theme_mgr.unsubscribe(self)
            except Exception:
                pass
            self._cleanup_done = True
        
    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        if self._left_header:
            self._main_layout.addWidget(self._left_header)
            
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setStyleSheet("background: transparent;")
        
        self._tabs_container = QWidget()
        self._tabs_container.setStyleSheet("background: transparent;")
        self._tabs_layout = QHBoxLayout(self._tabs_container)
        self._tabs_layout.setContentsMargins(0, 0, 0, 0)
        self._tabs_layout.setSpacing(TabViewConfig.TAB_SPACING)
        self._tabs_layout.addStretch()
        
        self._scroll_area.setWidget(self._tabs_container)
        self._main_layout.addWidget(self._scroll_area, 1)
        
        self._left_scroll_btn = TabViewScrollButton('left', self)
        self._left_scroll_btn.clicked.connect(self._scroll_left)
        self._left_scroll_btn.hide()
        
        self._right_scroll_btn = TabViewScrollButton('right', self)
        self._right_scroll_btn.clicked.connect(self._scroll_right)
        self._right_scroll_btn.hide()
        
        self._add_button = TabViewAddButton(self)
        self._add_button.clicked.connect(self.addTabClicked.emit)
        
        if self._show_add_button:
            self._main_layout.addWidget(self._add_button)
        else:
            self._add_button.hide()
            
        if self._right_header:
            self._main_layout.addWidget(self._right_header)
            
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = TabViewStyle.get_tabstrip_background()
        painter.fillRect(self.rect(), bg_color)
        
        super().paintEvent(event)
        
    def addTab(
        self, 
        header: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ) -> int:
        tab = TabViewItem(
            header=header,
            item_key=key,
            closable=closable,
            icon=icon
        )
        tab.clicked.connect(lambda: self._on_tab_clicked(tab))
        tab.closeRequested.connect(lambda: self._on_tab_close_requested(tab))
        tab.dragStarted.connect(lambda: self._on_tab_drag_started(tab))
        
        insert_index = self._tabs_layout.count() - 1
        self._tabs_layout.insertWidget(insert_index, tab)
        self._tabs.append(tab)
        
        index = len(self._tabs) - 1
        
        if self._selected_index == -1:
            self.setSelectedIndex(index)
            
        self._update_tab_widths()
        self._check_scroll_buttons()
        
        return index
        
    def insertTab(
        self, 
        index: int, 
        header: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ) -> int:
        tab = TabViewItem(
            header=header,
            item_key=key,
            closable=closable,
            icon=icon
        )
        tab.clicked.connect(lambda: self._on_tab_clicked(tab))
        tab.closeRequested.connect(lambda: self._on_tab_close_requested(tab))
        tab.dragStarted.connect(lambda: self._on_tab_drag_started(tab))
        
        actual_index = min(index, len(self._tabs))
        self._tabs_layout.insertWidget(actual_index, tab)
        self._tabs.insert(actual_index, tab)
        
        if self._selected_index >= actual_index:
            self._selected_index += 1
            
        self._update_tab_widths()
        self._check_scroll_buttons()
        
        return actual_index
        
    def removeTab(self, index: int) -> None:
        if 0 <= index < len(self._tabs):
            tab = self._tabs.pop(index)
            self._tabs_layout.removeWidget(tab)
            tab.deleteLater()
            
            if self._selected_index == index:
                if len(self._tabs) > 0:
                    new_index = min(index, len(self._tabs) - 1)
                    self.setSelectedIndex(new_index)
                else:
                    self._selected_index = -1
            elif self._selected_index > index:
                self._selected_index -= 1
                
            self._update_tab_widths()
            self._check_scroll_buttons()
            
    def setSelectedIndex(self, index: int) -> None:
        if 0 <= index < len(self._tabs):
            if self._selected_index != -1 and self._selected_index < len(self._tabs):
                self._tabs[self._selected_index].setSelected(False)
                
            self._selected_index = index
            self._tabs[index].setSelected(True)
            self._ensure_tab_visible(index)
            
    def selectedIndex(self) -> int:
        return self._selected_index
        
    def tabCount(self) -> int:
        return len(self._tabs)
        
    def tabAt(self, index: int) -> Optional[TabViewItem]:
        if 0 <= index < len(self._tabs):
            return self._tabs[index]
        return None
        
    def _on_tab_clicked(self, tab: TabViewItem) -> None:
        index = self._tabs.index(tab)
        self.setSelectedIndex(index)
        self.tabClicked.emit(index)
        
    def _on_tab_close_requested(self, tab: TabViewItem) -> None:
        index = self._tabs.index(tab)
        self.tabCloseRequested.emit(index)
        
    def _on_tab_drag_started(self, tab: TabViewItem) -> None:
        if not self._can_reorder:
            return
            
        self._drag_index = self._tabs.index(tab)
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self._drag_index))
        drag.setMimeData(mime_data)
        
        drag.exec(Qt.DropAction.MoveAction)
        
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.source() == self and self._can_reorder:
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.source() == self and self._can_reorder:
            pos = event.position().toPoint()
            
            for i, tab in enumerate(self._tabs):
                if tab.geometry().contains(pos):
                    self._drop_index = i
                    break
            else:
                self._drop_index = len(self._tabs)
                
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent) -> None:
        if event.source() == self and self._can_reorder:
            if self._drag_index != -1 and self._drop_index != -1:
                if self._drag_index != self._drop_index:
                    self._reorder_tabs(self._drag_index, self._drop_index)
                    self.tabReordered.emit(self._drag_index, self._drop_index)
                    
            self._drag_index = -1
            self._drop_index = -1
            event.acceptProposedAction()
            
    def _reorder_tabs(self, from_index: int, to_index: int) -> None:
        if from_index < to_index:
            to_index -= 1
            
        tab = self._tabs.pop(from_index)
        self._tabs.insert(to_index, tab)
        
        self._tabs_layout.removeWidget(tab)
        self._tabs_layout.insertWidget(to_index, tab)
        
        if self._selected_index == from_index:
            self._selected_index = to_index
        elif from_index < self._selected_index <= to_index:
            self._selected_index -= 1
        elif to_index <= self._selected_index < from_index:
            self._selected_index += 1
            
    def _update_tab_widths(self) -> None:
        if not self._tabs:
            return
            
        if self._tab_width_mode == TabViewWidthMode.EQUAL:
            available_width = self._scroll_area.width()
            tab_count = len(self._tabs)
            
            if tab_count > 0:
                tab_width = min(
                    available_width // tab_count,
                    TabViewConfig.TAB_MAX_WIDTH
                )
                tab_width = max(tab_width, TabViewConfig.TAB_MIN_WIDTH)
                
                for tab in self._tabs:
                    tab.setFixedWidth(tab_width)
        elif self._tab_width_mode == TabViewWidthMode.SIZE_TO_CONTENT:
            for tab in self._tabs:
                tab.setMinimumWidth(TabViewConfig.TAB_MIN_WIDTH)
                tab.setMaximumWidth(TabViewConfig.TAB_MAX_WIDTH)
                tab.setSizePolicy(
                    QSizePolicy.Policy.MinimumExpanding,
                    QSizePolicy.Policy.Fixed
                )
        elif self._tab_width_mode == TabViewWidthMode.COMPACT:
            for i, tab in enumerate(self._tabs):
                if tab.isSelected():
                    tab.setMinimumWidth(TabViewConfig.TAB_MIN_WIDTH)
                    tab.setMaximumWidth(TabViewConfig.TAB_MAX_WIDTH)
                else:
                    tab.setFixedWidth(TabViewConfig.TAB_MIN_WIDTH)
                    
    def _check_scroll_buttons(self) -> None:
        container_width = self._tabs_container.sizeHint().width()
        scroll_width = self._scroll_area.width()
        
        if container_width > scroll_width:
            self._left_scroll_btn.show()
            self._right_scroll_btn.show()
        else:
            self._left_scroll_btn.hide()
            self._right_scroll_btn.hide()
            
    def _scroll_left(self) -> None:
        scroll_bar = self._scroll_area.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.value() - 100)
        
    def _scroll_right(self) -> None:
        scroll_bar = self._scroll_area.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.value() + 100)
        
    def _ensure_tab_visible(self, index: int) -> None:
        if 0 <= index < len(self._tabs):
            tab = self._tabs[index]
            self._scroll_area.ensureWidgetVisible(tab)
            
    def setAddButtonVisible(self, visible: bool) -> None:
        self._show_add_button = visible
        self._add_button.setVisible(visible)
        
    def setCanReorder(self, can_reorder: bool) -> None:
        self._can_reorder = can_reorder
        
    def setTabWidthMode(self, mode: str) -> None:
        self._tab_width_mode = mode
        self._update_tab_widths()
        
    def setLeftHeader(self, widget: QWidget) -> None:
        if self._left_header:
            self._main_layout.removeWidget(self._left_header)
            
        self._left_header = widget
        self._main_layout.insertWidget(0, widget)
        
    def setRightHeader(self, widget: QWidget) -> None:
        if self._right_header:
            self._main_layout.removeWidget(self._right_header)
            
        self._right_header = widget
        self._main_layout.addWidget(widget)
        
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_tab_widths()
        self._check_scroll_buttons()
        
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Left:
            if self._selected_index > 0:
                self.setSelectedIndex(self._selected_index - 1)
        elif event.key() == Qt.Key.Key_Right:
            if self._selected_index < len(self._tabs) - 1:
                self.setSelectedIndex(self._selected_index + 1)
        elif event.key() == Qt.Key.Key_Home:
            if self._tabs:
                self.setSelectedIndex(0)
        elif event.key() == Qt.Key.Key_End:
            if self._tabs:
                self.setSelectedIndex(len(self._tabs) - 1)
        else:
            super().keyPressEvent(event)
