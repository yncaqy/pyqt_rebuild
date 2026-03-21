"""
标签栏组件

WinUI3 风格的标签栏控件，用于在多个标签页之间切换。

功能特性:
- 动态添加/删除标签，带关闭按钮
- 平滑的选择动画和背景高亮
- 键盘导航支持 (Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+F4)
- 主题集成
- 溢出处理，带滚动按钮
- 添加选项卡按钮 (+)
- 标签图标支持

Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tab-view

WinUI3 TabView Design Specifications:
- 选中标签: 背景高亮，非下划线
- 关闭按钮: 悬停时显示，16x16
- 添加按钮: 右侧 + 按钮
- 键盘: Ctrl+Tab 切换, Ctrl+F4 关闭
- 拖拽: 支持标签重排
"""

from typing import Optional, List, Dict, Callable, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QSizePolicy, QScrollArea, QFrame,
    QStackedWidget
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer, QEvent, pyqtProperty
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor, QFontMetrics, QIcon, QPainterPath

from core.themed_component_base import ThemedComponentBase
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_manager import ThemeManager
from core.icon_manager import IconManager
from themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG


class TabBarConfig:
    """标签栏配置常量，遵循 WinUI3 设计规范。"""

    ITEM_PADDING_H = 12
    ITEM_PADDING_V = 6
    ITEM_SPACING = 0
    CLOSE_BUTTON_SIZE = 16
    CLOSE_BUTTON_MARGIN = 8
    ICON_SIZE = 16
    ICON_TEXT_SPACING = 8
    FONT_SIZE = FONT_CONFIG['size']['body']
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_SELECTED = 600
    ANIMATION_DURATION = 167
    MIN_ITEM_WIDTH = WINUI3_CONTROL_SIZING['tab']['min_width']
    MAX_ITEM_WIDTH = 200
    ITEM_HEIGHT = 40
    ADD_BUTTON_SIZE = 32
    SCROLL_BUTTON_SIZE = 24
    TAB_RADIUS = 8


class TabCloseButton(ThemedComponentBase):
    """标签关闭按钮。"""

    clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        self._hovered = False
        self._pressed = False
        self._icon_mgr = IconManager.instance()

        super().__init__(parent)

        self.setFixedSize(TabBarConfig.CLOSE_BUTTON_SIZE, TabBarConfig.CLOSE_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._apply_initial_theme()

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self.update()

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._hovered:
            self.clicked.emit()
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = self.rect()

        if self._hovered:
            if self._pressed:
                bg_color = self.get_theme_color('tabbar.close_pressed', QColor(60, 60, 60))
            else:
                bg_color = self.get_theme_color('tabbar.close_hover', QColor(70, 70, 70))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 4, 4)

        icon_color = self.get_theme_color('tabbar.close_icon', QColor(140, 140, 140))
        if self._hovered:
            icon_color = self.get_theme_color('tabbar.close_icon_hover', QColor(255, 255, 255))

        icon = self._icon_mgr.get_colored_icon('window_close', icon_color, 10)
        icon_size = 10
        x = (rect.width() - icon_size) // 2
        y = (rect.height() - icon_size) // 2
        icon.paint(painter, x, y, icon_size, icon_size)


class TabAddButton(ThemedComponentBase):
    """添加标签按钮。"""

    clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        self._hovered = False
        self._pressed = False
        self._icon_mgr = IconManager.instance()

        super().__init__(parent)

        self.setFixedSize(TabBarConfig.ADD_BUTTON_SIZE, TabBarConfig.ITEM_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._apply_initial_theme()

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self.update()

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._hovered:
            self.clicked.emit()
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self._hovered:
            if self._pressed:
                bg_color = self.get_theme_color('tabbar.item.pressed', QColor(50, 50, 50))
            else:
                bg_color = self.get_theme_color('tabbar.item.hover', QColor(60, 60, 60))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 4, 4)

        icon_color = self.get_theme_color('tabbar.scroll_icon', QColor(150, 150, 150))
        if self._hovered:
            icon_color = self.get_theme_color('tabbar.item.text', QColor(200, 200, 200))

        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        center = rect.center()
        size = 8
        painter.drawLine(center.x() - size, center.y(), center.x() + size, center.y())
        painter.drawLine(center.x(), center.y() - size, center.x(), center.y() + size)


class TabItem(ThemedComponentBase):
    """
    单个标签项控件。

    WinUI3 设计规范:
    - 选中时显示背景高亮
    - 悬停时显示圆角背景
    - 关闭按钮在悬停或选中时显示
    - 支持图标
    """

    clicked = pyqtSignal()
    closeRequested = pyqtSignal()

    def __init__(
        self, 
        text: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ):
        self._text = text
        self._key = item_key or text
        self._closable = closable
        self._icon = icon
        self._selected = False
        self._hovered = False
        self._hover_opacity = 0.0
        self._close_button: Optional[TabCloseButton] = None

        super().__init__(parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setFixedHeight(TabBarConfig.ITEM_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._init_ui()
        self._apply_initial_theme()

    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(
            TabBarConfig.ITEM_PADDING_H,
            TabBarConfig.ITEM_PADDING_V,
            TabBarConfig.ITEM_PADDING_H - 4 if self._closable else TabBarConfig.ITEM_PADDING_H,
            TabBarConfig.ITEM_PADDING_V
        )
        self._main_layout.setSpacing(TabBarConfig.ICON_TEXT_SPACING)

        self._icon_label = QLabel()
        self._icon_label.setFixedSize(TabBarConfig.ICON_SIZE, TabBarConfig.ICON_SIZE)
        self._icon_label.hide()
        self._main_layout.addWidget(self._icon_label)

        self._text_label = QLabel(self._text)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._text_label)

        if self._closable:
            self._close_button = TabCloseButton(self)
            self._close_button.clicked.connect(self.closeRequested.emit)
            self._main_layout.addWidget(self._close_button)

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self.update()

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text
        self._text_label.setText(text)
        self.update()

    def key(self) -> str:
        return self._key

    def icon(self) -> Optional[QIcon]:
        return self._icon

    def setIcon(self, icon: Optional[QIcon]) -> None:
        self._icon = icon
        if icon:
            self._icon_label.setPixmap(icon.pixmap(TabBarConfig.ICON_SIZE, TabBarConfig.ICON_SIZE))
            self._icon_label.show()
        else:
            self._icon_label.hide()
        self.update()

    def isClosable(self) -> bool:
        return self._closable

    def isSelected(self) -> bool:
        return self._selected

    def setSelected(self, selected: bool) -> None:
        if self._selected != selected:
            self._selected = selected
            self._update_style()

    def _update_style(self) -> None:
        font = self._text_label.font()
        font.setWeight(
            TabBarConfig.FONT_WEIGHT_SELECTED if self._selected
            else TabBarConfig.FONT_WEIGHT_NORMAL
        )
        self._text_label.setFont(font)
        self.update()

    def getHoverOpacity(self) -> float:
        return self._hover_opacity

    def setHoverOpacity(self, opacity: float) -> None:
        self._hover_opacity = opacity
        self.update()

    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self._animate_hover(False)
        super().leaveEvent(event)

    def _animate_hover(self, hovered: bool) -> None:
        animation = QPropertyAnimation(self, b"hoverOpacity")
        animation.setDuration(TabBarConfig.ANIMATION_DURATION)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(self._hover_opacity)
        animation.setEndValue(1.0 if hovered else 0.0)
        animation.start()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        radius = TabBarConfig.TAB_RADIUS

        if self._selected:
            bg_color = self.get_theme_color('tabbar.item.background_selected', QColor(45, 45, 45))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            
            path = QPainterPath()
            path.moveTo(rect.left(), rect.bottom())
            path.lineTo(rect.left(), rect.top() + radius)
            path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
            path.lineTo(rect.right() - radius, rect.top())
            path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
            path.lineTo(rect.right(), rect.bottom())
            path.closeSubpath()
            painter.drawPath(path)
            
        elif self._hovered:
            hover_color = self.get_theme_color('tabbar.item.hover', QColor(255, 255, 255, 25))
            hover_color = QColor(hover_color)
            hover_color.setAlphaF(self._hover_opacity * 0.4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover_color)
            painter.drawRoundedRect(rect, radius, radius)

        text_color = self.get_theme_color(
            'tabbar.item.text_selected' if self._selected else 'tabbar.item.text',
            QColor(255, 255, 255) if self._selected else QColor(160, 160, 160)
        )
        self._text_label.setStyleSheet(f"color: {text_color.name()}; background: transparent;")

        if self._icon:
            self._icon_label.setStyleSheet(f"background: transparent;")

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self._text_label.font())
        text_width = fm.horizontalAdvance(self._text)

        width = text_width + TabBarConfig.ITEM_PADDING_H * 2

        if self._icon:
            width += TabBarConfig.ICON_SIZE + TabBarConfig.ICON_TEXT_SPACING

        if self._closable:
            width += TabBarConfig.CLOSE_BUTTON_SIZE + TabBarConfig.CLOSE_BUTTON_MARGIN

        width = max(TabBarConfig.MIN_ITEM_WIDTH, min(width, TabBarConfig.MAX_ITEM_WIDTH))

        return QSize(width, TabBarConfig.ITEM_HEIGHT)

    def cleanup(self) -> None:
        if self._close_button:
            self._close_button.cleanup()
        super().cleanup()


class TabBarScrollButton(ThemedComponentBase):
    """滚动按钮。"""

    clicked = pyqtSignal()

    def __init__(self, direction: str = 'left', parent: Optional[QWidget] = None):
        self._direction = direction
        self._hovered = False

        super().__init__(parent)

        self.setFixedSize(TabBarConfig.SCROLL_BUTTON_SIZE, TabBarConfig.ITEM_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._apply_initial_theme()

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self.update()

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._hovered:
            hover_color = self.get_theme_color('tabbar.item.hover', QColor(255, 255, 255, 20))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover_color)
            painter.drawRoundedRect(self.rect(), 4, 4)

        icon_color = self.get_theme_color('tabbar.scroll_icon', QColor(150, 150, 150))
        pen = QPen(icon_color, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        center = self.rect().center()
        offset = 5

        if self._direction == 'left':
            painter.drawLine(
                center.x() + offset, center.y() - offset,
                center.x() - offset, center.y()
            )
            painter.drawLine(
                center.x() - offset, center.y(),
                center.x() + offset, center.y() + offset
            )
        else:
            painter.drawLine(
                center.x() - offset, center.y() - offset,
                center.x() + offset, center.y()
            )
            painter.drawLine(
                center.x() + offset, center.y(),
                center.x() - offset, center.y() + offset
            )


class TabBar(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    WinUI3 风格标签栏控件。

    功能特性:
    - 动态添加/删除标签，带关闭按钮
    - 平滑的选择动画和背景高亮
    - 键盘导航支持 (Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+F4)
    - 主题集成
    - 溢出处理，带滚动按钮
    - 添加选项卡按钮 (+)
    - 标签图标支持

    Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tab-view
    """

    currentChanged = pyqtSignal(str)
    tabCloseRequested = pyqtSignal(str)
    tabAddRequested = pyqtSignal()
    tabAdded = pyqtSignal(str)
    tabRemoved = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None, show_add_button: bool = True):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._items: List[TabItem] = []
        self._item_keys: Dict[str, TabItem] = {}
        self._current_index = -1
        self._current_key: Optional[str] = None
        self._scroll_offset = 0
        self._show_add_button = show_add_button

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None

        self.setFixedHeight(TabBarConfig.ITEM_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._init_ui()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._left_scroll_btn = TabBarScrollButton('left', self)
        self._left_scroll_btn.clicked.connect(self._scroll_left)
        self._left_scroll_btn.hide()
        self._main_layout.addWidget(self._left_scroll_btn)

        self._tabs_container = QWidget(self)
        self._tabs_layout = QHBoxLayout(self._tabs_container)
        self._tabs_layout.setContentsMargins(0, 0, 0, 0)
        self._tabs_layout.setSpacing(TabBarConfig.ITEM_SPACING)
        self._tabs_layout.addStretch()
        self._main_layout.addWidget(self._tabs_container, 1)

        self._right_scroll_btn = TabBarScrollButton('right', self)
        self._right_scroll_btn.clicked.connect(self._scroll_right)
        self._right_scroll_btn.hide()
        self._main_layout.addWidget(self._right_scroll_btn)

        if self._show_add_button:
            self._add_button = TabAddButton(self)
            self._add_button.clicked.connect(self.tabAddRequested.emit)
            self._main_layout.addWidget(self._add_button)
        else:
            self._add_button = None

    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme(theme)

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        bg_color = self.get_style_color(self._current_theme, 'tabbar.background', QColor(32, 32, 32))

        cache_key: Tuple[str] = (bg_color.name(),)

        def build_stylesheet() -> str:
            return f"background: {bg_color.name()};"

        qss = self._get_cached_stylesheet(cache_key, build_stylesheet)
        self.setStyleSheet(qss)
        self.update()

    def addTab(
        self, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None,
        select: bool = False
    ) -> TabItem:
        item_key = key or text

        if item_key in self._item_keys:
            return self._item_keys[item_key]

        item = TabItem(text, self, item_key, closable, icon)
        item.clicked.connect(lambda: self._on_item_clicked(item))
        item.closeRequested.connect(lambda: self._on_close_requested(item))

        self._items.append(item)
        self._item_keys[item_key] = item

        self._tabs_layout.insertWidget(self._tabs_layout.count() - 1, item)

        if len(self._items) == 1 or select:
            self.setCurrentItem(item_key)

        self._update_scroll_buttons()
        self.tabAdded.emit(item_key)

        return item

    def insertTab(
        self, 
        index: int, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ) -> TabItem:
        item_key = key or text

        if item_key in self._item_keys:
            return self._item_keys[item_key]

        item = TabItem(text, self, item_key, closable, icon)
        item.clicked.connect(lambda: self._on_item_clicked(item))
        item.closeRequested.connect(lambda: self._on_close_requested(item))

        actual_index = max(0, min(index, len(self._items)))

        self._items.insert(actual_index, item)
        self._item_keys[item_key] = item

        self._tabs_layout.insertWidget(actual_index, item)

        if self._current_index >= actual_index:
            self._current_index += 1

        if len(self._items) == 1:
            self.setCurrentIndex(0)

        self._update_scroll_buttons()
        self.tabAdded.emit(item_key)

        return item

    def removeTab(self, key: str) -> bool:
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
        elif self._current_index > index:
            self._current_index -= 1

        self._items.remove(item)
        del self._item_keys[key]
        self._tabs_layout.removeWidget(item)
        item.cleanup()
        item.deleteLater()

        self._update_scroll_buttons()
        self.tabRemoved.emit(key)

        return True

    def clear(self) -> None:
        for item in self._items[:]:
            self._tabs_layout.removeWidget(item)
            item.cleanup()
            item.deleteLater()

        self._items.clear()
        self._item_keys.clear()
        self._current_index = -1
        self._current_key = None
        self._update_scroll_buttons()

    def count(self) -> int:
        return len(self._items)

    def tabAt(self, index: int) -> Optional[TabItem]:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def tab(self, key: str) -> Optional[TabItem]:
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

    def _on_item_clicked(self, item: TabItem) -> None:
        index = self._items.index(item)
        self._select_item(index)

    def _on_close_requested(self, item: TabItem) -> None:
        self.tabCloseRequested.emit(item.key())

    def _select_item(self, index: int) -> None:
        if not (0 <= index < len(self._items)):
            return

        old_index = self._current_index
        self._current_index = index

        for i, item in enumerate(self._items):
            item.setSelected(i == index)

        self._current_key = self._items[index].key()

        if old_index != index:
            self.currentChanged.emit(self._current_key)

    def _scroll_left(self) -> None:
        self._scroll_offset = max(0, self._scroll_offset - 100)
        self._apply_scroll()

    def _scroll_right(self) -> None:
        self._scroll_offset += 100
        self._apply_scroll()

    def _apply_scroll(self) -> None:
        self._update_scroll_buttons()

    def _update_scroll_buttons(self) -> None:
        total_width = sum(item.width() for item in self._items)
        visible_width = self._tabs_container.width()

        if total_width > visible_width:
            self._left_scroll_btn.show()
            self._right_scroll_btn.show()
        else:
            self._left_scroll_btn.hide()
            self._right_scroll_btn.hide()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_scroll_buttons()

    def keyPressEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Tab:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    if self._current_index > 0:
                        self.setCurrentIndex(self._current_index - 1)
                    elif len(self._items) > 0:
                        self.setCurrentIndex(len(self._items) - 1)
                else:
                    if self._current_index < len(self._items) - 1:
                        self.setCurrentIndex(self._current_index + 1)
                    elif len(self._items) > 0:
                        self.setCurrentIndex(0)
                return

            if event.key() == Qt.Key.Key_F4:
                if 0 <= self._current_index < len(self._items):
                    item = self._items[self._current_index]
                    if item.isClosable():
                        self.tabCloseRequested.emit(item.key())
                return

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

        if self._add_button:
            self._add_button.cleanup()

        if self._left_scroll_btn:
            self._left_scroll_btn.cleanup()

        if self._right_scroll_btn:
            self._right_scroll_btn.cleanup()

        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class TabWidget(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    WinUI3 风格的 TabWidget，组合 TabBar 和 QStackedWidget。

    功能特性:
    - 完整的标签页界面
    - 键盘快捷键支持
    - 添加选项卡按钮
    - 主题集成

    Design Reference: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tab-view
    """

    currentChanged = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)
    tabAddRequested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None, show_add_button: bool = True):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._pages: Dict[str, QWidget] = {}
        self._page_keys: List[str] = []
        self._show_add_button = show_add_button

        self._init_ui()

    def _init_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._tab_bar = TabBar(self, self._show_add_button)
        self._tab_bar.currentChanged.connect(self._on_tab_changed)
        self._tab_bar.tabCloseRequested.connect(self._on_tab_close_requested)
        self._tab_bar.tabAddRequested.connect(self.tabAddRequested.emit)
        self._main_layout.addWidget(self._tab_bar)

        self._stacked_widget = QStackedWidget(self)
        self._main_layout.addWidget(self._stacked_widget, 1)

    def _on_tab_changed(self, key: str) -> None:
        if key in self._pages:
            index = self._page_keys.index(key)
            self._stacked_widget.setCurrentIndex(index)
            self.currentChanged.emit(index)

    def _on_tab_close_requested(self, key: str) -> None:
        if key in self._pages:
            index = self._page_keys.index(key)
            self.tabCloseRequested.emit(index)
            self.removeTab(key)

    def addTab(
        self, 
        page: QWidget, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ) -> int:
        item_key = key or text

        self._pages[item_key] = page
        self._page_keys.append(item_key)
        self._stacked_widget.addWidget(page)

        self._tab_bar.addTab(text, item_key, closable, icon)

        if len(self._page_keys) == 1:
            self._stacked_widget.setCurrentIndex(0)

        return len(self._page_keys) - 1

    def insertTab(
        self, 
        index: int, 
        page: QWidget, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True,
        icon: Optional[QIcon] = None
    ) -> int:
        item_key = key or text

        actual_index = max(0, min(index, len(self._page_keys)))

        self._pages[item_key] = page
        self._page_keys.insert(actual_index, item_key)
        self._stacked_widget.insertWidget(actual_index, page)

        self._tab_bar.insertTab(actual_index, text, item_key, closable, icon)

        return actual_index

    def removeTab(self, key: str) -> bool:
        if key not in self._pages:
            return False

        page = self._pages[key]
        index = self._page_keys.index(key)

        self._stacked_widget.removeWidget(page)
        self._page_keys.remove(key)
        del self._pages[key]

        self._tab_bar.removeTab(key)

        page.deleteLater()

        return True

    def clear(self) -> None:
        for key in list(self._pages.keys()):
            self.removeTab(key)

    def count(self) -> int:
        return len(self._page_keys)

    def currentIndex(self) -> int:
        return self._stacked_widget.currentIndex()

    def setCurrentIndex(self, index: int) -> None:
        if 0 <= index < len(self._page_keys):
            self._stacked_widget.setCurrentIndex(index)
            self._tab_bar.setCurrentItem(self._page_keys[index])

    def currentKey(self) -> Optional[str]:
        index = self._stacked_widget.currentIndex()
        if 0 <= index < len(self._page_keys):
            return self._page_keys[index]
        return None

    def setCurrentKey(self, key: str) -> None:
        if key in self._pages:
            index = self._page_keys.index(key)
            self.setCurrentIndex(index)

    def currentWidget(self) -> Optional[QWidget]:
        return self._stacked_widget.currentWidget()

    def widget(self, key: str) -> Optional[QWidget]:
        return self._pages.get(key)

    def widgetAt(self, index: int) -> Optional[QWidget]:
        if 0 <= index < len(self._page_keys):
            return self._pages.get(self._page_keys[index])
        return None

    def tabBar(self) -> TabBar:
        return self._tab_bar

    def setAddButtonVisible(self, visible: bool) -> None:
        if self._tab_bar._add_button:
            self._tab_bar._add_button.setVisible(visible)

    def cleanup(self) -> None:
        self._tab_bar.cleanup()
        self._clear_stylesheet_cache()
        self.clear_overrides()
