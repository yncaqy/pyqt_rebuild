"""
Pivot Component

A fluent design style pivot/segmented widget for tab-like navigation.

Features:
- Smooth underline animation when switching tabs
- Horizontal layout with auto-sizing items
- Keyboard navigation support
- Theme integration
- Dynamic add/remove items
"""

from typing import Optional, List, Dict, Any, Union
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer, QEvent, pyqtProperty
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor

from core.theme_manager import ThemeManager, Theme


class PivotConfig:
    """Configuration constants for Pivot component."""
    
    ITEM_PADDING_H = 16
    ITEM_PADDING_V = 8
    ITEM_SPACING = 4
    
    UNDERLINE_HEIGHT = 3
    UNDERLINE_OFFSET = 4
    
    FONT_SIZE = 14
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_SELECTED = 600
    
    ANIMATION_DURATION = 200
    
    MIN_ITEM_WIDTH = 60
    MAX_ITEM_WIDTH = 200


class PivotItem(QWidget):
    """
    Individual pivot item widget.
    
    Features:
    - Text display with hover state
    - Selected state styling
    - Click handling
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
        self._hover_opacity = 0.0
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
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
            self.update()
    
    def _update_size(self) -> None:
        """Update widget size based on text."""
        font = QFont()
        font.setPixelSize(PivotConfig.FONT_SIZE)
        font.setWeight(
            PivotConfig.FONT_WEIGHT_SELECTED if self._selected 
            else PivotConfig.FONT_WEIGHT_NORMAL
        )
        
        from PyQt6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self._text)
        
        width = max(
            PivotConfig.MIN_ITEM_WIDTH,
            min(text_width + PivotConfig.ITEM_PADDING_H * 2, PivotConfig.MAX_ITEM_WIDTH)
        )
        height = fm.height() + PivotConfig.ITEM_PADDING_V * 2
        
        self.setFixedHeight(height)
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
        
        # Draw hover background
        if self._hovered and not self._selected:
            hover_color = theme.get_color('pivot.item.hover', QColor(255, 255, 255, 30))
            hover_color.setAlphaF(self._hover_opacity * 0.3)
            painter.fillRect(rect, hover_color)
        
        # Draw text
        font = QFont()
        font.setPixelSize(PivotConfig.FONT_SIZE)
        font.setWeight(
            PivotConfig.FONT_WEIGHT_SELECTED if self._selected 
            else PivotConfig.FONT_WEIGHT_NORMAL
        )
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
    Animated underline widget for Pivot.
    
    Features:
    - Smooth position and width animation
    - Theme-aware styling
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
        """Set geometry to cover parent widget."""
        self.setGeometry(parent_rect)
    
    def animate_to(self, x: int, width: int) -> None:
        """Animate underline to new position."""
        y = self.height() - PivotConfig.UNDERLINE_HEIGHT - PivotConfig.UNDERLINE_OFFSET // 2
        
        self._target_rect = QRect(int(x), int(y), int(width), PivotConfig.UNDERLINE_HEIGHT)
        
        # Position animation
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
        
        # Get underline color from theme
        underline_color = theme.get_color('pivot.underline', QColor(52, 152, 219))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(underline_color)
        painter.drawRoundedRect(self._current_rect, 2, 2)
    
    def cleanup(self) -> None:
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class Pivot(QWidget):
    """
    Fluent Design style pivot widget for tab-like navigation.
    
    Features:
    - Smooth underline animation when switching tabs
    - Horizontal layout with auto-sizing items
    - Keyboard navigation support
    - Theme integration
    - Dynamic add/remove items
    
    Usage:
        pivot = Pivot()
        pivot.addItem("Home", "home")
        pivot.addItem("Settings", "settings")
        pivot.addItem("About", "about")
        
        pivot.currentChanged.connect(lambda key: print(f"Selected: {key}"))
        
        # Connect to stacked widget
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
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setFixedHeight(40)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _init_ui(self) -> None:
        """Initialize the UI layout."""
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(PivotConfig.ITEM_SPACING)
        self._main_layout.addStretch()
        
        # Create underline widget (will be positioned at bottom)
        self._underline = PivotUnderline(self)
        self._underline.hide()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()
    
    def addItem(
        self, 
        text: str, 
        key: Optional[str] = None,
        select: bool = False
    ) -> PivotItem:
        """
        Add a new item to the pivot.
        
        Args:
            text: Display text for the item
            key: Optional unique key (defaults to text)
            select: Whether to select this item immediately
            
        Returns:
            The created PivotItem
        """
        item_key = key or text
        
        if item_key in self._item_keys:
            return self._item_keys[item_key]
        
        item = PivotItem(text, self, item_key)
        item.clicked.connect(lambda: self._on_item_clicked(item))
        
        self._items.append(item)
        self._item_keys[item_key] = item
        
        # Insert before stretch
        self._main_layout.insertWidget(self._main_layout.count() - 1, item)
        
        # Select first item by default or if requested
        if len(self._items) == 1 or select:
            self.setCurrentItem(item_key)
        
        return item
    
    def removeItem(self, key: str) -> bool:
        """
        Remove an item from the pivot.
        
        Args:
            key: Key of the item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        if key not in self._item_keys:
            return False
        
        item = self._item_keys[key]
        index = self._items.index(item)
        
        # Update selection if needed
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
        self._main_layout.removeWidget(item)
        item.cleanup()
        item.deleteLater()
        
        return True
    
    def clear(self) -> None:
        """Remove all items from the pivot."""
        for item in self._items[:]:
            self._main_layout.removeWidget(item)
            item.cleanup()
            item.deleteLater()
        
        self._items.clear()
        self._item_keys.clear()
        self._current_index = -1
        self._current_key = None
        self._underline.hide()
    
    def count(self) -> int:
        """Return the number of items."""
        return len(self._items)
    
    def itemAt(self, index: int) -> Optional[PivotItem]:
        """Get item at index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def item(self, key: str) -> Optional[PivotItem]:
        """Get item by key."""
        return self._item_keys.get(key)
    
    def currentIndex(self) -> int:
        """Return the index of the current item."""
        return self._current_index
    
    def setCurrentIndex(self, index: int) -> None:
        """Set the current item by index."""
        if 0 <= index < len(self._items) and index != self._current_index:
            self._select_item(index)
    
    def currentKey(self) -> Optional[str]:
        """Return the key of the current item."""
        return self._current_key
    
    def setCurrentItem(self, key: str) -> None:
        """Set the current item by key."""
        if key in self._item_keys:
            index = self._items.index(self._item_keys[key])
            self.setCurrentIndex(index)
    
    def currentText(self) -> str:
        """Return the text of the current item."""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index].text()
        return ""
    
    def _on_item_clicked(self, item: PivotItem) -> None:
        """Handle item click."""
        index = self._items.index(item)
        self._select_item(index)
    
    def _select_item(self, index: int) -> None:
        """Select item at index."""
        if not (0 <= index < len(self._items)):
            return
        
        old_index = self._current_index
        self._current_index = index
        
        # Update item states
        for i, item in enumerate(self._items):
            item.setSelected(i == index)
        
        # Update current key
        self._current_key = self._items[index].key()
        
        # Animate underline
        self._animate_underline(index)
        
        # Emit signal
        if old_index != index:
            self.currentChanged.emit(self._current_key)
    
    def _animate_underline(self, index: int) -> None:
        """Animate underline to item at index."""
        if not (0 <= index < len(self._items)):
            return
        
        item = self._items[index]
        item_rect = item.geometry()
        
        # Calculate underline position (centered under text)
        underline_width = min(item_rect.width() - 16, 60)
        underline_x = item_rect.x() + (item_rect.width() - underline_width) // 2
        
        # Update underline geometry to cover pivot
        self._underline.setGeometryFromParent(self.rect())
        self._underline.show()
        self._underline.raise_()
        self._underline.animate_to(underline_x, underline_width)
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        
        # Reposition underline
        if 0 <= self._current_index < len(self._items):
            self._animate_underline(self._current_index)
    
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
        
        if hasattr(self, '_underline') and self._underline:
            self._underline.cleanup()
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
