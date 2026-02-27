"""
Custom ListWidget Component

Provides a list widget with theme support, similar to QListWidget.

Features:
- Single and multi-selection modes
- Theme integration
- Hover and selection effects
- Custom item styling
- Full QListWidget API compatibility
"""

import logging
from typing import Optional, List, Any
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QObject, QEvent, 
    QPropertyAnimation, QEasingCurve, pyqtProperty,
    QRectF, QSize, pyqtSignal
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QFontMetrics, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QFrame, QAbstractItemView,
    QListWidget, QListWidgetItem, QStyledItemDelegate,
    QStyle, QStyleOptionViewItem
)
from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class ListWidgetConfig:
    """Configuration constants for list widget."""
    
    ITEM_HEIGHT = 36
    ITEM_PADDING = 8
    ITEM_BORDER_RADIUS = 4
    ICON_SIZE = 20
    ICON_MARGIN = 8
    TEXT_MARGIN = 8


class CustomListWidgetItem:
    """Custom list widget item with theme support."""
    
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
        return self._text
    
    def setText(self, text: str) -> None:
        self._text = text
        self._update_widget()
    
    def icon(self) -> Optional[QIcon]:
        return self._icon
    
    def setIcon(self, icon: QIcon) -> None:
        self._icon = icon
        self._update_widget()
    
    def data(self, role: int = Qt.ItemDataRole.UserRole) -> Any:
        return self._data
    
    def setData(self, role: int, value: Any) -> None:
        self._data = value
    
    def isSelected(self) -> bool:
        return self._selected
    
    def setSelected(self, selected: bool) -> None:
        self._selected = selected
        self._update_widget()
    
    def setFlags(self, flags: Qt.ItemFlag) -> None:
        self._flags = flags
    
    def flags(self) -> Qt.ItemFlag:
        return self._flags
    
    def _set_hovered(self, hovered: bool) -> None:
        self._hovered = hovered
        self._update_widget()
    
    def _set_widget(self, widget: QWidget) -> None:
        self._widget = widget
    
    def _set_row(self, row: int) -> None:
        self._row = row
    
    def _update_widget(self) -> None:
        if self._widget:
            self._widget.update()


class ListItemWidget(QWidget):
    """Widget for displaying a single list item."""
    
    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    
    def __init__(self, item: CustomListWidgetItem, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._item = item
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        self.setFixedHeight(ListWidgetConfig.ITEM_HEIGHT)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        item._set_widget(self)
    
    def _setup_ui(self) -> None:
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
        
        self._text_label = QLabel(self._item.text())
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self._layout.addWidget(self._icon_label)
        self._layout.addWidget(self._text_label, 1)
    
    def _update_icon(self) -> None:
        icon = self._item.icon()
        if icon and not icon.isNull():
            self._icon_label.setPixmap(icon.pixmap(ListWidgetConfig.ICON_SIZE, ListWidgetConfig.ICON_SIZE))
            self._icon_label.show()
        else:
            self._icon_label.hide()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()
    
    def item(self) -> CustomListWidgetItem:
        return self._item
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._item._row)
    
    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self._item._row)
    
    def enterEvent(self, event) -> None:
        self._item._set_hovered(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        self._item._set_hovered(False)
        super().leaveEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = ListWidgetConfig.ITEM_BORDER_RADIUS
        
        if self._theme:
            if self._item.isSelected():
                bg_color = self._theme.get_color('primary.main', QColor(0, 120, 212))
                text_color = QColor(255, 255, 255)
            elif self._item._hovered:
                bg_color = self._theme.get_color('button.background.hover', QColor(60, 60, 60))
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            else:
                bg_color = QColor(0, 0, 0, 0)
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
        else:
            if self._item.isSelected():
                bg_color = QColor(0, 120, 212)
                text_color = QColor(255, 255, 255)
            elif self._item._hovered:
                bg_color = QColor(60, 60, 60)
                text_color = QColor(200, 200, 200)
            else:
                bg_color = QColor(0, 0, 0, 0)
                text_color = QColor(200, 200, 200)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(rect), radius, radius)
        
        self._text_label.setStyleSheet(f"color: {text_color.name()}; background: transparent;")
        
        painter.end()
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class CustomListWidget(QWidget):
    """Custom list widget with theme support, similar to QListWidget."""
    
    currentItemChanged = pyqtSignal(object, object)
    itemClicked = pyqtSignal(object)
    itemDoubleClicked = pyqtSignal(object)
    itemSelectionChanged = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items: List[CustomListWidgetItem] = []
        self._current_item: Optional[CustomListWidgetItem] = None
        self._selected_items: List[CustomListWidgetItem] = []
        self._selection_mode = QAbstractItemView.SelectionMode.SingleSelection
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("CustomListWidget initialized")
    
    def _setup_ui(self) -> None:
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
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(4, 4, 4, 4)
        self._container_layout.setSpacing(2)
        self._container_layout.addStretch()
        
        self._scroll_area.setWidget(self._container)
        self._main_layout.addWidget(self._scroll_area)
        
        self._apply_theme()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        if not self._theme:
            return
        
        bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
        border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        
        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
            }}
            QWidget#container {{
                background-color: transparent;
            }}
        """)
        
        self._container.setStyleSheet("background-color: transparent;")
    
    def addItem(self, item: CustomListWidgetItem) -> None:
        self.insertItem(self.count(), item)
    
    def addItems(self, texts: List[str]) -> None:
        for text in texts:
            self.addItem(CustomListWidgetItem(text))
    
    def insertItem(self, row: int, item: CustomListWidgetItem) -> None:
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
        return len(self._items)
    
    def item(self, row: int) -> Optional[CustomListWidgetItem]:
        if row < 0 or row >= self.count():
            return None
        return self._items[row]
    
    def itemAt(self, pos) -> Optional[CustomListWidgetItem]:
        """Get item at position (supports QPoint and x, y coordinates).
        
        Args:
            pos: QPoint or (x, y) tuple for position relative to widget
            
        Returns:
            CustomListWidgetItem at position, or None if no item at that position
        """
        from PyQt6.QtCore import QPoint
        
        if isinstance(pos, QPoint):
            x, y = pos.x(), pos.y()
        elif isinstance(pos, tuple) and len(pos) == 2:
            x, y = pos
        else:
            return None
        
        # Iterate through item widgets to find which one contains the point
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
        return self._current_item
    
    def setCurrentItem(self, item: CustomListWidgetItem) -> None:
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
        
        self.currentItemChanged.emit(item, old_item)
        self.itemSelectionChanged.emit()
    
    def setCurrentRow(self, row: int) -> None:
        item = self.item(row)
        if item:
            self.setCurrentItem(item)
    
    def currentRow(self) -> int:
        if self._current_item:
            return self._current_item._row
        return -1
    
    def selectedItems(self) -> List[CustomListWidgetItem]:
        return self._selected_items.copy()
    
    def selectedRows(self) -> List[int]:
        return [item._row for item in self._selected_items]
    
    def clear(self) -> None:
        for i in range(self._container_layout.count() - 1):
            widget = self._container_layout.itemAt(0).widget()
            if widget:
                widget.cleanup()
                widget.deleteLater()
        
        self._items.clear()
        self._current_item = None
        self._selected_items.clear()
    
    def setSelectionMode(self, mode: QAbstractItemView.SelectionMode) -> None:
        self._selection_mode = mode
        
        if mode == QAbstractItemView.SelectionMode.SingleSelection:
            while len(self._selected_items) > 1:
                item = self._selected_items.pop(0)
                item.setSelected(False)
    
    def selectionMode(self) -> QAbstractItemView.SelectionMode:
        return self._selection_mode
    
    def scrollToItem(self, item: CustomListWidgetItem) -> None:
        if item._row >= 0 and item._row < self._container_layout.count() - 1:
            widget = self._container_layout.itemAt(item._row).widget()
            if widget:
                self._scroll_area.ensureWidgetVisible(widget)
    
    def _on_item_clicked(self, row: int) -> None:
        item = self.item(row)
        if not item:
            return
        
        if self._selection_mode == QAbstractItemView.SelectionMode.MultiSelection:
            if item.isSelected():
                item.setSelected(False)
                if item in self._selected_items:
                    self._selected_items.remove(item)
            else:
                item.setSelected(True)
                self._selected_items.append(item)
        elif self._selection_mode == QAbstractItemView.SelectionMode.ExtendedSelection:
            pass
        else:
            self.setCurrentItem(item)
        
        self._current_item = item
        self.itemClicked.emit(item)
    
    def _on_item_double_clicked(self, row: int) -> None:
        item = self.item(row)
        if item:
            self.itemDoubleClicked.emit(item)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        
        for i in range(self._container_layout.count() - 1):
            widget = self._container_layout.itemAt(i).widget()
            if widget and isinstance(widget, ListItemWidget):
                widget.cleanup()
        
        logger.debug("CustomListWidget cleaned up")
