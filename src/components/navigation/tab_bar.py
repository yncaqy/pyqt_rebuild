"""
标签栏组件

Fluent Design 风格的标签栏控件，用于在多个标签页之间切换。

功能特性:
- 动态添加/删除标签，带关闭按钮
- 平滑的选择动画
- 键盘导航支持
- 主题集成
- 溢出处理，带滚动按钮
- 标签拖拽支持（可选）
- 统一的 ThemedComponentBase 基类

参考: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
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
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor, QFontMetrics, QIcon

from core.themed_component_base import ThemedComponentBase
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_manager import ThemeManager
from core.icon_manager import IconManager
from themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG


class TabBarConfig:
    """标签栏配置常量。"""
    
    ITEM_PADDING_H = WINUI3_CONTROL_SIZING['tab']['padding_h']
    ITEM_PADDING_V = WINUI3_CONTROL_SIZING['tab']['padding_v']
    ITEM_SPACING = 2
    CLOSE_BUTTON_SIZE = 16
    CLOSE_BUTTON_MARGIN = 4
    FONT_SIZE = FONT_CONFIG['size']['body']
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_SELECTED = 600
    ANIMATION_DURATION = 150
    MIN_ITEM_WIDTH = WINUI3_CONTROL_SIZING['tab']['min_width']
    MAX_ITEM_WIDTH = 200
    ITEM_HEIGHT = WINUI3_CONTROL_SIZING['tab']['min_height']
    INDICATOR_HEIGHT = 3


class TabCloseButton(ThemedComponentBase):
    """标签关闭按钮。"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._hovered = False
        self._pressed = False
        self._icon_mgr = IconManager.instance()
        
        super().__init__(parent)
        
        self.setFixedSize(16, 16)
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
            painter.drawRoundedRect(rect, 3, 3)
        
        icon_color = self.get_theme_color('tabbar.close_icon', QColor(140, 140, 140))
        if self._hovered:
            icon_color = self.get_theme_color('tabbar.close_icon_hover', QColor(255, 255, 255))
        
        icon = self._icon_mgr.get_colored_icon('window_close', icon_color, 12)
        icon_size = 12
        x = (rect.width() - icon_size) // 2
        y = (rect.height() - icon_size) // 2
        icon.paint(painter, x, y, icon_size, icon_size)


class TabItem(ThemedComponentBase):
    """单个标签项控件。"""
    
    clicked = pyqtSignal()
    closeRequested = pyqtSignal()
    
    def __init__(
        self, 
        text: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None,
        closable: bool = True
    ):
        self._text = text
        self._key = item_key or text
        self._closable = closable
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
            TabBarConfig.ITEM_PADDING_H,
            TabBarConfig.ITEM_PADDING_V
        )
        self._main_layout.setSpacing(TabBarConfig.CLOSE_BUTTON_MARGIN)
        
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
        
        if self._hovered and not self._selected:
            hover_color = self.get_theme_color('tabbar.item.hover', QColor(255, 255, 255, 20))
            hover_color.setAlpha(int(hover_color.alpha() * self._hover_opacity))
            painter.fillRect(rect, hover_color)
        
        text_color = self.get_theme_color(
            'tabbar.item.text_selected' if self._selected else 'tabbar.item.text',
            QColor(0, 120, 212) if self._selected else QColor(100, 100, 100)
        )
        self._text_label.setStyleSheet(f"color: {text_color.name()}; background: transparent;")
    
    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self._text_label.font())
        text_width = fm.horizontalAdvance(self._text)
        
        width = text_width + TabBarConfig.ITEM_PADDING_H * 2
        
        if self._closable:
            width += TabBarConfig.CLOSE_BUTTON_SIZE + TabBarConfig.CLOSE_BUTTON_MARGIN
        
        width = max(TabBarConfig.MIN_ITEM_WIDTH, min(width, TabBarConfig.MAX_ITEM_WIDTH))
        
        return QSize(width, TabBarConfig.ITEM_HEIGHT)
    
    def cleanup(self) -> None:
        if self._close_button:
            self._close_button.cleanup()
        super().cleanup()


class TabIndicator(ThemedComponentBase):
    """选中标签的动画指示器。"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._target_rect = QRect()
        self._current_rect = QRect()
        
        super().__init__(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self.update()
    
    def animate_to(self, rect: QRect) -> None:
        self._target_rect = rect
        
        self._animation = QPropertyAnimation(self, b"indicatorRect")
        self._animation.setDuration(TabBarConfig.ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setStartValue(self._current_rect)
        self._animation.setEndValue(self._target_rect)
        self._animation.start()
    
    def getIndicatorRect(self) -> QRect:
        return self._current_rect
    
    def setIndicatorRect(self, rect: QRect) -> None:
        self._current_rect = rect
        self.update()
    
    indicatorRect = pyqtProperty(QRect, getIndicatorRect, setIndicatorRect)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        indicator_color = self.get_theme_color('tabbar.indicator', QColor(52, 152, 219))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(indicator_color)
        painter.drawRoundedRect(self._current_rect, 2, 2)


class TabBarScrollButton(ThemedComponentBase):
    """滚动按钮。"""
    
    clicked = pyqtSignal()
    
    def __init__(self, direction: str = 'left', parent: Optional[QWidget] = None):
        self._direction = direction
        self._hovered = False
        
        super().__init__(parent)
        
        self.setFixedSize(24, TabBarConfig.ITEM_HEIGHT)
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
            painter.fillRect(self.rect(), hover_color)
        
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
    Fluent Design 风格标签栏控件。
    
    功能特性:
    - 动态添加/删除标签，带关闭按钮
    - 平滑的选择动画
    - 键盘导航支持
    - 主题集成
    - 溢出处理，带滚动按钮
    - Style override 支持
    - Stylesheet caching
    """
    
    currentChanged = pyqtSignal(str)
    tabCloseRequested = pyqtSignal(str)
    tabAdded = pyqtSignal(str)
    tabRemoved = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_style_override()
        self._init_stylesheet_cache()
        
        self._items: List[TabItem] = []
        self._item_keys: Dict[str, TabItem] = {}
        self._current_index = -1
        self._current_key: Optional[str] = None
        self._scroll_offset = 0
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        
        self.setFixedHeight(TabBarConfig.ITEM_HEIGHT + 4)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)
    
    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, TabBarConfig.INDICATOR_HEIGHT)
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
        
        self._indicator = TabIndicator(self)
        self._indicator.hide()
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        bg_color = self.get_style_color(self._current_theme, 'tabbar.background', QColor(30, 30, 30))
        
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
        select: bool = False
    ) -> TabItem:
        item_key = key or text
        
        if item_key in self._item_keys:
            return self._item_keys[item_key]
        
        item = TabItem(text, self, item_key, closable)
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
        closable: bool = True
    ) -> TabItem:
        item_key = key or text
        
        if item_key in self._item_keys:
            return self._item_keys[item_key]
        
        item = TabItem(text, self, item_key, closable)
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
                self._indicator.hide()
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
        self._indicator.hide()
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
    
    def setTabText(self, key: str, text: str) -> bool:
        if key in self._item_keys:
            self._item_keys[key].setText(text)
            return True
        return False
    
    def setTabClosable(self, key: str, closable: bool) -> bool:
        if key in self._item_keys:
            return True
        return False
    
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
        
        self._animate_indicator(index)
        
        if old_index != index:
            self.currentChanged.emit(self._current_key)
    
    def _animate_indicator(self, index: int) -> None:
        if not (0 <= index < len(self._items)):
            return
        
        item = self._items[index]
        item_rect = item.geometry()
        
        indicator_width = min(item_rect.width() - 8, 40)
        indicator_x = item_rect.x() + (item_rect.width() - indicator_width) // 2
        indicator_y = self.height() - TabBarConfig.INDICATOR_HEIGHT
        
        target_rect = QRect(
            int(indicator_x), 
            int(indicator_y), 
            int(indicator_width), 
            TabBarConfig.INDICATOR_HEIGHT
        )
        
        self._indicator.setGeometry(self.rect())
        self._indicator.show()
        self._indicator.raise_()
        self._indicator.animate_to(target_rect)
    
    def _scroll_left(self) -> None:
        if self._scroll_offset > 0:
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
        
        if 0 <= self._current_index < len(self._items):
            self._animate_indicator(self._current_index)
    
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
        
        if self._indicator:
            self._indicator.cleanup()
        
        if self._left_scroll_btn:
            self._left_scroll_btn.cleanup()
        
        if self._right_scroll_btn:
            self._right_scroll_btn.cleanup()
        
        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class TabWidget(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    A combined TabBar and QStackedWidget.
    
    This widget provides a complete tab interface with a tab bar
    at the top and a stacked widget for content below.
    """
    
    currentChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_style_override()
        self._init_stylesheet_cache()
        
        self._pages: Dict[str, QWidget] = {}
        self._page_keys: List[str] = []
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._tab_bar = TabBar(self)
        self._tab_bar.currentChanged.connect(self._on_tab_changed)
        self._tab_bar.tabCloseRequested.connect(self._on_tab_close_requested)
        self._main_layout.addWidget(self._tab_bar)
        
        self._stacked_widget = QStackedWidget(self)
        self._main_layout.addWidget(self._stacked_widget, 1)
    
    def _on_tab_changed(self, key: str) -> None:
        if key in self._pages:
            index = self._page_keys.index(key)
            self._stacked_widget.setCurrentIndex(index)
            self.currentChanged.emit(index)
    
    def _on_tab_close_requested(self, key: str) -> None:
        self.removeTab(key)
    
    def addTab(
        self, 
        page: QWidget, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True
    ) -> int:
        item_key = key or text
        
        self._pages[item_key] = page
        self._page_keys.append(item_key)
        self._stacked_widget.addWidget(page)
        
        self._tab_bar.addTab(text, item_key, closable)
        
        if len(self._page_keys) == 1:
            self._stacked_widget.setCurrentIndex(0)
        
        return len(self._page_keys) - 1
    
    def insertTab(
        self, 
        index: int, 
        page: QWidget, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True
    ) -> int:
        item_key = key or text
        
        actual_index = max(0, min(index, len(self._page_keys)))
        
        self._pages[item_key] = page
        self._page_keys.insert(actual_index, item_key)
        self._stacked_widget.insertWidget(actual_index, page)
        
        self._tab_bar.insertTab(actual_index, text, item_key, closable)
        
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
    
    def cleanup(self) -> None:
        self._tab_bar.cleanup()
        self._clear_stylesheet_cache()
        self.clear_overrides()
