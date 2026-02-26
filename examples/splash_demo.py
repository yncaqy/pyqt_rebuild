"""
SplashScreen Demo

Demonstrates the SplashScreen component usage.
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from components.splash.splash_screen import SplashScreen
from components.buttons.custom_push_button import CustomPushButton
from components.containers.themed_widget import ThemedWidget
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME


class SplashDemoWindow(ThemedWidget):
    """Demo window for SplashScreen."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("SplashScreen Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("点击下方按钮查看 SplashScreen 效果")
        desc.setStyleSheet("font-size: 14px; color: #888;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        btn1 = CustomPushButton("显示 SplashScreen (带进度)")
        btn1.clicked.connect(self._show_splash_with_progress)
        layout.addWidget(btn1)
        
        btn2 = CustomPushButton("显示 SplashScreen (无进度)")
        btn2.clicked.connect(self._show_splash_simple)
        layout.addWidget(btn2)
        
        layout.addStretch()
        
        self.resize(400, 300)
        self.setWindowTitle("SplashScreen Demo")
    
    def _show_splash_with_progress(self):
        self._splash = SplashScreen()
        self._splash.setTitle("My Application")
        self._splash.setSubtitle("正在加载资源...")
        
        self._progress = 0
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(50)
        
        self._splash.show_and_fade_in()
    
    def _update_progress(self):
        if not hasattr(self, '_splash'):
            self._progress_timer.stop()
            return
        
        self._progress += 2
        self._splash.setProgress(self._progress)
        
        if self._progress < 30:
            self._splash.setSubtitle("正在初始化...")
        elif self._progress < 60:
            self._splash.setSubtitle("正在加载资源...")
        elif self._progress < 90:
            self._splash.setSubtitle("正在准备界面...")
        else:
            self._splash.setSubtitle("即将完成...")
        
        if self._progress >= 100:
            self._progress_timer.stop()
            QTimer.singleShot(500, self._close_splash)
    
    def _close_splash(self):
        if hasattr(self, '_splash'):
            self._splash.fade_out()
    
    def _show_splash_simple(self):
        self._splash2 = SplashScreen()
        self._splash2.setTitle("My Application")
        self._splash2.setSubtitle("正在启动...")
        self._splash2.show_and_fade_in()
        
        QTimer.singleShot(2000, self._close_splash2)
    
    def _close_splash2(self):
        if hasattr(self, '_splash2'):
            self._splash2.fade_out()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ThemeManager.instance().register_theme_dict('dark', DARK_THEME)
    ThemeManager.instance().set_theme('dark')
    
    window = SplashDemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
