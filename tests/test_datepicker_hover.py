import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout


class TestWidget(QWidget):
    """测试组件"""
    
    def __init__(self, border_width=1):
        super().__init__()
        self.setFixedSize(150, 32)
        self._hover = False
        self._border_width = border_width
        
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(42, 42, 42)
        border_color = QColor(68, 68, 68)
        border_hover = QColor(93, 173, 226)
        
        rect = self.rect()
        painter.setBrush(QBrush(bg_color))
        
        if self._hover:
            painter.setPen(QPen(border_hover, self._border_width))
        else:
            painter.setPen(QPen(border_color, 1))
        
        painter.drawRoundedRect(rect, 4, 4)
        
        painter.setPen(QPen(QColor(224, 224, 224)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"边框: {self._border_width}px")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.resize(600, 200)
    
    palette = window.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    window.setPalette(palette)
    window.setAutoFillBackground(True)
    
    layout = QVBoxLayout(window)
    layout.addStretch()
    
    row = QWidget()
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    
    for width in [1, 2, 3]:
        w = TestWidget(border_width=width)
        row_layout.addWidget(w)
        row_layout.addStretch()
    
    layout.addWidget(row)
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec())
