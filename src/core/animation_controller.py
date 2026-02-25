"""
Animation Control Module

Provides reusable animation controllers for PyQt widgets.
Decouples animation logic from component implementation.
"""
from typing import Dict, Optional, Any
from enum import Enum
from PyQt6.QtCore import (
    QObject, pyqtSignal,
    QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup,
    QVariantAnimation, QEasingCurve
)
from PyQt6.QtWidgets import QWidget


class AnimationType(Enum):
    """Types of supported animations."""
    COLOR = "color"
    NUMBER = "number"
    SIZE = "size"
    OPACITY = "opacity"
    GEOMETRY = "geometry"


class Transition:
    """
    Defines a single animation transition.

    Encapsulates the parameters for animating a property
    from a start value to an end value.
    """

    def __init__(
        self,
        property_name: str,
        start_value: Any,
        end_value: Any,
        duration: int = 200,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutQuad
    ):
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing

    def __repr__(self) -> str:
        return (f"Transition(property='{self.property_name}', "
                f"start={self.start_value}, end={self.end_value}, "
                f"duration={self.duration}ms)")


class AnimationController(QObject):
    """
    Reusable animation controller for widgets.

    Manages animation lifecycle, prevents conflicts, and provides
    a clean API for triggering state-based animations.

    Responsibilities:
    - Manage animation lifecycle
    - Bind state changes to property animations
    - Support parallel and sequential animations
    - Prevent animation conflicts

    Usage:
        controller = AnimationController(widget, parent=widget)
        controller.setup_transitions({
            'hover': Transition('bg_opacity', 0.0, 1.0, 150),
            'press': Transition('scale', 1.0, 0.95, 80)
        })
        controller.animate_to_state('hover')
    """

    # Signal emitted when all animations complete
    animationFinished = pyqtSignal()

    def __init__(self, target: QWidget, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._target = target
        self._animations: Dict[str, QVariantAnimation] = {}
        self._groups: Dict[str, QVariantAnimation] = {}
        self._is_animating = False

    def setup_transitions(self, transitions: Dict[str, Transition]) -> None:
        """
        Configure animation transitions for state changes.

        Creates QPropertyAnimation instances for each transition.

        Args:
            transitions: Dict mapping state names to Transition objects
                        e.g., {'hover': Transition('bg_opacity', 0.0, 1.0, 150)}
        """
        for state_name, transition in transitions.items():
            animation = QPropertyAnimation(self._target, transition.property_name.encode())
            animation.setDuration(transition.duration)
            animation.setEasingCurve(transition.easing)
            animation.setStartValue(transition.start_value)
            animation.setEndValue(transition.end_value)

            # Store animation
            self._animations[state_name] = animation

    def animate_to_state(self, state_name: str) -> None:
        """
        Trigger animation to specific state.

        Args:
            state_name: Name of the state transition to animate
        """
        if state_name not in self._animations:
            return

        # Stop any ongoing animation for this state
        if state_name in self._groups:
            self._groups[state_name].stop()

        animation = self._animations[state_name]

        # Connect finished signal if not already connected
        if not animation.receivers(animation.finished):
            animation.finished.connect(self._on_animation_finished)

        animation.start()
        self._is_animating = True

    def create_parallel_animation(
        self,
        name: str,
        animations: list[QVariantAnimation]
    ) -> QParallelAnimationGroup:
        """
        Create and store a parallel animation group.

        All animations in the group run simultaneously.

        Args:
            name: Name to identify this group
            animations: List of animations to run in parallel

        Returns:
            QParallelAnimationGroup instance
        """
        group = QParallelAnimationGroup(self)
        for anim in animations:
            group.addAnimation(anim)
        self._groups[name] = group
        return group

    def create_sequential_animation(
        self,
        name: str,
        animations: list[QVariantAnimation]
    ) -> QSequentialAnimationGroup:
        """
        Create and store a sequential animation group.

        Animations run one after another.

        Args:
            name: Name to identify this group
            animations: List of animations to run sequentially

        Returns:
            QSequentialAnimationGroup instance
        """
        group = QSequentialAnimationGroup(self)
        for anim in animations:
            group.addAnimation(anim)
        self._groups[name] = group
        return group

    def stop_all(self) -> None:
        """Stop all running animations."""
        for animation in self._animations.values():
            if animation.state() == animation.State.Running:
                animation.stop()
        for group in self._groups.values():
            if group.state() == group.State.Running:
                group.stop()
        self._is_animating = False

    def is_animating(self) -> bool:
        """
        Check if any animation is currently running.

        Returns:
            True if any animation is running
        """
        return any(
            anim.state() == QVariantAnimation.State.Running
            for anim in self._animations.values()
        )

    def _on_animation_finished(self) -> None:
        """Handle animation completion."""
        if not self.is_animating():
            self._is_animating = False
            self.animationFinished.emit()
