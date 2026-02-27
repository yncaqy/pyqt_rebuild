"""
TabBar Component

A fluent design style tab bar widget for switching between tabs.

Features:
- Dynamic add/remove tabs with close button
- Smooth selection animation
- Keyboard navigation support
- Theme integration
- Overflow handling with scroll buttons
- Tab drag support (optional)

Reference: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
"""

from typing import Optional, List, Dict, Callable
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

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager


class TabBarConfig:
    """Configuration constants for TabBar component."""
    
    ITEM_PADDING_H = 12
    ITEM_PADDING_V = 8
    ITEM_SPACING = 2
    
    CLOSE_BUTTON_SIZE = 16
    CLOSE_BUTTON_MARGIN = 4
    
    FONT_SIZE = 13
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_SELECTED = 500
    
    ANIMATION_DURATION = 150
    
    MIN_ITEM_WIDTH = 80
    MAX_ITEM_WIDTH = 200
    ITEM_HEIGHT = 36
    
    INDICATOR_HEIGHT = 3


class TabCloseButton(QPushButton):
    """Close button for tab items with fluent design style."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._hovered = False
        self._pressed = False
        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        theme = self._current_theme
        if not theme:
            return
        
        rect = self.rect()
        
        if self._hovered:
            if self._pressed:
                bg_color = theme.get_color('tabbar.close_pressed', QColor(60, 60, 60))
            else:
                bg_color = theme.get_color('tabbar.close_hover', QColor(70, 70, 70))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 3, 3)
        
        icon_color = theme.get_color('tabbar.close_icon', QColor(140, 140, 140))
        if self._hovered:
            icon_color = QColor(255, 255, 255)
        
        icon = self._icon_mgr.get_colored_icon('window_close', icon_color, 12)
        icon_size = 12
        x = (rect.width() - icon_size) // 2
        y = (rect.height() - icon_size) // 2
        icon.paint(painter, x, y, icon_size, icon_size)
    
    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class TabItem(QWidget):
    """
    Individual tab item widget.
    
    Features:
    - Text display with hover/selected state
    - Close button
    - Click handling
    """
    
    clicked = pyqtSignal()
    closeRequested = pyqtSignal()
    
    def __init__(
        self, 
        text: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None,
        closable: bool = True
    ):
        super().__init__(parent)
        
        self._text = text
        self._key = item_key or text
        self._closable = closable
        self._selected = False
        self._hovered = False
        self._hover_opacity = 0.0
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setFixedHeight(TabBarConfig.ITEM_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self._init_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _init_ui(self) -> None:
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(
            TabBarConfig.ITEM_PADDING_H,
            TabBarConfig.ITEM_PADDING_V,
            TabBarConfig.ITEM_PADDING_H // 2,
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
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self._update_style()
        self.update()
    
    def _update_style(self) -> None:
        if not self._current_theme:
            return
        
        font = QFont()
        font.setPixelSize(TabBarConfig.FONT_SIZE)
        font.setWeight(
            TabBarConfig.FONT_WEIGHT_SELECTED if self._selected 
            else TabBarConfig.FONT_WEIGHT_NORMAL
        )
        self._text_label.setFont(font)
        
        if self._selected:
            text_color = self._current_theme.get_color('tabbar.item.text_selected', QColor(255, 255, 255))
        else:
            text_color = self._current_theme.get_color('tabbar.item.text', QColor(180, 180, 180))
        
        self._text_label.setStyleSheet(f"color: {text_color.name()}; background: transparent;")
    
    def text(self) -> str:
        return self._text
    
    def setText(self, text: str) -> None:
        self._text = text
        self._text_label.setText(text)
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
            self._update_style()
            self.update()
    
    def isClosable(self) -> bool:
        return self._closable
    
    def _update_size(self) -> None:
        font = QFont()
        font.setPixelSize(TabBarConfig.FONT_SIZE)
        font.setWeight(TabBarConfig.FONT_WEIGHT_SELECTED)
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self._text)
        
        extra_width = TabBarConfig.ITEM_PADDING_H * 2
        if self._closable:
            extra_width += TabBarConfig.CLOSE_BUTTON_SIZE + TabBarConfig.CLOSE_BUTTON_MARGIN
        
        width = max(
            TabBarConfig.MIN_ITEM_WIDTH,
            min(text_width + extra_width, TabBarConfig.MAX_ITEM_WIDTH)
        )
        
        self.setMinimumWidth(int(width))
        self.setMaximumWidth(int(TabBarConfig.MAX_ITEM_WIDTH))
    
    def sizeHint(self) -> QSize:
        self._update_size()
        return super().sizeHint()
    
    def getHoverOpacity(self) -> float:
        return self._hover_opacity
    
    def setHoverOpacity(self, opacity: float) -> None:
        self._hover_opacity = opacity
        self.update()
    
    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)
    
    def _animate_hover(self, hover: bool) -> None:
        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(TabBarConfig.ANIMATION_DURATION)
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
        self._animate_hover(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self._current_theme
        if not theme:
            return
        
        rect = self.rect()
        
        if self._selected:
            bg_color = theme.get_color('tabbar.item.background_selected', QColor(50, 50, 50))
            painter.fillRect(rect, bg_color)
        elif self._hovered:
            hover_color = theme.get_color('tabbar.item.hover', QColor(255, 255, 255, 20))
            hover_color.setAlphaF(self._hover_opacity * 0.2)
            painter.fillRect(rect, hover_color)
    
    def cleanup(self) -> None:
        if hasattr(self, '_close_button') and self._close_button:
            self._close_button.cleanup()
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class TabIndicator(QWidget):
    """Animated indicator for selected tab."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._target_rect = QRect()
        self._current_rect = QRect()
        
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
        
        theme = self._current_theme
        if not theme:
            return
        
        indicator_color = theme.get_color('tabbar.indicator', QColor(52, 152, 219))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(indicator_color)
        painter.drawRoundedRect(self._current_rect, 2, 2)
    
    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class TabBarScrollButton(QPushButton):
    """Scroll button for overflow handling."""
    
    def __init__(self, direction: str = 'left', parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._direction = direction
        self._hovered = False
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setFixedSize(24, TabBarConfig.ITEM_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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
    
    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self._current_theme
        if not theme:
            return
        
        if self._hovered:
            hover_color = theme.get_color('tabbar.item.hover', QColor(255, 255, 255, 20))
            painter.fillRect(self.rect(), hover_color)
        
        icon_color = theme.get_color('tabbar.scroll_icon', QColor(150, 150, 150))
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
    
    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class TabBar(QWidget):
    """
    Fluent Design style tab bar widget.
    
    Features:
    - Dynamic add/remove tabs with close button
    - Smooth selection animation
    - Keyboard navigation support
    - Theme integration
    - Overflow handling with scroll buttons
    
    Signals:
        currentChanged: Emitted when current tab changes (key)
        tabCloseRequested: Emitted when tab close button is clicked (key)
        tabAdded: Emitted when a tab is added (key)
        tabRemoved: Emitted when a tab is removed (key)
    
    Usage:
        tab_bar = TabBar()
        tab_bar.addTab("Tab 1", "tab1")
        tab_bar.addTab("Tab 2", "tab2")
        tab_bar.addTab("Tab 3", "tab3", closable=False)
        
        tab_bar.currentChanged.connect(lambda key: print(f"Selected: {key}"))
        tab_bar.tabCloseRequested.connect(lambda key: print(f"Close: {key}"))
    """
    
    currentChanged = pyqtSignal(str)
    tabCloseRequested = pyqtSignal(str)
    tabAdded = pyqtSignal(str)
    tabRemoved = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items: List[TabItem] = []
        self._item_keys: Dict[str, TabItem] = {}
        self._current_index = -1
        self._current_key: Optional[str] = None
        self._scroll_offset = 0
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setFixedHeight(TabBarConfig.ITEM_HEIGHT + 4)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
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
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        bg_color = theme.get_color('tabbar.background', QColor(30, 30, 30))
        self.setStyleSheet(f"background: {bg_color.name()};")
        self.update()
    
    def addTab(
        self, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True,
        select: bool = False
    ) -> TabItem:
        """
        Add a new tab to the bar.
        
        Args:
            text: Display text for the tab
            key: Optional unique key (defaults to text)
            closable: Whether the tab can be closed
            select: Whether to select this tab immediately
            
        Returns:
            The created TabItem
        """
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
        """
        Insert a tab at the specified index.
        
        Args:
            index: Position to insert at
            text: Display text for the tab
            key: Optional unique key
            closable: Whether the tab can be closed
            
        Returns:
            The created TabItem
        """
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
        """
        Remove a tab from the bar.
        
        Args:
            key: Key of the tab to remove
            
        Returns:
            True if tab was removed, False if not found
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
        """Remove all tabs from the bar."""
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
        """Return the number of tabs."""
        return len(self._items)
    
    def tabAt(self, index: int) -> Optional[TabItem]:
        """Get tab at index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def tab(self, key: str) -> Optional[TabItem]:
        """Get tab by key."""
        return self._item_keys.get(key)
    
    def currentIndex(self) -> int:
        """Return the index of the current tab."""
        return self._current_index
    
    def setCurrentIndex(self, index: int) -> None:
        """Set the current tab by index."""
        if 0 <= index < len(self._items) and index != self._current_index:
            self._select_item(index)
    
    def currentKey(self) -> Optional[str]:
        """Return the key of the current tab."""
        return self._current_key
    
    def setCurrentItem(self, key: str) -> None:
        """Set the current tab by key."""
        if key in self._item_keys:
            index = self._items.index(self._item_keys[key])
            self.setCurrentIndex(index)
    
    def currentText(self) -> str:
        """Return the text of the current tab."""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index].text()
        return ""
    
    def setTabText(self, key: str, text: str) -> bool:
        """Set the text of a tab."""
        if key in self._item_keys:
            self._item_keys[key].setText(text)
            return True
        return False
    
    def setTabClosable(self, key: str, closable: bool) -> bool:
        """Set whether a tab is closable."""
        if key in self._item_keys:
            item = self._item_keys[key]
            if item.isClosable() != closable:
                pass
            return True
        return False
    
    def _on_item_clicked(self, item: TabItem) -> None:
        """Handle item click."""
        index = self._items.index(item)
        self._select_item(index)
    
    def _on_close_requested(self, item: TabItem) -> None:
        """Handle close button click."""
        self.tabCloseRequested.emit(item.key())
    
    def _select_item(self, index: int) -> None:
        """Select item at index."""
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
        """Animate indicator to item at index."""
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
        """Scroll tabs to the left."""
        if self._scroll_offset > 0:
            self._scroll_offset = max(0, self._scroll_offset - 100)
            self._apply_scroll()
    
    def _scroll_right(self) -> None:
        """Scroll tabs to the right."""
        self._scroll_offset += 100
        self._apply_scroll()
    
    def _apply_scroll(self) -> None:
        """Apply scroll offset to tabs container."""
        self._update_scroll_buttons()
    
    def _update_scroll_buttons(self) -> None:
        """Update visibility of scroll buttons."""
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
        """Handle keyboard navigation."""
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
        """Clean up resources."""
        for item in self._items:
            item.cleanup()
        
        if hasattr(self, '_indicator') and self._indicator:
            self._indicator.cleanup()
        
        if hasattr(self, '_left_scroll_btn') and self._left_scroll_btn:
            self._left_scroll_btn.cleanup()
        
        if hasattr(self, '_right_scroll_btn') and self._right_scroll_btn:
            self._right_scroll_btn.cleanup()
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class TabWidget(QWidget):
    """
    A combined TabBar and QStackedWidget.
    
    This widget provides a complete tab interface with a tab bar
    at the top and a stacked widget for content below.
    
    Usage:
        tab_widget = TabWidget()
        
        page1 = QWidget()
        page2 = QWidget()
        
        tab_widget.addTab(page1, "Page 1", "page1")
        tab_widget.addTab(page2, "Page 2", "page2")
    """
    
    currentChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
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
        """Handle tab bar current changed."""
        if key in self._pages:
            index = self._page_keys.index(key)
            self._stacked_widget.setCurrentIndex(index)
            self.currentChanged.emit(index)
    
    def _on_tab_close_requested(self, key: str) -> None:
        """Handle tab close request."""
        self.removeTab(key)
    
    def addTab(
        self, 
        page: QWidget, 
        text: str, 
        key: Optional[str] = None,
        closable: bool = True
    ) -> int:
        """
        Add a tab with associated page.
        
        Args:
            page: Widget to display as tab content
            text: Tab display text
            key: Optional unique key
            closable: Whether tab can be closed
            
        Returns:
            Index of the added tab
        """
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
        """Insert a tab at the specified index."""
        item_key = key or text
        
        actual_index = max(0, min(index, len(self._page_keys)))
        
        self._pages[item_key] = page
        self._page_keys.insert(actual_index, item_key)
        self._stacked_widget.insertWidget(actual_index, page)
        
        self._tab_bar.insertTab(actual_index, text, item_key, closable)
        
        return actual_index
    
    def removeTab(self, key: str) -> bool:
        """Remove a tab by key."""
        if key not in self._pages:
            return False
        
        page = self._pages[key]
        index = self._page_keys.index(key)
        
        self._stacked_widget.removeWidget(page)
        del self._pages[key]
        self._page_keys.remove(key)
        
        self._tab_bar.removeTab(key)
        
        page.deleteLater()
        
        return True
    
    def clear(self) -> None:
        """Remove all tabs."""
        for key in list(self._pages.keys()):
            self.removeTab(key)
    
    def count(self) -> int:
        """Return the number of tabs."""
        return len(self._page_keys)
    
    def currentIndex(self) -> int:
        """Return the index of the current tab."""
        return self._stacked_widget.currentIndex()
    
    def setCurrentIndex(self, index: int) -> None:
        """Set the current tab by index."""
        if 0 <= index < len(self._page_keys):
            key = self._page_keys[index]
            self._tab_bar.setCurrentItem(key)
    
    def currentKey(self) -> Optional[str]:
        """Return the key of the current tab."""
        return self._tab_bar.currentKey()
    
    def setCurrentKey(self, key: str) -> None:
        """Set the current tab by key."""
        self._tab_bar.setCurrentItem(key)
    
    def page(self, key: str) -> Optional[QWidget]:
        """Get page by key."""
        return self._pages.get(key)
    
    def tabBar(self) -> TabBar:
        """Get the tab bar widget."""
        return self._tab_bar
    
    def stackedWidget(self) -> QStackedWidget:
        """Get the stacked widget."""
        return self._stacked_widget
