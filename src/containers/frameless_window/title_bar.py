"""
无边框窗口标题栏组件

提供自定义标题栏实现，支持：
- 窗口标题显示
- 最小化/最大化/关闭按钮
- 双击最大化
- 拖动移动窗口
- 自定义组件支持（左侧、中间、右侧区域）
- 主题集成
"""

import logging
import sys
from typing import Optional, Dict, Tuple, Any

from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QColor, QIcon, QCursor
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)

from src.core.font_manager import FontManager
from src.core.icon_manager import IconManager
from src.core.theme_manager import ThemeManager, Theme
from .config import WindowConfig, TitleBarPosition

# Initialize logger
logger = logging.getLogger(__name__)


class TitleBar(QWidget):
    """
    无边框窗口的自定义标题栏。

    功能特性:
    - 窗口标题显示
    - 最小化/最大化/关闭按钮
    - 双击最大化
    - 拖动移动窗口
    - 自定义组件支持

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

        # 自定义组件存储: {position: [(widget, stretch), ...]}
        self._custom_widgets: Dict[str, list] = {
            TitleBarPosition.LEFT: [],
            TitleBarPosition.CENTER: [],
            TitleBarPosition.RIGHT: []
        }
        # 自定义组件布局引用
        self._custom_layouts: Dict[str, QHBoxLayout] = {}

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
        self.icon_label.setObjectName("iconLabel")
        self.icon_label.setFixedSize(
            WindowConfig.TITLEBAR_ICON_SIZE,
            WindowConfig.TITLEBAR_ICON_SIZE
        )
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_label)
        main_layout.addSpacing(WindowConfig.TITLEBAR_ICON_SPACING)

        # 左侧自定义组件区域（图标和标题之间）
        self._left_custom_layout = QHBoxLayout()
        self._left_custom_layout.setContentsMargins(0, 0, 0, 0)
        self._left_custom_layout.setSpacing(WindowConfig.CUSTOM_WIDGET_SPACING)
        main_layout.addLayout(self._left_custom_layout)
        self._custom_layouts[TitleBarPosition.LEFT] = self._left_custom_layout

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

        # 中间自定义组件区域（标题和控制按钮之间）
        self._center_custom_layout = QHBoxLayout()
        self._center_custom_layout.setContentsMargins(
            WindowConfig.CUSTOM_WIDGET_MARGIN, 0,
            WindowConfig.CUSTOM_WIDGET_MARGIN, 0
        )
        self._center_custom_layout.setSpacing(WindowConfig.CUSTOM_WIDGET_SPACING)
        main_layout.addLayout(self._center_custom_layout)
        self._custom_layouts[TitleBarPosition.CENTER] = self._center_custom_layout

        # 弹性空间
        main_layout.addStretch()

        # 右侧自定义组件区域（控制按钮左侧）
        self._right_custom_layout = QHBoxLayout()
        self._right_custom_layout.setContentsMargins(0, 0, 0, 0)
        self._right_custom_layout.setSpacing(WindowConfig.CUSTOM_WIDGET_SPACING)
        main_layout.addLayout(self._right_custom_layout)
        self._custom_layouts[TitleBarPosition.RIGHT] = self._right_custom_layout

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
        title_font = self._font_mgr.get_font('subtitle', theme)
        header_font = self._font_mgr.get_font('body', theme)

        # 提取字体属性
        title_family = title_font.family()
        title_size = title_font.pixelSize()
        title_weight = 'bold' if title_font.bold() else 'normal'

        header_family = header_font.family()
        header_size = header_font.pixelSize()
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

        # 检查是否在自定义组件上
        if local_pos and self._is_on_custom_widget(local_pos.toPoint()):
            event.ignore()
            return

        # 检查窗口是否正在调整大小
        if self._window and hasattr(self._window, '_resizing') and self._window._resizing:
            event.ignore()
            return

        # 开始拖动 - 记录初始状态用于绝对定位计算
        self._dragging = True
        self._drag_start_global = event.globalPosition().toPoint()
        self._drag_start_window_pos = self._window.pos() if self._window else QPoint()
        event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于窗口拖动。"""
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self._dragging:
            return

        if not self._window:
            return

        # 使用绝对定位方式计算新位置（避免跨显示器 DPI 缩放导致的累积误差）
        current_global = event.globalPosition().toPoint()
        delta = current_global - self._drag_start_global
        self._window.move(self._drag_start_window_pos + delta)

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件，用于切换最大化状态。"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # 仅在非按钮区域响应双击
        child = self.childAt(event.position().toPoint())
        if child and isinstance(child, QPushButton):
            return

        if self._window:
            self._toggle_maximize()
            event.accept()

    def _is_on_custom_widget(self, pos: QPoint) -> bool:
        """
        检查位置是否在自定义组件上。

        Args:
            pos: 标题栏内的局部位置

        Returns:
            如果在自定义组件上则返回 True
        """
        for position in [TitleBarPosition.LEFT, TitleBarPosition.CENTER, TitleBarPosition.RIGHT]:
            layout = self._custom_layouts.get(position)
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget()
                    if widget and widget.geometry().contains(pos):
                        return True
        return False

    def add_custom_widget(self, widget: QWidget, position: str = TitleBarPosition.CENTER, stretch: int = 0) -> None:
        """
        向标题栏添加自定义组件。

        Args:
            widget: 要添加的 QWidget 组件
            position: 组件位置（LEFT/CENTER/RIGHT）
            stretch: 组件的拉伸因子
        """
        if position not in self._custom_widgets:
            raise ValueError(f"Invalid position: {position}. Must be one of: {list(self._custom_widgets.keys())}")

        self._custom_widgets[position].append((widget, stretch))

        layout = self._custom_layouts.get(position)
        if layout:
            layout.addWidget(widget, stretch)

    def remove_custom_widget(self, widget: QWidget) -> bool:
        """
        从标题栏移除指定的自定义组件。

        Args:
            widget: 要移除的 QWidget 组件

        Returns:
            是否成功移除
        """
        for position in self._custom_widgets:
            widgets = self._custom_widgets[position]
            for i, (w, _) in enumerate(widgets):
                if w == widget:
                    widgets.pop(i)
                    layout = self._custom_layouts.get(position)
                    if layout:
                        layout.removeWidget(widget)
                        widget.setParent(None)
                    return True
        return False

    def clear_custom_widgets(self, position: str = None) -> None:
        """
        清除标题栏指定位置或所有自定义组件。

        Args:
            position: 要清除的位置，如果为 None 则清除所有位置
        """
        positions = [position] if position else list(self._custom_widgets.keys())

        for pos in positions:
            if pos in self._custom_widgets:
                widgets = self._custom_widgets[pos]
                layout = self._custom_layouts.get(pos)
                for widget, _ in widgets:
                    if layout:
                        layout.removeWidget(widget)
                        widget.setParent(None)
                self._custom_widgets[pos] = []

    def get_custom_widgets(self, position: str = None) -> list:
        """
        获取标题栏指定位置的自定义组件列表。

        Args:
            position: 位置，如果为 None 则返回所有组件

        Returns:
            组件列表，每个元素为 (widget, stretch) 元组
        """
        if position:
            return list(self._custom_widgets.get(position, []))

        result = []
        for position in [TitleBarPosition.LEFT, TitleBarPosition.CENTER, TitleBarPosition.RIGHT]:
            result.extend(self._custom_widgets.get(position, []))
        return result

    def cleanup(self):
        """清理资源并取消订阅以防止内存泄漏。"""
        # 取消订阅主题管理器以防止内存泄漏
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            # 不要将_theme_mgr设为None，保持引用以便后续安全访问

        # 清除窗口引用
        self._window = None
