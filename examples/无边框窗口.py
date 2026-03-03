import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QEvent, QPropertyAnimation, QEasingCurve, 
    QSequentialAnimationGroup, QParallelAnimationGroup, pyqtProperty
)
from PyQt6.QtGui import QFont, QPainter, QColor


class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("无边框窗口")
        self.resize(500, 350)
        self.setMinimumSize(300, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.drag_pos = QPoint()
        self.resizing = False
        self.resize_edge = None
        self.shadow_margin = 10
        self.edge_margin = 8
        self.setMouseTracking(True)
        
        self._maximized = False
        self._normal_geometry = None
        self._animation_running = False
        self._border_radius = 10
        self._pre_minimize_geometry = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QWidget()
        self.container.setMouseTracking(True)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: #3d3d3d;
                border-radius: 10px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.title_bar = QWidget()
        self.title_bar.setMouseTracking(True)
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setStyleSheet("""
            #title_bar {
                background-color: #2d2d2d;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        
        self.title_label = QLabel("无边框窗口")
        self.title_label.setMouseTracking(True)
        self.title_label.setStyleSheet("color: white; background: transparent;")
        self.title_label.setFont(QFont("Microsoft YaHei", 10))
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        btn_min = self._create_title_btn("─", self._minimize, "#555", "#666")
        btn_max = self._create_title_btn("□", self._toggle_maximize, "#555", "#666")
        btn_close = self._create_title_btn("✕", self.close, "#e81123", "#f1707a")
        
        title_layout.addWidget(btn_min)
        title_layout.addWidget(btn_max)
        title_layout.addWidget(btn_close)
        
        container_layout.addWidget(self.title_bar)
        
        self.content = QWidget()
        self.content.setMouseTracking(True)
        self.content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self.content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel("这是一个无边框窗口示例")
        self.label.setMouseTracking(True)
        self.label.setStyleSheet("color: white; font-size: 14px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.label)
        
        self.close_btn = QPushButton("关闭窗口")
        self.close_btn.setFixedSize(100, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        content_layout.addWidget(self.close_btn)
        
        container_layout.addWidget(self.content)
        
        layout.addWidget(self.container)
        
        for widget in [self.container, self.title_bar, self.title_label, 
                       self.content, self.label]:
            widget.installEventFilter(self)
    
    def _create_title_btn(self, text, callback, color, hover_color):
        btn = QPushButton(text)
        btn.setFixedSize(40, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: white;
            }}
        """)
        btn.clicked.connect(callback)
        return btn
    
    def _minimize(self):
        self._animate_minimize()
    
    def _animate_minimize(self):
        self._animation_running = True
        self._pre_minimize_geometry = QRect(self.geometry())
        
        self.anim_group = QParallelAnimationGroup(self)
        
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setDuration(150)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        screen = self.screen().availableGeometry()
        scale_anim = QPropertyAnimation(self, b"geometry")
        scale_anim.setDuration(150)
        scale_anim.setStartValue(self.geometry())
        target_rect = QRect(
            self.geometry().center().x() - 100,
            screen.bottom() - 10,
            200,
            30
        )
        scale_anim.setEndValue(target_rect)
        scale_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        
        self.anim_group.addAnimation(opacity_anim)
        self.anim_group.addAnimation(scale_anim)
        
        self.anim_group.finished.connect(self._finish_minimize)
        self.anim_group.start()
    
    def _finish_minimize(self):
        self.setGraphicsEffect(None)
        self._animation_running = False
        self.setGeometry(self._pre_minimize_geometry)
        self.showMinimized()
    
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self._pre_minimize_geometry:
                self._animate_restore_from_minimize()
        super().changeEvent(event)
    
    def _animate_restore_from_minimize(self):
        if self._animation_running:
            return
        self._animation_running = True
        
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)
        
        self.opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.opacity_anim.setDuration(150)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.opacity_anim.finished.connect(lambda: (
            self.setGraphicsEffect(None),
            setattr(self, '_animation_running', False)
        ))
        self.opacity_anim.start()
    
    def _toggle_maximize(self):
        if self._animation_running:
            return
            
        if self._maximized:
            self._animate_restore()
        else:
            self._animate_maximize()
    
    def _animate_maximize(self):
        self._animation_running = True
        self._normal_geometry = QRect(self.geometry())
        
        start_rect = self.geometry()
        screen = self.screen().availableGeometry()
        end_rect = screen
        
        self.geo_anim = QPropertyAnimation(self, b"geometry")
        self.geo_anim.setDuration(200)
        self.geo_anim.setStartValue(start_rect)
        self.geo_anim.setEndValue(end_rect)
        self.geo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.radius_anim = QPropertyAnimation(self, b"border_radius")
        self.radius_anim.setDuration(200)
        self.radius_anim.setStartValue(10)
        self.radius_anim.setEndValue(0)
        self.radius_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.margin_anim = QPropertyAnimation(self, b"window_margin")
        self.margin_anim.setDuration(200)
        self.margin_anim.setStartValue(10)
        self.margin_anim.setEndValue(0)
        self.margin_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.geo_anim)
        self.anim_group.addAnimation(self.radius_anim)
        self.anim_group.addAnimation(self.margin_anim)
        
        self.anim_group.finished.connect(self._finish_maximize)
        self.anim_group.start()
    
    def _finish_maximize(self):
        self._maximized = True
        self._animation_running = False
    
    def _animate_restore(self):
        self._animation_running = True
        
        start_rect = self.geometry()
        end_rect = self._normal_geometry
        
        self.geo_anim = QPropertyAnimation(self, b"geometry")
        self.geo_anim.setDuration(200)
        self.geo_anim.setStartValue(start_rect)
        self.geo_anim.setEndValue(end_rect)
        self.geo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.radius_anim = QPropertyAnimation(self, b"border_radius")
        self.radius_anim.setDuration(200)
        self.radius_anim.setStartValue(0)
        self.radius_anim.setEndValue(10)
        self.radius_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.margin_anim = QPropertyAnimation(self, b"window_margin")
        self.margin_anim.setDuration(200)
        self.margin_anim.setStartValue(0)
        self.margin_anim.setEndValue(10)
        self.margin_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.geo_anim)
        self.anim_group.addAnimation(self.radius_anim)
        self.anim_group.addAnimation(self.margin_anim)
        
        self.anim_group.finished.connect(self._finish_restore)
        self.anim_group.start()
    
    def _finish_restore(self):
        self._maximized = False
        self._animation_running = False
    
    def get_border_radius(self):
        return self._border_radius
    
    def set_border_radius(self, radius):
        self._border_radius = radius
        self._set_border_radius(int(radius))
    
    border_radius = pyqtProperty(float, get_border_radius, set_border_radius)
    
    def get_window_margin(self):
        return self.layout().contentsMargins().left()
    
    def set_window_margin(self, margin):
        self.layout().setContentsMargins(int(margin), int(margin), int(margin), int(margin))
    
    window_margin = pyqtProperty(float, get_window_margin, set_window_margin)
    
    def _set_border_radius(self, radius):
        self.container.setStyleSheet(f"""
            #container {{
                background-color: #3d3d3d;
                border-radius: {radius}px;
            }}
        """)
        self.title_bar.setStyleSheet(f"""
            #title_bar {{
                background-color: #2d2d2d;
                border-top-left-radius: {radius}px;
                border-top-right-radius: {radius}px;
            }}
        """)
    
    def paintEvent(self, event):
        if self._maximized:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(0, 0, 0, 60)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        
        rect = self.rect()
        margin = self.layout().contentsMargins().left()
        painter.drawRoundedRect(margin, margin, 
                                rect.width() - 2 * margin, 
                                rect.height() - 2 * margin, 
                                self._border_radius, self._border_radius)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseMove:
            self._handle_mouse_move(event)
        elif event.type() == QEvent.Type.MouseButtonPress:
            self._handle_mouse_press(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._handle_mouse_release()
        elif event.type() == QEvent.Type.MouseButtonDblClick:
            if obj in [self.title_bar, self.title_label]:
                self._toggle_maximize()
        return super().eventFilter(obj, event)
    
    def _get_edge(self, pos):
        if self._maximized:
            return None
            
        rect = self.rect()
        x, y = pos.x(), pos.y()
        edge = []
        
        left_edge = self.shadow_margin
        right_edge = rect.width() - self.shadow_margin
        top_edge = self.shadow_margin
        bottom_edge = rect.height() - self.shadow_margin
        
        if x <= left_edge + self.edge_margin:
            edge.append('left')
        elif x >= right_edge - self.edge_margin:
            edge.append('right')
        
        if y <= top_edge + self.edge_margin:
            edge.append('top')
        elif y >= bottom_edge - self.edge_margin:
            edge.append('bottom')
        
        return tuple(edge) if edge else None
    
    def _get_cursor(self, edge):
        if not edge:
            return Qt.CursorShape.ArrowCursor
        
        edge_set = set(edge)
        if edge_set == {'top'} or edge_set == {'bottom'}:
            return Qt.CursorShape.SizeVerCursor
        elif edge_set == {'left'} or edge_set == {'right'}:
            return Qt.CursorShape.SizeHorCursor
        elif edge_set == {'top', 'left'} or edge_set == {'bottom', 'right'}:
            return Qt.CursorShape.SizeFDiagCursor
        elif edge_set == {'top', 'right'} or edge_set == {'bottom', 'left'}:
            return Qt.CursorShape.SizeBDiagCursor
        return Qt.CursorShape.ArrowCursor
    
    def _handle_mouse_press(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
            
        global_pos = self.mapFromGlobal(event.globalPosition().toPoint())
        edge = self._get_edge(global_pos)
        
        if edge:
            self.resizing = True
            self.resize_edge = edge
            self.drag_pos = event.globalPosition().toPoint()
            self.orig_geometry = QRect(self.geometry())
        else:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def _handle_mouse_move(self, event):
        global_pos = self.mapFromGlobal(event.globalPosition().toPoint())
        
        if self.resizing and self.resize_edge:
            self._do_resize(event)
        else:
            edge = self._get_edge(global_pos)
            self.setCursor(self._get_cursor(edge))
            
            if event.buttons() & Qt.MouseButton.LeftButton and not self.resizing:
                if self._maximized:
                    self._maximized = False
                self.move(event.globalPosition().toPoint() - self.drag_pos)
    
    def _do_resize(self, event):
        delta = event.globalPosition().toPoint() - self.drag_pos
        geo = QRect(self.orig_geometry)
        updated = False
        
        if 'left' in self.resize_edge:
            new_left = geo.left() + delta.x()
            new_width = geo.right() - new_left
            if new_width >= self.minimumWidth():
                geo.setLeft(new_left)
                updated = True
        
        if 'right' in self.resize_edge:
            new_width = geo.width() + delta.x()
            if new_width >= self.minimumWidth():
                geo.setWidth(new_width)
                updated = True
        
        if 'top' in self.resize_edge:
            new_top = geo.top() + delta.y()
            new_height = geo.bottom() - new_top
            if new_height >= self.minimumHeight():
                geo.setTop(new_top)
                updated = True
        
        if 'bottom' in self.resize_edge:
            new_height = geo.height() + delta.y()
            if new_height >= self.minimumHeight():
                geo.setHeight(new_height)
                updated = True
        
        if updated:
            self.setGeometry(geo)
            self.orig_geometry = QRect(geo)
            self.drag_pos = event.globalPosition().toPoint()
    
    def _handle_mouse_release(self):
        self.resizing = False
        self.resize_edge = None
        self.drag_pos = QPoint()
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event):
        self._handle_mouse_press(event)
    
    def mouseMoveEvent(self, event):
        self._handle_mouse_move(event)
    
    def mouseReleaseEvent(self, event):
        self._handle_mouse_release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())
