"""
Containers Package

Provides container widgets with theme support.
"""

from .themed_widget import ThemedWidget
from .themed_group_box import ThemedGroupBox
from .themed_scroll_area import ThemedScrollArea
from .custom_scroll_bar import CustomScrollBar
from .elevated_card_widget import ElevatedCardWidget
from .splitter import Splitter, AnimatedSplitter, SplitterHandle, SplitterPanel

__all__ = [
    'ThemedWidget', 
    'ThemedGroupBox', 
    'ThemedScrollArea', 
    'CustomScrollBar', 
    'ElevatedCardWidget',
    'Splitter',
    'AnimatedSplitter',
    'SplitterHandle',
    'SplitterPanel'
]
