"""
Custom TableWidget Component

Provides a table widget with theme support, following WinUI3 design.
"""

import logging
from typing import Optional, List, Any, Tuple
from PyQt6.QtCore import Qt, QRect, QSize, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QIcon, QBrush, QPalette
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem
)
from core.themed_component_base import ThemedDelegateBase
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_manager import ThemeManager
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class TableConfig:
    """Configuration constants for table widget."""
    
    ROW_HEIGHT = 36
    HEADER_HEIGHT = 40
    CELL_PADDING = 12
    ICON_SIZE = 16


class TableItemDelegate(QStyledItemDelegate):
    """Custom delegate for painting table cells."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        if self.parent():
            self.parent().viewport().update()
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(0, TableConfig.ROW_HEIGHT)
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver
        
        is_dark = False
        if self._current_theme:
            is_dark = getattr(self._current_theme, 'is_dark', False)
        
        if is_selected:
            if is_dark:
                bg_color = QColor(255, 255, 255, 12)
            else:
                bg_color = QColor(0, 0, 0, 12)
        elif is_hovered:
            if is_dark:
                bg_color = QColor(255, 255, 255, 6)
            else:
                bg_color = QColor(0, 0, 0, 6)
        else:
            bg_color = QColor(0, 0, 0, 0)
        
        if is_dark:
            text_color = QColor(230, 230, 230)
            grid_color = QColor(255, 255, 255, 12)
        else:
            text_color = QColor(30, 30, 30)
            grid_color = QColor(0, 0, 0, 12)
        
        painter.fillRect(rect, bg_color)
        
        painter.setPen(QPen(grid_color, 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(QPen(text_color))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            
            text_rect = rect.adjusted(TableConfig.CELL_PADDING, 0, -TableConfig.CELL_PADDING, 0)
            
            alignment = index.data(Qt.ItemDataRole.TextAlignmentRole)
            if alignment is None:
                alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            
            painter.drawText(text_rect, alignment, str(text))
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            icon_size = TableConfig.ICON_SIZE
            icon_rect = QRect(
                rect.left() + TableConfig.CELL_PADDING, 
                rect.top() + (rect.height() - icon_size) // 2, 
                icon_size, 
                icon_size
            )
            painter.drawPixmap(icon_rect, icon.pixmap(icon_size, icon_size))
        
        painter.restore()
    
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        from PyQt6.QtWidgets import QLineEdit
        editor = QLineEdit(parent)
        editor.setText(str(index.data(Qt.ItemDataRole.DisplayRole) or ""))
        editor.setFixedHeight(TableConfig.ROW_HEIGHT - 6)
        
        is_dark = False
        if self._current_theme:
            is_dark = getattr(self._current_theme, 'is_dark', False)
        
        if is_dark:
            bg_color = QColor(45, 45, 45)
            border_color = QColor(255, 255, 255, 30)
            text_color = QColor(230, 230, 230)
        else:
            bg_color = QColor(255, 255, 255)
            border_color = QColor(0, 0, 0, 30)
            text_color = QColor(30, 30, 30)
        
        editor.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                border: 1px solid {border_color.name(QColor.NameFormat.HexArgb)};
                border-radius: 4px;
                padding: 0px 8px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }}
        """)
        
        return editor
    
    def setModelData(self, editor: QWidget, model: QAbstractTableModel, index: QModelIndex) -> None:
        model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
    
    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)


class CustomTableHeaderView(QHeaderView):
    """Custom horizontal header view with theme support."""
    
    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
        self.setFixedHeight(TableConfig.HEADER_HEIGHT)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setSectionsClickable(False)
        self.setHighlightSections(False)
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self._apply_theme()
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        is_dark = False
        if self._current_theme:
            is_dark = getattr(self._current_theme, 'is_dark', False)
        
        if is_dark:
            bg_color = QColor(255, 255, 255, 4)
            text_color = QColor(180, 180, 180)
            border_color = QColor(255, 255, 255, 12)
        else:
            bg_color = QColor(0, 0, 0, 4)
            text_color = QColor(100, 100, 100)
            border_color = QColor(0, 0, 0, 12)
        
        self.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                color: {text_color.name(QColor.NameFormat.HexArgb)};
                border: none;
                border-bottom: 1px solid {border_color.name(QColor.NameFormat.HexArgb)};
                padding: 0 {TableConfig.CELL_PADDING}px;
                font-family: 'Segoe UI';
                font-size: 10pt;
                font-weight: 600;
            }}
            QHeaderView {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border: none;
            }}
        """)
    
    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)


class CustomTableWidgetItem(QTableWidgetItem):
    """Custom table widget item."""
    
    def __init__(self, text: str = "", icon: Optional[QIcon] = None):
        super().__init__(text)
        self._icon = icon
        
        if icon:
            self.setIcon(icon)
    
    def setIcon(self, icon: QIcon) -> None:
        self._icon = icon
        super().setIcon(icon)


class CustomTableWidget(QTableWidget):
    """
    Custom table widget with theme support, following WinUI3 design.
    """
    
    def __init__(self, rows: int = 0, columns: int = 0, parent: Optional[QWidget] = None):
        super().__init__(rows, columns, parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        self._delegate: Optional[TableItemDelegate] = None
        self._header_view: Optional[CustomTableHeaderView] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("CustomTableWidget initialized")
    
    def _setup_ui(self) -> None:
        self._delegate = TableItemDelegate(self)
        self.setItemDelegate(self._delegate)
        
        self._header_view = CustomTableHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self._header_view)
        
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(TableConfig.ROW_HEIGHT)
        self.verticalHeader().setMinimumSectionSize(TableConfig.ROW_HEIGHT)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setShowGrid(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self._v_scroll_bar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._v_scroll_bar)
        
        self._h_scroll_bar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        self.setHorizontalScrollBar(self._h_scroll_bar)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.viewport().setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        
        self._apply_theme()
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        is_dark = False
        if self._current_theme:
            is_dark = getattr(self._current_theme, 'is_dark', False)
        
        if is_dark:
            bg_color = QColor(32, 32, 32)
            border_color = QColor(255, 255, 255, 15)
            highlight_color = QColor(255, 255, 255, 12)
            highlighted_text_color = QColor(230, 230, 230)
        else:
            bg_color = QColor(252, 252, 252)
            border_color = QColor(0, 0, 0, 15)
            highlight_color = QColor(0, 0, 0, 12)
            highlighted_text_color = QColor(30, 30, 30)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, highlighted_text_color)
        self.setPalette(palette)
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border: 1px solid {border_color.name(QColor.NameFormat.HexArgb)};
                border-radius: 8px;
                outline: none;
                padding: 0px;
                margin: 0px;
            }}
            QTableWidget::item {{
                border: none;
                background-color: transparent;
            }}
            QTableWidget QTableCornerButton::section {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border: none;
            }}
            QTableWidget QAbstractScrollArea {{
                padding: 0px;
                margin: 0px;
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
        self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        if self._header_view:
            self._header_view.cleanup()
        logger.debug("CustomTableWidget cleaned up")
