"""
SplashScreen Component

Provides a splash screen widget for displaying logo and title during application startup.

Features:
- Logo display with optional icon
- Title and subtitle support
- Progress bar for loading status
- Theme integration
- Fade in/out animations
- Customizable duration
"""

import logging
from typing import Optional
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QSize, QTimer, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QPoint
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QPixmap, QFontMetrics
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGraphicsOpacityEffect
from src.core.theme_manager import ThemeManager, Theme
from src.core.font_manager import FontManager

logger = logging.getLogger(__name__)


class SplashConfig:
    """Configuration constants for splash screen."""

    DEFAULT_WIDTH = 480
    DEFAULT_HEIGHT = 320
    BORDER_RADIUS = 12
    LOGO_SIZE = 80
    PROGRESS_HEIGHT = 4
    MARGIN = 40


class SplashScreen(QWidget):
    """
    Splash screen widget for displaying logo and title during application startup.

    Features:
    - Logo display with optional icon
    - Title and subtitle support
    - Progress bar for loading status
    - Theme integration
    - Fade in/out animations
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme

        self._title = "Application"
        self._subtitle = "Loading..."
        self._logo: Optional[QIcon] = None
        self._logo_pixmap: Optional[QPixmap] = None
        self._progress_value = 0
        self._opacity = 1.0

        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        logger.debug("SplashScreen initialized")

    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setFixedSize(SplashConfig.DEFAULT_WIDTH, SplashConfig.DEFAULT_HEIGHT)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        self._apply_theme()

    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._apply_theme()

    def _apply_theme(self) -> None:
        self.update()

    def setTitle(self, title: str) -> None:
        self._title = title
        self.update()

    def title(self) -> str:
        return self._title

    def setSubtitle(self, subtitle: str) -> None:
        self._subtitle = subtitle
        self.update()

    def subtitle(self) -> str:
        return self._subtitle

    def setLogo(self, logo: QIcon) -> None:
        self._logo = logo
        self._logo_pixmap = None
        self.update()

    def setLogoPixmap(self, pixmap: QPixmap) -> None:
        self._logo_pixmap = pixmap
        self._logo = None
        self.update()

    def setProgress(self, value: int) -> None:
        self._progress_value = max(0, min(100, value))
        self.update()

    def progress(self) -> int:
        return self._progress_value

    def get_opacity(self) -> float:
        return self._opacity

    def set_opacity(self, value: float) -> None:
        self._opacity = value
        if self._opacity_effect:
            self._opacity_effect.setOpacity(value)

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def fade_in(self, duration: int = 500) -> None:
        if self._opacity_effect:
            self._opacity_effect.setOpacity(0.0)
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(duration)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def fade_out(self, duration: int = 500) -> None:
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(duration)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self._animation.finished.connect(self.close)
        self._animation.start()

    def show_and_fade_in(self, duration: int = 500) -> None:
        if self._opacity_effect:
            self._opacity_effect.setOpacity(0.0)
        self.show()
        self.fade_in(duration)

    def finish(self, main_window: QWidget, duration: int = 300) -> None:
        self._fade_out_timer = QTimer(self)
        self._fade_out_timer.timeout.connect(lambda: self._do_finish(main_window, duration))
        self._fade_out_timer.start(500)

    def _do_finish(self, main_window: QWidget, duration: int) -> None:
        self._fade_out_timer.stop()
        main_window.show()
        self.fade_out(duration)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._theme:
            bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
            border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
            text_color = self._theme.get_color('label.text.title', QColor(255, 255, 255))
            subtext_color = self._theme.get_color('label.text.body', QColor(180, 180, 180))
            progress_bg = self._theme.get_color('window.border', QColor(60, 60, 60))
            progress_fg = self._theme.get_color('primary.main', QColor(0, 120, 212))
        else:
            bg_color = QColor(45, 45, 45)
            border_color = QColor(60, 60, 60)
            text_color = QColor(255, 255, 255)
            subtext_color = QColor(180, 180, 180)
            progress_bg = QColor(60, 60, 60)
            progress_fg = QColor(0, 120, 212)

        rect = self.rect()
        border_radius = SplashConfig.BORDER_RADIUS

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(QRectF(rect), border_radius, border_radius)

        logo_size = SplashConfig.LOGO_SIZE
        logo_x = (rect.width() - logo_size) // 2
        logo_y = SplashConfig.MARGIN

        if self._logo_pixmap and not self._logo_pixmap.isNull():
            scaled_pixmap = self._logo_pixmap.scaled(
                logo_size, logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(logo_x, logo_y, scaled_pixmap)
        elif self._logo and not self._logo.isNull():
            pixmap = self._logo.pixmap(logo_size, logo_size)
            painter.drawPixmap(logo_x, logo_y, pixmap)
        else:
            painter.setPen(QPen(progress_fg, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(logo_x, logo_y, logo_size, logo_size)

            painter.setFont(FontManager.get_title_font())
            painter.setPen(QPen(text_color))
            initial = self._title[0].upper() if self._title else "A"
            painter.drawText(QRect(logo_x, logo_y, logo_size, logo_size),
                           Qt.AlignmentFlag.AlignCenter, initial)

        title_y = logo_y + logo_size + 30
        painter.setFont(FontManager.get_title_font())
        painter.setPen(QPen(text_color))
        painter.drawText(QRect(0, title_y, rect.width(), 40),
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        self._title)

        subtitle_y = title_y + 45
        painter.setFont(FontManager.get_caption_font())
        painter.setPen(QPen(subtext_color))
        painter.drawText(QRect(0, subtitle_y, rect.width(), 20),
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        self._subtitle)

        progress_width = rect.width() - 2 * SplashConfig.MARGIN
        progress_height = SplashConfig.PROGRESS_HEIGHT
        progress_x = SplashConfig.MARGIN
        progress_y = rect.height() - SplashConfig.MARGIN - progress_height

        painter.setBrush(QBrush(progress_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(progress_x, progress_y, progress_width, progress_height),
                               progress_height // 2, progress_height // 2)

        if self._progress_value > 0:
            filled_width = int(progress_width * self._progress_value / 100)
            painter.setBrush(QBrush(progress_fg))
            painter.drawRoundedRect(QRectF(progress_x, progress_y, filled_width, progress_height),
                                   progress_height // 2, progress_height // 2)

    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("SplashScreen cleaned up")
