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
- Unified ThemedDelegateBase for delegates
"""

import logging
from typing import Optional, List, Tuple, Any
from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QModelIndex, QByteArray
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem
)
from PyQt6.QtSvg import QSvgRenderer
from core.themed_component_base import ThemedDelegateBase
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_manager import ThemeManager
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
    """Configuration constants for tree widget, following WinUI3 design."""
    
    ITEM_HEIGHT = 32
    INDENTATION = 24
    BORDER_RADIUS = 4
    ICON_SIZE = 16


class TreeItemDelegate(ThemedDelegateBase):
    """Custom delegate for painting tree items with theme support."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._apply_initial_theme()
    
    def _on_theme_changed(self, theme) -> None:
        """主题变化回调，触发视图更新。"""
        super()._on_theme_changed(theme)
        if self.parent():
            self.parent().viewport().update()
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(0, TreeConfig.ITEM_HEIGHT)
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        option.state &= ~QStyle.StateFlag.State_HasFocus
        
        rect = option.rect
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver
        
        theme = self._current_theme
        is_dark = getattr(theme, 'is_dark', True) if theme else True
        
        if is_selected:
            if is_dark:
                bg_color = QColor(255, 255, 255, 15)
                text_color = QColor(200, 200, 200)
            else:
                bg_color = QColor(0, 0, 0, 30)
                text_color = QColor(60, 60, 60)
        elif is_hovered:
            if is_dark:
                bg_color = QColor(255, 255, 255, 9)
                text_color = QColor(200, 200, 200)
            else:
                bg_color = QColor(0, 0, 0, 15)
                text_color = QColor(60, 60, 60)
        else:
            bg_color = QColor(0, 0, 0, 0)
            if is_dark:
                text_color = QColor(200, 200, 200)
            else:
                text_color = QColor(60, 60, 60)
        
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
            icon_size = TreeConfig.ICON_SIZE
            icon_x = rect.x() + TreeConfig.INDENTATION + 8
            icon_y = rect.y() + (rect.height() - icon_size) // 2
            painter.drawPixmap(QRect(icon_x, icon_y, icon_size, icon_size), icon.pixmap(icon_size, icon_size))
        
        painter.restore()


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


class CustomTreeWidget(QTreeWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Custom tree widget with theme support, similar to QTreeWidget.
    
    Features:
    - Full QTreeWidget API compatibility
    - Theme integration
    - Custom item styling
    - Hover and selection effects
    - Expandable/collapsible items
    - Custom scroll bars
    - Style override support
    - Stylesheet caching
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_style_override()
        self._init_stylesheet_cache()
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        
        self._delegate: Optional[TreeItemDelegate] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        
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
    
    def _on_theme_changed(self, theme: Any) -> None:
        """主题变化回调。"""
        self._current_theme = theme
        self._apply_theme()
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        is_dark = getattr(self._current_theme, 'is_dark', True) if self._current_theme else True
        
        bg_color = QColor(0, 0, 0, 0)
        if is_dark:
            border_color = QColor(255, 255, 255, 24)
            text_color = QColor(200, 200, 200)
        else:
            border_color = QColor(0, 0, 0, 24)
            text_color = QColor(60, 60, 60)
        
        cache_key: Tuple[str, str, str, str] = (
            'tree_widget',
            bg_color.name(QColor.NameFormat.HexArgb),
            border_color.name(QColor.NameFormat.HexArgb),
            text_color.name(QColor.NameFormat.HexArgb)
        )
        
        def build_stylesheet() -> str:
            return f"""
                QTreeWidget {{
                    background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                    border: 1px solid {border_color.name(QColor.NameFormat.HexArgb)};
                    border-radius: 4px;
                    outline: none;
                    color: {text_color.name(QColor.NameFormat.HexArgb)};
                    show-decoration-selected: 0;
                }}
                QTreeWidget::item {{
                    border: none;
                    padding: 0px;
                    outline: none;
                }}
                QTreeWidget::item:selected {{
                    background-color: transparent;
                    outline: none;
                }}
                QTreeWidget::branch {{
                    background-color: transparent;
                    outline: none;
                    border: none;
                    image: none;
                }}
                QTreeWidget::branch:selected {{
                    background-color: transparent;
                    outline: none;
                    border: none;
                    image: none;
                }}
                QTreeWidget::branch:has-children:!has-siblings:closed,
                QTreeWidget::branch:closed:has-children:has-siblings {{
                    background-color: transparent;
                    image: none;
                }}
                QTreeWidget::branch:open:has-children:!has-siblings,
                QTreeWidget::branch:open:has-children:has-siblings  {{
                    background-color: transparent;
                    image: none;
                }}
            """
        
        qss = self._get_cached_stylesheet(cache_key, build_stylesheet)
        self.setStyleSheet(qss)
    
    def drawBranches(self, painter: QPainter, rect: QRect, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_dark = getattr(self._current_theme, 'is_dark', True) if self._current_theme else True
        
        if is_dark:
            bg_color = QColor(0, 0, 0, 0)
            arrow_color = QColor(200, 200, 200)
        else:
            bg_color = QColor(0, 0, 0, 0)
            arrow_color = QColor(60, 60, 60)
        
        painter.fillRect(rect, bg_color)
        
        item = self.itemFromIndex(index)
        if not item:
            painter.restore()
            return
        
        has_children = item.childCount() > 0
        is_expanded = item.isExpanded()
        
        if has_children:
            svg_data = EXPANDED_SVG if is_expanded else COLLAPSED_SVG
            
            svg_colored = svg_data.replace('BG_COLOR', bg_color.name(QColor.NameFormat.HexArgb))
            svg_colored = svg_colored.replace('ARROW_COLOR', arrow_color.name(QColor.NameFormat.HexArgb))
            
            svg_bytes = QByteArray(svg_colored.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            if renderer.isValid():
                icon_size = TreeConfig.ICON_SIZE
                icon_x = rect.x() + (rect.width() - icon_size) // 2
                icon_y = rect.y() + (rect.height() - icon_size) // 2
                
                renderer.render(painter, QRectF(icon_x, icon_y, icon_size, icon_size))
        
        painter.restore()
    
    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        self._clear_stylesheet_cache()
        self.clear_overrides()
        logger.debug("CustomTreeWidget cleaned up")
