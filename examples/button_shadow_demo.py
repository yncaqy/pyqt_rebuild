"""
按钮阴影效果演示

展示按钮组件上的 WinUI 3 风格阴影效果。

运行方式:
    python examples/button_shadow_demo.py
"""

import sys
sys.path.insert(0, 'src')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.shadow_manager import ShadowDepth
from core.theme_manager import ThemeManager
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from components.buttons.custom_push_button import CustomPushButton


class ButtonShadowDemo(QMainWindow):
    """按钮阴影演示主窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("按钮阴影效果演示")
        self.setMinimumSize(800, 500)

        self._theme_mgr = ThemeManager.instance()
        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(32)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_label = QLabel("按钮阴影效果")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        theme_combo = QComboBox()
        theme_combo.addItems(["dark", "light"])
        current_theme = self._theme_mgr.current_theme()
        theme_combo.setCurrentText("dark" if (current_theme and current_theme.is_dark) else "light")
        theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_combo.setFixedWidth(100)
        header_layout.addWidget(theme_combo)

        main_layout.addLayout(header_layout)

        info_label = QLabel(
            "点击下方按钮切换阴影深度，观察不同深度级别的阴影效果。\n"
            "阴影深度: TOOLTIP < MENU < CARD < PANE < DIALOG"
        )
        info_label.setStyleSheet("font-size: 13px; color: #888; line-height: 1.5;")
        main_layout.addWidget(info_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(24)

        depths = [
            ("无阴影", ShadowDepth.NONE),
            ("Tooltip", ShadowDepth.TOOLTIP),
            ("Menu", ShadowDepth.MENU),
            ("Card", ShadowDepth.CARD),
            ("Dialog", ShadowDepth.DIALOG),
        ]

        is_dark = current_theme.is_dark if current_theme else True

        for label, depth in depths:
            btn_container = QFrame()
            btn_layout = QVBoxLayout(btn_container)
            btn_layout.setContentsMargins(16, 16, 16, 16)
            btn_layout.setSpacing(8)

            btn = CustomPushButton(label)
            btn.set_shadow_depth(depth, is_dark)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(100)
            btn_layout.addWidget(btn)

            depth_label = QLabel(f"深度: {depth.name}")
            depth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            depth_label.setStyleSheet("font-size: 11px; color: #666;")
            btn_layout.addWidget(depth_label)

            buttons_layout.addWidget(btn_container)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        main_layout.addStretch()

        self._update_theme_style()

    def _on_theme_changed(self, theme_name: str) -> None:
        self._theme_mgr.set_theme(theme_name)
        self._update_theme_style()

    def _update_theme_style(self) -> None:
        theme = self._theme_mgr.current_theme()
        if not theme:
            return

        is_dark = theme.is_dark

        bg_color = "#1a1a1a" if is_dark else "#f5f5f5"
        text_color = "#ffffff" if is_dark else "#1a1a1a"
        card_bg = "#2d2d2d" if is_dark else "#ffffff"
        border_color = "#404040" if is_dark else "#e0e0e0"

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QComboBox {{
                padding: 8px 16px;
                border: 1px solid {border_color};
                border-radius: 4px;
                background: {card_bg};
                color: {text_color};
            }}
            QFrame {{
                background: transparent;
            }}
        """)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.register_theme_dict('light', LIGHT_THEME)
    theme_mgr.set_theme('dark')

    window = ButtonShadowDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
