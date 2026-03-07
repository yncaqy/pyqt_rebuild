"""
BreadcrumbBar - 面包屑导航组件

提供功能完整、视觉美观的面包屑导航组件。

Features:
- 层级路径展示
- 当前位置高亮显示
- 点击交互反馈
- 自适应不同屏幕尺寸
- 支持自定义分隔符样式
- 可选的末尾当前页文本省略
- 深色/浅色主题支持

Example:
    breadcrumb = BreadcrumbBar()
    breadcrumb.set_path(["首页", "产品", "电子产品", "手机"])
    breadcrumb.current_changed.connect(lambda index, text: print(f"Clicked: {text}"))
"""

import logging
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize
)
from PyQt6.QtGui import QColor, QPainter

from core.theme_manager import ThemeManager, Theme
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class BreadcrumbConfig:
    """BreadcrumbBar配置常量"""
    
    DEFAULT_HEIGHT = 32
    DEFAULT_PADDING = 8
    ITEM_SPACING = 2
    FONT_SIZE = 13


class BreadcrumbItem(QWidget):
    """
    面包屑项组件。
    
    表示面包屑导航中的一个层级项。
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, text: str, index: int, is_current: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._text = text
        self._index = index
        self._is_current = is_current
        self._is_hovered = False
        
        self._text_color: QColor = QColor(100, 100, 100)
        self._current_color: QColor = QColor(60, 60, 60)
        self._hover_color: QColor = QColor(0, 120, 215)
        self._is_dark_theme: bool = True
        
        self._setup_ui()
        self.setCursor(Qt.CursorShape.PointingHandCursor if not is_current else Qt.CursorShape.ArrowCursor)
        
    def _setup_ui(self) -> None:
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(0)
        
        self._label = QLabel(self._text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)
        
        self._apply_style()
        
    def _apply_style(self) -> None:
        if self._is_current:
            color = self._current_color
            font_weight = "600"
        elif self._is_hovered:
            color = self._hover_color
            font_weight = "500"
        else:
            color = self._text_color
            font_weight = "400"
            
        self._label.setStyleSheet(f"""
            QLabel {{
                color: {color.name()};
                font-size: {BreadcrumbConfig.FONT_SIZE}px;
                font-weight: {font_weight};
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)
        
    @property
    def text(self) -> str:
        return self._text
        
    @property
    def index(self) -> int:
        return self._index
        
    def set_current(self, is_current: bool) -> None:
        self._is_current = is_current
        self.setCursor(Qt.CursorShape.PointingHandCursor if not is_current else Qt.CursorShape.ArrowCursor)
        self._apply_style()
        
    def apply_theme(self, theme: Theme) -> None:
        self._is_dark_theme = theme.name == 'dark'
        
        if self._is_dark_theme:
            self._text_color = QColor(180, 180, 180)
            self._current_color = QColor(240, 240, 240)
            self._hover_color = QColor(100, 180, 255)
        else:
            self._text_color = QColor(100, 100, 100)
            self._current_color = QColor(40, 40, 40)
            self._hover_color = QColor(0, 120, 215)
            
        self._apply_style()
        
    def enterEvent(self, event) -> None:
        if not self._is_current:
            self._is_hovered = True
            self._apply_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event) -> None:
        if not self._is_current:
            self._is_hovered = False
            self._apply_style()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._is_current:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def sizeHint(self) -> QSize:
        return self._label.sizeHint() + QSize(8, 0)


class BreadcrumbSeparator(QWidget):
    """
    面包屑分隔符组件。
    
    显示层级之间的分隔符，支持多种样式。
    """
    
    STYLE_ARROW = "arrow"
    STYLE_SLASH = "slash"
    STYLE_CHEVRON = "chevron"
    
    def __init__(self, style: str = STYLE_CHEVRON, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._separator_style = style
        self._separator_color: QColor = QColor(150, 150, 150)
        
        self.setFixedSize(16, 16)
        
    def apply_theme(self, theme: Theme) -> None:
        is_dark = theme.name == 'dark'
        self._separator_color = QColor(120, 120, 120) if is_dark else QColor(180, 180, 180)
        self.update()
        
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = painter.pen()
        pen.setColor(self._separator_color)
        pen.setWidthF(1.5)
        painter.setPen(pen)
        
        if self._separator_style == self.STYLE_CHEVRON:
            self._draw_chevron(painter)
        elif self._separator_style == self.STYLE_ARROW:
            self._draw_arrow(painter)
        else:
            self._draw_slash(painter)
            
        painter.end()
        
    def _draw_chevron(self, painter: QPainter) -> None:
        x, y = 6, 3
        painter.drawLine(x, y, x + 4, y + 5)
        painter.drawLine(x, y + 10, x + 4, y + 5)
        
    def _draw_arrow(self, painter: QPainter) -> None:
        x, y = 5, 4
        painter.drawLine(x, y, x + 6, y + 4)
        painter.drawLine(x, y + 8, x + 6, y + 4)
        
    def _draw_slash(self, painter: QPainter) -> None:
        painter.drawLine(5, 3, 11, 13)


class BreadcrumbBar(QWidget, StylesheetCacheMixin):
    """
    面包屑导航组件。
    
    显示层级路径，支持点击导航。
    
    Features:
    - 层级路径展示
    - 当前位置高亮显示
    - 点击交互反馈
    - 自适应不同屏幕尺寸
    - 支持自定义分隔符样式
    - 可选的末尾当前页文本省略
    - 深色/浅色主题支持
    
    Signals:
        current_changed: 当点击某个层级时发出 (index, text)
        
    Example:
        breadcrumb = BreadcrumbBar()
        breadcrumb.set_path(["首页", "产品", "电子产品", "手机"])
        breadcrumb.current_changed.connect(lambda i, t: print(f"Navigate to: {t}"))
    """
    
    current_changed = pyqtSignal(int, str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_stylesheet_cache(max_size=10)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self._items: List[BreadcrumbItem] = []
        self._separators: List[BreadcrumbSeparator] = []
        self._path: List[str] = []
        self._current_index: int = -1
        self._separator_style: str = BreadcrumbSeparator.STYLE_CHEVRON
        self._show_current: bool = True
        self._max_visible_items: int = 0
        
        self._setup_ui()
        self._apply_initial_theme()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        logger.debug("BreadcrumbBar initialized")
        
    def _setup_ui(self) -> None:
        self.setFixedHeight(BreadcrumbConfig.DEFAULT_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(
            BreadcrumbConfig.DEFAULT_PADDING, 0,
            BreadcrumbConfig.DEFAULT_PADDING, 0
        )
        self._layout.setSpacing(BreadcrumbConfig.ITEM_SPACING)
        self._layout.addStretch()
        
    def _apply_initial_theme(self) -> None:
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)
            
    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to BreadcrumbBar: {e}")
            
    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return
            
        self._current_theme = theme
        is_dark = theme.name == 'dark'
        
        bg_color = QColor(35, 35, 35) if is_dark else QColor(250, 250, 250)
        
        cache_key = ('breadcrumb', bg_color.name())
        
        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: f"""
                BreadcrumbBar {{
                    background-color: {bg_color.name()};
                }}
            """
        )
        
        self.setStyleSheet(qss)
        
        for item in self._items:
            item.apply_theme(theme)
        for sep in self._separators:
            sep.apply_theme(theme)
            
    def set_path(self, path: List[str]) -> None:
        """
        设置面包屑路径。
        
        Args:
            path: 层级路径列表，如 ["首页", "产品", "电子产品"]
        """
        self._path = path
        self._current_index = len(path) - 1 if path else -1
        self._rebuild_items()
        
    def get_path(self) -> List[str]:
        """获取当前路径"""
        return self._path.copy()
        
    def set_current_index(self, index: int) -> None:
        """
        设置当前高亮的层级索引。
        
        Args:
            index: 层级索引，-1表示最后一项
        """
        if index < 0:
            index = len(self._path) - 1
        if 0 <= index < len(self._path):
            self._current_index = index
            self._update_current_highlight()
            
    def set_separator_style(self, style: str) -> None:
        """
        设置分隔符样式。
        
        Args:
            style: 分隔符样式，可选值：chevron, arrow, slash
        """
        self._separator_style = style
        for sep in self._separators:
            sep._separator_style = style
            sep.update()
            
    def set_show_current(self, show: bool) -> None:
        """
        设置是否显示当前项。
        
        Args:
            show: True显示，False隐藏
        """
        self._show_current = show
        self._rebuild_items()
        
    def set_max_visible_items(self, max_items: int) -> None:
        """
        设置最大可见项数（0表示不限制）。
        
        Args:
            max_items: 最大可见项数
        """
        self._max_visible_items = max_items
        self._rebuild_items()
        
    def _rebuild_items(self) -> None:
        """重建面包屑项"""
        self._clear_items()
        
        if not self._path:
            return
            
        visible_path = self._get_visible_path()
        
        for i, text in enumerate(visible_path):
            actual_index = self._get_actual_index(i)
            is_current = (actual_index == self._current_index) if self._show_current else False
            
            if not self._show_current and actual_index == self._current_index:
                continue
                
            item = BreadcrumbItem(text, actual_index, is_current)
            item.apply_theme(self._current_theme) if self._current_theme else None
            item.clicked.connect(lambda checked=False, idx=actual_index: self._on_item_clicked(idx))
            
            self._items.append(item)
            self._layout.insertWidget(self._layout.count() - 1, item)
            
            if i < len(visible_path) - 1:
                sep = BreadcrumbSeparator(self._separator_style)
                if self._current_theme:
                    sep.apply_theme(self._current_theme)
                self._separators.append(sep)
                self._layout.insertWidget(self._layout.count() - 1, sep)
                
    def _get_visible_path(self) -> List[str]:
        """获取可见路径（处理省略）"""
        if self._max_visible_items <= 0 or len(self._path) <= self._max_visible_items:
            return self._path
            
        result = []
        result.append(self._path[0])
        result.append("...")
        
        remaining = self._max_visible_items - 2
        if remaining > 0:
            result.extend(self._path[-(remaining):])
            
        return result
        
    def _get_actual_index(self, visible_index: int) -> int:
        """获取实际索引"""
        if self._max_visible_items <= 0 or len(self._path) <= self._max_visible_items:
            return visible_index
            
        if visible_index == 0:
            return 0
        elif visible_index == 1:
            return -1
        else:
            remaining = self._max_visible_items - 2
            return len(self._path) - remaining + (visible_index - 2)
            
    def _clear_items(self) -> None:
        """清除所有项"""
        for item in self._items:
            self._layout.removeWidget(item)
            item.deleteLater()
        for sep in self._separators:
            self._layout.removeWidget(sep)
            sep.deleteLater()
            
        self._items.clear()
        self._separators.clear()
        
    def _update_current_highlight(self) -> None:
        """更新当前高亮"""
        for item in self._items:
            item.set_current(item.index == self._current_index)
            
    def _on_item_clicked(self, index: int) -> None:
        """处理项点击"""
        if index < 0:
            return
            
        self._path = self._path[:index + 1]
        self._current_index = len(self._path) - 1
        self._rebuild_items()
        self.current_changed.emit(index, self._path[-1])
        
    def clear(self) -> None:
        """清除路径"""
        self._path.clear()
        self._current_index = -1
        self._clear_items()
        
    def sizeHint(self) -> QSize:
        width = BreadcrumbConfig.DEFAULT_PADDING * 2
        for item in self._items:
            width += item.sizeHint().width()
        for sep in self._separators:
            width += sep.sizeHint().width()
        width += len(self._separators) * BreadcrumbConfig.ITEM_SPACING
        return QSize(width, BreadcrumbConfig.DEFAULT_HEIGHT)
        
    def cleanup(self) -> None:
        """清理资源"""
        self._clear_items()
        self._theme_mgr.unsubscribe(self)
