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
from PyQt6.QtGui import QColor

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase
from themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class ButtonConfig:
    """
    按钮行为和样式的配置常量。
    
    Attributes:
        DEFAULT_BORDER_RADIUS: 默认边框圆角（像素）
        DEFAULT_PADDING: 默认内边距
        DEFAULT_MIN_HEIGHT: 默认最小高度
        DEFAULT_MIN_WIDTH: 默认最小宽度
        DEFAULT_ICON_SIZE: 默认图标大小
    """

    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['button']['border_radius']
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h']}px"
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['button']['min_height']
    DEFAULT_MIN_WIDTH = WINUI3_CONTROL_SIZING['button']['min_width']
    DEFAULT_ICON_SIZE = WINUI3_CONTROL_SIZING['button']['icon_size']


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

    def __init__(self, text: str = "", parent: Optional[object] = None, icon_name: str = ""):
        """
        初始化主题化按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent, icon_name)
        self._icon_size = QSize(ButtonConfig.DEFAULT_ICON_SIZE, ButtonConfig.DEFAULT_ICON_SIZE)

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        根据主题数据生成完整的 QSS 样式表，包含所有状态样式。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        bg_normal = self.get_style_color(theme, 'button.background.normal', QColor(230, 230, 230))
        bg_hover = self.get_style_color(theme, 'button.background.hover', QColor(200, 200, 200))
        bg_pressed = self.get_style_color(theme, 'button.background.pressed', QColor(180, 180, 180))
        bg_disabled = self.get_style_color(theme, 'button.background.disabled', QColor(240, 240, 240))

        text_color = self.get_style_color(theme, 'button.text.normal', QColor(50, 50, 50))
        text_disabled = self.get_style_color(theme, 'button.text.disabled', QColor(150, 150, 150))

        border_color = self.get_style_color(theme, 'button.border.normal', QColor('transparent'))
        border_hover = self.get_style_color(theme, 'button.border.hover', QColor('transparent'))
        border_pressed = self.get_style_color(theme, 'button.border.pressed', QColor('transparent'))
        border_disabled = self.get_style_color(theme, 'button.border.disabled', QColor('transparent'))

        border_radius = self.get_style_value(theme, 'button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'button.padding', ButtonConfig.DEFAULT_PADDING)

        border_style_normal = self._build_border_style(border_color)
        border_style_hover = self._build_border_style(border_hover)
        border_style_pressed = self._build_border_style(border_pressed)
        border_style_disabled = self._build_border_style(border_disabled)

        qss = f"""
        CustomPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: {border_style_normal};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: center;
            min-height: {ButtonConfig.DEFAULT_MIN_HEIGHT}px;
        }}
        CustomPushButton:hover {{
            background-color: {bg_hover.name()};
            border: {border_style_hover};
        }}
        CustomPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: {border_style_pressed};
        }}
        CustomPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss
