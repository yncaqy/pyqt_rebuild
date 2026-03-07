"""
Toast 通知组件

提供现代 Toast 通知控件，具有以下特性：
- 主题集成，自动更新
- 平滑的淡入/淡出动画
- 多种 Toast 类型（信息、成功、警告、错误）
- 灵活的位置设置
- 自动隐藏，悬停时暂停
- 优化的样式缓存，提升性能
- 内存安全，正确清理资源
"""

import logging
from typing import Optional, Dict, Tuple, Any
from enum import Enum
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QRectF, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFrame, QGraphicsOpacityEffect, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class ToastPosition(Enum):
    """
    Toast 显示位置。
    
    位置相对于父控件或窗口。
    """
    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_CENTER = 5
    BOTTOM_RIGHT = 6
    CENTER = 7


class ToastType(Enum):
    """
    Toast 消息类型，具有语义含义。
    
    每种类型在主题中有自己的配色方案。
    """
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ToastConfig:
    """Toast 行为和样式配置常量。"""
    
    # 尺寸约束
    ICON_SIZE = 18
    CLOSE_BUTTON_SIZE = 16
    
    # 间距
    MARGIN = 20  # 距离父控件边缘的边距
    CONTENT_MARGIN_H = 12  # 水平内容边距
    CONTENT_MARGIN_V = 8   # 垂直内容边距
    SPACING = 8  # 元素之间的间距
    
    # 动画
    FADE_DURATION = 300  # 毫秒
    HOVER_DELAY = 500  # 鼠标离开后等待的毫秒数
    
    # 图标字符
    ICONS = {
        ToastType.INFO: "ℹ",
        ToastType.SUCCESS: "✓",
        ToastType.WARNING: "⚠",
        ToastType.ERROR: "✕"
    }
    
    # 图标样式
    ICON_FONT_SIZE = 14
    CLOSE_BUTTON_FONT_SIZE = 14
    
    # 消息样式
    MESSAGE_FONT_SIZE = 12
    
    # 默认持续时间
    DEFAULT_DURATION = 3000  # 毫秒
    
    # 缓存大小限制
    MAX_STYLESHEET_CACHE_SIZE = 50
    
    # 关闭按钮可见性
    DEFAULT_SHOW_CLOSE_BUTTON = False


class Toast(QFrame):
    """
    现代 Toast 通知控件，支持主题和平滑动画。

    功能特性:
    - 主题集成，自动更新
    - 使用 QPropertyAnimation 实现平滑淡入/淡出动画
    - 多种 Toast 类型（信息、成功、警告、错误）
    - 灵活的位置设置（9 个预定义位置）
    - 可配置持续时间的自动隐藏
    - 悬停暂停（鼠标悬停时暂停自动隐藏）
    - 点击关闭功能
    - 内存安全，正确清理资源

    架构说明:
        Toast 使用 Qt 的透明度效果和属性动画系统实现平滑的淡入淡出过渡。
        它与主题管理器集成，确保整个应用程序的样式一致性。

    使用示例:
        toast = Toast("操作成功完成", ToastType.SUCCESS)
        toast.show(ToastPosition.TOP_CENTER, parent_widget)
    """

    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = ToastConfig.DEFAULT_DURATION,
        show_close_button: bool = ToastConfig.DEFAULT_SHOW_CLOSE_BUTTON,
        parent: Optional[QWidget] = None
    ):
        """
        初始化 Toast 通知。

        Args:
            message: Toast 消息文本
            toast_type: Toast 类型（info, success, warning, error）
            duration: 自动隐藏持续时间（毫秒），0 表示不自动隐藏
            show_close_button: 是否显示关闭按钮
            parent: 父控件
        """
        super().__init__(parent)
        
        self._icon_mgr = IconManager.instance()
        
        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        self._show_close_button = show_close_button
        self._opacity = 0.0

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._setup_ui()

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self._setup_animations()

        if duration > 0:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._hide)
            self._timer.setSingleShot(True)

        self._prewarm_animations()

        logger.debug(f"Toast created: {message} (type: {toast_type.value}, duration: {duration}ms)")

    def _setup_ui(self) -> None:
        """初始化 UI 组件。"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            ToastConfig.CONTENT_MARGIN_H,
            ToastConfig.CONTENT_MARGIN_V,
            ToastConfig.CONTENT_MARGIN_H,
            ToastConfig.CONTENT_MARGIN_V
        )
        layout.setSpacing(ToastConfig.SPACING)
        
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(ToastConfig.ICON_SIZE, ToastConfig.ICON_SIZE)
        layout.addWidget(self._icon_label)
        
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(False)
        self._message_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self._message_label, 1)
        
        self._close_button = None
        if self._show_close_button:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(ToastConfig.CLOSE_BUTTON_SIZE, ToastConfig.CLOSE_BUTTON_SIZE)
            self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_button.clicked.connect(self._hide)
            layout.addWidget(self._close_button)

    def _setup_animations(self) -> None:
        """初始化淡入/淡出动画。"""
        self._fade_animation = QPropertyAnimation(self, b"opacity")
        self._fade_animation.setDuration(ToastConfig.FADE_DURATION)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._is_closing = False
        self._fade_animation.finished.connect(self._on_animation_finished)

    def _prewarm_animations(self) -> None:
        """
        预热动画系统以防止首次使用延迟。

        运行最小动画周期来初始化 Qt 的动画系统和图形效果管道，
        消除首次使用时的延迟。
        """
        try:
            self._opacity_effect.setOpacity(0.01)
            self._opacity_effect.setOpacity(0.0)
            self.update()
            self.adjustSize()
            logger.debug("Animation system pre-warmed")
        except Exception as e:
            logger.warning(f"Error pre-warming animations: {e}")

    def _on_animation_finished(self) -> None:
        """动画完成事件处理。"""
        if self._is_closing:
            self._close()
            self._is_closing = False

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器的主题变化通知。

        Args:
            theme: 要应用的新主题
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"Error applying theme to Toast: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到 Toast，支持缓存。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._current_theme = theme

        type_key = f'toast.{self._toast_type.value}'

        bg_color = theme.get_color(f'{type_key}.background', QColor(50, 50, 50))
        text_color = theme.get_color(f'{type_key}.text', QColor(255, 255, 255))
        border_color = theme.get_color(f'{type_key}.border', QColor(100, 100, 100))
        icon_color = theme.get_color(f'{type_key}.icon', QColor(255, 255, 255))

        border_radius = theme.get_value('toast.border_radius', 8)
        shadow_blur = theme.get_value('toast.shadow_blur', 10)

        cache_key = (
            bg_color.name(),
            text_color.name(),
            border_color.name(),
            icon_color.name(),
            border_radius,
            shadow_blur,
            self._toast_type.value,
        )

        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
            logger.debug("Using cached stylesheet for Toast")
        else:
            qss = f"""
            Toast {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {border_radius}px;
                padding: 0px;
            }}
            Toast QLabel {{
                color: {text_color.name()};
                background: transparent;
                border: none;
                font-size: {ToastConfig.MESSAGE_FONT_SIZE}px;
            }}
            Toast QPushButton {{
                color: {text_color.name()};
                background: transparent;
                border: none;
                font-size: {ToastConfig.CLOSE_BUTTON_FONT_SIZE}px;
                font-weight: bold;
            }}
            Toast QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: {border_radius}px;
            }}
            """

            if len(self._stylesheet_cache) < ToastConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss
                logger.debug(f"Cached stylesheet (cache size: {len(self._stylesheet_cache)})")

        self.setStyleSheet(qss)

        self.style().unpolish(self)
        self.style().polish(self)

        self._update_icon(icon_color)

        logger.debug(f"Theme applied to Toast: {theme.name if hasattr(theme, 'name') else 'unknown'}")

    def _update_icon(self, color: QColor) -> None:
        """
        根据 Toast 类型更新图标。

        Args:
            color: 图标颜色
        """
        icon_names = {
            ToastType.INFO: "info",
            ToastType.SUCCESS: "success",
            ToastType.WARNING: "warning",
            ToastType.ERROR: "error"
        }
        
        icon_name = icon_names.get(self._toast_type, "")
        
        if icon_name:
            icon = self._icon_mgr.get_icon(icon_name, ToastConfig.ICON_SIZE)
            self._icon_label.setPixmap(icon.pixmap(ToastConfig.ICON_SIZE, ToastConfig.ICON_SIZE))
            self._icon_label.setStyleSheet("")
        else:
            icon_text = ToastConfig.ICONS.get(self._toast_type, ToastConfig.ICONS[ToastType.INFO])
            self._icon_label.setText(icon_text)
            self._icon_label.setStyleSheet(
                f"color: {color.name()}; "
                f"font-size: {ToastConfig.ICON_FONT_SIZE}px; "
                f"font-weight: bold;"
            )

    @pyqtProperty(float)
    def opacity(self) -> float:
        """
        透明度属性（用于动画）。

        Returns:
            当前透明度值（0.0 到 1.0）
        """
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        """
        透明度属性设置器。

        Args:
            value: 新的透明度值（0.0 到 1.0）
        """
        self._opacity = value
        self._opacity_effect.setOpacity(value)
        self.update()
        logger.debug(f"Opacity set to: {value}")

    def show(self, position: ToastPosition = ToastPosition.TOP_CENTER, parent: Optional[QWidget] = None, show_close_button: bool = None) -> None:
        """
        在指定位置显示 Toast。

        Args:
            position: Toast 相对于父控件的位置
            parent: 父控件（如果为 None 则使用 window()）
            show_close_button: 是否显示关闭按钮（如果为 None 则使用实例默认值）

        使用示例:
            toast.show(ToastPosition.TOP_CENTER, main_window)
            toast.show(ToastPosition.TOP_CENTER, main_window, show_close_button=True)
        """
        if show_close_button is not None:
            self._show_close_button = show_close_button
        if parent:
            top_level = parent.window() if parent.window() else parent
            self.setParent(top_level)

        self.adjustSize()

        parent_widget = self.parent()
        if parent_widget:
            self._position_at(parent_widget, position)

        self.raise_()
        super().show()

        self._fade_in()

        if self._duration > 0 and hasattr(self, '_timer'):
            self._timer.start(self._duration)

        logger.info(f"Toast shown at {position.name}: {self._message}")

    def _position_at(self, parent: QWidget, position: ToastPosition) -> None:
        """
        将 Toast 定位到相对于父控件的位置。

        Args:
            parent: 用于定位的父控件
            position: 期望的 Toast 位置
        """
        rect = parent.rect()

        if self.width() == 0 or self.height() == 0:
            self.adjustSize()

        toast_width = self.width()
        toast_height = self.height()

        x, y = 0, 0
        margin = ToastConfig.MARGIN

        titlebar_height = 0
        if hasattr(parent, 'title_bar') and parent.title_bar:
            titlebar_height = parent.title_bar.height()

        top_margin = margin + titlebar_height

        if position == ToastPosition.TOP_LEFT:
            x = margin
            y = top_margin
        elif position == ToastPosition.TOP_CENTER:
            x = (rect.width() - toast_width) // 2
            y = top_margin
        elif position == ToastPosition.TOP_RIGHT:
            x = rect.width() - toast_width - margin
            y = top_margin
        elif position == ToastPosition.BOTTOM_LEFT:
            x = margin
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.BOTTOM_CENTER:
            x = (rect.width() - toast_width) // 2
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.BOTTOM_RIGHT:
            x = rect.width() - toast_width - margin
            y = rect.height() - toast_height - margin
        elif position == ToastPosition.CENTER:
            x = (rect.width() - toast_width) // 2
            y = (rect.height() - toast_height) // 2

        self.move(x, y)
        logger.debug(f"Positioned at ({x}, {y})")

    def _fade_in(self) -> None:
        """开始淡入动画。"""
        self._fade_animation.stop()
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._is_closing = False
        self._fade_animation.start()
        logger.debug("Fade in animation started")

    def _hide(self) -> None:
        """隐藏 Toast，带淡出动画。"""
        self._fade_animation.stop()
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._is_closing = True
        self._fade_animation.start()
        logger.debug("Fade out animation started")

    def _close(self) -> None:
        """关闭 Toast 并清理资源。"""
        self.timer_stop()
        super().close()
        logger.debug("Toast closed")

    def timer_stop(self) -> None:
        """停止自动隐藏定时器。"""
        if hasattr(self, '_timer') and self._timer.isActive():
            self._timer.stop()
            logger.debug("Auto-hide timer stopped")

    def close(self) -> None:
        """
        关闭 Toast，带淡出动画。

        这会在关闭 Toast 之前启动平滑的淡出效果。

        使用示例:
            toast.close()  # 淡出并关闭
        """
        self._hide()

    def mousePressEvent(self, event) -> None:
        """
        鼠标按下事件处理，实现点击关闭功能。

        点击 Toast 的任意位置都会关闭它。

        Args:
            event: 鼠标按下事件
        """
        self._hide()
        logger.debug("Toast closed by mouse click")

    def enterEvent(self, event: QEvent) -> None:
        """
        鼠标进入事件处理，暂停自动隐藏定时器。

        这允许用户阅读消息而不会消失。

        Args:
            event: 进入事件
        """
        if hasattr(self, '_timer') and self._timer.isActive():
            self._timer.stop()
            logger.debug("Auto-hide paused (mouse entered)")

    def leaveEvent(self, event: QEvent) -> None:
        """
        鼠标离开事件处理，恢复自动隐藏定时器。

        以短延迟重新启动定时器，允许平滑的鼠标移动。

        Args:
            event: 离开事件
        """
        if hasattr(self, '_timer') and self._duration > 0:
            self._timer.start(ToastConfig.HOVER_DELAY)
            logger.debug(f"Auto-hide resumed (mouse left, delay: {ToastConfig.HOVER_DELAY}ms)")

    def set_message(self, message: str) -> None:
        """
        更新 Toast 消息。

        Args:
            message: 新的消息文本

        使用示例:
            toast.set_message("更新的消息")
        """
        self._message = message
        self._message_label.setText(message)
        self.adjustSize()
        logger.debug(f"Message updated: {message}")

    def get_message(self) -> str:
        """
        获取当前 Toast 消息。

        Returns:
            当前消息文本

        使用示例:
            message = toast.get_message()
        """
        return self._message

    def get_type(self) -> ToastType:
        """
        获取 Toast 类型。

        Returns:
            ToastType 枚举值

        使用示例:
            toast_type = toast.get_type()
        """
        return self._toast_type

    def is_visible(self) -> bool:
        """
        检查 Toast 是否可见。

        Returns:
            如果可见返回 True，否则返回 False

        使用示例:
            if toast.is_visible():
                print("Toast 正在显示")
        """
        return super().isVisible()

    def cleanup(self) -> None:
        """
        清理资源并取消主题管理器订阅。

        此方法应在 Toast 销毁之前调用，以防止内存泄漏。

        使用示例:
            toast.cleanup()
            toast.deleteLater()
        """
        if hasattr(self, '_timer'):
            self._timer.stop()

        self._theme_mgr.unsubscribe(self)
        logger.debug("Toast unsubscribed from theme manager")

        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("Stylesheet cache cleared")
        
        self._cleanup_icon_mixin()

    def deleteLater(self) -> None:
        """
        安排控件删除，自动执行清理。

        重写 Qt 的 deleteLater 以确保正确清理。

        使用示例:
            toast.deleteLater()  # 自动调用 cleanup()
        """
        self.cleanup()
        super().deleteLater()
        logger.debug("Toast scheduled for deletion")
