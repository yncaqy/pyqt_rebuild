from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .toast import Toast, ToastPosition, ToastType


class ToastManager(QObject):
    """Manager for displaying multiple toasts with automatic positioning."""

    instance = None
    _prewarmed = False

    @classmethod
    def get_instance(cls) -> 'ToastManager':
        """Get singleton instance."""
        if cls.instance is None:
            cls.instance = ToastManager()
        return cls.instance

    def __init__(self):
        super().__init__()
        self._active_toasts: List[Toast] = []
        self._default_position = ToastPosition.TOP_CENTER
        self._default_duration = 3000
        self._spacing = 10

    @classmethod
    def prewarm(cls) -> None:
        """Pre-warm toast system to prevent first-toast lag.

        This creates and immediately destroys a hidden toast to initialize
        all Qt subsystems (animations, graphics effects, stylesheets, etc.).

        Call this during application startup for optimal performance.

        Example:
            ToastManager.prewarm()  # Call during app startup
        """
        if cls._prewarmed:
            return

        try:
            # Create a temporary toast for pre-warming
            temp_toast = Toast("prewarm", ToastType.INFO, 0)
            # Force initialization of all subsystems
            temp_toast.setStyleSheet(temp_toast.styleSheet())
            temp_toast.update()

            # Clean up
            temp_toast.cleanup()
            temp_toast.deleteLater()

            cls._prewarmed = True
            print("Toast system pre-warmed")
        except Exception as e:
            print(f"Warning: Failed to pre-warm toast system: {e}")

    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = None,
        position: ToastPosition = None,
        parent: QWidget = None
    ) -> Toast:
        """Show a toast notification."""
        if duration is None:
            duration = self._default_duration
        if position is None:
            position = self._default_position

        # Create toast
        toast = Toast(message, toast_type, duration, parent)

        # Calculate offset if multiple toasts
        offset = self._calculate_offset(position)
        toast._position_offset = offset

        # Connect cleanup
        toast.destroyed.connect(lambda: self._remove_toast(toast))

        # Add to active list
        self._active_toasts.append(toast)

        # Show toast
        toast.show(position, parent)

        return toast

    def info(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None) -> Toast:
        """Show info toast."""
        return self.show(message, ToastType.INFO, duration, position, parent)

    def success(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None) -> Toast:
        """Show success toast."""
        return self.show(message, ToastType.SUCCESS, duration, position, parent)

    def warning(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None) -> Toast:
        """Show warning toast."""
        return self.show(message, ToastType.WARNING, duration, position, parent)

    def error(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None) -> Toast:
        """Show error toast."""
        return self.show(message, ToastType.ERROR, duration, position, parent)

    def _calculate_offset(self, position: ToastPosition) -> int:
        """Calculate vertical offset for stacking toasts."""
        # Count toasts in similar positions
        count = 0
        for toast in self._active_toasts:
            if hasattr(toast, '_position'):
                if toast._position == position:
                    count += 1

        return count * (100 + self._spacing)  # Approximate height + spacing

    def _remove_toast(self, toast: Toast) -> None:
        """Remove toast from active list."""
        if toast in self._active_toasts:
            self._active_toasts.remove(toast)

    def clear_all(self) -> None:
        """Close all active toasts."""
        for toast in self._active_toasts[:]:
            toast.close()
        self._active_toasts.clear()

    def set_default_position(self, position: ToastPosition) -> None:
        """Set default position for new toasts."""
        self._default_position = position

    def set_default_duration(self, duration: int) -> None:
        """Set default duration for new toasts."""
        self._default_duration = duration

    def set_spacing(self, spacing: int) -> None:
        """Set spacing between stacked toasts."""
        self._spacing = spacing
