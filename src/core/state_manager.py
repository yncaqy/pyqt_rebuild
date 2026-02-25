"""
State Management Module

Provides unified state management for PyQt widgets using Q_PROPERTY.
Centralizes state tracking and change notifications.
"""
from enum import Flag, auto
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty


class WidgetState(Flag):
    """
    Widget state flags using Python's Flag enum.

    Combines multiple states into single value for efficient
    state tracking and comparison.

    States can be combined using bitwise operators:
        state = WidgetState.HOVER | WidgetState.PRESSED
    """
    NORMAL = auto()
    HOVER = auto()
    PRESSED = auto()
    FOCUSED = auto()
    DISABLED = auto()
    CHECKED = auto()


class StateManager(QObject):
    """
    Unified state management with Q_PROPERTY support.

    Responsibilities:
    - Track widget state using single enum
    - Emit notifications on state changes
    - Provide property access for animations

    Usage:
        manager = StateManager(widget)
        manager.hover = True  # Emits hoverChanged signal
        manager.pressed = True  # Emits pressedChanged signal
    """

    # Signals for state changes
    stateChanged = pyqtSignal(int)  # New state flags
    hoverChanged = pyqtSignal(bool)
    pressedChanged = pyqtSignal(bool)
    focusedChanged = pyqtSignal(bool)
    disabledChanged = pyqtSignal(bool)
    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._state = WidgetState.NORMAL

    @pyqtProperty(int)
    def state(self) -> int:
        """Current state as integer flag."""
        return self._state.value

    @state.setter
    def state(self, value: int) -> None:
        """
        Set state and emit change signal.

        Args:
            value: Integer value of state flags
        """
        new_state = WidgetState(value)
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            self.stateChanged.emit(self._state.value)
            self._emit_specific_changes(old_state, new_state)

    @pyqtProperty(bool)
    def hover(self) -> bool:
        """Hover state property."""
        return bool(WidgetState.HOVER & self._state)

    @hover.setter
    def hover(self, value: bool) -> None:
        """Set hover state."""
        if value:
            self._state |= WidgetState.HOVER
        else:
            self._state &= ~WidgetState.HOVER
        self.hoverChanged.emit(value)

    @pyqtProperty(bool)
    def pressed(self) -> bool:
        """Pressed state property."""
        return bool(WidgetState.PRESSED & self._state)

    @pressed.setter
    def pressed(self, value: bool) -> None:
        """Set pressed state."""
        if value:
            self._state |= WidgetState.PRESSED
        else:
            self._state &= ~WidgetState.PRESSED
        self.pressedChanged.emit(value)

    @pyqtProperty(bool)
    def focused(self) -> bool:
        """Focused state property."""
        return bool(WidgetState.FOCUSED & self._state)

    @focused.setter
    def focused(self, value: bool) -> None:
        """Set focused state."""
        if value:
            self._state |= WidgetState.FOCUSED
        else:
            self._state &= ~WidgetState.FOCUSED
        self.focusedChanged.emit(value)

    @pyqtProperty(bool)
    def disabled(self) -> bool:
        """Disabled state property."""
        return bool(WidgetState.DISABLED & self._state)

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set disabled state."""
        if value:
            self._state |= WidgetState.DISABLED
        else:
            self._state &= ~WidgetState.DISABLED
        self.disabledChanged.emit(value)

    @pyqtProperty(bool)
    def checked(self) -> bool:
        """Checked state property."""
        return bool(WidgetState.CHECKED & self._state)

    @checked.setter
    def checked(self, value: bool) -> None:
        """Set checked state."""
        if value:
            self._state |= WidgetState.CHECKED
        else:
            self._state &= ~WidgetState.CHECKED
        self.checkedChanged.emit(value)

    def _emit_specific_changes(
        self,
        old_state: WidgetState,
        new_state: WidgetState
    ) -> None:
        """
        Emit specific property changes based on diff.

        Compares old and new state to determine which specific
        properties changed and emits their signals.
        """
        # Check hover state change
        if (WidgetState.HOVER & new_state) and not (WidgetState.HOVER & old_state):
            self.hoverChanged.emit(True)
        elif not (WidgetState.HOVER & new_state) and (WidgetState.HOVER & old_state):
            self.hoverChanged.emit(False)

        # Check pressed state change
        if (WidgetState.PRESSED & new_state) and not (WidgetState.PRESSED & old_state):
            self.pressedChanged.emit(True)
        elif not (WidgetState.PRESSED & new_state) and (WidgetState.PRESSED & old_state):
            self.pressedChanged.emit(False)

        # Check focused state change
        if (WidgetState.FOCUSED & new_state) and not (WidgetState.FOCUSED & old_state):
            self.focusedChanged.emit(True)
        elif not (WidgetState.FOCUSED & new_state) and (WidgetState.FOCUSED & old_state):
            self.focusedChanged.emit(False)

        # Check disabled state change
        if (WidgetState.DISABLED & new_state) and not (WidgetState.DISABLED & old_state):
            self.disabledChanged.emit(True)
        elif not (WidgetState.DISABLED & new_state) and (WidgetState.DISABLED & old_state):
            self.disabledChanged.emit(False)

        # Check checked state change
        if (WidgetState.CHECKED & new_state) and not (WidgetState.CHECKED & old_state):
            self.checkedChanged.emit(True)
        elif not (WidgetState.CHECKED & new_state) and (WidgetState.CHECKED & old_state):
            self.checkedChanged.emit(False)

    def has_state(self, state: WidgetState) -> bool:
        """Check if specific state flag is set."""
        return bool(state & self._state)

    def reset(self) -> None:
        """Reset to normal state."""
        self._state = WidgetState.NORMAL
        self.stateChanged.emit(self._state.value)
