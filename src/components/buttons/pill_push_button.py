"""
胶囊按钮组件

提供胶囊形状的可切换按钮，具有以下特性：
- 胶囊形状（两端完全圆角）
- 主题集成，自动更新样式
- 支持正常、悬停、选中、禁用状态
- 可用作标签或过滤器
- 支持文本和图标显示
- 自动资源清理机制
"""

import logging
from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase

logger = logging.getLogger(__name__)


class PillConfig:
    """胶囊按钮行为和样式的配置常量。"""

    DEFAULT_PADDING = '6px 12px'
    DEFAULT_HEIGHT = 28
    DEFAULT_BORDER_RADIUS = DEFAULT_HEIGHT // 2


class PillPushButton(ThemedButtonBase):
    """
    胶囊形状的可切换按钮组件，支持现代样式和自动主题更新。

    特性：
    - 胶囊形状（两端完全圆角）
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、选中、禁用状态
    - 优化的样式缓存机制，避免重复计算
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 支持文本和图标显示
    - 可切换状态，适合用作标签或过滤器
    - 自动资源清理

    信号：
        toggled(bool): 当按钮状态改变时发出，参数为新的选中状态（继承自 QPushButton）

    示例:
        button = PillPushButton("标签")
        button.toggled.connect(lambda checked: print(f"状态: {checked}"))
        button.setChecked(True)
    """

    def __init__(self, text: str = "", parent=None, icon_name: str = ""):
        """
        初始化胶囊按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent, icon_name, checkable=True)
        self.setFixedHeight(PillConfig.DEFAULT_HEIGHT)
        self._icon_size = QSize(14, 14)

    def _get_checked_text_color_key(self) -> str:
        """
        获取选中状态的文本颜色键。

        Returns:
            主题颜色键
        """
        return 'pill.text.checked'

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        bg_normal = self.get_style_color(theme, 'pill.background.normal', 
                                         theme.get_color('button.background.normal', QColor(58, 58, 58)))
        bg_hover = self.get_style_color(theme, 'pill.background.hover', 
                                        theme.get_color('button.background.hover', QColor(74, 74, 74)))
        bg_disabled = self.get_style_color(theme, 'pill.background.disabled', 
                                           theme.get_color('button.background.disabled', QColor(42, 42, 42)))
        bg_checked = self.get_style_color(theme, 'pill.background.checked', 
                                          theme.get_color('button.background.checked', QColor(93, 173, 226)))
        bg_checked_hover = self.get_style_color(theme, 'pill.background.checked_hover', 
                                                theme.get_color('button.background.checked_hover', QColor(52, 152, 219)))

        text_normal = self.get_style_color(theme, 'pill.text.normal', 
                                           theme.get_color('button.text.normal', QColor(224, 224, 224)))
        text_disabled = self.get_style_color(theme, 'pill.text.disabled', 
                                             theme.get_color('button.text.disabled', QColor(102, 102, 102)))
        text_checked = self.get_style_color(theme, 'pill.text.checked', 
                                            theme.get_color('button.text.checked', QColor(255, 255, 255)))

        border_normal = self.get_style_color(theme, 'pill.border.normal', 
                                             theme.get_color('button.border.normal', QColor('transparent')))
        border_hover = self.get_style_color(theme, 'pill.border.hover', 
                                            theme.get_color('button.border.hover', QColor('transparent')))
        border_disabled = self.get_style_color(theme, 'pill.border.disabled', 
                                               theme.get_color('button.border.disabled', QColor('transparent')))
        border_checked = self.get_style_color(theme, 'pill.border.checked', 
                                              theme.get_color('button.border.checked', QColor('transparent')))

        padding = self.get_style_value(theme, 'pill.padding', PillConfig.DEFAULT_PADDING)
        border_radius = PillConfig.DEFAULT_BORDER_RADIUS

        border_style_normal = self._build_border_style(border_normal)
        border_style_hover = self._build_border_style(border_hover)
        border_style_disabled = self._build_border_style(border_disabled)
        border_style_checked = self._build_border_style(border_checked)

        qss = f"""
        PillPushButton {{
            background-color: {bg_normal.name()};
            color: {text_normal.name()};
            border: {border_style_normal};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: center;
        }}
        PillPushButton:hover {{
            background-color: {bg_hover.name()};
            border: {border_style_hover};
        }}
        PillPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        PillPushButton:checked {{
            background-color: {bg_checked.name()};
            color: {text_checked.name()};
            border: {border_style_checked};
        }}
        PillPushButton:checked:hover {{
            background-color: {bg_checked_hover.name()};
            border: {border_style_checked};
        }}
        PillPushButton:checked:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss
