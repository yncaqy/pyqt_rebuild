"""
FlowLayout Component

Provides a flow layout that automatically wraps items when they exceed
the viewport width.

Features:
- Automatic line wrapping
- Adjustable spacing and margins
- Support for left-to-right and right-to-left layouts
- Height-for-width support
"""

import logging
from typing import List, Optional, Tuple
from PyQt6.QtCore import (
    Qt, QRect, QSize, QPoint, QMargins
)
from PyQt6.QtWidgets import QLayout, QLayoutItem, QWidgetItem, QWidget
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class FlowLayout(QLayout):
    """
    Flow layout that automatically wraps items when they exceed
    the viewport width.
    
    Features:
    - Automatic line wrapping
    - Adjustable spacing and margins
    - Support for left-to-right and right-to-left layouts
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._item_list: List[QLayoutItem] = []
        self._horizontal_spacing: int = 10
        self._vertical_spacing: int = 10
        self._margins = QMargins(0, 0, 0, 0)
        
        if parent:
            self.setParent(parent)
        
        logger.debug("FlowLayout initialized")
    
    def addItem(self, item: QLayoutItem) -> None:
        """Add an item to the layout."""
        self._item_list.append(item)
        self.invalidate()
    
    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)
    
    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        """Return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None
    
    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._item_list):
            item = self._item_list.pop(index)
            self.invalidate()
            return item
        return None
    
    def expandingDirections(self) -> Qt.Orientation:
        """Return the expanding directions."""
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self) -> bool:
        """Return True if the layout has height for width."""
        return True
    
    def heightForWidth(self, width: int) -> int:
        """Return the height for the given width."""
        height = self._do_layout(QRect(0, 0, width, 0), test_only=True)
        return height
    
    def setGeometry(self, rect: QRect) -> None:
        """Set the geometry of the layout."""
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)
    
    def sizeHint(self) -> QSize:
        """Return the size hint for the layout."""
        return self.minimumSize()
    
    def minimumSize(self) -> QSize:
        """Return the minimum size for the layout."""
        size = QSize()
        
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        size += QSize(
            self._margins.left() + self._margins.right(),
            self._margins.top() + self._margins.bottom()
        )
        
        return size
    
    def setHorizontalSpacing(self, spacing: int) -> None:
        """Set the horizontal spacing between items."""
        self._horizontal_spacing = spacing
        self.invalidate()
    
    def horizontalSpacing(self) -> int:
        """Return the horizontal spacing."""
        return self._horizontal_spacing
    
    def setVerticalSpacing(self, spacing: int) -> None:
        """Set the vertical spacing between lines."""
        self._vertical_spacing = spacing
        self.invalidate()
    
    def verticalSpacing(self) -> int:
        """Return the vertical spacing."""
        return self._vertical_spacing
    
    def setSpacing(self, spacing: int) -> None:
        """Set both horizontal and vertical spacing."""
        self._horizontal_spacing = spacing
        self._vertical_spacing = spacing
        self.invalidate()
    
    def setContentsMargins(self, left: int, top: int, right: int, bottom: int) -> None:
        """Set the content margins."""
        self._margins = QMargins(left, top, right, bottom)
        self.invalidate()
    
    def contentsMargins(self) -> QMargins:
        """Return the content margins."""
        return self._margins
    
    def _do_layout(self, rect: QRect, test_only: bool = False) -> int:
        """
        Perform the layout calculation.
        
        Args:
            rect: The available rectangle
            test_only: If True, only calculate height without positioning
            
        Returns:
            The total height of the layout
        """
        left = self._margins.left()
        top = self._margins.top()
        right = self._margins.right()
        bottom = self._margins.bottom()
        
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        
        x = effective_rect.x()
        y = effective_rect.y()
        
        line_height = 0
        space_x = self._horizontal_spacing
        space_y = self._vertical_spacing
        
        for item in self._item_list:
            if item.isEmpty():
                continue
            
            widget = item.widget()
            if widget and widget.isHidden():
                continue
            
            item_size = item.sizeHint()
            
            next_x = x + item_size.width() + space_x
            
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item_size.width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))
            
            x = next_x
            line_height = max(line_height, item_size.height())
        
        total_height = y + line_height - rect.y() + bottom
        
        return total_height
    
    def clear(self) -> None:
        """Clear all items from the layout."""
        while self._item_list:
            item = self._item_list.pop()
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                item.layout().deleteLater()
        self.invalidate()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.clear()
        logger.debug("FlowLayout cleaned up")
