"""
动画系统核心模块

提供类似微软 Windows 动画系统的功能：
- 全局动画开关
- 动画预设配置
- 动画效果类型
- 组件动画混入

使用方式：
    from core.animation import AnimationManager, AnimatableMixin, AnimationPreset

    # 获取动画管理器实例
    anim_mgr = AnimationManager.instance()

    # 全局开启/关闭动画
    anim_mgr.set_enabled(True)
    anim_mgr.set_enabled(False)

    # 检查动画是否启用
    if anim_mgr.is_enabled():
        ...

    # 组件使用动画混入
    class MyWidget(QWidget, AnimatableMixin):
        def __init__(self):
            super().__init__()
            self.setup_animation(AnimationPreset.FLYOUT)

        def showEvent(self, event):
            super().showEvent(event)
            self.animate_show()

        def hideEvent(self, event):
            self.animate_hide()
            super().hideEvent(event)
"""

from enum import Enum, auto
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field

from PyQt6.QtCore import (
    QObject, QPropertyAnimation, QEasingCurve, QPoint, QSize,
    QPointF, QRectF, pyqtSignal, QTimer, Qt
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


class AnimationType(Enum):
    """动画类型枚举。"""
    FADE = auto()
    SCALE = auto()
    SLIDE = auto()
    FADE_SCALE = auto()
    FADE_SLIDE = auto()
    SCALE_SLIDE = auto()
    FADE_SCALE_SLIDE = auto()


class EasingType(Enum):
    """缓动曲线类型枚举，对应 WinUI 3 动画曲线。"""
    LINEAR = QEasingCurve.Type.Linear
    IN_QUAD = QEasingCurve.Type.InQuad
    OUT_QUAD = QEasingCurve.Type.OutQuad
    IN_OUT_QUAD = QEasingCurve.Type.InOutQuad
    IN_CUBIC = QEasingCurve.Type.InCubic
    OUT_CUBIC = QEasingCurve.Type.OutCubic
    IN_OUT_CUBIC = QEasingCurve.Type.InOutCubic
    IN_QUART = QEasingCurve.Type.InQuart
    OUT_QUART = QEasingCurve.Type.OutQuart
    IN_OUT_QUART = QEasingCurve.Type.InOutQuart
    IN_QUINT = QEasingCurve.Type.InQuint
    OUT_QUINT = QEasingCurve.Type.OutQuint
    IN_OUT_QUINT = QEasingCurve.Type.InOutQuint
    IN_SINE = QEasingCurve.Type.InSine
    OUT_SINE = QEasingCurve.Type.OutSine
    IN_OUT_SINE = QEasingCurve.Type.InOutSine
    IN_EXPO = QEasingCurve.Type.InExpo
    OUT_EXPO = QEasingCurve.Type.OutExpo
    IN_OUT_EXPO = QEasingCurve.Type.InOutExpo
    IN_CIRC = QEasingCurve.Type.InCirc
    OUT_CIRC = QEasingCurve.Type.OutCirc
    IN_OUT_CIRC = QEasingCurve.Type.InOutCirc
    IN_ELASTIC = QEasingCurve.Type.InElastic
    OUT_ELASTIC = QEasingCurve.Type.OutElastic
    IN_OUT_ELASTIC = QEasingCurve.Type.InOutElastic
    IN_BACK = QEasingCurve.Type.InBack
    OUT_BACK = QEasingCurve.Type.OutBack
    IN_OUT_BACK = QEasingCurve.Type.InOutBack
    IN_BOUNCE = QEasingCurve.Type.InBounce
    OUT_BOUNCE = QEasingCurve.Type.OutBounce
    IN_OUT_BOUNCE = QEasingCurve.Type.InOutBounce


class SlideDirection(Enum):
    """滑动方向枚举。"""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()


@dataclass
class AnimationConfig:
    """
    动画配置数据类。

    Attributes:
        duration: 动画持续时间（毫秒）
        easing: 缓动曲线类型
        delay: 动画延迟（毫秒）
        opacity_start: 透明度起始值
        opacity_end: 透明度结束值
        scale_start: 缩放起始值
        scale_end: 缩放结束值
        slide_direction: 滑动方向
        slide_distance: 滑动距离（像素）
    """
    duration: int = 150
    easing: EasingType = EasingType.OUT_CUBIC
    delay: int = 0
    opacity_start: float = 0.0
    opacity_end: float = 1.0
    scale_start: float = 1.0
    scale_end: float = 1.0
    slide_direction: SlideDirection = SlideDirection.UP
    slide_distance: int = 0

    def copy(self, **kwargs) -> 'AnimationConfig':
        """创建副本，可覆盖部分属性。"""
        return AnimationConfig(
            duration=kwargs.get('duration', self.duration),
            easing=kwargs.get('easing', self.easing),
            delay=kwargs.get('delay', self.delay),
            opacity_start=kwargs.get('opacity_start', self.opacity_start),
            opacity_end=kwargs.get('opacity_end', self.opacity_end),
            scale_start=kwargs.get('scale_start', self.scale_start),
            scale_end=kwargs.get('scale_end', self.scale_end),
            slide_direction=kwargs.get('slide_direction', self.slide_direction),
            slide_distance=kwargs.get('slide_distance', self.slide_distance),
        )


class AnimationPreset:
    """
    动画预设类，提供 WinUI 3 风格的动画预设。

    预设包括：
    - FLYOUT: 弹出菜单/面板动画
    - POPUP: 弹窗动画
    - DIALOG: 对话框动画
    - BUTTON: 按钮动画
    - TOOLTIP: 工具提示动画
    - NOTIFICATION: 通知动画
    - SLIDE_IN: 滑入动画
    - FADE_ONLY: 仅淡入淡出
    """

    FLYOUT = AnimationConfig(
        duration=150,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        scale_start=0.95,
        scale_end=1.0,
    )

    FLYOUT_HIDE = AnimationConfig(
        duration=100,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
        scale_start=1.0,
        scale_end=0.98,
    )

    POPUP = AnimationConfig(
        duration=200,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        scale_start=0.9,
        scale_end=1.0,
    )

    POPUP_HIDE = AnimationConfig(
        duration=150,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
        scale_start=1.0,
        scale_end=0.95,
    )

    DIALOG = AnimationConfig(
        duration=250,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        scale_start=0.95,
        scale_end=1.0,
    )

    DIALOG_HIDE = AnimationConfig(
        duration=150,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
        scale_start=1.0,
        scale_end=0.98,
    )

    BUTTON = AnimationConfig(
        duration=100,
        easing=EasingType.OUT_CUBIC,
        opacity_start=1.0,
        opacity_end=1.0,
        scale_start=1.0,
        scale_end=0.97,
    )

    BUTTON_RELEASE = AnimationConfig(
        duration=100,
        easing=EasingType.OUT_CUBIC,
        opacity_start=1.0,
        opacity_end=1.0,
        scale_start=0.97,
        scale_end=1.0,
    )

    TOOLTIP = AnimationConfig(
        duration=100,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        scale_start=0.95,
        scale_end=1.0,
    )

    TOOLTIP_HIDE = AnimationConfig(
        duration=50,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
    )

    NOTIFICATION = AnimationConfig(
        duration=200,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        slide_direction=SlideDirection.RIGHT,
        slide_distance=20,
    )

    NOTIFICATION_HIDE = AnimationConfig(
        duration=150,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
        slide_direction=SlideDirection.RIGHT,
        slide_distance=20,
    )

    SLIDE_UP = AnimationConfig(
        duration=200,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        slide_direction=SlideDirection.UP,
        slide_distance=30,
    )

    SLIDE_DOWN = AnimationConfig(
        duration=200,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
        slide_direction=SlideDirection.DOWN,
        slide_distance=30,
    )

    FADE_ONLY = AnimationConfig(
        duration=150,
        easing=EasingType.OUT_CUBIC,
        opacity_start=0.0,
        opacity_end=1.0,
    )

    FADE_ONLY_HIDE = AnimationConfig(
        duration=100,
        easing=EasingType.IN_CUBIC,
        opacity_start=1.0,
        opacity_end=0.0,
    )


class AnimationManager(QObject):
    """
    全局动画管理器（单例模式）。

    功能：
    - 管理全局动画开关
    - 管理动画配置
    - 提供动画预设
    - 监听系统动画设置

    使用方式：
        manager = AnimationManager.instance()
        manager.set_enabled(True)
        if manager.is_enabled():
            ...
    """

    _instance: Optional['AnimationManager'] = None

    animation_enabled_changed = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._enabled: bool = True
        self._scale_factor: float = 1.0
        self._configs: Dict[str, AnimationConfig] = {}
        self._load_system_settings()

    @classmethod
    def instance(cls) -> 'AnimationManager':
        """获取单例实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_system_settings(self) -> None:
        """加载系统动画设置（Windows）。"""
        try:
            import platform
            if platform.system() == 'Windows':
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Control Panel\Desktop",
                    0,
                    winreg.KEY_READ
                )
                value, _ = winreg.QueryValueEx(key, "UserPreferencesMask")
                winreg.CloseKey(key)
                if value and len(value) > 8:
                    self._enabled = bool(value[8] & 0x80)
        except Exception:
            pass

    def is_enabled(self) -> bool:
        """检查动画是否启用。"""
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """
        设置全局动画开关。

        Args:
            enabled: 是否启用动画
        """
        if self._enabled != enabled:
            self._enabled = enabled
            self.animation_enabled_changed.emit(enabled)

    def get_scale_factor(self) -> float:
        """获取动画速度缩放因子。"""
        return self._scale_factor

    def set_scale_factor(self, factor: float) -> None:
        """
        设置动画速度缩放因子。

        Args:
            factor: 缩放因子，1.0 为正常速度，2.0 为两倍速度
        """
        self._scale_factor = max(0.1, min(5.0, factor))

    def get_config(self, name: str) -> Optional[AnimationConfig]:
        """
        获取动画配置。

        Args:
            name: 配置名称

        Returns:
            动画配置，如果不存在返回 None
        """
        return self._configs.get(name)

    def set_config(self, name: str, config: AnimationConfig) -> None:
        """
        设置动画配置。

        Args:
            name: 配置名称
            config: 动画配置
        """
        self._configs[name] = config

    def get_scaled_duration(self, duration: int) -> int:
        """
        获取缩放后的动画时长。

        Args:
            duration: 原始时长（毫秒）

        Returns:
            缩放后的时长（毫秒）
        """
        if not self._enabled:
            return 0
        return int(duration / self._scale_factor)

    def should_animate(self) -> bool:
        """检查是否应该执行动画。"""
        return self._enabled


class AnimationController(QObject):
    """
    动画控制器，管理单个组件的动画。

    功能：
    - 管理动画效果
    - 处理动画生命周期
    - 支持动画队列
    """

    animation_finished = pyqtSignal()

    def __init__(self, widget: QWidget, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._widget = widget
        self._animations: List[QPropertyAnimation] = []
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None
        self._original_pos: Optional[QPoint] = None
        self._is_animating: bool = False
        self._animation_count: int = 0

        self._manager = AnimationManager.instance()
        self._manager.animation_enabled_changed.connect(self._on_enabled_changed)

    def _on_enabled_changed(self, enabled: bool) -> None:
        """动画开关变化回调。"""
        if not enabled and self._is_animating:
            self._stop_all_animations()

    def _stop_all_animations(self) -> None:
        """停止所有动画。"""
        for anim in self._animations:
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        self._animations.clear()
        self._is_animating = False
        self._animation_count = 0

    def _on_animation_finished(self) -> None:
        """动画完成回调。"""
        self._animation_count -= 1
        if self._animation_count <= 0:
            self._is_animating = False
            self.animation_finished.emit()

    def _setup_opacity_effect(self) -> None:
        """设置透明度效果。"""
        if self._opacity_effect is None:
            self._opacity_effect = QGraphicsOpacityEffect(self._widget)
            self._opacity_effect.setOpacity(1.0)
            self._widget.setGraphicsEffect(self._opacity_effect)

    def animate(self, config: AnimationConfig) -> None:
        """
        执行动画。

        Args:
            config: 动画配置
        """
        if not self._manager.should_animate():
            return

        self._stop_all_animations()
        self._is_animating = True

        duration = self._manager.get_scaled_duration(config.duration)
        easing = QEasingCurve(config.easing.value)

        has_opacity = config.opacity_start != config.opacity_end
        has_slide = config.slide_distance > 0

        if has_opacity:
            self._setup_opacity_effect()
            anim = QPropertyAnimation(self._opacity_effect, b"opacity")
            anim.setDuration(duration)
            anim.setStartValue(config.opacity_start)
            anim.setEndValue(config.opacity_end)
            anim.setEasingCurve(easing)
            anim.finished.connect(self._on_animation_finished)
            anim.start()
            self._animations.append(anim)
            self._animation_count += 1

        if has_slide:
            self._original_pos = self._widget.pos()
            offset_x, offset_y = 0, 0

            if config.slide_direction in [SlideDirection.UP, SlideDirection.UP_LEFT, SlideDirection.UP_RIGHT]:
                offset_y = config.slide_distance
            elif config.slide_direction in [SlideDirection.DOWN, SlideDirection.DOWN_LEFT, SlideDirection.DOWN_RIGHT]:
                offset_y = -config.slide_distance

            if config.slide_direction in [SlideDirection.LEFT, SlideDirection.UP_LEFT, SlideDirection.DOWN_LEFT]:
                offset_x = config.slide_distance
            elif config.slide_direction in [SlideDirection.RIGHT, SlideDirection.UP_RIGHT, SlideDirection.DOWN_RIGHT]:
                offset_x = -config.slide_distance

            start_pos = self._original_pos + QPoint(offset_x, offset_y)
            end_pos = self._original_pos

            anim = QPropertyAnimation(self._widget, b"pos")
            anim.setDuration(duration)
            anim.setStartValue(start_pos)
            anim.setEndValue(end_pos)
            anim.setEasingCurve(easing)
            anim.finished.connect(self._on_animation_finished)
            anim.start()
            self._animations.append(anim)
            self._animation_count += 1

        if self._animation_count == 0:
            self._is_animating = False

    def animate_show(self, config: Optional[AnimationConfig] = None) -> None:
        """
        执行显示动画。

        Args:
            config: 动画配置，默认使用 FLYOUT 预设
        """
        if config is None:
            config = AnimationPreset.FLYOUT
        self.animate(config)

    def animate_hide(self, config: Optional[AnimationConfig] = None) -> None:
        """
        执行隐藏动画。

        Args:
            config: 动画配置，默认使用 FLYOUT_HIDE 预设
        """
        if config is None:
            config = AnimationPreset.FLYOUT_HIDE
        self.animate(config)

    def is_animating(self) -> bool:
        """检查是否正在动画中。"""
        return self._is_animating

    def stop(self) -> None:
        """停止当前动画。"""
        self._stop_all_animations()

    def cleanup(self) -> None:
        """清理资源。"""
        self._stop_all_animations()
        if self._opacity_effect:
            self._opacity_effect.deleteLater()
            self._opacity_effect = None
        self._manager.animation_enabled_changed.disconnect(self._on_enabled_changed)


class AnimatableMixin:
    """
    动画混入类，为组件添加动画能力。

    使用方式：
        class MyWidget(QWidget, AnimatableMixin):
            def __init__(self):
                super().__init__()
                self.setup_animation(AnimationPreset.FLYOUT)

            def showEvent(self, event):
                super().showEvent(event)
                self.animate_show()

            def hideEvent(self, event):
                self.animate_hide()
                super().hideEvent(event)
    """

    def setup_animation(
        self,
        show_config: Optional[AnimationConfig] = None,
        hide_config: Optional[AnimationConfig] = None
    ) -> None:
        """
        设置动画配置。

        Args:
            show_config: 显示动画配置
            hide_config: 隐藏动画配置
        """
        if not hasattr(self, '_animation_controller'):
            self._animation_controller = AnimationController(self)
            self._show_config = show_config or AnimationPreset.FLYOUT
            self._hide_config = hide_config or AnimationPreset.FLYOUT_HIDE

    def animate_show(self, config: Optional[AnimationConfig] = None) -> None:
        """
        执行显示动画。

        Args:
            config: 动画配置，默认使用初始化时设置的配置
        """
        if hasattr(self, '_animation_controller'):
            self._animation_controller.animate_show(config or self._show_config)

    def animate_hide(self, config: Optional[AnimationConfig] = None) -> None:
        """
        执行隐藏动画。

        Args:
            config: 动画配置，默认使用初始化时设置的配置
        """
        if hasattr(self, '_animation_controller'):
            self._animation_controller.animate_hide(config or self._hide_config)

    def is_animating(self) -> bool:
        """检查是否正在动画中。"""
        if hasattr(self, '_animation_controller'):
            return self._animation_controller.is_animating()
        return False

    def stop_animation(self) -> None:
        """停止当前动画。"""
        if hasattr(self, '_animation_controller'):
            self._animation_controller.stop()

    def cleanup_animation(self) -> None:
        """清理动画资源。"""
        if hasattr(self, '_animation_controller'):
            self._animation_controller.cleanup()
            del self._animation_controller
