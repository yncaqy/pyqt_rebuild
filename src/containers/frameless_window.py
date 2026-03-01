"""
无边框窗口组件

提供现代无边框窗口支持，具有以下特性：
- 自定义标题栏和窗口控制按钮
- 通过标题栏拖动窗口
- 边缘调整大小
- 主题集成
- 平台特定功能（Windows 11 圆角等）

类:
    WindowConfig: 无边框窗口配置常量
    TitleBar: 自定义标题栏
    FramelessWindow: 主无边框窗口类
"""

import sys
import logging
import time
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QPoint, QEvent, QTimer
from PyQt6.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QLayout
)
from core.theme_manager import ThemeManager, Theme
from core.font_manager import FontManager
from core.platform import get_platform_instance
from core.icon_manager import IconManager

# Initialize logger
logger = logging.getLogger(__name__)


class WindowConfig:
    """无边框窗口行为配置常量。"""

    # 边缘检测
    DEFAULT_EDGE_MARGIN = 6  # 像素
    TITLEBAR_EDGE_MARGIN = 6  # 像素

    # 标题栏尺寸
    TITLEBAR_HEIGHT = 40
    TITLEBAR_BUTTON_WIDTH = 46
    TITLEBAR_BUTTON_HEIGHT = 40
    TITLEBAR_ICON_SIZE = 24
    TITLEBAR_ICON_SPACING = 12  # 图标和标题之间的间距
    TITLEBAR_LAYOUT_MARGIN_LEFT = 10  # 标题栏布局左边距

    # 图标尺寸
    BUTTON_ICON_SOURCE_SIZE = 32  # 加载时的源尺寸（HiDPI 支持）
    BUTTON_ICON_DISPLAY_SIZE = 20  # 按钮上的显示尺寸
    BUTTON_COLORED_ICON_SOURCE_SIZE = 32  # 彩色图标的源尺寸

    # 窗口约束
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300

    # 性能调优
    EVENT_FILTER_THRESHOLD_MS = 16  # 约 60fps
    MAX_EDGE_CACHE_SIZE = 1000

    # 内容边距
    CONTENT_MARGIN = 10

    # 默认颜色值（主题不可用时的回退值）
    DEFAULT_TITLEBAR_TEXT_COLOR = QColor(220, 220, 220)
    DEFAULT_TITLEBAR_BG_COLOR = QColor(30, 30, 30)
    DEFAULT_BUTTON_HOVER_COLOR = QColor(50, 50, 50)
    DEFAULT_CLOSE_HOVER_COLOR = QColor(231, 76, 60)
    DEFAULT_WINDOW_BG_COLOR = QColor(25, 25, 25)
    DEFAULT_BORDER_COLOR = QColor(40, 40, 40)

    # 边缘调整大小的光标
    CURSOR_MAP = {
        'top': Qt.CursorShape.SizeVerCursor,
        'bottom': Qt.CursorShape.SizeVerCursor,
        'left': Qt.CursorShape.SizeHorCursor,
        'right': Qt.CursorShape.SizeHorCursor,
        'top-left': Qt.CursorShape.SizeFDiagCursor,
        'top-right': Qt.CursorShape.SizeBDiagCursor,
        'bottom-left': Qt.CursorShape.SizeBDiagCursor,
        'bottom-right': Qt.CursorShape.SizeFDiagCursor,
        'none': Qt.CursorShape.ArrowCursor
    }


class TitleBar(QWidget):
    """
    无边框窗口的自定义标题栏。

    功能特性:
    - 窗口标题显示
    - 最小化/最大化/关闭按钮
    - 双击最大化
    - 拖动移动窗口

    属性:
        icon_label: 窗口图标标签
        title_label: 窗口标题标签
        minimize_btn: 最小化按钮
        maximize_btn: 最大化/还原按钮
        close_btn: 关闭按钮
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(WindowConfig.TITLEBAR_HEIGHT)
        self._theme_mgr = ThemeManager.instance()
        self._font_mgr = FontManager.instance()
        self._icon_mgr = IconManager.instance()
        self._icon = None
        self._dragging = False
        self._drag_position = QPoint()
        self._window = None
        self._edge_margin = WindowConfig.TITLEBAR_EDGE_MARGIN

        # 标题栏样式表缓存
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # 启用鼠标追踪
        self.setMouseTracking(True)

        # 创建布局
        self._init_ui()
        self._init_control_buttons()

        # 订阅主题变化
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        # 应用初始主题
        current_theme = self._theme_mgr.current_theme()
        if current_theme:
            self._apply_theme(current_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器的主题变化通知。
        
        Args:
            theme: 要应用的新主题
        """
        self._apply_theme(theme)

    def _init_ui(self) -> None:
        """初始化 UI 布局。"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(WindowConfig.TITLEBAR_LAYOUT_MARGIN_LEFT, 0, 0, 0)
        main_layout.setSpacing(0)

        # 图标标签
        self.icon_label = QLabel()
        self.icon_label.setObjectName("iconLabel")  # 设置 objectName 用于样式选择器
        self.icon_label.setFixedSize(
            WindowConfig.TITLEBAR_ICON_SIZE,
            WindowConfig.TITLEBAR_ICON_SIZE
        )
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_label)
        # 添加固定宽度的spacing作为图标和标题之间的间距
        main_layout.addSpacing(WindowConfig.TITLEBAR_ICON_SPACING)

        # 标题标签
        self.title_label = QLabel()
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        main_layout.addWidget(self.title_label)

        # 窗口按钮的间隔
        main_layout.addStretch()

    def _init_control_buttons(self):
        """初始化窗口控制按钮。"""
        # 为最小化按钮加载 SVG 图标
        self.minimize_btn = self._create_button("", "minimize", "window_minimize")
        # 为最大化按钮加载 SVG 图标
        self.maximize_btn = self._create_button("", "maximize", "window_maximize")
        # 为关闭按钮加载 SVG 图标
        self.close_btn = self._create_button("", "close", "window_close")

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn_layout.addWidget(self.minimize_btn)
        btn_layout.addWidget(self.maximize_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout = self.layout()
        main_layout.addLayout(btn_layout)

    def _create_button(self, text: str, name: str, icon_name: str = None) -> QPushButton:
        """
        创建具有指定文本和对象名称的窗口控制按钮。

        Args:
            text: 按钮文本/标签
            name: 用于样式的对象名称（如 'minimize', 'maximize', 'close'）
            icon_name: 可选的 SVG 图标名称，从 IconManager 加载

        Returns:
            配置好的 QPushButton 实例
        """
        btn = QPushButton(text)
        btn.setFixedSize(
            WindowConfig.TITLEBAR_BUTTON_WIDTH,
            WindowConfig.TITLEBAR_BUTTON_HEIGHT
        )
        btn.setObjectName(f"titlebar_{name}_btn")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # 如果提供了图标名称则加载图标
        if icon_name:
            try:
                # 以较大尺寸加载图标以获得更好的渲染质量
                # 高 DPI 显示器在较大源尺寸下效果更好
                icon = self._icon_mgr.get_icon(icon_name, WindowConfig.BUTTON_ICON_SOURCE_SIZE)
                if not icon.isNull():
                    btn.setIcon(icon)
                    from PyQt6.QtCore import QSize
                    btn.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                         WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                    btn.setProperty("no-text", "true")
                    btn.setText("")  # 使用图标时清除文本
                    logger.info(f"Loaded icon '{icon_name}' for button '{name}'")
                else:
                    logger.warning(f"Icon '{icon_name}' is null, failed to load")
            except Exception as e:
                logger.warning(f"Failed to load icon {icon_name}: {e}")

        return btn

    def _update_button_icon(self, button: QPushButton, icon_name: str, color: QColor, button_type: str) -> None:
        """
        使用主题颜色更新按钮图标（适用于所有窗口控制按钮的通用方法）。

        Args:
            button: 要更新的 QPushButton 实例
            icon_name: 从 IconManager 加载的图标名称
            color: 要应用到图标的主题颜色
            button_type: 用于日志记录的按钮类型名称（如 'close', 'minimize', 'maximize'）
        """
        try:
            # 以较大尺寸加载图标以获得更好的渲染质量
            # 使用 IconManager 的 get_colored_icon 方法应用主题颜色
            colored_icon = self._icon_mgr.get_colored_icon(icon_name, color,
                                                          WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)
            if not colored_icon.isNull():
                button.setIcon(colored_icon)
                from PyQt6.QtCore import QSize
                button.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                       WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                logger.debug(f"{button_type.capitalize()} button icon updated with color: {color.name()}")
            else:
                logger.warning(f"Failed to create colored icon for {button_type} button")
        except Exception as e:
            logger.warning(f"Error updating {button_type} button icon: {e}")

    def _update_close_button_icon(self, color: QColor) -> None:
        """
        使用主题颜色更新关闭按钮图标。

        Args:
            color: 要应用到图标的主题颜色
        """
        self._update_button_icon(self.close_btn, 'window_close', color, 'close')

    def _update_minimize_button_icon(self, color: QColor) -> None:
        """
        使用主题颜色更新最小化按钮图标。

        Args:
            color: 要应用到图标的主题颜色
        """
        self._update_button_icon(self.minimize_btn, 'window_minimize', color, 'minimize')

    def _update_maximize_button_icon(self, color: QColor) -> None:
        """
        使用主题颜色更新最大化按钮图标。

        Args:
            color: 要应用到图标的主题颜色
        """
        self._update_button_icon(self.maximize_btn, 'window_maximize', color, 'maximize')

    def _toggle_maximize(self):
        """切换最大化和正常状态。"""
        if self._window:
            # 使用 Qt 内置的最大化功能
            if self._window.isMaximized():
                self._window.showNormal()
            else:
                self._window.showMaximized()
            # 状态改变后更新图标
            self._update_maximize_icon_state()

    def _update_maximize_icon_state(self):
        """根据窗口状态更新最大化按钮图标。"""
        if not self._window:
            return

        try:
            # 获取当前主题颜色
            theme = self._theme_mgr.current_theme()
            if not theme:
                return

            text_color = theme.get_color('titlebar.text', WindowConfig.DEFAULT_TITLEBAR_TEXT_COLOR)

            # 根据窗口状态使用适当的图标
            if self._window.isMaximized():
                # 显示还原图标
                colored_icon = self._icon_mgr.get_colored_icon('window_restore', text_color,
                                                              WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)
            else:
                # 显示最大化图标
                colored_icon = self._icon_mgr.get_colored_icon('window_maximize', text_color,
                                                              WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)

            if not colored_icon.isNull():
                from PyQt6.QtCore import QSize
                self.maximize_btn.setIcon(colored_icon)
                self.maximize_btn.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                                   WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                logger.debug(f"Maximize button icon updated: {'restore' if self._window.isMaximized() else 'maximize'}")
        except Exception as e:
            logger.warning(f"Error updating maximize button icon state: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到标题栏，支持缓存。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        logger.debug(f"TitleBar._apply_theme called with theme: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        if not theme:
            logger.debug("Theme is None, returning")
            return

        bg_color = theme.get_color('titlebar.background', WindowConfig.DEFAULT_TITLEBAR_BG_COLOR)
        text_color = theme.get_color('titlebar.text', WindowConfig.DEFAULT_TITLEBAR_TEXT_COLOR)
        hover_bg = theme.get_color('titlebar.button.hover', WindowConfig.DEFAULT_BUTTON_HOVER_COLOR)
        close_hover = theme.get_color('titlebar.button.close_hover', WindowConfig.DEFAULT_CLOSE_HOVER_COLOR)
        border_color = theme.get_color('window.border', WindowConfig.DEFAULT_BORDER_COLOR)

        # 将主题颜色应用到所有按钮图标
        self._update_minimize_button_icon(text_color)
        self._update_maximize_button_icon(text_color)
        self._update_close_button_icon(text_color)

        # 获取主题字体
        title_font = self._font_mgr.get_font('title', theme)
        header_font = self._font_mgr.get_font('header', theme)
        
        # 提取字体属性
        title_family = title_font.family()
        title_size = title_font.pointSize()
        title_weight = 'bold' if title_font.bold() else 'normal'
        
        header_family = header_font.family()
        header_size = header_font.pointSize()
        header_weight = 'bold' if header_font.bold() else 'normal'

        # 检查窗口是否最大化
        is_maximized = self._window.isMaximized() if self._window else False

        # 创建缓存键
        cache_key = (
            bg_color.name(),
            text_color.name(),
            hover_bg.name(),
            close_hover.name(),
            border_color.name(),
            title_family,
            title_size,
            title_weight,
            header_family,
            header_size,
            header_weight,
            sys.platform == 'win32',
            is_maximized
        )

        # 检查缓存
        if cache_key not in self._stylesheet_cache:
            # 仅在非最大化时应用圆角和底部边框
            if sys.platform == 'win32' and not is_maximized:
                # Windows 11: 让系统处理圆角
                border_radius_css = "border-top-left-radius: 8px; border-top-right-radius: 8px;"
                border_bottom_css = f"border-bottom: 1px solid {border_color.name()};"
            else:
                border_radius_css = ""
                border_bottom_css = "border-bottom: none;"

            stylesheet = f"""
                TitleBar {{
                    background-color: {bg_color.name()};
                    {border_bottom_css}
                    {border_radius_css}
                }}
                QLabel {{
                    color: {text_color.name()};
                    font-family: "{title_family}";
                    font-size: {title_size}px;
                    font-weight: {title_weight};
                }}
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {text_color.name()};
                    font-family: "{header_family}";
                    font-size: {header_size}px;
                    font-weight: {header_weight};
                    border-radius: 0px;
                    /* 图标居中 */
                }}
                QPushButton:hover {{
                    background-color: {close_hover.name()};
                    color: white;
                }}
                /* 有图标的按钮样式 */
                QPushButton[no-text="true"] {{
                    padding: 0px;
                }}
                QPushButton#titlebar_close_btn {{
                    padding: 0px;
                }}
            """

            # 缓存样式表
            self._stylesheet_cache[cache_key] = stylesheet

        # 应用缓存的样式表
        self.setStyleSheet(self._stylesheet_cache[cache_key])

        # 强制刷新样式
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        logger.debug("TitleBar style applied")

    def setTitle(self, title: str) -> None:
        """
        设置窗口标题。

        Args:
            title: 窗口标题文本
        """
        self.title_label.setText(title)

    def setIcon(self, icon: QIcon) -> None:
        """
        设置窗口图标。

        Args:
            icon: 要在标题栏显示的 QIcon
        """
        self._icon = icon
        self.icon_label.setPixmap(icon.pixmap(24, 24))

    def setWindow(self, window: 'FramelessWindow') -> None:
        """设置父窗口引用。"""
        self._window = window
        # 连接按钮信号
        self.minimize_btn.clicked.connect(window.showMinimized)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.close_btn.clicked.connect(window.close)

    def _is_on_top_edge(self, pos: QPoint) -> bool:
        """
        检查位置是否在顶部边缘，用于调整大小检测。

        Args:
            pos: 标题栏内的局部位置

        Returns:
            如果 y 位置在边缘边距内则返回 True
        """
        margin = self._edge_margin
        return pos.y() <= margin

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口拖动。"""
        if event.button() != Qt.MouseButton.LeftButton:
            return
            
        # 优先检查是否在调整大小边缘
        local_pos = event.position()
        if local_pos and self._is_on_top_edge(local_pos.toPoint()):
            event.ignore()
            return
            
        # 检查窗口是否正在调整大小
        if self._window and getattr(self._window, '_resizing', False):
            event.ignore()
            return
            
        # 开始拖拽
        self._dragging = True
        pos = event.globalPosition()
        self._drag_position = pos.toPoint() if pos else QPoint()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口拖动。"""
        # 不在拖拽状态或不是左键按下时不处理
        if not self._dragging or event.buttons() != Qt.MouseButton.LeftButton:
            return
            
        # 检查窗口状态
        if not self._window or self._window.isMaximized():
            return
            
        # 执行窗口移动
        pos = event.globalPosition()
        if pos:
            current_pos = pos.toPoint()
            delta = current_pos - self._drag_position
            new_pos = self._window.pos() + delta
            self._window.move(new_pos)
            self._drag_position = current_pos

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event):
        """处理双击事件，切换最大化状态。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()

    def cleanup(self):
        """清理资源并取消事件订阅。"""
        # 取消订阅主题管理器以防止内存泄漏
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            # 不要将_theme_mgr设为None，保持引用以便后续安全访问

        # 清除窗口引用
        self._window = None


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
            geo = self._geometry

            # 最小尺寸约束
            min_w = WindowConfig.MIN_WINDOW_WIDTH
            min_h = WindowConfig.MIN_WINDOW_HEIGHT

            # 获取当前窗口几何
            current_geo = self.geometry()
            current_w = current_geo.width()
            current_h = current_geo.height()

            # 关键：检查是否已达到最小尺寸并尝试进一步缩小
            # 这可以防止在最小尺寸时窗口移动
            if 'top' in self._edge or 'bottom' in self._edge:
                if current_h <= min_h:
                    # 已达到最小高度，检查是否尝试缩小
                    if ('top' in self._edge and delta.y() > 0) or \
                       ('bottom' in self._edge and delta.y() < 0):
                        return  # 尝试缩小到最小以下，完全停止

            if 'left' in self._edge or 'right' in self._edge:
                if current_w <= min_w:
                    # 已达到最小宽度，检查是否尝试缩小
                    if ('left' in self._edge and delta.x() > 0) or \
                       ('right' in self._edge and delta.x() < 0):
                        return  # 尝试缩小到最小以下，完全停止

            # 计算新边界
            new_left = geo.left()
            new_top = geo.top()
            new_right = geo.right()
            new_bottom = geo.bottom()

            # 应用边缘特定的调整大小，强制执行最小尺寸
            if 'top' in self._edge:
                new_top = geo.top() + delta.y()
                if geo.bottom() - new_top < min_h:
                    new_top = geo.bottom() - min_h
            if 'bottom' in self._edge:
                new_bottom = geo.bottom() + delta.y()
                if new_bottom - geo.top() < min_h:
                    new_bottom = geo.top() + min_h
            if 'left' in self._edge:
                new_left = geo.left() + delta.x()
                if geo.right() - new_left < min_w:
                    new_left = geo.right() - min_w
            if 'right' in self._edge:
                new_right = geo.right() + delta.x()
                if new_right - geo.left() < min_w:
                    new_right = geo.left() + min_w

            # 关键：仅在实际会修改窗口时应用几何变化
            # 这可以防止在最小尺寸时的虚假位置变化
            if (new_left != geo.left() or new_top != geo.top() or
                new_right != geo.right() or new_bottom != geo.bottom()):
                self.setGeometry(new_left, new_top, new_right - new_left, new_bottom - new_top)
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
                self._geometry = self.frameGeometry()

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
            except Exception:
                pass

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

                # 重新应用主题以更新边框和圆角
                if self._theme:
                    self._apply_theme(self._theme)
                    # 标题栏主题会在_on_theme_changed中统一处理

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
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到窗口，优化样式刷新。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        logger.debug(f"FramelessWindow._apply_theme called with theme: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._theme = theme
        bg_color = theme.get_color('window.background', WindowConfig.DEFAULT_WINDOW_BG_COLOR)
        border_color = theme.get_color('window.border', WindowConfig.DEFAULT_BORDER_COLOR)

        logger.debug(f"Background color: {bg_color.name()}, Border color: {border_color.name()}, Is maximized: {self._is_maximized}")

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

        # 仅将背景应用到关键容器（不是所有子控件）
        bg_style = f"background-color: {bg_color.name()};"

        if hasattr(self, 'content_container'):
            self.content_container.setStyleSheet(bg_style)

        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(bg_style)

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
