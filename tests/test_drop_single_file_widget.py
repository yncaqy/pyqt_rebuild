"""
DropSingleFileWidget 组件测试

测试单文件拖拽选择组件的功能。
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt

from components.widgets.drop_single_file_widget import DropSingleFileWidget
from components.containers.themed_group_box import ThemedGroupBox
from components.labels.themed_label import ThemedLabel
from components.buttons.custom_push_button import CustomPushButton
from core.theme_manager import ThemeManager
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME


class TestWindow(QMainWindow):
    """测试窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DropSingleFileWidget 测试")
        self.setMinimumSize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self._setup_theme_selector(main_layout)

        self._setup_default_widget(main_layout)

        self._setup_image_filter_widget(main_layout)

        self._setup_info_panel(main_layout)

        self._apply_theme()

    def _setup_theme_selector(self, layout: QVBoxLayout) -> None:
        theme_group = ThemedGroupBox("主题选择")
        theme_layout = QHBoxLayout(theme_group)

        theme_label = ThemedLabel("当前主题:")
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self._theme_combo)
        theme_layout.addStretch()

        layout.addWidget(theme_group)

    def _setup_default_widget(self, layout: QVBoxLayout) -> None:
        default_group = ThemedGroupBox("默认文件选择器（所有文件）")
        default_group.setFixedHeight(220)
        default_layout = QVBoxLayout(default_group)

        self._default_file_widget = DropSingleFileWidget()
        self._default_file_widget.fileSelected.connect(self._on_file_selected)
        self._default_file_widget.fileCleared.connect(self._on_file_cleared)
        self._default_file_widget.errorOccurred.connect(self._on_error)

        default_layout.addWidget(self._default_file_widget)

        layout.addWidget(default_group)

    def _setup_image_filter_widget(self, layout: QVBoxLayout) -> None:
        image_group = ThemedGroupBox("图片文件选择器（仅支持 PNG, JPG, JPEG）")
        image_group.setFixedHeight(220)
        image_layout = QVBoxLayout(image_group)

        self._image_file_widget = DropSingleFileWidget(
            title="拖拽图片到此处",
            subtitle="支持 PNG, JPG, JPEG 格式"
        )
        self._image_file_widget.setFilter(["*.png", "*.jpg", "*.jpeg"])
        self._image_file_widget.fileSelected.connect(self._on_file_selected)
        self._image_file_widget.errorOccurred.connect(self._on_error)

        image_layout.addWidget(self._image_file_widget)

        layout.addWidget(image_group)

    def _setup_info_panel(self, layout: QVBoxLayout) -> None:
        info_group = ThemedGroupBox("文件信息")
        info_layout = QVBoxLayout(info_group)

        self._file_path_label = ThemedLabel("文件路径: 未选择")
        self._file_path_label.setWordWrap(True)

        self._file_name_label = ThemedLabel("文件名: 未选择")
        self._file_name_label.setWordWrap(True)

        clear_btn = CustomPushButton("清除文件")
        clear_btn.clicked.connect(self._clear_files)

        info_layout.addWidget(self._file_path_label)
        info_layout.addWidget(self._file_name_label)
        info_layout.addWidget(clear_btn)

        layout.addWidget(info_group)

    def _on_theme_changed(self, theme_name: str) -> None:
        theme_mgr = ThemeManager.instance()
        theme_mgr.set_theme(theme_name)

    def _apply_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        current = theme_mgr.current_theme()
        if current:
            self._theme_combo.setCurrentText(current.name)

    def _on_file_selected(self, file_path: str) -> None:
        self._file_path_label.setText(f"文件路径: {file_path}")
        self._file_name_label.setText(f"文件名: {os.path.basename(file_path)}")

    def _on_file_cleared(self) -> None:
        self._file_path_label.setText("文件路径: 未选择")
        self._file_name_label.setText("文件名: 未选择")

    def _on_error(self, error_msg: str) -> None:
        print(f"错误: {error_msg}")

    def _clear_files(self) -> None:
        self._default_file_widget.clearFile()
        self._image_file_widget.clearFile()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.register_theme_dict('light', LIGHT_THEME)
    theme_mgr.set_theme('dark')

    window = TestWindow()
    window.show()

    sys.exit(app.exec())
