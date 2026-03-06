"""
文件选择对话框组件

基于 MessageBoxBase 的文件选择对话框，支持主题集成。

功能特性:
- 模态遮罩层
- 淡入/淡出动画
- 主题集成
- 文件格式过滤
- 文件导航
"""

import os
import logging
from typing import Optional, List, Tuple
from PyQt6.QtCore import Qt, QDir, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QFileSystemModel
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListView, QTreeView, QSplitter, QComboBox, QLineEdit,
    QAbstractItemView, QSizePolicy, QFileIconProvider
)

from components.dialogs.message_box import MessageBoxBase
from components.buttons.custom_push_button import CustomPushButton
from components.inputs.modern_line_edit import ModernLineEdit
from components.labels.themed_label import ThemedLabel
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class FileDialog(MessageBoxBase):
    """
    文件选择对话框。

    功能特性:
    - 模态遮罩层
    - 淡入/淡出动画
    - 主题集成
    - 文件格式过滤
    - 文件导航

    信号:
        fileSelected: 文件选择成功时发出，携带文件路径
    """

    fileSelected = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "选择文件",
        directory: str = "",
        filters: Optional[List[str]] = None
    ):
        self._directory = directory or QDir.homePath()
        self._filters = filters or ["所有文件
        self._selected_file: Optional[str] = None
        self._icon_mgr = IconManager.instance()

        super().__init__(parent, title)

        self._setup_file_view()
        self._update_file_list()

        self.resize(800, 500)

    def _setup_ui(self) -> None:
        """初始化 UI 布局。"""
        super()._setup_ui()

        self._nav_layout = QHBoxLayout()
        self._nav_layout.setSpacing(8)

        self._back_btn = CustomPushButton("←")
        self._back_btn.setFixedSize(32, 32)
        self._back_btn.clicked.connect(self._go_back)

        self._forward_btn = CustomPushButton("→")
        self._forward_btn.setFixedSize(32, 32)
        self._forward_btn.clicked.connect(self._go_forward)

        self._up_btn = CustomPushButton("↑")
        self._up_btn.setFixedSize(32, 32)
        self._up_btn.clicked.connect(self._go_up)

        self._path_edit = ModernLineEdit()
        self._path_edit.setText(self._directory)
        self._path_edit.returnPressed.connect(self._navigate_to_path)

        self._nav_layout.addWidget(self._back_btn)
        self._nav_layout.addWidget(self._forward_btn)
        self._nav_layout.addWidget(self._up_btn)
        self._nav_layout.addWidget(self._path_edit, 1)

        self.viewLayout.addLayout(self._nav_layout)

        self._filter_layout = QHBoxLayout()
        self._filter_layout.setSpacing(8)

        self._filter_label = ThemedLabel("文件类型:")
        self._filter_combo = QComboBox()
        self._filter_combo.addItems(self._filters)
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)

        self._filter_layout.addWidget(self._filter_label)
        self._filter_layout.addWidget(self._filter_combo, 1)

        self._file_name_layout = QHBoxLayout()
        self._file_name_layout.setSpacing(8)

        self._file_name_label = ThemedLabel("文件名:")
        self._file_name_edit = ModernLineEdit()
        self._file_name_edit.setPlaceholderText("输入文件名")

        self._file_name_layout.addWidget(self._file_name_label)
        self._file_name_layout.addWidget(self._file_name_edit, 1)

        self.viewLayout.addLayout(self._filter_layout)
        self.viewLayout.addLayout(self._file_name_layout)

        self._add_buttons()

    def _setup_file_view(self) -> None:
        """设置文件视图。"""
        self._file_model = QFileSystemModel()
        self._file_model.setRootPath(QDir.rootPath())
        self._file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        self._file_view = QListView()
        self._file_view.setModel(self._file_model)
        self._file_view.setRootIndex(self._file_model.index(self._directory))
        self._file_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._file_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._file_view.doubleClicked.connect(self._on_item_double_clicked)
        self._file_view.clicked.connect(self._on_item_clicked)

        self.viewLayout.addWidget(self._file_view, 1)

    def _add_buttons(self) -> None:
        """添加按钮。"""
        self._open_btn = self.add_button("打开", 1)
        self._cancel_btn = self.add_button("取消", 0)

        self._open_btn.clicked.disconnect()
        self._open_btn.clicked.connect(self._on_open_clicked)

    def _update_file_list(self) -> None:
        """更新文件列表。"""
        self._file_view.setRootIndex(self._file_model.index(self._directory))
        self._path_edit.setText(self._directory)

    def _on_item_clicked(self, index) -> None:
        """项目点击处理。"""
        file_path = self._file_model.filePath(index)
        if os.path.isfile(file_path):
            self._file_name_edit.setText(os.path.basename(file_path))
            self._selected_file = file_path

    def _on_item_double_clicked(self, index) -> None:
        """项目双击处理。"""
        file_path = self._file_model.filePath(index)
        if os.path.isdir(file_path):
            self._directory = file_path
            self._update_file_list()
        elif os.path.isfile(file_path):
            self._selected_file = file_path
            self._on_open_clicked()

    def _go_back(self) -> None:
        """后退。"""
        pass

    def _go_forward(self) -> None:
        """前进。"""
        pass

    def _go_up(self) -> None:
        """向上。"""
        parent = os.path.dirname(self._directory)
        if parent and parent != self._directory:
            self._directory = parent
            self._update_file_list()

    def _navigate_to_path(self) -> None:
        """导航到指定路径。"""
        path = self._path_edit.text()
        if os.path.isdir(path):
            self._directory = path
            self._update_file_list()

    def _on_filter_changed(self, index: int) -> None:
        """过滤器变更处理。"""
        pass

    def _on_open_clicked(self) -> None:
        """打开按钮点击处理。"""
        if self._selected_file and os.path.isfile(self._selected_file):
            self.fileSelected.emit(self._selected_file)
            self.hide()

    def selectedFile(self) -> Optional[str]:
        """获取选中的文件路径。"""
        return self._selected_file

    def setDirectory(self, directory: str) -> None:
        """设置初始目录。"""
        if os.path.isdir(directory):
            self._directory = directory
            self._update_file_list()

    def setFilter(self, filters: List[str]) -> None:
        """设置文件过滤器。"""
        self._filters = filters
        self._filter_combo.clear()
        self._filter_combo.addItems(filters)


def get_open_file_name(
    parent: Optional[QWidget] = None,
    title: str = "选择文件",
    directory: str = "",
    filters: Optional[List[str]] = None
) -> Tuple[Optional[str], str]:
    """
    打开文件选择对话框并返回选中的文件路径。

    Args:
        parent: 父控件
        title: 对话框标题
        directory: 初始目录
        filters: 文件过滤器列表

    Returns:
        (文件路径, 过滤器) 元组
    """
    dialog = FileDialog(parent, title, directory, filters)
    dialog.exec()

    return dialog.selectedFile(), ""
