"""
MessageBox Component

Provides modal dialog components with mask overlay and theme support.

Features:
- Modal mask overlay
- Fade in/out animation
- Theme integration
- Customizable buttons
- Standard message box types (info, warning, error, question)
"""

import logging
from typing import Optional, List
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QObject, QEvent, 
    QPropertyAnimation, QEasingCurve, pyqtProperty,
    QRectF, QSize
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QFontMetrics, QPainterPath, QIcon
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGraphicsOpacityEffect,
    QSpacerItem, QSizePolicy
)
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class MaskWidget(QWidget):
    """Semi-transparent mask overlay widget."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._opacity = 0.0
        self._setup_animation()
        
    def _setup_animation(self) -> None:
        self._animation = QPropertyAnimation(self, b"maskOpacity")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def get_opacity(self) -> float:
        return self._opacity
    
    def set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()
    
    maskOpacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def fade_in(self) -> None:
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
    
    def fade_out(self) -> None:
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(120 * self._opacity)))


class MessageBoxBase(QWidget):
    """Base class for message boxes with mask overlay."""
    
    def __init__(self, parent: Optional[QWidget] = None, title: str = "消息"):
        super().__init__(parent)
        
        self._title = title
        self._theme_mgr = ThemeManager.instance()
        self._theme: Optional[Theme] = None
        self._result = 0
        self._mask: Optional[MaskWidget] = None
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._theme = initial_theme
        
        self._setup_ui()
        self._setup_animation()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        logger.debug("MessageBoxBase initialized")
    
    def _setup_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._content_widget = QWidget()
        self._content_widget.setObjectName("messageBoxContent")
        
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(20, 20, 20, 20)
        self._content_layout.setSpacing(16)
        
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("messageBoxTitle")
        self._title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self._content_layout.addWidget(self._title_label)
        
        self._view_layout = QVBoxLayout()
        self._view_layout.setSpacing(8)
        self._content_layout.addLayout(self._view_layout)
        
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(10)
        self._button_layout.addStretch()
        self._content_layout.addLayout(self._button_layout)
        
        self._main_layout.addWidget(self._content_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        self._apply_theme()
    
    def _setup_animation(self) -> None:
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        if not self._theme:
            return
        
        bg_color = self._theme.get_color('window.background', QColor(45, 45, 45))
        text_color = self._theme.get_color('label.text.title', QColor(255, 255, 255))
        border_color = self._theme.get_color('window.border', QColor(60, 60, 60))
        
        self._content_widget.setStyleSheet(f"""
            #messageBoxContent {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 8px;
            }}
            #messageBoxTitle {{
                color: {text_color.name()};
            }}
        """)
    
    @property
    def viewLayout(self) -> QVBoxLayout:
        return self._view_layout
    
    @property
    def buttonLayout(self) -> QHBoxLayout:
        return self._button_layout
    
    def add_button(self, text: str, role: int = 0) -> QPushButton:
        button = QPushButton(text)
        button.setFixedHeight(32)
        button.setMinimumWidth(80)
        
        if self._theme:
            btn_bg = self._theme.get_color('button.background.normal', QColor(60, 60, 60))
            btn_hover = self._theme.get_color('button.background.hover', QColor(70, 70, 70))
            btn_text = self._theme.get_color('button.text.normal', QColor(255, 255, 255))
            btn_border = self._theme.get_color('button.border.normal', QColor(80, 80, 80))
            
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_bg.name()};
                    color: {btn_text.name()};
                    border: 1px solid {btn_border.name()};
                    border-radius: 4px;
                    padding: 6px 16px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover.name()};
                }}
                QPushButton:pressed {{
                    background-color: {btn_bg.darker(120).name()};
                }}
            """)
        
        button.clicked.connect(lambda: self._on_button_clicked(role))
        self._button_layout.addWidget(button)
        return button
    
    def _on_button_clicked(self, role: int) -> None:
        self._result = role
        self.hide()
    
    def fade_in(self) -> None:
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
        if self._mask:
            self._mask.fade_in()
    
    def fade_out(self) -> None:
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()
        if self._mask:
            self._mask.fade_out()
    
    def exec(self) -> int:
        parent = self.parent()
        if parent:
            self._mask = MaskWidget(parent)
            self._mask.resize(parent.size())
            self._mask.show()
            self._mask.fade_in()
        
        self.resize(self.sizeHint())
        
        if parent:
            parent_rect = parent.rect()
            global_center = parent.mapToGlobal(parent_rect.center())
            self.move(
                global_center.x() - self.width() // 2,
                global_center.y() - self.height() // 2
            )
        
        self.show()
        self.fade_in()
        
        self._event_loop = QEventLoop()
        result = self._event_loop.exec()
        
        return self._result
    
    def hide(self) -> None:
        self.fade_out()
        if self._mask:
            self._mask.fade_out()
        
        QTimer.singleShot(150, self._close_all)
    
    def _close_all(self) -> None:
        if self._mask:
            self._mask.hide()
            self._mask.deleteLater()
            self._mask = None
        
        super().hide()
        
        if hasattr(self, '_event_loop') and self._event_loop:
            self._event_loop.quit()
    
    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        logger.debug("MessageBoxBase cleaned up")


from PyQt6.QtCore import QEventLoop


class MessageBox(MessageBoxBase):
    """Standard message box with icon and content."""
    
    INFO = 1
    WARNING = 2
    ERROR = 3
    QUESTION = 4
    
    OK = 1
    CANCEL = 0
    
    def __init__(
        self, 
        title: str = "消息",
        content: str = "",
        parent: Optional[QWidget] = None,
        box_type: int = 1
    ):
        self._content = content
        self._box_type = box_type
        super().__init__(parent, title)
        
        self._setup_content()
        self._setup_buttons()
    
    def _setup_content(self) -> None:
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(48, 48)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        icon_svg = self._get_icon_svg()
        self._icon_label.setText(icon_svg)
        self._icon_label.setTextFormat(Qt.TextFormat.RichText)
        
        self._content_label = QLabel(self._content)
        self._content_label.setWordWrap(True)
        self._content_label.setMaximumWidth(350)
        
        if self._theme:
            text_color = self._theme.get_color('label.text.body', QColor(200, 200, 200))
            self._content_label.setStyleSheet(f"color: {text_color.name()};")
        
        content_layout.addWidget(self._icon_label)
        content_layout.addWidget(self._content_label, 1)
        
        self.viewLayout.addLayout(content_layout)
    
    def _get_icon_svg(self) -> str:
        icon_size = 48
        
        if self._box_type == self.INFO:
            color = "#2196F3"
            svg = f'''<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="{color}"/>
                <path d="M12 7V13" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="17" r="1" fill="white"/>
            </svg>'''
        elif self._box_type == self.WARNING:
            color = "#FF9800"
            svg = f'''<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 22H22L12 2Z" fill="{color}"/>
                <path d="M12 9V14" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="18" r="1" fill="white"/>
            </svg>'''
        elif self._box_type == self.ERROR:
            color = "#F44336"
            svg = f'''<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="{color}"/>
                <path d="M8 8L16 16M16 8L8 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>'''
        else:
            color = "#4CAF50"
            svg = f'''<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="{color}"/>
                <path d="M8 12L11 15L16 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>'''
        
        return svg
    
    def _setup_buttons(self) -> None:
        if self._box_type == self.QUESTION:
            self.add_button("确定", self.OK)
            self.add_button("取消", self.CANCEL)
        else:
            self.add_button("确定", self.OK)
    
    @staticmethod
    def information(
        parent: Optional[QWidget],
        title: str,
        content: str
    ) -> int:
        box = MessageBox(title, content, parent, MessageBox.INFO)
        return box.exec()
    
    @staticmethod
    def warning(
        parent: Optional[QWidget],
        title: str,
        content: str
    ) -> int:
        box = MessageBox(title, content, parent, MessageBox.WARNING)
        return box.exec()
    
    @staticmethod
    def critical(
        parent: Optional[QWidget],
        title: str,
        content: str
    ) -> int:
        box = MessageBox(title, content, parent, MessageBox.ERROR)
        return box.exec()
    
    @staticmethod
    def question(
        parent: Optional[QWidget],
        title: str,
        content: str
    ) -> int:
        box = MessageBox(title, content, parent, MessageBox.QUESTION)
        return box.exec()
