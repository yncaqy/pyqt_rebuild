"""
Custom TableWidget Component

Provides a table widget with theme support, similar to QTableWidget.

Features:
- Full QTableWidget API compatibility
- Theme integration
- Custom header styling
- Hover and selection effects
- Custom item delegate for painting
- Editable cells support
"""

import logging
from typing import Optional, List, Any
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QModelIndex, pyqtSignal, QAbstractTableModel
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem, QScrollBar
)
from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class TableConfig:
    """Configuration constants for table widget."""
    
    ROW_HEIGHT = 36
    HEADER_HEIGHT = 40
    CELL_PADDING = 8
    BORDER_RADIUS = 4


class TableItemDelegate(QStyledItemDelegate):
    """Custom delegate for painting table cells with theme support."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(0, TableConfig.ROW_HEIGHT)
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver
        
        if self._theme:
            bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
            if is_selected:
                bg_color = self._theme.get_color('primary.main', QColor(0, 120, 212))
                text_color = QColor(255, 255, 255)
            elif is_hovered:
                bg_color = self._theme.get_color('button.background.hover', QColor(55, 55, 55))
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            else:
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            
            grid_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        else:
            bg_color = QColor(45, 45, 45)
            if is_selected:
                bg_color = QColor(0, 120, 212)
                text_color = QColor(255, 255, 255)
            elif is_hovered:
                bg_color = QColor(55, 55, 55)
                text_color = QColor(200, 200, 200)
            else:
                text_color = QColor(200, 200, 200)
            grid_color = QColor(60, 60, 60)
        
        painter.fillRect(rect, bg_color)
        
        painter.setPen(QPen(grid_color, 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomRight())
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(QPen(text_color))
            font = QFont("Arial", 10)
            painter.setFont(font)
            
            text_rect = rect.adjusted(TableConfig.CELL_PADDING, 0, -TableConfig.CELL_PADDING, 0)
            
            alignment = index.data(Qt.ItemDataRole.TextAlignmentRole)
            if alignment is None:
                alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            
            painter.drawText(text_rect, alignment, str(text))
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            icon_size = 20
            icon_rect = QRect(rect.left() + 8, rect.top() + (rect.height() - icon_size) // 2, icon_size, icon_size)
            painter.drawPixmap(icon_rect, icon.pixmap(icon_size, icon_size))
        
        painter.restore()
    
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        from PyQt6.QtWidgets import QLineEdit
        editor = QLineEdit(parent)
        editor.setText(str(index.data(Qt.ItemDataRole.DisplayRole) or ""))
        editor.setFixedHeight(TableConfig.ROW_HEIGHT - 4)
        
        if self._theme:
            bg_color = self._theme.get_color('input.background.normal', QColor(50, 50, 50))
            text_color = self._theme.get_color('input.text.normal', QColor(200, 200, 200))
            border_focus = self._theme.get_color('input.border.focus', QColor(52, 152, 219))
            
            editor.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {bg_color.name()};
                    color: {text_color.name()};
                    border: 2px solid {border_focus.name()};
                    border-radius: 2px;
                    padding: 0px 6px;
                }}
            """)
        
        return editor
    
    def setModelData(self, editor: QWidget, model: QAbstractTableModel, index: QModelIndex) -> None:
        model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class CustomTableHeaderView(QHeaderView):
    """Custom horizontal header view with theme support."""
    
    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setFixedHeight(TableConfig.HEADER_HEIGHT)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self._apply_theme()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        if not self._theme:
            return
        
        bg_color = self._theme.get_color('groupbox.background', QColor(50, 50, 50))
        text_color = self._theme.get_color('label.text.title', QColor(255, 255, 255))
        border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        
        self.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: none;
                border-bottom: 1px solid {border_color.name()};
                border-right: 1px solid {border_color.name()};
                padding: 0 {TableConfig.CELL_PADDING}px;
                font-weight: bold;
            }}
            QHeaderView {{
                background-color: {bg_color.name()};
                border: none;
            }}
        """)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class CustomTableWidgetItem(QTableWidgetItem):
    """Custom table widget item with theme support."""
    
    def __init__(self, text: str = "", icon: Optional[QIcon] = None):
        super().__init__(text)
        self._icon = icon
        
        if icon:
            self.setIcon(icon)
    
    def setIcon(self, icon: QIcon) -> None:
        self._icon = icon
        super().setIcon(icon)


class CustomTableWidget(QTableWidget):
    """Custom table widget with theme support, similar to QTableWidget."""
    
    def __init__(self, rows: int = 0, columns: int = 0, parent: Optional[QWidget] = None):
        super().__init__(rows, columns, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._delegate: Optional[TableItemDelegate] = None
        self._header_view: Optional[CustomTableHeaderView] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("CustomTableWidget initialized")
    
    def _setup_ui(self) -> None:
        self._delegate = TableItemDelegate(self)
        self.setItemDelegate(self._delegate)
        
        self._header_view = CustomTableHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self._header_view)
        
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setShowGrid(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        self._v_scroll_bar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._v_scroll_bar)
        
        self._h_scroll_bar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        self.setHorizontalScrollBar(self._h_scroll_bar)
        
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
            QTableWidget {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                outline: none;
            }}
            QTableWidget::item {{
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: transparent;
            }}
        """)
    
    def setHorizontalHeaderLabels(self, labels: List[str]) -> None:
        super().setHorizontalHeaderLabels(labels)
    
    def setItem(self, row: int, column: int, item: QTableWidgetItem) -> None:
        super().setItem(row, column, item)
    
    def item(self, row: int, column: int) -> Optional[QTableWidgetItem]:
        return super().item(row, column)
    
    def setRowCount(self, rows: int) -> None:
        super().setRowCount(rows)
    
    def setColumnCount(self, columns: int) -> None:
        super().setColumnCount(columns)
    
    def rowCount(self) -> int:
        return super().rowCount()
    
    def columnCount(self) -> int:
        return super().columnCount()
    
    def clear(self) -> None:
        super().clear()
    
    def clearContents(self) -> None:
        super().clearContents()
    
    def resizeColumnsToContents(self) -> None:
        super().resizeColumnsToContents()
    
    def resizeRowsToContents(self) -> None:
        super().resizeRowsToContents()
    
    def setColumnWidth(self, column: int, width: int) -> None:
        super().setColumnWidth(column, width)
    
    def setRowHeight(self, row: int, height: int) -> None:
        super().setRowHeight(row, height)
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        if self._header_view:
            self._header_view.cleanup()
        logger.debug("CustomTableWidget cleaned up")
