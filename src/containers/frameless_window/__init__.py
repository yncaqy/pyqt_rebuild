"""
无边框窗口主组件

提供现代无边框窗口实现，具有以下特性：
- 自定义标题栏和窗口控制按钮
- 通过标题栏拖动窗口
- 边缘调整大小
- 主题集成
- 最大化/还原支持
- 平台特定功能（Windows 11 圆角等）

主要类:
    FramelessWindow: 主无边框窗口类
"""

import logging
import sys
import time
from typing import Optional, Dict, Tuple, Any

from PyQt6.QtCore import Qt, QPoint, QEvent, QTimer, QRect
from PyQt6.QtGui import QColor, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QLayout
)

from src.core.font_manager import FontManager
from src.core.icon_manager import IconManager
from src.core.platform import get_platform_instance
from src.core.theme_manager import ThemeManager, Theme

from .config import WindowConfig, TitleBarPosition
from .title_bar import TitleBar

# Initialize logger
logger = logging.getLogger(__name__)


class FramelessWindow(QWidget):
    """
    现代无边框窗口，带自定义标题栏。

    功能特性:
    - 无边框窗口，自定义外观
    - 自定义标题栏和窗口控制按钮
    - 通过标题栏拖动窗口
    - 边缘调整大小
    - 主题集成
    - 最大化/还原支持
    - 平台特定功能（Windows 11 圆角等）

    属性:
        title_bar: 窗口控制的标题栏实例
        content_container: 主容器控件
        content_widget: 用户控件的内容区域
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # 获取平台实例用于平台特定操作
        self._platform = get_platform_instance()

        # 获取图标管理器用于默认图标
        self._icon_mgr = IconManager.instance()

        # 设置无边框窗口标志
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMinMaxButtonsHint
        )

        # 使用配置常量初始化状态
        self._press_pos = QPoint()
        self._geometry = None
        self._edge = 'none'
        self._edge_margin = WindowConfig.DEFAULT_EDGE_MARGIN
        self._resizing = False
        self._theme = None
        self._last_cursor = None
        self._is_maximized = False
        self._saved_geometry = None

        # 边缘检测缓存
        self._edge_cache: Dict[Tuple[int, int], str] = {}
        self._cache_window_size: Optional[Tuple[int, int]] = None

        # 样式表缓存
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # 事件过滤器节流
        self._last_event_filter_time = 0
        self._event_filter_threshold = WindowConfig.EVENT_FILTER_THRESHOLD_MS

        # 启用鼠标追踪
        self.setMouseTracking(True)

        # 初始化 UI
        self._init_ui()

        # 在子控件上安装事件过滤器
        self._install_event_filters()
        self._install_event_filter_recursive(self)

        # 订阅主题变化
        ThemeManager.instance().subscribe(self, self._on_theme_changed)
        # 立即应用当前主题，确保初始化时就有正确的样式
        current_theme = ThemeManager.instance().current_theme()
        if current_theme:
            self._on_theme_changed(current_theme)

    def _set_default_icon(self) -> None:
        """从 IconManager 设置默认窗口图标。"""
        try:
            # 从 IconManager 获取默认图标
            icon = self._icon_mgr.get_icon('default_window_icon', 24)
            if not icon.isNull():
                self.setWindowIcon(icon)
                logger.info("Default window icon set successfully")
            else:
                logger.warning("Failed to load default window icon")
        except Exception as e:
            logger.error(f"Error setting default window icon: {e}")

    def _init_ui(self):
        """初始化窗口 UI。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 内容容器
        self.content_container = QWidget()
        self.content_container.setObjectName("contentContainer")
        self.content_container.setMouseTracking(True)
        main_layout.addWidget(self.content_container)

        # 容器布局
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 标题栏
        self.title_bar = TitleBar(self)
        self.title_bar.setWindow(self)
        container_layout.addWidget(self.title_bar)

        # 设置默认窗口图标
        self._set_default_icon()

        # 内容控件
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setMouseTracking(True)
        container_layout.addWidget(self.content_widget)

    def _install_event_filters(self):
        """在所有子控件上安装事件过滤器。"""
        widgets = [self.content_container, self.title_bar, self.content_widget]
        for widget in widgets:
            if widget:
                widget.installEventFilter(self)

    def _install_event_filter_recursive(self, widget):
        """递归地在控件及其子控件上安装事件过滤器。"""
        if widget is None:
            return
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            if child is not widget:
                child.installEventFilter(self)

    def _is_on_resize_edge(self, pos: QPoint, widget: Optional[QWidget] = None) -> bool:
        """
        检查位置是否在调整大小边缘。

        Args:
            pos: 相对于控件的局部位置
            widget: 要检查的控件（如果为 None，使用 self）

        Returns:
            如果在调整大小边缘则返回 True，否则返回 False
        """
        if widget is None:
            widget = self

        margin = self._edge_margin
        w = widget.width()
        h = widget.height()

        return (
                pos.x() <= margin or
                pos.x() >= w - margin or
                pos.y() <= margin or
                pos.y() >= h - margin
        )

    def setEdgeMargin(self, margin: int) -> None:
        """
        设置调整大小检测的边缘边距。

        Args:
            margin: 边缘边距（像素）
        """
        self._edge_margin = margin

    def _get_resize_edge(self, pos: QPoint) -> str:
        """检测鼠标所在的边缘，支持缓存。"""
        # 如果窗口大小改变则清除缓存
        current_size = (self.width(), self.height())
        if self._cache_window_size != current_size:
            self._edge_cache.clear()
            self._cache_window_size = current_size

        # 检查缓存
        cache_key = (pos.x(), pos.y())
        if cache_key in self._edge_cache:
            return self._edge_cache[cache_key]

        # 计算边缘
        margin = self._edge_margin
        w, h = current_size

        # 防止无效的窗口尺寸
        if w <= 0 or h <= 0:
            return 'none'

        # 首先检查角落边缘
        edge = []
        if pos.y() < margin:
            edge.append('top')
        elif pos.y() > h - margin:
            edge.append('bottom')

        if pos.x() < margin:
            edge.append('left')
        elif pos.x() > w - margin:
            edge.append('right')

        result = '-'.join(edge) if edge else 'none'

        # 缓存结果（限制缓存大小以防止内存膨胀）
        if len(self._edge_cache) < WindowConfig.MAX_EDGE_CACHE_SIZE:
            self._edge_cache[cache_key] = result

        return result

    def _update_cursor(self, edge: str) -> None:
        """
        根据边缘更新光标形状。

        Args:
            edge: 边缘标识符（如 'top', 'left', 'top-left', 'none'）
        """
        new_cursor = WindowConfig.CURSOR_MAP.get(edge, Qt.CursorShape.ArrowCursor)
        if new_cursor != self._last_cursor:
            self.setCursor(new_cursor)
            self._last_cursor = new_cursor

    def _resize_window(self, global_pos: QPoint) -> None:
        """
        根据调整大小操作期间的鼠标移动调整窗口大小。

        Args:
            global_pos: 当前全局鼠标位置
        """
        try:
            if self._geometry is None:
                return

            delta = global_pos - self._press_pos
            geo = QRect(self._geometry)
            updated = False

            if 'left' in self._edge:
                new_left = geo.left() + delta.x()
                new_width = geo.right() - new_left
                if new_width >= self.minimumWidth():
                    geo.setLeft(new_left)
                    updated = True

            if 'right' in self._edge:
                new_width = geo.width() + delta.x()
                if new_width >= self.minimumWidth():
                    geo.setWidth(new_width)
                    updated = True

            if 'top' in self._edge:
                new_top = geo.top() + delta.y()
                new_height = geo.bottom() - new_top
                if new_height >= self.minimumHeight():
                    geo.setTop(new_top)
                    updated = True

            if 'bottom' in self._edge:
                new_height = geo.height() + delta.y()
                if new_height >= self.minimumHeight():
                    geo.setHeight(new_height)
                    updated = True

            if updated:
                self.setGeometry(geo)
                self._geometry = QRect(geo)
                self._press_pos = global_pos
        except Exception as e:
            logger.error(f"_resize_window error: {e}")

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于调整大小。"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                pos = event.globalPosition()
                if pos is None:
                    return

                self._press_pos = pos.toPoint()
                self._geometry = QRect(self.geometry())

                local_pos = event.position()
                if local_pos is None:
                    return

                self._edge = self._get_resize_edge(local_pos.toPoint())
                if self._edge != 'none':
                    self._resizing = True
                    # 调整大小时停止标题栏处理拖动
                    if hasattr(self, 'title_bar'):
                        self.title_bar._dragging = False
                    # 捕获鼠标以确保接收所有鼠标事件
                    try:
                        self.grabMouse()
                    except Exception as grab_error:
                        logger.warning(f"Failed to grab mouse: {grab_error}")
                        # 如果捕获失败，确保释放鼠标
                        self.releaseMouse()
                    event.accept()
        except Exception as e:
            logger.error(f"mousePressEvent error: {e}")

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于光标更新和调整大小。"""
        try:
            if not self._resizing:
                # 更新光标
                pos = event.position()
                if pos is not None:
                    edge = self._get_resize_edge(pos.toPoint())
                    self._update_cursor(edge)
            elif event.buttons() == Qt.MouseButton.LeftButton:
                # 调整窗口大小
                global_pos = event.globalPosition()
                if global_pos is not None:
                    self._resize_window(global_pos.toPoint())
        except Exception as e:
            logger.error(f"mouseMoveEvent error: {e}")

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self._edge = 'none'

            # 释放鼠标捕获
            self.releaseMouse()

            # 关键：确保标题栏拖动状态已重置
            if hasattr(self, 'title_bar') and self.title_bar:
                self.title_bar._dragging = False

            # 调整大小后将光标重置为当前边缘状态
            try:
                pos = event.position()
                if pos is not None:
                    edge = self._get_resize_edge(pos.toPoint())
                    self._update_cursor(edge)
            except Exception as e:
                logger.debug(f"处理鼠标移动事件时出错: {e}")

    def eventFilter(self, obj, event):
        """事件过滤器，捕获子控件的鼠标事件并进行节流。"""
        try:
            # 仅处理来自子控件的鼠标移动事件
            if obj is self:
                return False

            # 调整大小时不处理
            if self._resizing:
                return False

            if event.type() == QEvent.Type.MouseMove:
                # 如果标题栏正在拖动，不更新光标
                if hasattr(self, 'title_bar') and self.title_bar._dragging:
                    return False

                # 节流事件处理以减少 CPU 使用
                current_time = time.time() * 1000  # 转换为毫秒
                if current_time - self._last_event_filter_time < self._event_filter_threshold:
                    return False
                self._last_event_filter_time = current_time

                # 直接获取全局鼠标位置
                pos = event.globalPosition()
                if pos is None:
                    return False

                global_pos = pos.toPoint()
                window_pos = self.mapFromGlobal(global_pos)

                # 在昂贵计算之前进行快速边界检查
                w, h = self.width(), self.height()
                if not (0 <= window_pos.x() <= w and 0 <= window_pos.y() <= h):
                    return False

                # 仅在靠近边缘时处理（优化）
                margin = self._edge_margin * 2  # 使用更大的边距进行早期检测
                if not (window_pos.x() < margin or window_pos.x() > w - margin or
                        window_pos.y() < margin or window_pos.y() > h - margin):
                    # 不在任何边缘附近，重置光标一次
                    if self._last_cursor != Qt.CursorShape.ArrowCursor:
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                        self._last_cursor = Qt.CursorShape.ArrowCursor
                    return False

                # 处理边缘检测
                edge = self._get_resize_edge(window_pos)
                self._update_cursor(edge)
        except Exception as e:
            logger.debug(f"Event filter error: {e}", exc_info=True)
        return False

    def changeEvent(self, event):
        """处理窗口状态变化（最大化/还原）。"""
        # 调整大小时清除边缘缓存
        if event.type() == QEvent.Type.Resize:
            self._edge_cache.clear()

        if event.type() == QEvent.Type.WindowStateChange:
            is_now_maximized = self.isMaximized()

            # 仅在状态实际改变时处理
            if is_now_maximized != self._is_maximized:
                self._is_maximized = is_now_maximized

                # 更新最大化按钮图标
                if hasattr(self, 'title_bar'):
                    self.title_bar._update_maximize_icon_state()

                # 处理平台特定的圆角首选项
                hwnd = int(self.winId())
                if is_now_maximized:
                    # 最大化时禁用圆角
                    self._platform.set_corner_preference(hwnd, rounded=False)
                else:
                    # 还原时重新启用圆角
                    self._platform.set_corner_preference(hwnd, rounded=True)

                # 处理几何
                if is_now_maximized and not self._saved_geometry:
                    # 外部最大化，保存几何
                    self._saved_geometry = self.normalGeometry()

                    # 平台特定的最大化调整
                    QTimer.singleShot(0, self._adjust_maximized_geometry)

                # 延迟重新应用主题以避免闪烁
                if self._theme:
                    QTimer.singleShot(10, lambda: self._apply_theme(self._theme))

    def _adjust_maximized_geometry(self):
        """使用平台特定实现调整最大化时的窗口几何以填充屏幕。"""
        if self._is_maximized:
            hwnd = int(self.winId())
            self._platform.maximize_window(hwnd)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题变化通知。

        Args:
            theme: 要应用的新主题
        """
        try:
            self._apply_theme(theme)
            # TitleBar 现在自行订阅主题变化
        except Exception as e:
            logger.error(f"Error applying theme to FramelessWindow: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到窗口，优化样式刷新。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        logger.debug(
            f"FramelessWindow._apply_theme called with theme: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._theme = theme
        bg_color = theme.get_color('window.background', WindowConfig.DEFAULT_WINDOW_BG_COLOR)
        border_color = theme.get_color('window.border', WindowConfig.DEFAULT_BORDER_COLOR)

        logger.debug(
            f"Background color: {bg_color.name()}, Border color: {border_color.name()}, Is maximized: {self._is_maximized}")

        # 创建缓存键
        cache_key = (
            bg_color.name(),
            border_color.name(),
            self._is_maximized,
            sys.platform == 'win32'
        )

        # 检查缓存
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            # 构建样式表
            if self._is_maximized:
                border_radius = 0
                border_css = "border: none;"
            elif sys.platform == 'win32' and not self._is_maximized:
                # Windows 11: 让系统处理圆角
                border_radius = 0
                border_css = f"border: 1px solid {border_color.name()};"
            else:
                # 其他平台：使用 CSS border-radius
                border_radius = theme.get_value('window.border_radius', 10)
                border_css = f"border: 1px solid {border_color.name()};"

            # 设置 CSS 选择器的 object name
            self.setObjectName("FramelessWindow")

            qss = f"""
                #{self.objectName()} {{
                    background-color: {bg_color.name()};
                    {border_css}
                    border-radius: {border_radius}px;
                }}
            """

            # 缓存样式表
            self._stylesheet_cache[cache_key] = qss

        # 应用样式到主窗口
        self.setStyleSheet(qss)

        # 仅将背景应用到关键容器，使用 objectName 限定范围避免样式继承问题
        container_style = f"""
            #{self.content_container.objectName()} {{
                background-color: {bg_color.name()};
            }}
            #{self.content_container.objectName()}:hover {{
                background-color: {bg_color.name()};
            }}
        """

        widget_style = f"""
            #{self.content_widget.objectName()} {{
                background-color: {bg_color.name()};
            }}
            #{self.content_widget.objectName()}:hover {{
                background-color: {bg_color.name()};
            }}
        """

        if hasattr(self, 'content_container'):
            self.content_container.setStyleSheet(container_style)

        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(widget_style)

        # 优化刷新：仅刷新主窗口和直接子控件
        # Qt 的 setStyleSheet 自动传播到子控件
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        logger.debug("Stylesheet applied to main window")

    def setWindowTitle(self, title: str) -> None:
        """
        设置窗口标题（QWidget 标准接口）。

        此方法重写 QWidget 的 setWindowTitle 以同时更新标题栏。

        Args:
            title: 窗口标题文本
        """
        super().setWindowTitle(title)
        self.title_bar.setTitle(title)

    def setTitle(self, title: str) -> None:
        """
        设置窗口标题（便捷方法，setWindowTitle 的别名）。

        Args:
            title: 窗口标题文本
        """
        self.setWindowTitle(title)

    def setWindowIcon(self, icon: QIcon) -> None:
        """
        设置窗口图标。

        Args:
            icon: 要显示的 QIcon
        """
        super().setWindowIcon(icon)
        self.title_bar.setIcon(icon)

    def setMinimizeButtonVisible(self, visible: bool) -> None:
        """
        设置最小化按钮可见性。

        Args:
            visible: True 显示最小化按钮，False 隐藏
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.minimize_btn.setVisible(visible)

    def setMaximizeButtonVisible(self, visible: bool) -> None:
        """
        设置最大化按钮可见性。

        Args:
            visible: True 显示最大化按钮，False 隐藏
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.maximize_btn.setVisible(visible)

    def setCloseButtonVisible(self, visible: bool) -> None:
        """
        设置关闭按钮可见性。

        Args:
            visible: True 显示关闭按钮，False 隐藏
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.close_btn.setVisible(visible)

    def setMinimizeButtonEnabled(self, enabled: bool) -> None:
        """
        设置最小化按钮启用状态。

        Args:
            enabled: True 启用最小化按钮，False 禁用
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.minimize_btn.setEnabled(enabled)

    def setMaximizeButtonEnabled(self, enabled: bool) -> None:
        """
        设置最大化按钮启用状态。

        Args:
            enabled: True 启用最大化按钮，False 禁用
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.maximize_btn.setEnabled(enabled)

    def setCloseButtonEnabled(self, enabled: bool) -> None:
        """
        设置关闭按钮启用状态。

        Args:
            enabled: True 启用关闭按钮，False 禁用
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.close_btn.setEnabled(enabled)

    def titleBar(self) -> Optional['TitleBar']:
        """
        获取标题栏控件。

        Returns:
            TitleBar 实例，如果未初始化则返回 None
        """
        return self.title_bar if hasattr(self, 'title_bar') else None

    def addTitleBarWidget(
            self,
            widget: QWidget,
            position: str = TitleBarPosition.CENTER,
            stretch: int = 0
    ) -> None:
        """
        向标题栏添加自定义组件。

        Args:
            widget: 要添加的 QWidget 组件
            position: 组件位置，可选值：
                - TitleBarPosition.LEFT: 图标和标题之间
                - TitleBarPosition.CENTER: 标题和控制按钮之间
                - TitleBarPosition.RIGHT: 控制按钮左侧
            stretch: 组件的拉伸因子，默认为 0（不拉伸）

        Example:
            # 添加搜索框到标题栏中间区域
            search_box = QLineEdit()
            search_box.setPlaceholderText("搜索...")
            window.addTitleBarWidget(search_box, TitleBarPosition.CENTER)

            # 添加按钮到右侧区域
            settings_btn = QPushButton("设置")
            window.addTitleBarWidget(settings_btn, TitleBarPosition.RIGHT)
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.add_custom_widget(widget, position, stretch)

    def removeTitleBarWidget(self, widget: QWidget) -> bool:
        """
        从标题栏移除指定的自定义组件。

        Args:
            widget: 要移除的 QWidget 组件

        Returns:
            bool: 是否成功移除
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            return self.title_bar.remove_custom_widget(widget)
        return False

    def clearTitleBarWidgets(self, position: str = None) -> None:
        """
        清除标题栏指定位置或所有自定义组件。

        Args:
            position: 要清除的位置，如果为 None 则清除所有位置
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.clear_custom_widgets(position)

    def getTitleBarWidgets(self, position: str = None) -> list:
        """
        获取标题栏指定位置的自定义组件列表。

        Args:
            position: 位置，如果为 None 则返回所有组件

        Returns:
            list: 组件列表，每个元素为 (widget, stretch) 元组
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            return self.title_bar.get_custom_widgets(position)
        return []

    def setCentralWidget(self, widget: QWidget) -> None:
        """
        设置中央内容控件（QMainWindow 风格）。

        Args:
            widget: 要设置为中央内容的控件

        注意:
            这会清除任何现有的布局和控件。
        """
        # 清除现有内容
        layout = self.content_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                child_widget = item.widget()
                if child_widget:
                    child_widget.deleteLater()

        # 添加新控件
        new_layout = QVBoxLayout(self.content_widget)
        new_layout.setContentsMargins(
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN
        )
        new_layout.addWidget(widget)

    def getCentralWidget(self) -> Optional[QWidget]:
        """
        获取中央内容控件。

        Returns:
            中央控件，如果未设置则返回 None
        """
        layout = self.content_widget.layout()
        if layout and layout.count() > 0:
            return layout.itemAt(0).widget()
        return None

    def getContentWidget(self) -> QWidget:
        """
        获取内容控件容器。

        Returns:
            内容控件容器
        """
        return self.content_widget

    def setLayout(self, layout: QLayout) -> None:
        """
        为内容区域设置布局（QWidget 风格）。

        这允许 FramelessWindow 像 QWidget 一样使用：

            window = FramelessWindow()
            layout = QVBoxLayout()
            layout.addWidget(widget1)
            layout.addWidget(widget2)
            window.setLayout(layout)

        Args:
            layout: 要应用到内容区域的布局
        """
        existing_layout = self.content_widget.layout()
        if existing_layout:
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                elif item.layout():
                    item.layout().setParent(None)
            existing_layout.deleteLater()

        layout.setContentsMargins(
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN
        )
        self.content_widget.setLayout(layout)

    def layout(self) -> Optional[QLayout]:
        """
        获取内容区域的布局（QWidget 风格）。

        Returns:
            内容区域的布局，如果未设置则返回 None
        """
        return self.content_widget.layout()

    def addWidget(self, widget: QWidget) -> None:
        """
        便捷方法，向内容区域添加控件。

        如果不存在 QVBoxLayout 则创建一个，并添加控件。

        Args:
            widget: 要添加的控件

        示例:
            window = FramelessWindow()
            window.addWidget(label1)
            window.addWidget(button1)
        """
        layout = self.content_widget.layout()

        # 如果不存在布局则创建
        if layout is None:
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN
            )

        layout.addWidget(widget)

    def addLayout(self, layout: QLayout) -> None:
        """
        便捷方法，向内容区域添加子布局。

        Args:
            layout: 要添加的布局

        示例:
            window = FramelessWindow()
            main_layout = window.contentLayout
            sub_layout = QHBoxLayout()
            sub_layout.addWidget(button1)
            sub_layout.addWidget(button2)
            main_layout.addLayout(sub_layout)
        """
        parent_layout = self.content_widget.layout()

        # 如果不存在布局则创建
        if parent_layout is None:
            parent_layout = QVBoxLayout(self.content_widget)
            parent_layout.setContentsMargins(
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN
            )

        parent_layout.addLayout(layout)

    @property
    def contentLayout(self) -> QLayout:
        """
        获取内容区域的布局，如果需要则创建一个。

        Returns:
            内容区域的布局（总是返回有效的布局）

        示例:
            window = FramelessWindow()
            window.contentLayout.addWidget(widget)
        """
        layout = self.content_widget.layout()
        if layout is None:
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN
            )
        return layout

    @contentLayout.setter
    def contentLayout(self, layout: QLayout) -> None:
        """
        设置内容区域的布局。

        Args:
            layout: 要应用的布局

        示例:
            window = FramelessWindow()
            window.contentLayout = QVBoxLayout()
        """
        self.setLayout(layout)

    def showEvent(self, event):
        """处理显示事件，启用平台特定的窗口功能。"""
        super().showEvent(event)
        if event.isAccepted():
            # 应用初始主题
            if not self._theme:
                current_theme = ThemeManager.instance().current_theme()
                if current_theme:
                    self._on_theme_changed(current_theme)

            # 启用平台特定功能（如 Windows 11 的圆角）
            hwnd = int(self.winId())
            self._platform.set_corner_preference(hwnd, rounded=True)

    def closeEvent(self, event):
        """处理关闭事件。"""
        # 关闭前保存窗口状态
        if hasattr(self, 'title_bar'):
            self.title_bar._window = None
            # 关键：调用 cleanup 以取消订阅主题管理器
            self.title_bar.cleanup()

        # 取消订阅主题管理器
        ThemeManager.instance().unsubscribe(self)

        super().closeEvent(event)
