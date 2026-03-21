"""
阴影系统核心模块

参考 WinUI 3 ThemeShadow 设计，提供统一的阴影管理：
- 基于深度级别的预设阴影
- 主题感知（深色/浅色模式）
- 简单易用的 API

WinUI 3 深度级别参考：
- 16px: Tooltips
- 32px: Context menus, ComboBox, Flyouts
- 48px: Cards, Elevated elements
- 64px: Navigation panes
- 128px: Dialogs, Modal overlays

使用方式：
    from core.shadow_manager import ShadowManager, ShadowDepth

    # 获取阴影管理器实例
    shadow_mgr = ShadowManager.instance()

    # 应用预设阴影
    shadow = shadow_mgr.create_shadow(ShadowDepth.MENU)
    widget.setGraphicsEffect(shadow)

    # 或使用混入类
    class MyWidget(QWidget, ShadowMixin):
        def __init__(self):
            super().__init__()
            self.set_shadow_depth(ShadowDepth.CARD)
"""

import logging
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, QPointF

logger = logging.getLogger(__name__)


class ShadowDepth(Enum):
    """
    阴影深度枚举，对应 WinUI 3 的 z-depth 概念。

    深度级别越高，阴影越明显，表示元素在 z 轴上越"高"。
    """
    NONE = auto()
    TOOLTIP = auto()
    MENU = auto()
    CARD = auto()
    PANE = auto()
    DIALOG = auto()
    CUSTOM = auto()


@dataclass
class ShadowPreset:
    """
    阴影预设配置。

    Attributes:
        offset: 阴影偏移 (x, y)
        blur_radius: 模糊半径
        color_light: 浅色主题下的阴影颜色
        color_dark: 深色主题下的阴影颜色
        spread: 阴影扩散半径
    """
    offset: Tuple[float, float]
    blur_radius: float
    color_light: Tuple[int, int, int, int]
    color_dark: Tuple[int, int, int, int]
    spread: float = 0.0

    def get_color(self, is_dark: bool) -> QColor:
        """获取当前主题下的阴影颜色。"""
        color = self.color_dark if is_dark else self.color_light
        return QColor(*color)


class ShadowManager(QObject):
    """
    阴影管理器，提供统一的阴影效果创建和管理。

    参考 WinUI 3 ThemeShadow 设计，基于深度级别自动计算阴影参数。

    Features:
        - 预设阴影配置
        - 主题感知阴影颜色
        - 阴影效果缓存
        - 简单易用的 API

    Example:
        shadow_mgr = ShadowManager.instance()
        shadow = shadow_mgr.create_shadow(ShadowDepth.MENU, is_dark=True)
        widget.setGraphicsEffect(shadow)
    """

    _instance: Optional['ShadowManager'] = None

    PRESETS: Dict[ShadowDepth, ShadowPreset] = {
        ShadowDepth.NONE: ShadowPreset(
            offset=(0, 0),
            blur_radius=0,
            color_light=(0, 0, 0, 0),
            color_dark=(0, 0, 0, 0)
        ),
        ShadowDepth.TOOLTIP: ShadowPreset(
            offset=(0, 2),
            blur_radius=8,
            color_light=(0, 0, 0, 25),
            color_dark=(0, 0, 0, 40),
            spread=0
        ),
        ShadowDepth.MENU: ShadowPreset(
            offset=(0, 4),
            blur_radius=16,
            color_light=(0, 0, 0, 30),
            color_dark=(0, 0, 0, 50),
            spread=2
        ),
        ShadowDepth.CARD: ShadowPreset(
            offset=(0, 8),
            blur_radius=24,
            color_light=(0, 0, 0, 35),
            color_dark=(0, 0, 0, 60),
            spread=4
        ),
        ShadowDepth.PANE: ShadowPreset(
            offset=(0, 12),
            blur_radius=32,
            color_light=(0, 0, 0, 40),
            color_dark=(0, 0, 0, 70),
            spread=6
        ),
        ShadowDepth.DIALOG: ShadowPreset(
            offset=(0, 16),
            blur_radius=48,
            color_light=(0, 0, 0, 50),
            color_dark=(0, 0, 0, 80),
            spread=8
        ),
    }

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._effects_cache: Dict[int, QGraphicsDropShadowEffect] = {}

    @classmethod
    def instance(cls) -> 'ShadowManager':
        """获取阴影管理器单例实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_shadow(
        self,
        depth: ShadowDepth,
        is_dark: bool = True,
        custom_preset: Optional[ShadowPreset] = None
    ) -> QGraphicsDropShadowEffect:
        """
        创建阴影效果。

        Args:
            depth: 阴影深度级别
            is_dark: 是否为深色主题
            custom_preset: 自定义预设（仅当 depth 为 CUSTOM 时使用）

        Returns:
            QGraphicsDropShadowEffect 实例
        """
        if depth == ShadowDepth.NONE:
            return None

        if depth == ShadowDepth.CUSTOM and custom_preset:
            preset = custom_preset
        else:
            preset = self.PRESETS.get(depth, self.PRESETS[ShadowDepth.MENU])

        effect = QGraphicsDropShadowEffect()
        effect.setOffset(QPointF(*preset.offset))
        effect.setBlurRadius(preset.blur_radius)
        effect.setColor(preset.get_color(is_dark))

        logger.debug(f"创建阴影: depth={depth.name}, blur={preset.blur_radius}, is_dark={is_dark}")
        return effect

    def apply_shadow(
        self,
        widget: QWidget,
        depth: ShadowDepth,
        is_dark: bool = True,
        custom_preset: Optional[ShadowPreset] = None
    ) -> Optional[QGraphicsDropShadowEffect]:
        """
        将阴影效果应用到组件。

        Args:
            widget: 目标组件
            depth: 阴影深度级别
            is_dark: 是否为深色主题
            custom_preset: 自定义预设

        Returns:
            应用的阴影效果，如果 depth 为 NONE 则返回 None
        """
        if depth == ShadowDepth.NONE:
            widget.setGraphicsEffect(None)
            return None

        effect = self.create_shadow(depth, is_dark, custom_preset)
        widget.setGraphicsEffect(effect)
        return effect

    def update_shadow_color(
        self,
        effect: QGraphicsDropShadowEffect,
        depth: ShadowDepth,
        is_dark: bool = True
    ) -> None:
        """
        更新阴影颜色（用于主题切换）。

        Args:
            effect: 阴影效果实例
            depth: 阴影深度级别
            is_dark: 是否为深色主题
        """
        if effect is None or depth == ShadowDepth.NONE:
            return

        preset = self.PRESETS.get(depth)
        if preset:
            effect.setColor(preset.get_color(is_dark))

    def get_preset(self, depth: ShadowDepth) -> Optional[ShadowPreset]:
        """获取指定深度的预设配置。"""
        return self.PRESETS.get(depth)

    def register_preset(self, depth: ShadowDepth, preset: ShadowPreset) -> None:
        """
        注册自定义预设。

        Args:
            depth: 深度级别
            preset: 预设配置
        """
        self.PRESETS[depth] = preset
        logger.info(f"注册阴影预设: {depth.name}")


class ShadowMixin:
    """
    阴影混入类，为组件提供阴影支持。

    使用方式:
        class MyWidget(QWidget, ShadowMixin):
            def __init__(self):
                super().__init__()
                self._init_shadow()
                self.set_shadow_depth(ShadowDepth.CARD)

            def _on_theme_changed(self, theme):
                self._update_shadow_color(theme.is_dark)
    """

    _shadow_depth: ShadowDepth = ShadowDepth.NONE
    _shadow_effect: Optional[QGraphicsDropShadowEffect] = None
    _shadow_enabled: bool = True

    def _init_shadow(self, depth: ShadowDepth = ShadowDepth.NONE) -> None:
        """
        初始化阴影系统。

        Args:
            depth: 初始阴影深度
        """
        self._shadow_depth = depth
        self._shadow_effect = None
        self._shadow_enabled = True

    def set_shadow_depth(
        self,
        depth: ShadowDepth,
        is_dark: bool = True,
        custom_preset: Optional[ShadowPreset] = None
    ) -> None:
        """
        设置阴影深度。

        Args:
            depth: 阴影深度级别
            is_dark: 是否为深色主题
            custom_preset: 自定义预设
        """
        self._shadow_depth = depth

        if not self._shadow_enabled or depth == ShadowDepth.NONE:
            if hasattr(self, 'setGraphicsEffect'):
                self.setGraphicsEffect(None)
            self._shadow_effect = None
            return

        shadow_mgr = ShadowManager.instance()
        self._shadow_effect = shadow_mgr.apply_shadow(
            self, depth, is_dark, custom_preset
        )

    def get_shadow_depth(self) -> ShadowDepth:
        """获取当前阴影深度。"""
        return self._shadow_depth

    def set_shadow_enabled(self, enabled: bool, is_dark: bool = True) -> None:
        """
        启用或禁用阴影。

        Args:
            enabled: 是否启用
            is_dark: 是否为深色主题
        """
        self._shadow_enabled = enabled

        if enabled and self._shadow_depth != ShadowDepth.NONE:
            self.set_shadow_depth(self._shadow_depth, is_dark)
        elif hasattr(self, 'setGraphicsEffect'):
            self.setGraphicsEffect(None)
            self._shadow_effect = None

    def is_shadow_enabled(self) -> bool:
        """检查阴影是否启用。"""
        return self._shadow_enabled

    def _update_shadow_color(self, is_dark: bool) -> None:
        """
        更新阴影颜色（主题切换时调用）。

        Args:
            is_dark: 是否为深色主题
        """
        if self._shadow_effect and self._shadow_depth != ShadowDepth.NONE:
            shadow_mgr = ShadowManager.instance()
            shadow_mgr.update_shadow_color(
                self._shadow_effect, self._shadow_depth, is_dark
            )

    def _clear_shadow(self) -> None:
        """清除阴影效果。"""
        if hasattr(self, 'setGraphicsEffect'):
            self.setGraphicsEffect(None)
        self._shadow_effect = None


def create_custom_shadow(
    offset: Tuple[float, float] = (0, 4),
    blur_radius: float = 16,
    color: Tuple[int, int, int, int] = (0, 0, 0, 50),
    spread: float = 0
) -> ShadowPreset:
    """
    创建自定义阴影预设。

    Args:
        offset: 阴影偏移 (x, y)
        blur_radius: 模糊半径
        color: 阴影颜色 (r, g, b, a)
        spread: 扩散半径

    Returns:
        ShadowPreset 实例
    """
    return ShadowPreset(
        offset=offset,
        blur_radius=blur_radius,
        color_light=color,
        color_dark=color,
        spread=spread
    )
