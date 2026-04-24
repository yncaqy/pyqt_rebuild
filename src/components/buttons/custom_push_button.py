"""
自定义按钮组件

提供现代化的主题按钮，具有以下特性：
- 主题集成，自动更新样式
- 支持正常、悬停、按下、禁用四种状态
- 可自定义圆角和内边距
- 优化的样式缓存机制，提升性能
- 支持本地样式覆盖，无需修改共享主题
- 统一的图标管理接口（IconMixin）
- 自动资源清理机制
"""

import logging
from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget

from src.core.theme_manager import Theme
from src.core.font_manager import FontManager
from src.core.shadow_manager import ShadowDepth
from src.components.buttons.themed_button_base import ThemedButtonBase
from src.themes.colors import WINUI3_CONTROL_SIZING, FALLBACK_COLORS, FALLBACK_COLORS_LIGHT

logger = logging.getLogger(__name__)

TRANSPARENT_COLOR = QColor(0, 0, 0, 0)


class ButtonConfig:
    """
    按钮行为和样式的配置常量。

    Attributes:
        DEFAULT_BORDER_RADIUS: 默认边框圆角（像素）
        DEFAULT_PADDING: 默认内边距
        DEFAULT_MIN_HEIGHT: 默认最小高度
        DEFAULT_ICON_SIZE: 默认图标大小
    """

    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['button']['border_radius']
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h']}px"
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['button']['min_height']
    DEFAULT_ICON_SIZE = WINUI3_CONTROL_SIZING['button']['icon_size']
    DEFAULT_PADDING_V = WINUI3_CONTROL_SIZING['button']['padding_v']
    DEFAULT_PADDING_H = WINUI3_CONTROL_SIZING['button']['padding_h']

    @staticmethod
    def get_fallback_bg_normal(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['background']['normal'] if is_dark else FALLBACK_COLORS_LIGHT['background']['normal'])

    @staticmethod
    def get_fallback_bg_hover(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['background']['hover'] if is_dark else FALLBACK_COLORS_LIGHT['background']['hover'])

    @staticmethod
    def get_fallback_bg_pressed(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['background']['pressed'] if is_dark else FALLBACK_COLORS_LIGHT['background']['pressed'])

    @staticmethod
    def get_fallback_bg_disabled(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['background']['disabled'] if is_dark else FALLBACK_COLORS_LIGHT['background']['disabled'])

    @staticmethod
    def get_fallback_text_normal(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['text']['primary'] if is_dark else FALLBACK_COLORS_LIGHT['text']['primary'])

    @staticmethod
    def get_fallback_text_disabled(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['text']['disabled'] if is_dark else FALLBACK_COLORS_LIGHT['text']['disabled'])


class CustomPushButton(ThemedButtonBase):
    """
    主题化按钮组件，支持现代样式和自动主题更新。

    特性：
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、按下、禁用四种状态
    - 可自定义圆角和内边距
    - 优化的样式缓存机制，避免重复计算
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 统一的图标管理接口
    - 自动资源清理

    示例:
        button = CustomPushButton("点击我")
        button.set_theme('dark')
        button.clicked.connect(lambda: print("已点击!"))

        # 设置图标
        button.set_icon("Play")
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, icon_name: str = ""):
        """
        初始化主题化按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent, icon_name)
        self._icon_size = QSize(ButtonConfig.DEFAULT_ICON_SIZE, ButtonConfig.DEFAULT_ICON_SIZE)
        self.setMinimumHeight(ButtonConfig.DEFAULT_MIN_HEIGHT)
        self._setup_font()

        if self._current_theme:
            is_dark = self._current_theme.is_dark
            self.set_shadow_depth(ShadowDepth.TOOLTIP, is_dark)

    def _setup_font(self) -> None:
        """设置按钮字体，遵循 WinUI 3 设计规范。"""
        font = FontManager.get_button_font()
        self.setFont(font)

    def sizeHint(self) -> QSize:
        """返回推荐尺寸，遵循 WinUI 3 设计规范。"""
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text()) if self.text() else 0

        padding_h = WINUI3_CONTROL_SIZING['button']['padding_h']

        icon_width = 0
        if not self.icon().isNull():
            icon_width = self._icon_size.width() + WINUI3_CONTROL_SIZING['button']['icon_text_spacing']

        width = text_width + icon_width + padding_h * 2 + 8
        height = ButtonConfig.DEFAULT_MIN_HEIGHT

        return QSize(max(width, 80), height)

    def _build_stylesheet(self, theme: Theme) -> str:
        is_dark = theme.is_dark if theme else True

        bg_normal = self.get_style_color(theme, 'button.background.normal', ButtonConfig.get_fallback_bg_normal(is_dark))
        bg_hover = self.get_style_color(theme, 'button.background.hover', ButtonConfig.get_fallback_bg_hover(is_dark))
        bg_pressed = self.get_style_color(theme, 'button.background.pressed', ButtonConfig.get_fallback_bg_pressed(is_dark))
        bg_disabled = self.get_style_color(theme, 'button.background.disabled', ButtonConfig.get_fallback_bg_disabled(is_dark))

        text_color = self.get_style_color(theme, 'button.text.normal', ButtonConfig.get_fallback_text_normal(is_dark))
        text_disabled = self.get_style_color(theme, 'button.text.disabled', ButtonConfig.get_fallback_text_disabled(is_dark))

        border_color = self.get_style_color(theme, 'button.border.normal', TRANSPARENT_COLOR)
        border_hover = self.get_style_color(theme, 'button.border.hover', TRANSPARENT_COLOR)
        border_pressed = self.get_style_color(theme, 'button.border.pressed', TRANSPARENT_COLOR)
        border_disabled = self.get_style_color(theme, 'button.border.disabled', TRANSPARENT_COLOR)

        border_radius = self.get_style_value(theme, 'button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS)
        padding_v = self.get_style_value(theme, 'button.padding_v', ButtonConfig.DEFAULT_PADDING_V)
        padding_h = self.get_style_value(theme, 'button.padding_h', ButtonConfig.DEFAULT_PADDING_H)

        border_style_normal = self._build_border_style(border_color)
        border_style_hover = self._build_border_style(border_hover)
        border_style_disabled = self._build_border_style(border_disabled)

        qss = f"""
        CustomPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: {border_style_normal};
            border-radius: {border_radius}px;
            padding-left: {padding_h}px;
            padding-right: {padding_h}px;
            padding-top: {padding_v}px;
            padding-bottom: {padding_v}px;
        }}
        CustomPushButton:hover {{
            background-color: {bg_hover.name()};
            border: {border_style_hover};
        }}
        CustomPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: none;
        }}
        CustomPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss
