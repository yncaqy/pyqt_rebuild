"""
RoundMenu Demo

Demonstrates the RoundMenu component with:
- Basic actions
- Icons
- Shortcuts
- Checkable items
- Submenus
- Theme switching
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel
)

from containers.frameless_window import FramelessWindow
from components.buttons.custom_push_button import CustomPushButton
from components.buttons.primary_push_button import PrimaryPushButton
from components.menus.round_menu import RoundMenu
from components.labels.themed_label import ThemedLabel
from core.theme_manager import ThemeManager
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME


class MenuDemoWindow(FramelessWindow):
    """Demo window for RoundMenu component."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoundMenu Demo")
        self.resize(600, 400)

        # Initialize theme
        self._init_theme()

        # Build UI
        self._build_ui()

    def _init_theme(self):
        """Initialize theme manager."""
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict('dark', DARK_THEME)
        theme_mgr.register_theme_dict('light', LIGHT_THEME)
        theme_mgr.set_theme('dark')

    def _build_ui(self):
        """Build the demo UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = ThemedLabel("RoundMenu Component Demo", font_role='title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = ThemedLabel("Right-click or use buttons below to show menus", font_role='body')
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Button row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        # Basic menu button
        basic_btn = PrimaryPushButton("Basic Menu")
        basic_btn.clicked.connect(self._show_basic_menu)
        btn_layout.addWidget(basic_btn)

        # Context menu button
        context_btn = CustomPushButton("Context Menu")
        context_btn.clicked.connect(self._show_context_menu)
        btn_layout.addWidget(context_btn)

        # Theme toggle button
        self._theme_btn = CustomPushButton("Switch Theme")
        self._theme_btn.clicked.connect(self._toggle_theme)
        btn_layout.addWidget(self._theme_btn)

        layout.addLayout(btn_layout)

        # Result label
        self._result_label = ThemedLabel("Click a menu item to see result...", font_role='body')
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._result_label)

        # Instructions
        instructions = ThemedLabel(
            "Features:\n"
            "• Hover animations\n"
            "• Keyboard navigation (↑↓ Enter Esc)\n"
            "• Checkable items\n"
            "• Submenus\n"
            "• Theme integration",
            font_role='small'
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        layout.addStretch()

        self.setLayout(layout)

        # Enable context menu on content widget (not main window)
        self.content_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.content_widget.customContextMenuRequested.connect(self._show_context_menu)

    def _show_basic_menu(self):
        """Show basic menu example."""
        menu = RoundMenu("File")

        menu.addAction(
            "New File",
            lambda: self._on_action("New File"),
            shortcut="Ctrl+N"
        )
        menu.addAction(
            "Open File",
            lambda: self._on_action("Open File"),
            shortcut="Ctrl+O"
        )
        menu.addAction(
            "Save",
            lambda: self._on_action("Save"),
            shortcut="Ctrl+S"
        )
        menu.addAction(
            "Save As...",
            lambda: self._on_action("Save As"),
            shortcut="Ctrl+Shift+S"
        )

        menu.addSeparator()

        # Checkable items
        menu.addAction(
            "Auto Save",
            lambda: self._on_action("Auto Save toggled"),
            checkable=True,
            checked=True
        )
        menu.addAction(
            "Word Wrap",
            lambda: self._on_action("Word Wrap toggled"),
            checkable=True,
            checked=False
        )

        menu.addSeparator()

        # Submenu
        recent_menu = menu.addMenu("Recent Files")
        recent_menu.addAction("document1.txt", lambda: self._on_action("Opened document1.txt"))
        recent_menu.addAction("project.py", lambda: self._on_action("Opened project.py"))
        recent_menu.addAction("config.json", lambda: self._on_action("Opened config.json"))

        menu.addSeparator()

        menu.addAction("Exit", lambda: self._on_action("Exit"))

        # Show menu
        btn = self.sender()
        if btn:
            pos = btn.mapToGlobal(QPoint(0, btn.height()))
            menu.exec(pos)

    def _show_context_menu(self, pos=None):
        """Show context menu example."""
        menu = RoundMenu("Context")

        menu.addAction(
            "Copy",
            lambda: self._on_action("Copy"),
            shortcut="Ctrl+C"
        )
        menu.addAction(
            "Cut",
            lambda: self._on_action("Cut"),
            shortcut="Ctrl+X"
        )
        menu.addAction(
            "Paste",
            lambda: self._on_action("Paste"),
            shortcut="Ctrl+V"
        )

        menu.addSeparator()

        menu.addAction(
            "Select All",
            lambda: self._on_action("Select All"),
            shortcut="Ctrl+A"
        )

        menu.addSeparator()

        # View submenu
        view_menu = menu.addMenu("View")
        view_menu.addAction("Zoom In", lambda: self._on_action("Zoom In"))
        view_menu.addAction("Zoom Out", lambda: self._on_action("Zoom Out"))
        view_menu.addAction("Reset Zoom", lambda: self._on_action("Reset Zoom"))

        # Show menu
        from PyQt6.QtCore import QPoint
        if pos is None or isinstance(pos, bool):
            cursor_pos = self.cursor().pos()
        elif isinstance(pos, QPoint):
            cursor_pos = self.content_widget.mapToGlobal(pos)
        else:
            cursor_pos = self.cursor().pos()
        menu.exec(cursor_pos)

    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        theme_mgr = ThemeManager.instance()
        current = theme_mgr.current_theme()
        if current and current.name == 'dark':
            theme_mgr.set_theme('light')
            self._theme_btn.setText("Switch to Dark")
        else:
            theme_mgr.set_theme('dark')
            self._theme_btn.setText("Switch to Light")

    def _on_action(self, action_name: str):
        """Handle menu action."""
        self._result_label.setText(f"Action: {action_name}")


def main():
    app = QApplication(sys.argv)

    # Show splash screen
    from components.splash.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()

    # Create and show main window
    window = MenuDemoWindow()
    window.show()

    # Close splash
    splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
