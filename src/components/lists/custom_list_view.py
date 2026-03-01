"""
自定义列表视图组件

提供带主题支持的列表视图，类似 QListView。
使用 Model-View 架构进行数据绑定。

功能特性:
- Model-View 架构支持
- 主题集成
- 悬停和选中效果
- 自定义项目委托绘制
- 完整的 QListView API 兼容性
"""

import logging
from typing import Optional
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QModelIndex, pyqtSignal
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QListView, QAbstractItemView, QStyledItemDelegate,
    QStyle, QStyleOptionViewItem
)
from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class ListViewDelegate(QStyledItemDelegate):
    """带主题支持的列表视图项目委托。"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._hovered_row = -1
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._theme = theme
    
    def set_hovered_row(self, row: int) -> None:
        """设置悬停行号。"""
        self._hovered_row = row
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """返回项目尺寸提示。"""
        return QSize(0, 36)
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """绘制项目。"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect.adjusted(4, 2, -4, -2)
        radius = 4
        
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = index.row() == self._hovered_row
        is_enabled = option.state & QStyle.StateFlag.State_Enabled
        
        if self._theme:
            if is_selected:
                bg_color = self._theme.get_color('primary.main', QColor(0, 120, 212))
                text_color = QColor(255, 255, 255)
            elif is_hovered:
                bg_color = self._theme.get_color('button.background.hover', QColor(60, 60, 60))
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            else:
                bg_color = QColor(0, 0, 0, 0)
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
        else:
            if is_selected:
                bg_color = QColor(0, 120, 212)
                text_color = QColor(255, 255, 255)
            elif is_hovered:
                bg_color = QColor(60, 60, 60)
                text_color = QColor(200, 200, 200)
            else:
                bg_color = QColor(0, 0, 0, 0)
                text_color = QColor(200, 200, 200)
        
        if bg_color.alpha() > 0:
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(rect), radius, radius)
        
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(QPen(text_color))
            font = QFont("Arial", 10)
            painter.setFont(font)
            
            text_rect = rect.adjusted(12, 0, -12, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            icon_size = 20
            icon_rect = QRect(rect.left() + 8, rect.top() + (rect.height() - icon_size) // 2, icon_size, icon_size)
            painter.drawPixmap(icon_rect, icon.pixmap(icon_size, icon_size))
        
        painter.restore()
    
    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class CustomListView(QListView):
    """
    带主题支持的自定义列表视图，类似 QListView。
    
    功能特性:
    - Model-View 架构支持
    - 主题集成
    - 悬停和选中效果
    - 自定义项目委托绘制
    
    使用示例:
        from PyQt6.QtCore import QStringListModel
        
        list_view = CustomListView()
        model = QStringListModel(["项目 1", "项目 2", "项目 3"])
        list_view.setModel(model)
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._delegate: Optional[ListViewDelegate] = None
        self._hovered_index = QModelIndex()
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setMouseTracking(True)
        
        logger.debug("CustomListView initialized")
    
    def _setup_ui(self) -> None:
        """初始化 UI 布局。"""
        self._delegate = ListViewDelegate(self)
        self.setItemDelegate(self._delegate)
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        self._custom_scroll_bar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._custom_scroll_bar)
        
        self._apply_theme()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """应用主题样式。"""
        if not self._theme:
            return
        
        bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
        border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        
        self.setStyleSheet(f"""
            QListView {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                outline: none;
            }}
            QListView::item {{
                background: transparent;
                border: none;
            }}
        """)
    
    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件处理。"""
        index = self.indexAt(event.pos())
        if index != self._hovered_index:
            self._hovered_index = index
            if self._delegate:
                self._delegate.set_hovered_row(index.row() if index.isValid() else -1)
            self.viewport().update()
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件处理。"""
        self._hovered_index = QModelIndex()
        if self._delegate:
            self._delegate.set_hovered_row(-1)
        self.viewport().update()
        super().leaveEvent(event)
    
    def cleanup(self) -> None:
        """清理资源。"""
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        logger.debug("CustomListView cleaned up")
