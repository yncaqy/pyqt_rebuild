"""
Custom TreeWidget Component

Provides a tree widget with theme support, similar to QTreeWidget.

Features:
- Full QTreeWidget API compatibility
- Theme integration
- Custom item styling
- Hover and selection effects
- Expandable/collapsible items
- Custom scroll bars
"""

import logging
from typing import Optional, List, Any
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QModelIndex, pyqtSignal, QPointF, QByteArray
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QPolygonF, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem, QHeaderView
)
from PyQt6.QtSvg import QSvgRenderer
from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


COLLAPSED_SVG = """<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M230.4 0h435.2c71.68 0 128 56.32 128 128v768c0 71.68-56.32 128-128 128H230.4V0z" fill="BG_COLOR"/>
    <path d="M432.64 734.72l209.92-202.24c10.24-10.24 10.24-28.16 0-38.4l-212.48-202.24c-12.8-10.24-30.72-10.24-40.96 0-10.24 10.24-10.24 28.16 0 38.4l192 184.32-192 181.76c-10.24 10.24-10.24 28.16 0 38.4 15.36 10.24 33.28 10.24 43.52 0z" fill="ARROW_COLOR"/>
</svg>"""

EXPANDED_SVG = """<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M230.4 0h435.2c71.68 0 128 56.32 128 128v768c0 71.68-56.32 128-128 128H230.4V0z" fill="BG_COLOR"/>
    <path d="M734.72 432.64l-202.24 209.92c-10.24 10.24-28.16 10.24-38.4 0l-202.24-212.48c-10.24-12.8-10.24-30.72 0-40.96 10.24-10.24 28.16-10.24 38.4 0l184.32 192 181.76-192c10.24-10.24 28.16-10.24 38.4 0 10.24 15.36 10.24 33.28 0 43.52z" fill="ARROW_COLOR"/>
</svg>"""


class TreeConfig:
    """Configuration constants for tree widget."""
    
    ITEM_HEIGHT = 32
    INDENTATION = 24
    BRANCH_WIDTH = 20
    BORDER_RADIUS = 4


class TreeItemDelegate(QStyledItemDelegate):
    """Custom delegate for painting tree items with theme support."""
    
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
        return QSize(0, TreeConfig.ITEM_HEIGHT)
    
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
        
        item_rect = QRectF(rect.x() + 4, rect.y() + 2, rect.width() - 8, rect.height() - 4)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(item_rect, TreeConfig.BORDER_RADIUS, TreeConfig.BORDER_RADIUS)
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(QPen(text_color))
            font = QFont("Arial", 10)
            painter.setFont(font)
            
            text_rect = rect.adjusted(TreeConfig.INDENTATION + 8, 0, -8, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            icon_size = 16
            icon_x = rect.x() + TreeConfig.INDENTATION + 8
            icon_y = rect.y() + (rect.height() - icon_size) // 2
            painter.drawPixmap(QRect(icon_x, icon_y, icon_size, icon_size), icon.pixmap(icon_size, icon_size))
        
        painter.restore()
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class CustomTreeWidgetItem(QTreeWidgetItem):
    """Custom tree widget item with theme support."""
    
    def __init__(self, parent: Optional[QTreeWidgetItem] = None, text: str = "", icon: Optional[QIcon] = None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        
        if text:
            self.setText(0, text)
        
        if icon:
            self.setIcon(0, icon)
        
        self._icon = icon
    
    def setIcon(self, column: int, icon: QIcon) -> None:
        self._icon = icon
        super().setIcon(column, icon)


class CustomTreeWidget(QTreeWidget):
    """Custom tree widget with theme support, similar to QTreeWidget."""
    
    itemClicked = pyqtSignal(QTreeWidgetItem, int)
    itemDoubleClicked = pyqtSignal(QTreeWidgetItem, int)
    itemExpanded = pyqtSignal(QTreeWidgetItem)
    itemCollapsed = pyqtSignal(QTreeWidgetItem)
    currentItemChanged = pyqtSignal(QTreeWidgetItem, QTreeWidgetItem)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._delegate: Optional[TreeItemDelegate] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("CustomTreeWidget initialized")
    
    def _setup_ui(self) -> None:
        self._delegate = TreeItemDelegate(self)
        self.setItemDelegate(self._delegate)
        
        self.setHeaderHidden(True)
        self.setIndentation(TreeConfig.INDENTATION)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        
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
        text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
        
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                outline: none;
                color: {text_color.name()};
            }}
            QTreeWidget::item {{
                border: none;
                padding: 0px;
            }}
            QTreeWidget::item:selected {{
                background-color: transparent;
            }}
            QTreeWidget::branch {{
                background-color: transparent;
            }}
            QTreeWidget::branch:selected {{
                background-color: transparent;
            }}
        """)
    
    def addTopLevelItem(self, item: QTreeWidgetItem) -> None:
        super().addTopLevelItem(item)
    
    def drawBranches(self, painter: QPainter, rect: QRect, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._theme:
            bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
        else:
            bg_color = QColor(45, 45, 45)
        
        painter.fillRect(rect, bg_color)
        
        item = self.itemFromIndex(index)
        if not item:
            painter.restore()
            return
        
        has_children = item.childCount() > 0
        is_expanded = item.isExpanded()
        
        if has_children:
            svg_data = EXPANDED_SVG if is_expanded else COLLAPSED_SVG
            
            if self._theme:
                arrow_color = self._theme.get_color('label.text.body', QColor(150, 150, 150))
            else:
                arrow_color = QColor(150, 150, 150)
            
            svg_colored = svg_data.replace('BG_COLOR', bg_color.name())
            svg_colored = svg_colored.replace('ARROW_COLOR', arrow_color.name())
            
            svg_bytes = QByteArray(svg_colored.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            if renderer.isValid():
                icon_size = 16
                icon_x = rect.x() + (rect.width() - icon_size) // 2
                icon_y = rect.y() + (rect.height() - icon_size) // 2
                
                renderer.render(painter, QRectF(icon_x, icon_y, icon_size, icon_size))
        
        painter.restore()
    
    def addTopLevelItems(self, items: List[QTreeWidgetItem]) -> None:
        super().addTopLevelItems(items)
    
    def takeTopLevelItem(self, index: int) -> Optional[QTreeWidgetItem]:
        return super().takeTopLevelItem(index)
    
    def topLevelItem(self, index: int) -> Optional[QTreeWidgetItem]:
        return super().topLevelItem(index)
    
    def topLevelItemCount(self) -> int:
        return super().topLevelItemCount()
    
    def currentItem(self) -> Optional[QTreeWidgetItem]:
        return super().currentItem()
    
    def setCurrentItem(self, item: QTreeWidgetItem) -> None:
        super().setCurrentItem(item)
    
    def selectedItems(self) -> List[QTreeWidgetItem]:
        return super().selectedItems()
    
    def expandItem(self, item: QTreeWidgetItem) -> None:
        super().expandItem(item)
    
    def collapseItem(self, item: QTreeWidgetItem) -> None:
        super().collapseItem(item)
    
    def isItemExpanded(self, item: QTreeWidgetItem) -> bool:
        return item.isExpanded()
    
    def setItemExpanded(self, item: QTreeWidgetItem, expanded: bool) -> None:
        item.setExpanded(expanded)
    
    def clear(self) -> None:
        super().clear()
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        logger.debug("CustomTreeWidget cleaned up")
