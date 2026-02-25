"""
Circular Progress Painter

Painting strategy for circular progress widgets.
Demonstrates complete separation of rendering logic from component.
"""
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

from .widget_painter import WidgetPainter, PaintContext


class CircularProgressPainter(WidgetPainter):
    """
    Painting strategy for circular progress widgets.

    Features:
    - Configurable thickness, colors
    - Optional background track
    - Center text display
    - Clean, maintainable code

    All drawing parameters come from the PaintContext,
    making this painter completely independent of widget implementation.
    """

    def paint(self, context: PaintContext) -> None:
        """Paint the circular progress indicator."""
        self.prepare_painter(context)

        painter = context.painter
        rect = context.rect

        # Get parameters from context
        value = context.get_value('value', 0)
        maximum = context.get_value('maximum', 100)
        thickness = context.get_value('thickness', 10)
        show_text = context.get_value('show_text', True)

        # Colors from theme
        track_color = context.get_color('progress.circular.background', QColor(230, 230, 230))
        fill_color = context.get_color('progress.circular.progress', QColor(52, 152, 219))
        text_color = context.get_color('progress.circular.text', QColor(50, 50, 50))

        # Calculate geometry
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - thickness / 2 - 2

        # Draw background track
        self._draw_track(painter, center, radius, thickness, track_color)

        # Draw progress arc
        if value > 0:
            progress_angle = (value / maximum) * 360
            self._draw_progress(
                painter, center, radius, thickness,
                progress_angle, fill_color
            )

        # Draw center text
        if show_text:
            self._draw_text(
                painter, rect, value, maximum, text_color
            )

        self.cleanup_painter(context)

    def _draw_track(
        self,
        painter: QPainter,
        center: QRectF,
        radius: float,
        thickness: float,
        color: QColor
    ) -> None:
        """Draw background track circle."""
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawEllipse(
            center,
            radius,
            radius
        )

    def _draw_progress(
        self,
        painter: QPainter,
        center: QRectF,
        radius: float,
        thickness: float,
        angle: float,
        color: QColor
    ) -> None:
        """Draw progress arc."""
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Convert angle to Qt units (1/16th of a degree)
        # Start at 12 o'clock (-90 degrees)
        start_angle = -90 * 16
        span_angle = int(angle * 16)

        # Calculate bounding rect for arc
        rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2
        )

        painter.drawArc(rect, start_angle, span_angle)

    def _draw_text(
        self,
        painter: QPainter,
        rect: QRectF,
        value: float,
        maximum: float,
        color: QColor
    ) -> None:
        """Draw percentage text in center."""
        percentage = int((value / maximum) * 100)
        text = f"{percentage}%"

        painter.setPen(color)
        font = painter.font()
        font.setPixelSize(int(rect.height() * 0.2))
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


class CircularProgressGradientPainter(CircularProgressPainter):
    """
    Enhanced circular progress painter with gradient support.

    Demonstrates how to extend a painter for visual variations
    without modifying the component.
    """

    def paint(self, context: PaintContext) -> None:
        """Paint with gradient effect."""
        self.prepare_painter(context)

        painter = context.painter
        rect = context.rect

        # Get parameters
        value = context.get_value('value', 0)
        maximum = context.get_value('maximum', 100)
        thickness = context.get_value('thickness', 10)
        show_text = context.get_value('show_text', True)

        # Get gradient colors from theme
        gradient_start = context.get_color(
            'progress.circular.progress',
            QColor(52, 152, 219)
        )
        gradient_end = context.get_color(
            'progress.circular.gradient_end',
            QColor(155, 89, 182)
        )
        track_color = context.get_color('progress.circular.background', QColor(230, 230, 230))
        text_color = context.get_color('progress.circular.text', QColor(50, 50, 50))

        # Calculate geometry
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - thickness / 2 - 2

        # Draw background track
        self._draw_track(painter, center, radius, thickness, track_color)

        # Draw progress with gradient
        if value > 0:
            progress_angle = (value / maximum) * 360
            self._draw_progress_gradient(
                painter, center, radius, thickness,
                progress_angle, gradient_start, gradient_end
            )

        # Draw center text
        if show_text:
            self._draw_text(
                painter, rect, value, maximum, text_color
            )

        self.cleanup_painter(context)

    def _draw_progress_gradient(
        self,
        painter: QPainter,
        center: QRectF,
        radius: float,
        thickness: float,
        angle: float,
        start_color: QColor,
        end_color: QColor
    ) -> None:
        """Draw progress arc with gradient."""
        # For gradient effect on an arc, we use a conical gradient
        from PyQt6.QtGui import QConicalGradient

        # Create gradient centered on the widget
        gradient = QConicalGradient(center, -90)  # Start at top

        # Set color stops based on progress angle
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(angle / 360, end_color)
        gradient.setColorAt(angle / 360 + 0.001, Qt.GlobalColor.transparent)  # Gap
        gradient.setColorAt(1, Qt.GlobalColor.transparent)

        # Create pen with gradient
        pen = QPen(gradient, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Draw the arc
        start_angle = -90 * 16
        span_angle = int(angle * 16)

        rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2
        )

        painter.drawArc(rect, start_angle, span_angle)
