"""
阴影系统演示程序

展示 WinUI 3 风格的阴影效果，参考微软 ThemeShadow 设计。

运行方式:
    python examples/shadow_demo.py
"""

import sys
sys.path.insert(0, 'src')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from core.shadow_manager import ShadowManager, ShadowDepth, ShadowMixin, create_custom_shadow
from core.theme_manager import ThemeManager
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME


class ShadowCard(QFrame, ShadowMixin):
    """带阴影效果的卡片组件。"""

    def __init__(self, title: str, depth: ShadowDepth, parent=None):
        super().__init__(parent)
        self._init_shadow()
        self._setup_ui(title, depth)

    def _setup_ui(self, title: str, depth: ShadowDepth) -> None:
        self.setObjectName("shadowCard")
        self.setMinimumSize(200, 120)
        self.setMaximumSize(200, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title_label)

        depth_label = QLabel(f"深度: {depth.name}")
        depth_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(depth_label)

        preset = ShadowManager.PRESETS.get(depth)
        if preset:
            info_label = QLabel(f"模糊: {preset.blur_radius}px")
            info_label.setStyleSheet("font-size: 11px; color: #888;")
            layout.addWidget(info_label)

        self.setStyleSheet("""
            #shadowCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        theme_mgr = ThemeManager.instance()
        current_theme = theme_mgr.current_theme()
        is_dark = current_theme.is_dark if current_theme else False
        self.set_shadow_depth(depth, is_dark)


class ShadowDemoWindow(QMainWindow):
    """阴影演示主窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinUI 3 阴影系统演示")
        self.setMinimumSize(900, 600)

        self._theme_mgr = ThemeManager.instance()
        self._shadow_mgr = ShadowManager.instance()

        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_label = QLabel("WinUI 3 阴影系统")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        theme_combo = QComboBox()
        theme_combo.addItems(["dark", "light"])
        current_theme = self._theme_mgr.current_theme()
        theme_combo.setCurrentText("dark" if (current_theme and current_theme.is_dark) else "light")
        theme_combo.currentTextChanged.connect(self._on_theme_changed)
        header_layout.addWidget(theme_combo)

        main_layout.addLayout(header_layout)

        info_label = QLabel(
            "参考微软 ThemeShadow 设计，基于 z-depth 深度级别自动计算阴影参数。\n"
            "深度级别越高，阴影越明显，表示元素在 z 轴上越高。"
        )
        info_label.setStyleSheet("font-size: 13px; color: #666; line-height: 1.5;")
        main_layout.addWidget(info_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(32)

        sections = [
            ("基础阴影级别", [
                ("Tooltip (16px)", ShadowDepth.TOOLTIP),
                ("Menu (32px)", ShadowDepth.MENU),
                ("Card (48px)", ShadowDepth.CARD),
                ("Pane (64px)", ShadowDepth.PANE),
                ("Dialog (128px)", ShadowDepth.DIALOG),
            ]),
        ]

        for section_title, cards in sections:
            section_label = QLabel(section_title)
            section_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-top: 8px;")
            scroll_layout.addWidget(section_label)

            cards_layout = QHBoxLayout()
            cards_layout.setSpacing(24)

            for card_title, depth in cards:
                card = ShadowCard(card_title, depth)
                cards_layout.addWidget(card)

            cards_layout.addStretch()
            scroll_layout.addLayout(cards_layout)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

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

    window = ShadowDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
