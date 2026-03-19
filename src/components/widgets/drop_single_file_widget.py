"""
单文件拖拽选择组件

提供现代 Fluent Design 风格的文件选择器，具有以下特性：
- 拖拽文件选择
- 点击打开文件对话框
- 文件格式过滤
- 拖拽状态视觉反馈
- 文件选择成功提示
- 错误处理机制
- 主题集成

使用方式:
    file_widget = DropSingleFileWidget()
    file_widget.setFilter(["*.png", "*.jpg", "*.jpeg"])
    file_widget.fileSelected.connect(lambda path: print(f"选中文件: {path}"))
"""

import logging
import os
from typing import Optional, List
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF, QPropertyAnimation,
    QEasingCurve, pyqtSignal, pyqtProperty, QEvent, QTimer
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont,
    QPaintEvent, QDragEnterEvent, QDragMoveEvent,
    QDropEvent, QMouseEvent, QFontMetrics
)
from PyQt6.QtWidgets import (
    QWidget, QFileDialog, QSizePolicy
)

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class DropSingleFileConfig:
    """单文件拖拽选择组件配置常量。"""

    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 180
    BORDER_RADIUS = 12
    BORDER_WIDTH = 2
    DASH_WIDTH = 4

    ICON_SIZE = 48
    BUTTON_ICON_SIZE = 16

    ANIMATION_DURATION = 200

    MAX_STYLESHEET_CACHE_SIZE = 100

    DEFAULT_FILTER = ["*.*"]


class DropSingleFileWidget(QWidget, StyleOverrideMixin):
    """
    文件拖拽选择组件。

    功能特性:
    - 拖拽文件选择（支持单文件或多文件）
    - 点击打开文件对话框
    - 文件格式过滤
    - 拖拽状态视觉反馈
    - 文件选择成功提示
    - 错误处理机制
    - 主题集成

    信号:
        fileSelected: 单文件选择成功时发出，携带文件路径
        filesSelected: 多文件选择成功时发出，携带文件路径列表
        fileCleared: 文件清除时发出
        errorOccurred: 错误发生时发出，携带错误消息

    示例:
        file_widget = DropSingleFileWidget()
        file_widget.setFilter(["*.png", "*.jpg"])
        file_widget.fileSelected.connect(lambda path: print(f"选中: {path}"))
    """

    fileSelected = pyqtSignal(str)
    filesSelected = pyqtSignal(list)
    fileCleared = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "拖拽文件到此处",
        subtitle: str = "或点击选择文件"
    ):
        super().__init__(parent)

        self._init_style_override()

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumHeight(DropSingleFileConfig.DEFAULT_HEIGHT)
        self.setMinimumWidth(DropSingleFileConfig.DEFAULT_WIDTH)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self._title = title
        self._subtitle = subtitle
        self._file_path: Optional[str] = None
        self._file_paths: List[str] = []
        self._multi_select = False
        self._file_filters: List[str] = DropSingleFileConfig.DEFAULT_FILTER
        self._dialog_title = "选择文件"

        self._is_drag_over = False
        self._is_drag_valid = False
        self._is_hovered = False
        self._show_success = False
        self._success_opacity = 0.0
        self._error_message: Optional[str] = None

        self._success_animation: Optional[QPropertyAnimation] = None

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug("DropSingleFileWidget 初始化完成")

    def sizeHint(self) -> QSize:
        return QSize(
            DropSingleFileConfig.DEFAULT_WIDTH,
            DropSingleFileConfig.DEFAULT_HEIGHT
        )

    def setTitle(self, title: str) -> None:
        self._title = title
        self.update()

    def title(self) -> str:
        return self._title

    def setSubtitle(self, subtitle: str) -> None:
        self._subtitle = subtitle
        self.update()

    def subtitle(self) -> str:
        return self._subtitle

    def setFilter(self, filters: List[str]) -> None:
        """
        设置文件格式过滤器。

        Args:
            filters: 文件过滤器列表，如 ["*.png", "*.jpg", "*.jpeg"]
        """
        self._file_filters = filters if filters else DropSingleFileConfig.DEFAULT_FILTER
        logger.debug(f"文件过滤器已设置: {self._file_filters}")

    def filter(self) -> List[str]:
        return self._file_filters.copy()

    def setMultiSelect(self, enabled: bool) -> None:
        """
        设置是否支持多文件选择。

        Args:
            enabled: True 支持多文件，False 仅支持单文件
        """
        self._multi_select = enabled
        logger.debug(f"多文件选择模式: {enabled}")

    def isMultiSelect(self) -> bool:
        return self._multi_select

    def setDialogTitle(self, title: str) -> None:
        self._dialog_title = title

    def filePath(self) -> Optional[str]:
        return self._file_path

    def filePaths(self) -> List[str]:
        return self._file_paths.copy()

    def fileName(self) -> Optional[str]:
        if self._file_path:
            return os.path.basename(self._file_path)
        return None

    def fileNames(self) -> List[str]:
        return [os.path.basename(p) for p in self._file_paths]

    def clearFile(self) -> None:
        self._file_path = None
        self._file_paths = []
        self._show_success = False
        self._error_message = None
        self.update()
        self.fileCleared.emit()
        logger.debug("文件已清除")

    def _is_valid_file(self, file_path: str) -> bool:
        if not os.path.isfile(file_path):
            return False

        if self._file_filters == DropSingleFileConfig.DEFAULT_FILTER:
            return True

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        for pattern in self._file_filters:
            if pattern == "*.*":
                return True
            if pattern.startswith("*."):
                if ext == pattern[1:].lower():
                    return True

        return False

    def _get_error_message(self, file_path: str) -> str:
        if not os.path.isfile(file_path):
            return "不是一个有效的文件"

        _, ext = os.path.splitext(file_path)
        allowed = ", ".join(self._file_filters)
        return f"不支持的文件格式 {ext}\n支持的格式: {allowed}"

    def _handle_file_drop(self, file_path: str) -> None:
        if self._is_valid_file(file_path):
            self._file_path = file_path
            self._file_paths = [file_path]
            self._show_success = True
            self._error_message = None
            self._animate_success()
            self.fileSelected.emit(file_path)
            self.filesSelected.emit([file_path])
            logger.info(f"文件已选择: {file_path}")
        else:
            self._error_message = self._get_error_message(file_path)
            self._show_success = False
            self.errorOccurred.emit(self._error_message)
            logger.warning(f"文件格式不支持: {file_path}")
            QTimer.singleShot(3000, self._clear_error)

        self.update()

    def _handle_files_drop(self, file_paths: List[str]) -> None:
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            if self._is_valid_file(file_path):
                valid_files.append(file_path)
            else:
                invalid_files.append(os.path.basename(file_path))
        
        if invalid_files:
            self._error_message = f"以下文件格式不支持:\n{', '.join(invalid_files[:3])}"
            if len(invalid_files) > 3:
                self._error_message += f" 等{len(invalid_files)}个文件"
            self._show_success = False
            self.errorOccurred.emit(self._error_message)
            logger.warning(f"部分文件格式不支持: {invalid_files}")
            QTimer.singleShot(3000, self._clear_error)
            self.update()
            return
        
        if valid_files:
            self._file_paths = valid_files
            self._file_path = valid_files[0]
            self._show_success = True
            self._error_message = None
            
            if len(valid_files) == 1:
                self.fileSelected.emit(valid_files[0])
            
            self._animate_success()
            self.filesSelected.emit(valid_files)
            logger.info(f"已选择 {len(valid_files)} 个文件")
        
        self.update()

    def _clear_error(self) -> None:
        self._error_message = None
        self.update()

    def _animate_success(self) -> None:
        if self._success_animation:
            self._success_animation.stop()

        self._success_animation = QPropertyAnimation(self, b"successOpacity")
        self._success_animation.setDuration(DropSingleFileConfig.ANIMATION_DURATION)
        self._success_animation.setStartValue(1.0)
        self._success_animation.setEndValue(0.0)
        self._success_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._success_animation.start()

    def get_successOpacity(self) -> float:
        return self._success_opacity

    def set_successOpacity(self, value: float) -> None:
        self._success_opacity = value
        self.update()

    successOpacity = pyqtProperty(float, get_successOpacity, set_successOpacity)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            
            if self._multi_select:
                valid_count = sum(1 for p in file_paths if self._is_valid_file(p))
                self._is_drag_valid = valid_count > 0
                self._is_drag_over = True
                self.update()
                event.acceptProposedAction()
            else:
                if len(urls) == 1:
                    file_path = urls[0].toLocalFile()
                    self._is_drag_valid = self._is_valid_file(file_path)
                    self._is_drag_over = True
                    self.update()
                    event.acceptProposedAction()
                else:
                    self._is_drag_valid = False
                    self._is_drag_over = True
                    self._error_message = "仅支持单个文件"
                    self.update()
                    event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QEvent) -> None:
        self._is_drag_over = False
        self._is_drag_valid = False
        if self._error_message == "仅支持单个文件":
            self._error_message = None
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        self._is_drag_over = False
        self._is_drag_valid = False

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            
            if self._multi_select:
                self._handle_files_drop(file_paths)
                event.acceptProposedAction()
            else:
                if len(urls) == 1:
                    file_path = urls[0].toLocalFile()
                    self._handle_file_drop(file_path)
                    event.acceptProposedAction()
                else:
                    self._error_message = "仅支持单个文件"
                    self.errorOccurred.emit(self._error_message)
                    self.update()
                    QTimer.singleShot(3000, self._clear_error)
        else:
            event.ignore()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog()
        super().mousePressEvent(event)

    def _open_file_dialog(self) -> None:
        if self._file_filters == DropSingleFileConfig.DEFAULT_FILTER:
            filter_str = "所有文件 (*.*)"
        else:
            filter_str = ";;".join([f"文件 {f}" for f in self._file_filters])
            filter_str = f"支持的文件;;{filter_str};;所有文件 (*.*)"

        if self._multi_select:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                self._dialog_title,
                "",
                filter_str
            )
            if file_paths:
                self._handle_files_drop(file_paths)
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                self._dialog_title,
                "",
                filter_str
            )
            if file_path:
                self._handle_file_drop(file_path)

    def enterEvent(self, event: QEvent) -> None:
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 DropSingleFileWidget 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        theme = self._current_theme
        if not theme:
            return

        bg_color = theme.get_color('card.background', QColor(45, 45, 45))
        border_color = theme.get_color('card.border', QColor(68, 68, 68))
        text_primary = theme.get_color('label.text.title', QColor(224, 224, 224))
        text_secondary = theme.get_color('label.text.small', QColor(153, 153, 153))
        primary_color = theme.get_color('primary.main', QColor(93, 173, 226))
        error_color = theme.get_color('error.main', QColor(231, 76, 60))
        success_color = theme.get_color('success.main', QColor(39, 174, 96))

        rect = QRect(0, 0, self.width(), self.height())
        radius = DropSingleFileConfig.BORDER_RADIUS

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        if self._is_drag_over:
            if self._is_drag_valid:
                border_pen = QPen(primary_color, DropSingleFileConfig.BORDER_WIDTH)
            else:
                border_pen = QPen(error_color, DropSingleFileConfig.BORDER_WIDTH)
            border_pen.setStyle(Qt.PenStyle.DashLine)
            border_pen.setDashOffset(0)
            border_pen.setWidth(DropSingleFileConfig.DASH_WIDTH)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(rect).adjusted(2, 2, -2, -2), radius - 2, radius - 2)
        elif self._is_hovered:
            border_pen = QPen(primary_color, DropSingleFileConfig.BORDER_WIDTH)
            border_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(rect).adjusted(2, 2, -2, -2), radius - 2, radius - 2)
        else:
            border_pen = QPen(border_color, 1)
            border_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(rect).adjusted(2, 2, -2, -2), radius - 2, radius - 2)

        center_x = self.width() // 2
        center_y = self.height() // 2

        if self._file_paths:
            icon_color = success_color
            icon_name = self._icon_mgr.resolve_icon_name("Completed", "dark" if theme.is_dark else "light")
            icon = self._icon_mgr.get_colored_icon(icon_name, icon_color, DropSingleFileConfig.ICON_SIZE)
            icon_y = center_y - DropSingleFileConfig.ICON_SIZE // 2 - 30
            self.draw_icon(painter, icon, center_x - DropSingleFileConfig.ICON_SIZE // 2, icon_y, DropSingleFileConfig.ICON_SIZE)
            
            text_y = icon_y + DropSingleFileConfig.ICON_SIZE + 15

            font = QFont("Microsoft YaHei", 10)
            painter.setFont(font)
            painter.setPen(QPen(text_primary))

            if len(self._file_paths) == 1:
                file_name = self.fileName()
                fm = QFontMetrics(font)
                max_width = self.width() - 40
                elided_name = fm.elidedText(file_name, Qt.TextElideMode.ElideMiddle, max_width)
                
                painter.drawText(QRect(20, text_y, self.width() - 40, 25),
                               Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, elided_name)

                font_small = QFont("Microsoft YaHei", 9)
                painter.setFont(font_small)
                painter.setPen(QPen(text_secondary))
                size_str = self._format_file_size(self._file_path)
                painter.drawText(QRect(20, text_y + 22, self.width() - 40, 20),
                               Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, size_str)
            else:
                font_bold = QFont("Microsoft YaHei", 11, QFont.Weight.Bold)
                painter.setFont(font_bold)
                painter.setPen(QPen(text_primary))
                painter.drawText(QRect(20, text_y, self.width() - 40, 25),
                               Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, 
                               f"已选择 {len(self._file_paths)} 个文件")
                
                font_small = QFont("Microsoft YaHei", 9)
                painter.setFont(font_small)
                painter.setPen(QPen(text_secondary))
                painter.drawText(QRect(20, text_y + 22, self.width() - 40, 20),
                               Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, 
                               "点击重新选择")

            if self._show_success and self._success_opacity > 0:
                overlay_color = QColor(success_color)
                overlay_color.setAlpha(int(30 * self._success_opacity))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(overlay_color))
                painter.drawRoundedRect(QRectF(rect), radius, radius)

        elif self._error_message:
            icon_color = error_color
            icon_name = self._icon_mgr.resolve_icon_name("Cancel", "dark" if theme.is_dark else "light")
            icon = self._icon_mgr.get_colored_icon(icon_name, icon_color, DropSingleFileConfig.ICON_SIZE)
            icon_y = center_y - DropSingleFileConfig.ICON_SIZE // 2 - 30
            self.draw_icon(painter, icon, center_x - DropSingleFileConfig.ICON_SIZE // 2, icon_y, DropSingleFileConfig.ICON_SIZE)

            font = QFont("Microsoft YaHei", 10)
            painter.setFont(font)
            painter.setPen(QPen(error_color))

            lines = self._error_message.split('\n')
            y_offset = icon_y + DropSingleFileConfig.ICON_SIZE + 15
            for line in lines:
                painter.drawText(QRect(20, y_offset, self.width() - 40, 25),
                               Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, line)
                y_offset += 25

        else:
            icon_color = text_secondary
            icon_name = self._icon_mgr.resolve_icon_name("Folder", "dark" if theme.is_dark else "light")
            icon = self._icon_mgr.get_colored_icon(icon_name, icon_color, DropSingleFileConfig.ICON_SIZE)
            icon_y = center_y - DropSingleFileConfig.ICON_SIZE // 2 - 30
            self.draw_icon(painter, icon, center_x - DropSingleFileConfig.ICON_SIZE // 2, icon_y, DropSingleFileConfig.ICON_SIZE)

            font = QFont("Microsoft YaHei", 11, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(text_primary))
            text_y = icon_y + DropSingleFileConfig.ICON_SIZE + 15
            painter.drawText(QRect(20, text_y, self.width() - 40, 30),
                           Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._title)

            font_small = QFont("Microsoft YaHei", 9)
            painter.setFont(font_small)
            painter.setPen(QPen(text_secondary))
            painter.drawText(QRect(20, text_y + 28, self.width() - 40, 20),
                           Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._subtitle)

    def _format_file_size(self, file_path: str) -> str:
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except Exception:
            return "未知大小"

    def cleanup(self) -> None:
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

        if self._success_animation:
            self._success_animation.stop()
            self._success_animation = None

        self.clear_overrides()

    def __del__(self) -> None:
        try:
            self.cleanup()
        except Exception as e:
            logger.debug(f"Error in DropSingleFileWidget.__del__: {e}")
