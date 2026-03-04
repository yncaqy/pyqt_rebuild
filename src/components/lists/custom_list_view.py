"""
自定义列表视图组件

提供带主题支持的列表视图，类似 QListView。
使用 Model-View 架构进行数据绑定。

功能特性:
- Model-View 架构支持
- 主题集成
- 悬停和选中效果
- 自定义项目委托绘制
- 选中项左侧指示器动画
- 完整的 QListView API 兼容性
"""

import logging
from typing import Optional
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QModelIndex,
    QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QFont, QIcon
from PyQt6.QtWidgets import (
    QListView, QAbstractItemView, QStyledItemDelegate,
    QStyle, QStyleOptionViewItem, QWidget
)
from core.theme_manager import ThemeManager, Theme
from components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)


class ListViewConfig:
    """列表视图配置常量。"""
    
    ITEM_HEIGHT = 36
    ITEM_PADDING = 8
    ITEM_BORDER_RADIUS = 4
    
    INDICATOR_WIDTH = 3
    INDICATOR_MARGIN = 4
    INDICATOR_ANIMATION_DURATION = 200


class ListSelectionIndicator(QWidget):
    """
    列表选中指示器控件。
    
    在选中项左侧显示垂直指示条，支持平滑动画过渡。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._indicator_rect = QRect()
        self._animation: Optional[QPropertyAnimation] = None
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
        self.hide()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._current_theme = theme
        self.update()
    
    def animate_to(self, rect: QRect) -> None:
        """
        动画移动指示器到新位置。
        
        参数:
            rect: 目标矩形
        """
        if self._indicator_rect.isEmpty():
            self._indicator_rect = rect
            self.show()
            self.update()
            return
        
        if self._indicator_rect != rect:
            if self._animation:
                self._animation.stop()
            
            self._animation = QPropertyAnimation(self, b"indicatorRect")
            self._animation.setDuration(ListViewConfig.INDICATOR_ANIMATION_DURATION)
            self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._animation.setStartValue(self._indicator_rect)
            self._animation.setEndValue(rect)
            self._animation.start()
    
    def hide_indicator(self) -> None:
        """隐藏指示器。"""
        if self._animation:
            self._animation.stop()
            self._animation = None
        self._indicator_rect = QRect()
        self.hide()
    
    def getIndicatorRect(self) -> QRect:
        """获取指示器矩形。"""
        return self._indicator_rect
    
    def setIndicatorRect(self, rect: QRect) -> None:
        """设置指示器矩形（动画属性）。"""
        self._indicator_rect = rect
        self.update()
    
    indicatorRect = pyqtProperty(QRect, getIndicatorRect, setIndicatorRect)
    
    def paintEvent(self, event) -> None:
        """绘制事件处理。"""
        if self._indicator_rect.isEmpty():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self._current_theme
        if not theme:
            return
        
        indicator_color = theme.get_color('primary.main', QColor(0, 120, 212))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(indicator_color)
        painter.drawRoundedRect(self._indicator_rect, 2, 2)
    
    def cleanup(self) -> None:
        """清理资源。"""
        if self._animation:
            self._animation.stop()
            self._animation = None
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class ListViewDelegate(QStyledItemDelegate):
    """带主题支持的列表视图项目委托。"""
    
    def __init__(self, parent: Optional[QListView] = None):
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
        return QSize(0, ListViewConfig.ITEM_HEIGHT)
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """绘制项目。"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect.adjusted(
            ListViewConfig.ITEM_PADDING, 
            2, 
            -ListViewConfig.ITEM_PADDING, 
            -2
        )
        radius = ListViewConfig.ITEM_BORDER_RADIUS
        
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = index.row() == self._hovered_row
        
        if self._theme:
            if is_selected:
                bg_color = QColor(0, 0, 0, 0)
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            elif is_hovered:
                bg_color = self._theme.get_color('button.background.hover', QColor(60, 60, 60))
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            else:
                bg_color = QColor(0, 0, 0, 0)
                text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
        else:
            if is_selected:
                bg_color = QColor(0, 0, 0, 0)
                text_color = QColor(200, 200, 200)
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
            painter.setPen(text_color)
            font = QFont("Arial", 10)
            painter.setFont(font)
            
            text_rect = rect.adjusted(12, 0, -12, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon) and not icon.isNull():
            icon_size = 20
            icon_rect = QRect(
                rect.left() + 8, 
                rect.top() + (rect.height() - icon_size) // 2, 
                icon_size, 
                icon_size
            )
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
    - 选中项左侧指示器动画
    
    使用示例:
        from PyQt6.QtCore import QStringListModel
        
        list_view = CustomListView()
        model = QStringListModel(["项目 1", "项目 2", "项目 3"])
        list_view.setModel(model)
    """
    
    def __init__(self, parent=None):
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
        
        self._indicator = ListSelectionIndicator(self.viewport())
        
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
    
    def _update_indicator(self) -> None:
        """更新选中指示器位置。"""
        selected_indexes = self.selectedIndexes()
        if not selected_indexes:
            self._indicator.hide_indicator()
            return
        
        index = selected_indexes[0]
        rect = self.visualRect(index)
        
        if not rect.isValid():
            self._indicator.hide_indicator()
            return
        
        indicator_height = rect.height() - 8
        indicator_y = rect.top() + 4
        
        indicator_rect = QRect(
            ListViewConfig.INDICATOR_MARGIN,
            int(indicator_y),
            ListViewConfig.INDICATOR_WIDTH,
            int(indicator_height)
        )
        
        self._indicator.setGeometry(self.viewport().rect())
        self._indicator.animate_to(indicator_rect)
        self._indicator.raise_()
    
    def selectionChanged(self, selected, deselected) -> None:
        """选择变化处理。"""
        super().selectionChanged(selected, deselected)
        QTimer.singleShot(10, self._update_indicator)
    
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
    
    def resizeEvent(self, event) -> None:
        """窗口大小变化时更新指示器。"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_indicator)
    
    def scrollContentsBy(self, dx, dy) -> None:
        """滚动内容时更新指示器。"""
        super().scrollContentsBy(dx, dy)
        QTimer.singleShot(0, self._update_indicator)
    
    def cleanup(self) -> None:
        """清理资源。"""
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        if self._indicator:
            self._indicator.cleanup()
        logger.debug("CustomListView cleaned up")
