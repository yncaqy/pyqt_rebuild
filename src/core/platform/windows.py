"""
Windows-specific platform implementation for frameless window features.

Provides Windows 11 rounded corners support and custom window management.
"""

import ctypes
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Windows API imports
from ctypes import windll, byref, c_void_p, c_ulong, c_int, POINTER
from ctypes.wintypes import RECT, DWORD

# Windows API constants
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2
DWMWCP_DONOTROUND = 1
DWMWCP_SMALL = 0
SWP_FRAMECHANGED = 0x0020
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
MONITOR_DEFAULTTONEAREST = 0x00000002
MONITORINFOF_PRIMARY = 0x00000001


class MONITORINFO(ctypes.Structure):
    """Structure for monitor information."""

    _fields_ = [
        ('cbSize', DWORD),
        ('rcMonitor', RECT),
        ('rcWork', RECT),
        ('dwFlags', DWORD),
    ]


class WindowsPlatform:
    """Windows-specific implementation of platform window operations."""

    def __init__(self):
        """Initialize Windows platform with required API handles."""
        self._user32 = windll.user32
        self._dwmapi = windll.dwmapi

        # Configure function signatures
        self._setup_api_signatures()

    def _setup_api_signatures(self):
        """Configure Windows API function signatures."""
        # User32 functions
        self._user32.GetSystemMetrics.restype = c_int
        self._user32.GetSystemMetrics.argtypes = [c_int]
        self._user32.MonitorFromWindow.restype = c_void_p
        self._user32.MonitorFromWindow.argtypes = [c_void_p, c_ulong]
        self._user32.GetMonitorInfoW.restype = c_int
        self._user32.GetMonitorInfoW.argtypes = [c_void_p, POINTER(MONITORINFO)]
        self._user32.SetWindowPos.restype = c_void_p

        # DwmApi functions
        self._dwmapi.DwmSetWindowAttribute.restype = c_int
        self._dwmapi.DwmSetWindowAttribute.argtypes = [
            c_void_p, c_ulong, c_void_p, c_ulong
        ]

    def set_corner_preference(self, hwnd: int, rounded: bool = True) -> bool:
        """Set window corner preference for Windows 11.

        Args:
            hwnd: Window handle
            rounded: Whether to use rounded corners (True) or square corners (False)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate parameters
            if not hwnd:
                logger.warning("Invalid window handle for set_corner_preference")
                return False

            # Check if API is available
            if not self._dwmapi:
                logger.warning("DWM API not available")
                return False

            # Create attribute value
            attr_value = c_ulong(DWMWCP_ROUND if rounded else DWMWCP_DONOTROUND)
            size = c_ulong(4)  # sizeof(DWORD) = 4 bytes

            # Call Windows API
            result = self._dwmapi.DwmSetWindowAttribute(
                int(hwnd),
                DWMWA_WINDOW_CORNER_PREFERENCE,
                byref(attr_value),
                size
            )

            # Check return value (S_OK = 0)
            success = result == 0
            if not success:
                logger.warning(f"DwmSetWindowAttribute failed with code: {result}")

            return success

        except Exception as e:
            logger.warning(f"Failed to set corner preference: {e}")
            return False  # Graceful degradation

    def maximize_window(self, hwnd: int) -> bool:
        """Maximize window to fill the current monitor's work area.

        Args:
            hwnd: Window handle

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate parameters
            if not hwnd:
                logger.warning("Invalid window handle for maximize_window")
                return False

            # Set square corners before maximizing
            self.set_corner_preference(hwnd, rounded=False)

            # Get the monitor where the window is located
            monitor = self._user32.MonitorFromWindow(int(hwnd), MONITOR_DEFAULTTONEAREST)
            if not monitor:
                logger.warning("Failed to get monitor from window")
                return False

            # Get monitor information
            info = MONITORINFO()
            info.cbSize = c_ulong(ctypes.sizeof(MONITORINFO))
            if not self._user32.GetMonitorInfoW(monitor, byref(info)):
                logger.warning("Failed to get monitor info")
                return False

            # Extract work area rectangle (excluding taskbar/dock)
            x = info.rcWork.left
            y = info.rcWork.top
            cx = info.rcWork.right - info.rcWork.left
            cy = info.rcWork.bottom - info.rcWork.top

            # Validate dimensions
            if cx <= 0 or cy <= 0:
                logger.warning(f"Invalid work area size: {cx}x{cy}")
                return False

            # Use SetWindowPos to position and resize the window
            result = self._user32.SetWindowPos(
                int(hwnd),  # hWnd
                None,  # hWndInsertAfter (None = keep current z-order)
                x, y, cx, cy,  # X, Y, Width, Height
                SWP_FRAMECHANGED | SWP_NOZORDER | SWP_NOACTIVATE
            )

            success = bool(result)
            if not success:
                logger.warning("SetWindowPos failed")

            return success

        except Exception as e:
            logger.warning(f"Failed to maximize window: {e}")
            return False  # Graceful degradation
