"""
开关按钮组件

提供现代化的开关按钮，具有以下特性：
- 主题集成，自动更新样式
- 平滑的开关动画效果
- 支持正常、悬停、选中、禁用状态
- 优化的样式缓存机制
- 本地样式覆盖，不影响共享主题
- 开关状态改变时发送 checkedChanged 信号
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, QRectF, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QBrush, QPaintEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class SwitchButtonConfig:
    """
    开关按钮行为和样式的配置常量。

    Attributes:
        DEFAULT_HORIZONTAL_POLICY: 默认水平尺寸策略
        DEFAULT_VERTICAL_POLICY: 默认垂直尺寸策略
        DEFAULT_WIDTH: 默认开关宽度
        DEFAULT_HEIGHT: 默认开关高度
        DEFAULT_HANDLE_SIZE: 默认手柄尺寸
        DEFAULT_MARGIN: 默认边距
        ANIMATION_DURATION: 动画持续时间（毫秒）
    """

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed

    DEFAULT_WIDTH = 44
    DEFAULT_HEIGHT = 22
    DEFAULT_HANDLE_SIZE = 18
    DEFAULT_MARGIN = 2
    ANIMATION_DURATION = 150


class SwitchButton(QWidget, StyleOverrideMixin):
    """
    开关按钮组件，表示两种相互对立的状态间的切换。

    特性：
    - 主题集成，自动响应主题切换
    - 平滑的开关动画效果
    - 支持正常、选中、禁用状态
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题

    信号:
        checkedChanged: 开关状态改变时发出，参数为新的选中状态

    示例:
        switch = SwitchButton()
        switch.setChecked(True)
        switch.checkedChanged.connect(lambda checked: print(f"开关状态: {checked}"))
    """

    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化开关按钮。

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._init_style_override()

        self.setSizePolicy(
            SwitchButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            SwitchButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        self.setFixedSize(
            SwitchButtonConfig.DEFAULT_WIDTH,
            SwitchButtonConfig.DEFAULT_HEIGHT
        )

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._checked: bool = False
        self._handle_position: float = 0.0

        self._animation = QPropertyAnimation(self, b"handlePosition", self)
        self._animation.setDuration(SwitchButtonConfig.ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._track_color_off = QColor(176, 176, 176)
        self._track_color_on = QColor(52, 152, 219)
        self._handle_color = QColor(255, 255, 255)

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        logger.debug("SwitchButton 初始化完成")

    def isChecked(self) -> bool:
        """
        返回开关是否处于选中状态。

        Returns:
            是否选中
        """
        return self._checked

    def setChecked(self, checked: bool, animate: bool = True) -> None:
        """
        设置开关的选中状态。

        Args:
            checked: 是否选中
            animate: 是否使用动画
        """
        if self._checked == checked:
            return

        self._checked = checked

        if animate:
            self._start_animation(checked)
        else:
            self._handle_position = 1.0 if checked else 0.0
            self.update()

        self.checkedChanged.emit(checked)
        logger.debug(f"SwitchButton 状态改变: {checked}")

    def toggle(self) -> None:
        """切换开关状态。"""
        self.setChecked(not self._checked)

    def _start_animation(self, checked: bool) -> None:
        """
        启动开关动画。

        Args:
            checked: 目标状态
        """
        self._animation.stop()
        self._animation.setStartValue(self._handle_position)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    @pyqtProperty(float)
    def handlePosition(self) -> float:
        """
        获取手柄位置属性（用于动画）。

        Returns:
            手柄位置（0.0 到 1.0）
        """
        return self._handle_position

    @handlePosition.setter
    def handlePosition(self, position: float) -> None:
        """
        设置手柄位置属性（用于动画）。

        Args:
            position: 手柄位置（0.0 到 1.0）
        """
        self._handle_position = position
        self.update()

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        Args:
            theme: 新的主题对象
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 SwitchButton 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到开关按钮。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        if not theme:
            return

        self._current_theme = theme

        track_off = self.get_style_color(theme, 'switch.track.off', QColor(176, 176, 176))
        track_on = self.get_style_color(theme, 'switch.track.on', QColor(52, 152, 219))
        handle_color = self.get_style_color(theme, 'switch.handle', QColor(255, 255, 255))
        handle_disabled = self.get_style_color(theme, 'switch.handle.disabled', QColor(200, 200, 200))
        track_disabled = self.get_style_color(theme, 'switch.track.disabled', QColor(200, 200, 200))

        self._track_color_off = track_off
        self._track_color_on = track_on
        self._handle_color = handle_color
        self._handle_disabled = handle_disabled
        self._track_disabled = track_disabled

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        重写绘制事件，绘制开关按钮。

        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        margin = SwitchButtonConfig.DEFAULT_MARGIN
        handle_size = SwitchButtonConfig.DEFAULT_HANDLE_SIZE

        track_rect = QRectF(0, 0, width, height)
        track_radius = height / 2

        is_enabled = self.isEnabled()

        if is_enabled:
            if self._checked:
                track_color = self._track_color_on
            else:
                track_color = self._track_color_off
            handle_color = self._handle_color
        else:
            track_color = self._track_disabled
            handle_color = self._handle_disabled

        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, track_radius, track_radius)

        handle_margin = (height - handle_size) / 2
        handle_x = margin + self._handle_position * (width - handle_size - margin * 2)
        handle_rect = QRectF(
            handle_x,
            handle_margin,
            handle_size,
            handle_size
        )

        painter.setBrush(QBrush(handle_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(handle_rect)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        处理鼠标按下事件。

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.toggle()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:
        """
        处理键盘事件。

        空格键或回车键切换开关状态。

        Args:
            event: 键盘事件
        """
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.isEnabled():
                self.toggle()
            return
        super().keyPressEvent(event)

    def sizeHint(self) -> QSize:
        """
        返回按钮的建议尺寸。

        Returns:
            建议尺寸
        """
        return QSize(
            SwitchButtonConfig.DEFAULT_WIDTH,
            SwitchButtonConfig.DEFAULT_HEIGHT
        )

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，释放资源。
        """
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("SwitchButton 已取消主题订阅")

        if hasattr(self, '_animation') and self._animation:
            self._animation.stop()

        self.clear_overrides()

    def __del__(self) -> None:
        """析构函数，自动清理资源。"""
        try:
            self.cleanup()
        except Exception:
            pass
