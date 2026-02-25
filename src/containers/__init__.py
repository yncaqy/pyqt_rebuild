"""
Container Components Package

This package provides high-level container components that combine
multiple UI elements and provide complex layouts and functionality.

Components:
    FramelessWindow: Modern frameless window with custom title bar,
                     edge resizing, and theme support

Usage:
    from containers import FramelessWindow

    window = FramelessWindow()
    window.setTitle("My Application")
    window.setLayout(layout)
    window.show()
"""

from .frameless_window import FramelessWindow, TitleBar, WindowConfig

__all__ = [
    'FramelessWindow',
    'TitleBar',
    'WindowConfig',
]
