"""Test Toast notification component"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt

from core.theme_manager import ThemeManager
from components.toasts import Toast, ToastPosition, ToastType, ToastManager
from components.buttons import CustomPushButton
from themes import DEFAULT_THEME, DARK_THEME


class ToastDemoWindow(QMainWindow):
    """Demo window for Toast testing."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toast Component Test")
        self.setGeometry(100, 100, 600, 400)

        # Initialize theme manager
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict("default", DEFAULT_THEME)
        theme_mgr.register_theme_dict("dark", DARK_THEME)
        theme_mgr.set_current_theme("default")

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Toast Notification Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Toast type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Toast Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["INFO", "SUCCESS", "WARNING", "ERROR"])
        self.type_combo.setCurrentText("INFO")
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Position selection
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Position:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems([
            "TOP_LEFT", "TOP_CENTER", "TOP_RIGHT",
            "BOTTOM_LEFT", "BOTTOM_CENTER", "BOTTOM_RIGHT",
            "CENTER"
        ])
        self.pos_combo.setCurrentText("TOP_RIGHT")
        pos_layout.addWidget(self.pos_combo)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)

        # Show toast button
        self.show_button = CustomPushButton("Show Toast")
        self.show_button.clicked.connect(self._show_toast)
        layout.addWidget(self.show_button)

        # Clear all button
        self.clear_button = CustomPushButton("Clear All Toasts")
        self.clear_button.clicked.connect(self._clear_all)
        layout.addWidget(self.clear_button)

        # Instructions
        info = QLabel(
            "<b>Features:</b><br>"
            "&bull; Click 'Show Toast' to display a notification<br>"
            "&bull; Toasts auto-hide after 3 seconds<br>"
            "&bull; Hover pauses auto-hide<br>"
            "&bull; Click toast to close immediately<br>"
            "&bull; Change position and type to test different configurations"
        )
        info.setStyleSheet("color: #666; font-size: 11px;")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        layout.addStretch()

    def _show_toast(self):
        """Show toast with selected type and position."""
        # Get selected type
        type_name = self.type_combo.currentText()
        toast_type = ToastType[type_name]

        # Get selected position
        pos_name = self.pos_combo.currentText()
        position = ToastPosition[pos_name]

        # Messages for each type
        messages = {
            ToastType.INFO: "This is an informational message.",
            ToastType.SUCCESS: "Operation completed successfully!",
            ToastType.WARNING: "Please check your input carefully.",
            ToastType.ERROR: "An error occurred. Please try again."
        }

        message = messages.get(toast_type, "Message")

        # Show toast using ToastManager
        toast_mgr = ToastManager.get_instance()
        toast_mgr.show(message, toast_type, position=position, parent=self)

    def _clear_all(self):
        """Clear all active toasts."""
        toast_mgr = ToastManager.get_instance()
        toast_mgr.clear_all()


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ToastDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
