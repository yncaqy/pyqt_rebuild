"""
自定义列表组件

提供带主题支持的列表控件，类似 QListWidget。

功能特性:
- 单选和多选模式
- 主题集成
- 悬停和选中效果
- 自定义项目样式
- 选中项左侧指示器动画
- 完整的 QListWidget API 兼容性
- 统一的 ThemedComponentBase 基类
"""

import logging
from typing import Optional, List, Any, Tuple
from PyQt6.QtCore import (
    Qt, QTimer, QPoint,
    QPropertyAnimation, QEasingCurve, pyqtProperty,
    QRectF, pyqtSignal, QRect
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QFrame, QAbstractItemView
)
from core.themed_component_base import ThemedComponentBase
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class ListWidgetConfig:
    """列表控件配置常量。"""
    
    ITEM_HEIGHT = 36
    ITEM_PADDING = 8
    ITEM_BORDER_RADIUS = 4
    ICON_SIZE = 20
    ICON_MARGIN = 8
    TEXT_MARGIN = 8
    
    INDICATOR_WIDTH = 3
    INDICATOR_MARGIN = 4
    INDICATOR_ANIMATION_DURATION = 200


class ListSelectionIndicator(ThemedComponentBase):
    """
    列表选中指示器控件。
    
    在选中项左侧显示垂直指示条，支持多选模式。
    
    功能特性:
    - 支持多个选中项的指示器
    - 平滑的位置和高度动画
    - 主题感知样式
    - 圆角设计
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._indicators: List[QRect] = []
        self._animation: Optional[QPropertyAnimation] = None
        self._is_single_mode: bool = True
        
        super().__init__(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.hide()
    
    def set_single_indicator(self, rect: QRect, animate: bool = True) -> None:
        """
        设置单个指示器位置（带动画）。
        
        参数:
            rect: 指示器矩形
            animate: 是否启用动画
        """
        self._is_single_mode = True
        
        if self._indicators:
            old_rect = self._indicators[0]
            if old_rect.isEmpty():
                self._indicators = [rect]
                self.show()
                self.update()
                return
            
            if animate and old_rect != rect:
                if self._animation:
                    self._animation.stop()
                
                self._animation = QPropertyAnimation(self, b"indicatorRect")
                self._animation.setDuration(ListWidgetConfig.INDICATOR_ANIMATION_DURATION)
                self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._animation.setStartValue(old_rect)
                self._animation.setEndValue(rect)
                self._animation.start()
            else:
                self._indicators = [rect]
                self.show()
                self.update()
        else:
            self._indicators = [rect]
            self.show()
            self.update()
    
    def set_indicators(self, rects: List[QRect]) -> None:
        """
        设置指示器位置列表（多选模式）。
        
        参数:
            rects: 指示器矩形列表
        """
        self._is_single_mode = False
        if self._animation:
            self._animation.stop()
            self._animation = None
        
        self._indicators = rects
        if rects:
            self.show()
        else:
            self.hide()
        self.update()
    
    def clear_indicators(self) -> None:
        """清除所有指示器。"""
        if self._animation:
            self._animation.stop()
            self._animation = None
        self._indicators.clear()
        self.hide()
    
    def hide_indicator(self) -> None:
        """隐藏指示器。"""
        self.clear_indicators()
    
    def getIndicatorRect(self) -> QRect:
        """获取指示器矩形。"""
        if self._indicators:
            return self._indicators[0]
        return QRect()
    
    def setIndicatorRect(self, rect: QRect) -> None:
        """设置指示器矩形（动画属性）。"""
        if self._is_single_mode:
            self._indicators = [rect]
            self.update()
    
    indicatorRect = pyqtProperty(QRect, getIndicatorRect, setIndicatorRect)
    
    def paintEvent(self, event) -> None:
        """绘制事件处理。"""
        if not self._indicators:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        indicator_color = self.get_theme_color('primary.main', QColor(0, 120, 212))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(indicator_color)
        
        for rect in self._indicators:
            painter.drawRoundedRect(rect, 2, 2)
    
    def cleanup(self) -> None:
        """清理资源。"""
        if self._animation:
            self._animation.stop()
            self._animation = None
        super().cleanup()


class CustomListWidgetItem:
    """带主题支持的自定义列表项。"""
    
    def __init__(self, text: str = "", icon: Optional[QIcon] = None, data: Any = None):
        self._text = text
        self._icon = icon
        self._data = data
        self._selected = False
        self._hovered = False
        self._widget: Optional[QWidget] = None
        self._row = -1
        self._flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
    
    def text(self) -> str:
        """获取文本。"""
        return self._text
    
    def setText(self, text: str) -> None:
        """设置文本。"""
        self._text = text
        self._update_widget()
    
    def icon(self) -> Optional[QIcon]:
        """获取图标。"""
        return self._icon
    
    def setIcon(self, icon: QIcon) -> None:
        """设置图标。"""
        self._icon = icon
        self._update_widget()
    
    def data(self, role: int = Qt.ItemDataRole.UserRole) -> Any:
        """获取项目数据。"""
        return self._data
    
    def setData(self, role: int, value: Any) -> None:
        """设置项目数据。"""
        self._data = value
    
    def isSelected(self) -> bool:
        """是否选中。"""
        return self._selected
    
    def setSelected(self, selected: bool) -> None:
        """设置选中状态。"""
        self._selected = selected
        self._update_widget()
    
    def setFlags(self, flags: Qt.ItemFlag) -> None:
        """设置项目标志。"""
        self._flags = flags
    
    def flags(self) -> Qt.ItemFlag:
        """获取项目标志。"""
        return self._flags
    
    def _set_hovered(self, hovered: bool) -> None:
        """设置悬停状态（内部方法）。"""
        self._hovered = hovered
        self._update_widget()
    
    def _set_widget(self, widget: QWidget) -> None:
        """关联显示控件（内部方法）。"""
        self._widget = widget
    
    def _set_row(self, row: int) -> None:
        """设置行号（内部方法）。"""
        self._row = row
    
    def _update_widget(self) -> None:
        """更新关联的控件。"""
        if self._widget:
            self._widget.update()


class ListItemWidget(ThemedComponentBase):
    """单个列表项显示控件。"""
    
    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    
    def __init__(self, item: CustomListWidgetItem, parent: Optional[QWidget] = None):
        self._list_item = item
        
        super().__init__(parent)
        
        self._setup_ui()
        self._apply_initial_theme()
        self.setFixedHeight(ListWidgetConfig.ITEM_HEIGHT)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        item._set_widget(self)
    
    def _setup_ui(self) -> None:
        """初始化 UI 布局。"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(
            ListWidgetConfig.ITEM_PADDING,
            0,
            ListWidgetConfig.ITEM_PADDING,
            0
        )
        self._layout.setSpacing(ListWidgetConfig.ICON_MARGIN)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(ListWidgetConfig.ICON_SIZE, ListWidgetConfig.ICON_SIZE)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()
        
        self._text_label = QLabel(self._list_item.text())
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self._layout.addWidget(self._icon_label)
        self._layout.addWidget(self._text_label, 1)
    
    def _update_icon(self) -> None:
        """更新图标显示。"""
        icon = self._list_item.icon()
        if icon and not icon.isNull():
            self._icon_label.setPixmap(icon.pixmap(ListWidgetConfig.ICON_SIZE, ListWidgetConfig.ICON_SIZE))
            self._icon_label.show()
        else:
            self._icon_label.hide()
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式。"""
        self.update()
    
    def item(self) -> CustomListWidgetItem:
        """获取关联的列表项。"""
        return self._list_item
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件处理。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._list_item._row)
    
    def mouseDoubleClickEvent(self, event) -> None:
        """鼠标双击事件处理。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self._list_item._row)
    
    def enterEvent(self, event) -> None:
        """鼠标进入事件处理。"""
        self._list_item._set_hovered(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件处理。"""
        self._list_item._set_hovered(False)
        super().leaveEvent(event)
    
    def paintEvent(self, event) -> None:
        """绘制事件处理。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = ListWidgetConfig.ITEM_BORDER_RADIUS
        
        if self._list_item.isSelected():
            bg_color = QColor(0, 0, 0, 0)
            text_color = self.get_theme_color('label.text.body', QColor(200, 200, 200))
        elif self._list_item._hovered:
            bg_color = self.get_theme_color('button.background.hover', QColor(60, 60, 60))
            text_color = self.get_theme_color('label.text.body', QColor(200, 200, 200))
        else:
            bg_color = QColor(0, 0, 0, 0)
            text_color = self.get_theme_color('label.text.body', QColor(200, 200, 200))
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(rect), radius, radius)
        
        self._text_label.setStyleSheet(f"color: {text_color.name()}; background: transparent;")
        
        painter.end()


class CustomListWidget(ThemedComponentBase):
    """
    带主题支持的自定义列表控件，类似 QListWidget。
    
    功能特性:
    - 单选和多选模式
    - 主题集成
    - 悬停和选中效果
    - 自定义项目样式
    - 选中项左侧指示器动画
    
    使用示例:
        list_widget = CustomListWidget()
        list_widget.addItem(CustomListWidgetItem("项目 1"))
        list_widget.addItem(CustomListWidgetItem("项目 2"))
        
        list_widget.itemClicked.connect(lambda item: print(f"点击: {item.text()}"))
    """
    
    currentItemChanged = pyqtSignal(object, object)
    itemClicked = pyqtSignal(object)
    itemDoubleClicked = pyqtSignal(object)
    itemSelectionChanged = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._items: List[CustomListWidgetItem] = []
        self._current_item: Optional[CustomListWidgetItem] = None
        self._selected_items: List[CustomListWidgetItem] = []
        self._selection_mode = QAbstractItemView.SelectionMode.SingleSelection
        
        super().__init__(parent)
        
        self._setup_ui()
        self._apply_initial_theme()
        
        logger.debug("CustomListWidget initialized")
    
    def _setup_ui(self) -> None:
        """初始化 UI 布局。"""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self._custom_scroll_bar = CustomScrollBar(Qt.Orientation.Vertical, self._scroll_area)
        self._scroll_area.setVerticalScrollBar(self._custom_scroll_bar)
        
        self._container = QWidget()
        self._container.setObjectName("container")
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(4, 4, 4, 4)
        self._container_layout.setSpacing(2)
        self._container_layout.addStretch()
        
        self._scroll_area.setWidget(self._container)
        self._main_layout.addWidget(self._scroll_area)
        
        self._indicator = ListSelectionIndicator(self._container)
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式。"""
        bg_color = self.get_theme_color('window.background', QColor(45, 45, 45))
        border_color = self.get_theme_color('window.border', QColor(60, 60, 60))
        
        cache_key: Tuple[str, str, str] = (
            'list_widget',
            bg_color.name(),
            border_color.name()
        )
        
        def build_stylesheet() -> str:
            return f"""
                QScrollArea {{
                    background-color: {bg_color.name()};
                    border: 1px solid {border_color.name()};
                    border-radius: 4px;
                }}
                QWidget#container {{
                    background-color: transparent;
                }}
            """
        
        qss = self.get_cached_stylesheet(cache_key, build_stylesheet)
        self.setStyleSheet(qss)
        
        self._container.setStyleSheet("background-color: transparent;")
    
    def addItem(self, item: CustomListWidgetItem) -> None:
        """添加项目到列表末尾。"""
        self.insertItem(self.count(), item)
    
    def addItems(self, texts: List[str]) -> None:
        """批量添加文本项目。"""
        for text in texts:
            self.addItem(CustomListWidgetItem(text))
    
    def insertItem(self, row: int, item: CustomListWidgetItem) -> None:
        """在指定位置插入项目。"""
        row = max(0, min(row, self.count()))
        
        item._set_row(row)
        self._items.insert(row, item)
        
        for i in range(row + 1, len(self._items)):
            self._items[i]._set_row(i)
        
        widget = ListItemWidget(item, self._container)
        widget.clicked.connect(self._on_item_clicked)
        widget.doubleClicked.connect(self._on_item_double_clicked)
        
        self._container_layout.insertWidget(row, widget)
    
    def takeItem(self, row: int) -> Optional[CustomListWidgetItem]:
        """移除并返回指定行的项目。"""
        if row < 0 or row >= self.count():
            return None
        
        item = self._items.pop(row)
        
        widget = self._container_layout.itemAt(row).widget()
        if widget:
            widget.cleanup()
            widget.deleteLater()
        
        for i in range(row, len(self._items)):
            self._items[i]._set_row(i)
        
        if item == self._current_item:
            self._current_item = None
        
        if item in self._selected_items:
            self._selected_items.remove(item)
        
        return item
    
    def count(self) -> int:
        """返回项目数量。"""
        return len(self._items)
    
    def item(self, row: int) -> Optional[CustomListWidgetItem]:
        """获取指定行的项目。"""
        if row < 0 or row >= self.count():
            return None
        return self._items[row]
    
    def itemAt(self, pos) -> Optional[CustomListWidgetItem]:
        """
        获取指定位置的项目。
        
        Args:
            pos: QPoint 或 (x, y) 元组，相对于控件的位置
            
        Returns:
            该位置的 CustomListWidgetItem，如果该位置没有项目则返回 None
        """
        if isinstance(pos, QPoint):
            x, y = pos.x(), pos.y()
        elif isinstance(pos, tuple) and len(pos) == 2:
            x, y = pos
        else:
            return None
        
        for i, item in enumerate(self._items):
            widget = self._container_layout.itemAt(i)
            if widget:
                item_widget = widget.widget()
                if item_widget:
                    widget_rect = item_widget.geometry()
                    if widget_rect.contains(x, y):
                        return item
        
        return None
    
    def currentItem(self) -> Optional[CustomListWidgetItem]:
        """获取当前项目。"""
        return self._current_item
    
    def setCurrentItem(self, item: CustomListWidgetItem) -> None:
        """设置当前项目。"""
        if item not in self._items:
            return
        
        old_item = self._current_item
        
        if self._selection_mode == QAbstractItemView.SelectionMode.SingleSelection:
            for selected in self._selected_items[:]:
                selected.setSelected(False)
            self._selected_items.clear()
        
        self._current_item = item
        item.setSelected(True)
        self._selected_items.append(item)
        
        QTimer.singleShot(50, self._update_indicator)
        
        self.currentItemChanged.emit(item, old_item)
        self.itemSelectionChanged.emit()
    
    def _update_indicator(self) -> None:
        """更新选中指示器位置。"""
        if not self._selected_items:
            self._indicator.hide_indicator()
            return
        
        if self._selection_mode == QAbstractItemView.SelectionMode.SingleSelection:
            item = self._selected_items[0]
            widget = self._find_item_widget(item)
            if widget:
                rect = QRect(
                    ListWidgetConfig.INDICATOR_MARGIN,
                    widget.y() + 4,
                    ListWidgetConfig.INDICATOR_WIDTH,
                    widget.height() - 8
                )
                self._indicator.set_single_indicator(rect)
        else:
            rects = []
            for item in self._selected_items:
                widget = self._find_item_widget(item)
                if widget:
                    rect = QRect(
                        ListWidgetConfig.INDICATOR_MARGIN,
                        widget.y() + 4,
                        ListWidgetConfig.INDICATOR_WIDTH,
                        widget.height() - 8
                    )
                    rects.append(rect)
            self._indicator.set_indicators(rects)
    
    def _find_item_widget(self, item: CustomListWidgetItem) -> Optional[ListItemWidget]:
        """查找项目对应的控件。"""
        for i in range(self._container_layout.count() - 1):
            widget = self._container_layout.itemAt(i).widget()
            if isinstance(widget, ListItemWidget) and widget.item() == item:
                return widget
        return None
    
    def selectedItems(self) -> List[CustomListWidgetItem]:
        """返回选中的项目列表。"""
        return self._selected_items.copy()
    
    def setSelected(self, row: int, selected: bool) -> None:
        """设置指定行的选中状态。"""
        item = self.item(row)
        if item:
            if selected:
                self.setCurrentItem(item)
            else:
                item.setSelected(False)
                if item in self._selected_items:
                    self._selected_items.remove(item)
                self._update_indicator()
    
    def clearSelection(self) -> None:
        """清除所有选中。"""
        for item in self._selected_items:
            item.setSelected(False)
        self._selected_items.clear()
        self._current_item = None
        self._indicator.hide_indicator()
        self.itemSelectionChanged.emit()
    
    def clear(self) -> None:
        """清空列表。"""
        for i in range(self._container_layout.count() - 1):
            widget = self._container_layout.itemAt(0).widget()
            if widget:
                widget.cleanup()
                widget.deleteLater()
        
        self._items.clear()
        self._selected_items.clear()
        self._current_item = None
        self._indicator.hide_indicator()
    
    def setSelectionMode(self, mode: QAbstractItemView.SelectionMode) -> None:
        """设置选择模式。"""
        self._selection_mode = mode
        if mode == QAbstractItemView.SelectionMode.SingleSelection:
            if len(self._selected_items) > 1:
                first = self._selected_items[0]
                self.clearSelection()
                self.setCurrentItem(first)
    
    def selectionMode(self) -> QAbstractItemView.SelectionMode:
        """返回选择模式。"""
        return self._selection_mode
    
    def scrollToItem(self, item: CustomListWidgetItem) -> None:
        """滚动到指定项目。"""
        widget = self._find_item_widget(item)
        if widget:
            self._scroll_area.ensureWidgetVisible(widget)
    
    def _on_item_clicked(self, row: int) -> None:
        """项目点击处理。"""
        item = self.item(row)
        if item:
            self.setCurrentItem(item)
            self.itemClicked.emit(item)
    
    def _on_item_double_clicked(self, row: int) -> None:
        """项目双击处理。"""
        item = self.item(row)
        if item:
            self.itemDoubleClicked.emit(item)
    
    def cleanup(self) -> None:
        """清理资源。"""
        for i in range(self._container_layout.count() - 1):
            widget = self._container_layout.itemAt(i).widget()
            if widget and isinstance(widget, ListItemWidget):
                widget.cleanup()
        
        self._indicator.cleanup()
        
        super().cleanup()
        
        logger.debug("CustomListWidget cleaned up")
    
    def resizeEvent(self, event) -> None:
        """窗口大小变化时更新指示器。"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_indicator)
