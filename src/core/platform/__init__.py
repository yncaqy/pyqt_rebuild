"""
Platform abstraction layer for frameless window functionality.

This module provides a unified interface for platform-specific operations
such as window management, corner preferences, and maximization.

Supported platforms:
- Windows (win32)
- macOS (darwin) - Placeholder for future implementation
- Linux - Placeholder for future implementation
"""

import sys
import logging
from typing import Optional, Protocol

logger = logging.getLogger(__name__)


class WindowPlatform(Protocol):
    """Protocol defining the interface for platform-specific window operations."""

    def set_corner_preference(self, hwnd: int, rounded: bool = True) -> bool:
        """Set window corner preference for rounded corners.

        Args:
            hwnd: Window handle
            rounded: Whether to use rounded corners

        Returns:
            True if successful, False otherwise
        """
        ...

    def maximize_window(self, hwnd: int) -> bool:
        """Maximize window to fill the current monitor's work area.

        Args:
            hwnd: Window handle

        Returns:
            True if successful, False otherwise
        """
        ...


class BasePlatform:
    """Base class for platform implementations with graceful degradation."""

    def set_corner_preference(self, hwnd: int, rounded: bool = True) -> bool:
        """Default implementation - no operation."""
        logger.debug(f"set_corner_preference not implemented on this platform")
        return False

    def maximize_window(self, hwnd: int) -> bool:
        """Default implementation - no operation."""
        logger.debug(f"maximize_window not implemented on this platform")
        return False


def get_platform() -> WindowPlatform:
    """Get the appropriate platform implementation for the current system.

    Returns:
        Platform implementation instance
    """
    platform_name = sys.platform

    if platform_name == 'win32':
        from .windows import WindowsPlatform
        return WindowsPlatform()
    elif platform_name == 'darwin':
        from .darwin import DarwinPlatform
        return DarwinPlatform()
    else:
        # Default/fallback platform
        logger.info(f"Using base platform implementation for {platform_name}")
        return BasePlatform()


# Singleton instance
_platform_instance: Optional[WindowPlatform] = None


def get_platform_instance() -> WindowPlatform:
    """Get or create the singleton platform instance.

    Returns:
        Platform implementation instance
    """
    global _platform_instance
    if _platform_instance is None:
        _platform_instance = get_platform()
    return _platform_instance
