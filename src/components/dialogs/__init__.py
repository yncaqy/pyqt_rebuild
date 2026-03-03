"""
Dialogs Package

Provides modal dialog components with theme support.
"""

from .message_box import MessageBox, MessageBoxBase
from .color_dialog import ColorDialog

__all__ = ['MessageBox', 'MessageBoxBase', 'ColorDialog']
