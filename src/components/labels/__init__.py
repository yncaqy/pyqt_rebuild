#!/usr/bin/env python3
"""
Labels package for themed UI components.

This package contains label components with automatic theme integration:
- ThemedLabel: Theme-aware label with automatic styling updates
- ImageLabel: Image label with high DPI support

All components automatically adapt their appearance based on the current
application theme, providing consistent styling across the user interface.
"""

from .themed_label import ThemedLabel
from .image_label import ImageLabel

__all__ = [
    'ThemedLabel',
    'ImageLabel',
]