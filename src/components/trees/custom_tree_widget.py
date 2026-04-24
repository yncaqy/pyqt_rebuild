"""
Custom TreeWidget Component

Provides a tree widget with theme support, following WinUI3 design.
Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tree-view
"""

import logging
from typing import Optional, Any
from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QModelIndex, QPointF, QByteArray
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QPalette, QPolygonF
from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem
)
from PyQt6.QtSvg import QSvgRenderer
from src.core.theme_manager import ThemeManager
from src.core.font_manager import FontManager
from src.components.containers.custom_scroll_bar import CustomScrollBar

logger = logging.getLogger(__name__)

CHEVRON_DOWN_SVG = """<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M736 480c-12.5-12.5-32.8-12.5-45.3 0L523.3 647.4c-6.2 6.2-16.4 6.2-22.6 0L333.3 480c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L466.7 704c25 25 65.5 25 90.5 0L736 525.3c12.5-12.5 12.5-32.8 0-45.3z" fill="CHEVRON_COLOR"/>
</svg>"""

CHEVRON_RIGHT_SVG = """<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M384 256c-12.5 12.5-12.5 32.8 0 45.3l167.4 167.4c6.2 6.2 6.2 16.4 0 22.6L384 658.7c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l178.7-178.7c25-25 25-65.5 0-90.5L429.3 256c-12.5-12.5-32.8-12.5-45.3 0z" fill="CHEVRON_COLOR"/>
</svg>"""


class TreeConfig:
    """Configuration constants for tree widget, following WinUI3 design."""

    ITEM_HEIGHT = 32
    INDENTATION = 24
    BORDER_RADIUS = 4
    ICON_SIZE = 16
    CHEVRON_SIZE = 12
    INDICATOR_WIDTH = 3
    INDICATOR_MARGIN = 4


class TreeItemDelegate(QStyledItemDelegate):
    """Custom delegate for painting tree items."""

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
        return QSize(0, TreeConfig.ITEM_HEIGHT)

    def _draw_chevron(self, painter: QPainter, x: float, y: float, size: float, expanded: bool, color: QColor) -> None:
        svg_data = CHEVRON_DOWN_SVG if expanded else CHEVRON_RIGHT_SVG
        color_hex = color.name(QColor.NameFormat.HexRgb)
        svg_colored = svg_data.replace('CHEVRON_COLOR', color_hex)

        svg_bytes = QByteArray(svg_colored.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)

        if renderer.isValid():
            renderer.render(painter, QRectF(x, y, size, size))

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        is_dark = False
        if self._current_theme:
            is_dark = getattr(self._current_theme, 'is_dark', False)

        tree_widget = self.parent()
        depth = 0
        has_children = False
        is_expanded = False

        if tree_widget:
            item = tree_widget.itemFromIndex(index)
            if item:
                parent = item.parent()
                while parent:
                    depth += 1
                    parent = parent.parent()
                has_children = item.childCount() > 0
                is_expanded = item.isExpanded()

        indent = depth * TreeConfig.INDENTATION

        if is_selected:
            if is_dark:
                bg_color = QColor(255, 255, 255, 15)
            else:
                bg_color = QColor(0, 0, 0, 10)
        elif is_hovered:
            if is_dark:
                bg_color = QColor(255, 255, 255, 8)
            else:
                bg_color = QColor(0, 0, 0, 5)
        else:
            bg_color = QColor(0, 0, 0, 0)

        if is_dark:
            text_color = QColor(230, 230, 230)
            chevron_color = QColor(180, 180, 180)
        else:
            text_color = QColor(30, 30, 30)
            chevron_color = QColor(120, 120, 120)

        content_x = rect.x() + indent + 4

        if is_selected:
            indicator_color = QColor(89, 89, 89)
            indicator_rect = QRectF(
                TreeConfig.INDICATOR_MARGIN,
                rect.y() + 8,
                TreeConfig.INDICATOR_WIDTH,
                rect.height() - 16
            )
            painter.setBrush(QBrush(indicator_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(indicator_rect, 1.5, 1.5)

        if bg_color.alpha() > 0:
            item_rect = QRectF(rect.x() + 4, rect.y() + 2, rect.width() - 8, rect.height() - 4)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(item_rect, TreeConfig.BORDER_RADIUS, TreeConfig.BORDER_RADIUS)

        content_x += 8

        if has_children:
            chevron_x = content_x
            chevron_y = rect.y() + (rect.height() - TreeConfig.CHEVRON_SIZE) // 2
            self._draw_chevron(painter, chevron_x, chevron_y, TreeConfig.CHEVRON_SIZE, is_expanded, chevron_color)
            content_x += TreeConfig.CHEVRON_SIZE + 4
        else:
            content_x += TreeConfig.CHEVRON_SIZE + 4

        icon = index.data(Qt.ItemDataRole.DecorationRole)
        icon_x = content_x + 4
        icon_y = rect.y() + (rect.height() - TreeConfig.ICON_SIZE) // 2

        if icon and isinstance(icon, QIcon) and not icon.isNull():
            painter.drawPixmap(QRect(icon_x, icon_y, TreeConfig.ICON_SIZE, TreeConfig.ICON_SIZE),
                             icon.pixmap(TreeConfig.ICON_SIZE, TreeConfig.ICON_SIZE))
            text_offset = TreeConfig.ICON_SIZE + 4
        else:
            text_offset = 0

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.setPen(QPen(text_color))
            font = FontManager.get_caption_font()
            painter.setFont(font)

            text_rect = rect.adjusted(content_x + 4 + text_offset, 0, -8, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

        painter.restore()

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)


class CustomTreeWidgetItem(QTreeWidgetItem):
    """Custom tree widget item."""

    def __init__(self, parent: Optional[QTreeWidgetItem] = None, text: str = "", icon: Optional[QIcon] = None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()

        if text:
            self.setText(0, text)

        if icon:
            self.setIcon(0, icon)


class CustomTreeWidget(QTreeWidget):
    """
    Custom tree widget with theme support, following WinUI3 design.

    Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tree-view
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

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
        self.setIndentation(0)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)

        self._v_scroll_bar = CustomScrollBar(Qt.Orientation.Vertical, self)
        self.setVerticalScrollBar(self._v_scroll_bar)

        self._h_scroll_bar = CustomScrollBar(Qt.Orientation.Horizontal, self)
        self.setHorizontalScrollBar(self._h_scroll_bar)

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
        else:
            bg_color = QColor(252, 252, 252)
            border_color = QColor(0, 0, 0, 15)

        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color.name(QColor.NameFormat.HexArgb)};
                border: 1px solid {border_color.name(QColor.NameFormat.HexArgb)};
                border-radius: 8px;
                outline: none;
                padding: 4px;
            }}
            QTreeWidget::item {{
                border: none;
                padding: 0px;
                margin: 0px;
            }}
            QTreeWidget::item:selected {{
                background-color: transparent;
            }}
            QTreeWidget::item:hover {{
                background-color: transparent;
            }}
            QTreeWidget::branch {{
                background-color: transparent;
                border: none;
                image: none;
                width: 0px;
            }}
            QTreeWidget::branch:selected {{
                background-color: transparent;
            }}
        """)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item and item.childCount() > 0:
                index = self.indexFromItem(item)
                rect = self.visualRect(index)
                depth = 0
                parent = item.parent()
                while parent:
                    depth += 1
                    parent = parent.parent()

                indent = depth * TreeConfig.INDENTATION
                content_x = rect.x() + indent + 4 + 8
                chevron_rect = QRect(
                    content_x,
                    rect.y(),
                    TreeConfig.CHEVRON_SIZE,
                    rect.height()
                )

                if chevron_rect.contains(event.pos()):
                    item.setExpanded(not item.isExpanded())
                    return

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item and item.childCount() > 0:
                item.setExpanded(not item.isExpanded())
                return

        super().mouseDoubleClickEvent(event)

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        if self._delegate:
            self._delegate.cleanup()
        logger.debug("CustomTreeWidget cleaned up")
