"""
Pivot 组件

WinUI3 风格的枢轴控件，用于类似标签页的导航。

功能特性:
- 切换标签时的平滑下划线动画
- 水平布局，项目自动调整大小
- 键盘导航支持
- 触控滑动支持
- 主题集成
- 动态添加/删除项目
- LeftHeader / RightHeader 支持
- 固定/旋转模式切换

Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/pivot

WinUI3 Pivot Design Specifications:
- 项目高度: 40px
- 项目内边距: 12px 水平, 8px 垂直
- 字体: 14px, Semibold (选中), Normal (未选中)
- 下划线: 3px 高度, 圆角
- 触控滑动: 支持在项目和内容区域滑动切换
- 固定模式: 所有标题适合可用空间
- 旋转模式: 标题超出空间时轮播
"""

from typing import Optional, List, Dict, Any, Union
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QStackedWidget, QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer, QEvent, pyqtProperty
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor, QFontMetrics

from core.theme_manager import ThemeManager, Theme
from core.font_manager import FontManager
from themes.colors import WINUI3_CONTROL_SIZING


class PivotConfig:
    """Pivot 组件配置常量，遵循 WinUI3 设计规范。"""

    ITEM_PADDING_H = WINUI3_CONTROL_SIZING['tab']['padding_h']
    ITEM_PADDING_V = WINUI3_CONTROL_SIZING['tab']['padding_v']
    ITEM_SPACING = 0
    UNDERLINE_HEIGHT = 3
    UNDERLINE_OFFSET = 0
    FONT_SIZE = 14
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_SELECTED = 600
    ANIMATION_DURATION = 167
    MIN_ITEM_WIDTH = 80
    MAX_ITEM_WIDTH = 200
    PIVOT_HEIGHT = WINUI3_CONTROL_SIZING['tab']['min_height']
    SWIPE_THRESHOLD = 50
    HEADER_SPACING = WINUI3_CONTROL_SIZING['spacing']['small']


class PivotItem(QWidget):
    """
    单个 Pivot 项目控件。

    功能特性:
    - 文本显示，支持悬停状态
    - 选中状态样式
    - 点击处理
    - WinUI3 风格
    """

    clicked = pyqtSignal()

    def __init__(
        self, 
        text: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None
    ):
        super().__init__(parent)

        self._text = text
        self._key = item_key or text
        self._selected = False
        self._hovered = False
        self._pressed = False
        self._hover_opacity = 0.0

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(PivotConfig.PIVOT_HEIGHT)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text
        self.update()
        self._update_size()

    def key(self) -> str:
        return self._key

    def setKey(self, key: str) -> None:
        self._key = key

    def isSelected(self) -> bool:
        return self._selected

    def setSelected(self, selected: bool) -> None:
        if self._selected != selected:
            self._selected = selected
            self._update_size()
            self.update()

    def _update_size(self) -> None:
        font = FontManager.get_body_font()
        if self._selected:
            font.setWeight(QFont.Weight.DemiBold)

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self._text)

        width = max(
            PivotConfig.MIN_ITEM_WIDTH,
            min(text_width + PivotConfig.ITEM_PADDING_H * 2, PivotConfig.MAX_ITEM_WIDTH)
        )

        self.setMinimumWidth(int(width))
        self.setMaximumWidth(int(PivotConfig.MAX_ITEM_WIDTH))

    def sizeHint(self) -> QSize:
        self._update_size()
        return super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        self._update_size()
        return super().minimumSizeHint()

    def getHoverOpacity(self) -> float:
        return self._hover_opacity

    def setHoverOpacity(self, opacity: float) -> None:
        self._hover_opacity = opacity
        self.update()

    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)

    def _animate_hover(self, hover: bool) -> None:
        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(PivotConfig.ANIMATION_DURATION)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0 if hover else 0.0)
        self._hover_animation.start()

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self._pressed = False
        self._animate_hover(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            was_pressed = self._pressed
            self._pressed = False
            self.update()
            if was_pressed and self.rect().contains(event.pos()):
                self.clicked.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        rect = self.rect()

        if self._hovered and not self._selected:
            hover_color = theme.get_color('pivot.item.hover', QColor(255, 255, 255, 30))
            hover_color = QColor(hover_color)
            hover_color.setAlphaF(self._hover_opacity * 0.3)
            painter.setBrush(hover_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 4, 4)

        font = FontManager.get_body_font()
        if self._selected:
            font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)

        if self._selected:
            text_color = theme.get_color('pivot.item.text_selected', QColor(255, 255, 255))
        else:
            text_color = theme.get_color('pivot.item.text', QColor(180, 180, 180))

        painter.setPen(text_color)
        painter.drawText(
            rect, 
            Qt.AlignmentFlag.AlignCenter, 
            self._text
        )

    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class PivotUnderline(QWidget):
    """
    Pivot 的动画下划线控件。

    功能特性:
    - 平滑的位置和宽度动画
    - 主题感知样式
    - WinUI3 风格
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._target_rect = QRect(0, 0, 0, PivotConfig.UNDERLINE_HEIGHT)
        self._current_rect = QRect(0, 0, 0, PivotConfig.UNDERLINE_HEIGHT)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def setGeometryFromParent(self, parent_rect: QRect) -> None:
        self.setGeometry(parent_rect)

    def animate_to(self, x: int, width: int) -> None:
        y = self.height() - PivotConfig.UNDERLINE_HEIGHT

        self._target_rect = QRect(int(x), int(y), int(width), PivotConfig.UNDERLINE_HEIGHT)

        self._pos_animation = QPropertyAnimation(self, b"underlineRect")
        self._pos_animation.setDuration(PivotConfig.ANIMATION_DURATION)
        self._pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pos_animation.setStartValue(self._current_rect)
        self._pos_animation.setEndValue(self._target_rect)
        self._pos_animation.start()

    def getUnderlineRect(self) -> QRect:
        return self._current_rect

    def setUnderlineRect(self, rect: QRect) -> None:
        self._current_rect = rect
        self.update()

    underlineRect = pyqtProperty(QRect, getUnderlineRect, setUnderlineRect)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        underline_color = theme.get_color('pivot.underline', QColor(89, 89, 89))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(underline_color)
        painter.drawRoundedRect(self._current_rect, 2, 2)

    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class PivotHeader(QWidget):
    """
    Pivot 标题区域容器。

    支持触控滑动和固定/旋转模式。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._swipe_start_pos: Optional[QPoint] = None
        self._is_swiping = False

        self.setFixedHeight(PivotConfig.PIVOT_HEIGHT)
        self.setMouseTracking(True)

        self._init_ui()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(PivotConfig.ITEM_SPACING)

        self._left_header_layout = QHBoxLayout()
        self._left_header_layout.setSpacing(PivotConfig.HEADER_SPACING)
        self._main_layout.addLayout(self._left_header_layout)

        self._items_container = QWidget()
        self._items_layout = QHBoxLayout(self._items_container)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(PivotConfig.ITEM_SPACING)
        self._items_layout.addStretch()
        self._main_layout.addWidget(self._items_container, 1)

        self._right_header_layout = QHBoxLayout()
        self._right_header_layout.setSpacing(PivotConfig.HEADER_SPACING)
        self._main_layout.addLayout(self._right_header_layout)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def itemsLayout(self) -> QHBoxLayout:
        return self._items_layout

    def leftHeaderLayout(self) -> QHBoxLayout:
        return self._left_header_layout

    def rightHeaderLayout(self) -> QHBoxLayout:
        return self._right_header_layout

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        bg_color = theme.get_color('pivot.background', QColor('transparent'))
        if bg_color != 'transparent':
            painter.fillRect(self.rect(), bg_color)

    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class Pivot(QWidget):
    """
    WinUI3 风格的 Pivot 控件，用于类似标签页的导航。

    功能特性:
    - 切换标签时的平滑下划线动画
    - 水平布局，项目自动调整大小
    - 键盘导航支持
    - 触控滑动支持
    - 主题集成
    - 动态添加/删除项目
    - LeftHeader / RightHeader 支持
    - 固定/旋转模式切换

    Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/pivot

    使用示例:
        pivot = Pivot()
        pivot.addItem("首页", "home")
        pivot.addItem("设置", "settings")
        pivot.addItem("关于", "about")

        pivot.currentChanged.connect(lambda key: print(f"选中: {key}"))

        # 添加右侧头部控件
        pivot.setRightHeader(my_command_bar)

        # 连接到 QStackedWidget
        stacked = QStackedWidget()
        pivot.currentChanged.connect(lambda key: stacked.setCurrentIndex(...))
    """

    currentChanged = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[PivotItem] = []
        self._item_keys: Dict[str, PivotItem] = {}
        self._current_index = -1
        self._current_key: Optional[str] = None
        self._swipe_start_pos: Optional[QPoint] = None
        self._is_swiping = False

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setMinimumHeight(PivotConfig.PIVOT_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        self._init_ui()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._header = PivotHeader(self)
        self._main_layout.addWidget(self._header)

        self._underline = PivotUnderline(self)
        self._underline.hide()

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def setLeftHeader(self, widget: QWidget) -> None:
        """
        设置左侧头部控件。

        Args:
            widget: 要添加到左侧头部的控件

        Example:
            pivot.setLeftHeader(my_icon_label)
        """
        layout = self._header.leftHeaderLayout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        layout.addWidget(widget)

    def setRightHeader(self, widget: QWidget) -> None:
        """
        设置右侧头部控件。

        Args:
            widget: 要添加到右侧头部的控件

        Example:
            command_bar = QCommandBar()
            pivot.setRightHeader(command_bar)
        """
        layout = self._header.rightHeaderLayout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        layout.addWidget(widget)

    def addItem(
        self, 
        text: str, 
        key: Optional[str] = None,
        select: bool = False
    ) -> PivotItem:
        """
        添加新项目到 Pivot。

        Args:
            text: 显示文本
            key: 可选的唯一键（默认为文本）
            select: 是否立即选中此项

        Returns:
            创建的 PivotItem
        """
        item_key = key or text

        if item_key in self._item_keys:
            return self._item_keys[item_key]

        item = PivotItem(text, self, item_key)
        item.clicked.connect(lambda: self._on_item_clicked(item))

        self._items.append(item)
        self._item_keys[item_key] = item

        items_layout = self._header.itemsLayout()
        items_layout.insertWidget(items_layout.count() - 1, item)

        if len(self._items) == 1 or select:
            self.setCurrentItem(item_key)

        return item

    def removeItem(self, key: str) -> bool:
        """
        从 Pivot 移除项目。

        Args:
            key: 要移除的项目键

        Returns:
            移除成功返回 True，未找到返回 False
        """
        if key not in self._item_keys:
            return False

        item = self._item_keys[key]
        index = self._items.index(item)

        if self._current_index == index:
            if len(self._items) > 1:
                new_index = min(index, len(self._items) - 2)
                self.setCurrentIndex(new_index)
            else:
                self._current_index = -1
                self._current_key = None
                self._underline.hide()
        elif self._current_index > index:
            self._current_index -= 1

        self._items.remove(item)
        del self._item_keys[key]
        self._header.itemsLayout().removeWidget(item)
        item.cleanup()
        item.deleteLater()

        return True

    def clear(self) -> None:
        """移除所有项目。"""
        items_layout = self._header.itemsLayout()
        for item in self._items[:]:
            items_layout.removeWidget(item)
            item.cleanup()
            item.deleteLater()

        self._items.clear()
        self._item_keys.clear()
        self._current_index = -1
        self._current_key = None
        self._underline.hide()

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> Optional[PivotItem]:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def item(self, key: str) -> Optional[PivotItem]:
        return self._item_keys.get(key)

    def currentIndex(self) -> int:
        return self._current_index

    def setCurrentIndex(self, index: int) -> None:
        if 0 <= index < len(self._items) and index != self._current_index:
            self._select_item(index)

    def currentKey(self) -> Optional[str]:
        return self._current_key

    def setCurrentItem(self, key: str) -> None:
        if key in self._item_keys:
            index = self._items.index(self._item_keys[key])
            self.setCurrentIndex(index)

    def currentText(self) -> str:
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index].text()
        return ""

    def _on_item_clicked(self, item: PivotItem) -> None:
        index = self._items.index(item)
        self._select_item(index)

    def _select_item(self, index: int) -> None:
        if not (0 <= index < len(self._items)):
            return

        old_index = self._current_index
        self._current_index = index

        for i, item in enumerate(self._items):
            item.setSelected(i == index)

        self._current_key = self._items[index].key()

        self._animate_underline(index)

        if old_index != index:
            self.currentChanged.emit(self._current_key)

    def _animate_underline(self, index: int) -> None:
        if not (0 <= index < len(self._items)):
            return

        item = self._items[index]
        item_rect = item.geometry()

        header_pos = self._header.pos()
        item_global_rect = QRect(
            header_pos.x() + item_rect.x(),
            header_pos.y() + item_rect.y(),
            item_rect.width(),
            item_rect.height()
        )

        underline_width = min(item_rect.width() - 16, 60)
        underline_x = item_global_rect.x() + (item_global_rect.width() - underline_width) // 2

        self._underline.setGeometry(self.rect())
        self._underline.show()
        self._underline.raise_()
        self._underline.animate_to(underline_x, underline_width)

    def _handle_swipe(self, delta: int) -> None:
        if len(self._items) <= 1:
            return

        if delta > PivotConfig.SWIPE_THRESHOLD:
            if self._current_index < len(self._items) - 1:
                self.setCurrentIndex(self._current_index + 1)
        elif delta < -PivotConfig.SWIPE_THRESHOLD:
            if self._current_index > 0:
                self.setCurrentIndex(self._current_index - 1)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._swipe_start_pos = event.pos()
            self._is_swiping = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._is_swiping and self._swipe_start_pos:
            pass
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_swiping and self._swipe_start_pos:
            delta = event.pos().x() - self._swipe_start_pos.x()
            self._handle_swipe(-delta)
            self._swipe_start_pos = None
            self._is_swiping = False
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        if 0 <= self._current_index < len(self._items):
            self._animate_underline(self._current_index)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Left:
            if self._current_index > 0:
                self.setCurrentIndex(self._current_index - 1)
            elif len(self._items) > 0:
                self.setCurrentIndex(len(self._items) - 1)
            return

        if event.key() == Qt.Key.Key_Right:
            if self._current_index < len(self._items) - 1:
                self.setCurrentIndex(self._current_index + 1)
            elif len(self._items) > 0:
                self.setCurrentIndex(0)
            return

        if event.key() == Qt.Key.Key_Home:
            if len(self._items) > 0:
                self.setCurrentIndex(0)
            return

        if event.key() == Qt.Key.Key_End:
            if len(self._items) > 0:
                self.setCurrentIndex(len(self._items) - 1)
            return

        super().keyPressEvent(event)

    def cleanup(self) -> None:
        for item in self._items:
            item.cleanup()

        if hasattr(self, '_underline') and self._underline:
            self._underline.cleanup()

        if hasattr(self, '_header') and self._header:
            self._header.cleanup()

        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
