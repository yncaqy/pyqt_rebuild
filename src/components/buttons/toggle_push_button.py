"""
切换按钮组件

提供可切换状态的按钮，具有以下特性：
- 主题集成，自动更新样式
- 支持正常、悬停、按下、选中、禁用状态
- 可自定义圆角和内边距
- 优化的样式缓存机制，提升性能
- 支持本地样式覆盖，无需修改共享主题
- 支持文本和图标显示
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


class ToggleConfig:
    """切换按钮行为和样式的配置常量。"""
    
    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['button']['border_radius']
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h']}px"


class TogglePushButton(ThemedButtonBase):
    """
    可切换状态的按钮组件，支持现代样式和自动主题更新。

    特性：
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、按下、选中、禁用状态
    - 可自定义圆角和内边距
    - 优化的样式缓存机制，避免重复计算
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 支持文本和图标显示
    - 可切换状态，类似开关按钮
    - 自动资源清理

    信号：
        toggled(bool): 当按钮状态改变时发出，参数为新的选中状态（继承自 QPushButton）

    示例:
        button = TogglePushButton("点击切换")
        button.toggled.connect(lambda checked: print(f"状态: {checked}"))
        button.setChecked(True)
    """

    def __init__(self, text: str = "", parent=None, icon_name: str = ""):
        """
        初始化切换按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent, icon_name, checkable=True)
        self._icon_size = QSize(16, 16)

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        bg_normal = self.get_style_color(theme, 'button.background.normal', QColor(230, 230, 230))
        bg_hover = self.get_style_color(theme, 'button.background.hover', QColor(200, 200, 200))
        bg_pressed = self.get_style_color(theme, 'button.background.pressed', QColor(180, 180, 180))
        bg_disabled = self.get_style_color(theme, 'button.background.disabled', QColor(240, 240, 240))
        bg_checked = self.get_style_color(theme, 'button.background.checked', QColor(0, 120, 212))
        bg_checked_hover = self.get_style_color(theme, 'button.background.checked_hover', QColor(0, 100, 192))
        bg_checked_pressed = self.get_style_color(theme, 'button.background.checked_pressed', QColor(0, 80, 172))

        text_color = self.get_style_color(theme, 'button.text.normal', QColor(50, 50, 50))
        text_disabled = self.get_style_color(theme, 'button.text.disabled', QColor(150, 150, 150))
        text_checked = self.get_style_color(theme, 'button.text.checked', QColor(255, 255, 255))

        border_color = self.get_style_color(theme, 'button.border.normal', QColor('transparent'))
        border_hover = self.get_style_color(theme, 'button.border.hover', QColor('transparent'))
        border_pressed = self.get_style_color(theme, 'button.border.pressed', QColor('transparent'))
        border_disabled = self.get_style_color(theme, 'button.border.disabled', QColor('transparent'))
        border_checked = self.get_style_color(theme, 'button.border.checked', QColor('transparent'))

        border_radius = self.get_style_value(theme, 'button.border_radius', ToggleConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'button.padding', ToggleConfig.DEFAULT_PADDING)

        border_style_normal = self._build_border_style(border_color)
        border_style_hover = self._build_border_style(border_hover)
        border_style_pressed = self._build_border_style(border_pressed)
        border_style_disabled = self._build_border_style(border_disabled)
        border_style_checked = self._build_border_style(border_checked)

        qss = f"""
        TogglePushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: {border_style_normal};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: center;
        }}
        TogglePushButton:hover {{
            background-color: {bg_hover.name()};
            border: {border_style_hover};
        }}
        TogglePushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: {border_style_pressed};
        }}
        TogglePushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        TogglePushButton:checked {{
            background-color: {bg_checked.name()};
            color: {text_checked.name()};
            border: {border_style_checked};
        }}
        TogglePushButton:checked:hover {{
            background-color: {bg_checked_hover.name()};
            border: {border_style_checked};
        }}
        TogglePushButton:checked:pressed {{
            background-color: {bg_checked_pressed.name()};
            border: {border_style_checked};
        }}
        TogglePushButton:checked:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss
