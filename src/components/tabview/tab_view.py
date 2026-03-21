"""
TabView 主组件

严格遵循 WinUI3 TabView 设计规范。
参考: https://learn.microsoft.com/zh-cn/windows/apps/design/controls/tab-view
"""

import logging
from typing import Optional, List, Union
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QSizePolicy, QLabel
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize
)
from PyQt6.QtGui import QIcon, QKeyEvent

from .config import TabViewConfig, TabViewWidthMode, TabViewCloseButtonOverlayMode
from .styles import TabViewStyle
from .tab_view_item import TabViewItem
from .tab_view_tab_strip import TabViewTabStrip
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class TabView(QWidget):
    """
    TabView 主控件。
    
    WinUI3 TabView 设计规范:
    - TabStrip: 标签条，包含所有 TabViewItem
    - Content: 内容区域，显示选中标签的内容
    - LeftHeader: 左侧头部区域
    - RightHeader: 右侧头部区域
    - AddTabButton: 添加标签按钮
    - 支持键盘导航: Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+F4
    - 支持拖拽重排
    - 支持标签撕裂（Tab Tear-out）
    """
    
    currentChanged = pyqtSignal(object)
    tabCloseRequested = pyqtSignal(int)
    tabReordered = pyqtSignal(int, int)
    addTabRequested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._tab_width_mode = TabViewWidthMode.EQUAL
        self._close_button_overlay_mode = TabViewCloseButtonOverlayMode.AUTO
        self._show_add_button = True
        self._can_reorder = True
        self._key_to_index: dict = {}
        self._index_to_key: dict = {}
        self._theme_mgr = ThemeManager.instance()
        self._cleanup_done = False
        
        super().__init__(parent)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        self._connect_signals()
        self._subscribe_theme()
        
    def _subscribe_theme(self) -> None:
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_destroyed)
        
    def _on_theme_changed(self, theme: Theme) -> None:
        self.update()
        
    def _on_destroyed(self) -> None:
        if not self._cleanup_done:
            try:
                self._theme_mgr.unsubscribe(self)
            except Exception as e:
                logger.debug(f"取消主题订阅时出错: {e}")
            self._cleanup_done = True
        
    def _init_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._tab_strip = TabViewTabStrip(self)
        self._tab_strip.setAddButtonVisible(self._show_add_button)
        self._tab_strip.setCanReorder(self._can_reorder)
        self._main_layout.addWidget(self._tab_strip)
        
        self._content_area = QStackedWidget()
        self._content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self._main_layout.addWidget(self._content_area, 1)
        
    def _connect_signals(self) -> None:
        self._tab_strip.tabClicked.connect(self._on_tab_clicked)
        self._tab_strip.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tab_strip.tabReordered.connect(self._on_tab_reordered)
        self._tab_strip.addTabClicked.connect(self._on_add_tab_clicked)
        
    def _on_tab_clicked(self, index: int) -> None:
        self._content_area.setCurrentIndex(index)
        key = self._index_to_key.get(index)
        self.currentChanged.emit(key if key is not None else index)
        
    def _on_tab_close_requested(self, index: int) -> None:
        self.tabCloseRequested.emit(index)
        
    def _on_tab_reordered(self, from_index: int, to_index: int) -> None:
        widget = self._content_area.widget(from_index)
        if widget:
            self._content_area.removeWidget(widget)
            self._content_area.insertWidget(to_index, widget)
            
        self._rebuild_key_mappings()
        self.tabReordered.emit(from_index, to_index)
        
    def _on_add_tab_clicked(self) -> None:
        self.addTabRequested.emit()
        
    def _rebuild_key_mappings(self) -> None:
        self._key_to_index.clear()
        self._index_to_key.clear()
        for i in range(self._tab_strip.tabCount()):
            tab = self._tab_strip.tabAt(i)
            if tab:
                key = tab.key()
                self._key_to_index[key] = i
                self._index_to_key[i] = key
        
    def addTab(
        self, 
        header_or_content, 
        key_or_header: Optional[str] = None,
        key: Optional[str] = None,
        *,
        closable: bool = True,
        icon: Optional[QIcon] = None,
        content: Optional[QWidget] = None
    ) -> int:
        if isinstance(header_or_content, QWidget):
            content = header_or_content
            header = key_or_header
            final_key = key
        else:
            header = header_or_content
            final_key = key_or_header
            
        index = self._tab_strip.addTab(header, final_key, closable, icon)
        
        if final_key:
            self._key_to_index[final_key] = index
            self._index_to_key[index] = final_key
            
        if content is None:
            content = QLabel(f"{header} 内容")
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        self._content_area.addWidget(content)
        
        if self._tab_strip.tabCount() == 1:
            self._content_area.setCurrentIndex(0)
            
        return index
        
    def insertTab(
        self, 
        index: int, 
        header: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None,
        content: Optional[QWidget] = None
    ) -> int:
        actual_index = self._tab_strip.insertTab(index, header, key, closable, icon)
        
        self._rebuild_key_mappings()
        
        if content is None:
            content = QLabel(f"{header} 内容")
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        self._content_area.insertWidget(actual_index, content)
        
        return actual_index
        
    def removeTab(self, index_or_key: Union[int, str]) -> None:
        if isinstance(index_or_key, str):
            index = self._key_to_index.get(index_or_key, -1)
            if index == -1:
                return
        else:
            index = index_or_key
            
        key = self._index_to_key.get(index)
        if key:
            del self._key_to_index[key]
            
        widget = self._content_area.widget(index)
        if widget:
            self._content_area.removeWidget(widget)
            widget.deleteLater()
            
        self._tab_strip.removeTab(index)
        self._rebuild_key_mappings()
        
    def tab(self, key_or_index: Union[str, int]) -> Optional[TabViewItem]:
        if isinstance(key_or_index, str):
            index = self._key_to_index.get(key_or_index, -1)
            if index == -1:
                return None
            return self._tab_strip.tabAt(index)
        else:
            return self._tab_strip.tabAt(key_or_index)
        
    def currentKey(self) -> Optional[str]:
        index = self._tab_strip.selectedIndex()
        return self._index_to_key.get(index)
        
    def count(self) -> int:
        return self._tab_strip.tabCount()
        
    def setCurrentIndex(self, index: int) -> None:
        self._tab_strip.setSelectedIndex(index)
        self._content_area.setCurrentIndex(index)
        
    def currentIndex(self) -> int:
        return self._tab_strip.selectedIndex()
        
    def setCurrentWidget(self, widget: QWidget) -> None:
        index = self._content_area.indexOf(widget)
        if index >= 0:
            self.setCurrentIndex(index)
            
    def currentWidget(self) -> Optional[QWidget]:
        return self._content_area.currentWidget()
        
    def tabCount(self) -> int:
        return self._tab_strip.tabCount()
        
    def tabAt(self, index: int) -> Optional[TabViewItem]:
        return self._tab_strip.tabAt(index)
        
    def contentAt(self, index: int) -> Optional[QWidget]:
        return self._content_area.widget(index)
        
    def setContentAt(self, index: int, widget: QWidget) -> None:
        old_widget = self._content_area.widget(index)
        if old_widget:
            self._content_area.removeWidget(old_widget)
            old_widget.deleteLater()
            
        self._content_area.insertWidget(index, widget)
        
    def setTabWidthMode(self, mode: str) -> None:
        self._tab_width_mode = mode
        self._tab_strip.setTabWidthMode(mode)
        
    def tabWidthMode(self) -> str:
        return self._tab_width_mode
        
    def setCloseButtonOverlayMode(self, mode: str) -> None:
        self._close_button_overlay_mode = mode
        
    def closeButtonOverlayMode(self) -> str:
        return self._close_button_overlay_mode
        
    def setAddTabButtonVisible(self, visible: bool) -> None:
        self._show_add_button = visible
        self._tab_strip.setAddButtonVisible(visible)
        
    def isAddTabButtonVisible(self) -> bool:
        return self._show_add_button
        
    def setCanReorderTabs(self, can_reorder: bool) -> None:
        self._can_reorder = can_reorder
        self._tab_strip.setCanReorder(can_reorder)
        
    def canReorderTabs(self) -> bool:
        return self._can_reorder
        
    def setLeftHeader(self, widget: QWidget) -> None:
        self._tab_strip.setLeftHeader(widget)
        
    def setRightHeader(self, widget: QWidget) -> None:
        self._tab_strip.setRightHeader(widget)
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        modifiers = event.modifiers()
        key = event.key()
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Tab:
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    self._select_previous_tab()
                else:
                    self._select_next_tab()
            elif key == Qt.Key.Key_F4:
                index = self.currentIndex()
                if index >= 0:
                    self.tabCloseRequested.emit(index)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
            
    def _select_next_tab(self) -> None:
        count = self.tabCount()
        if count > 0:
            current = self.currentIndex()
            next_index = (current + 1) % count
            self.setCurrentIndex(next_index)
            
    def _select_previous_tab(self) -> None:
        count = self.tabCount()
        if count > 0:
            current = self.currentIndex()
            prev_index = (current - 1 + count) % count
            self.setCurrentIndex(prev_index)
            
    def sizeHint(self) -> QSize:
        return QSize(400, 300)
        
    def minimumSizeHint(self) -> QSize:
        return QSize(200, 150)


TabBar = TabView
TabWidget = TabView
