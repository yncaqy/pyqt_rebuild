"""
Primary Push Button Component

Provides a prominent push button for highlighting important actions.

Features:
- Prominent styling with accent color background
- Theme integration with automatic updates
- Support for normal, hover, pressed, disabled states
- Support for text and icon display
- Customizable border radius and padding
- Support for icon name loading via IconManager
- Local style overrides without modifying shared theme
- Automatic resource cleanup
"""

import logging
from typing import Optional, Union

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase
from themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)


class PrimaryButtonConfig:
    """Configuration constants for primary button behavior and styling."""

    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h']}px"
    DEFAULT_ICON_SIZE = WINUI3_CONTROL_SIZING['button']['icon_size']


class PrimaryPushButton(ThemedButtonBase):
    """
    Prominent push button for highlighting important actions.

    Features:
    - Prominent styling with accent color background
    - Theme integration with automatic updates
    - Support for normal, hover, pressed, disabled states
    - Support for text and icon display
    - Customizable border radius and padding
    - Support for icon name, SVG string, or QIcon
    - Local style overrides without modifying shared theme
    - Automatic resource cleanup

    Example:
        button = PrimaryPushButton("Submit", icon_name="Check_white")
        button.clicked.connect(lambda: print("Submitted!"))
    """

    def __init__(
        self, 
        text: str = "", 
        parent: Optional[object] = None, 
        icon_name: str = "",
        icon: str = ""
    ):
        super().__init__(text, parent, icon_name or icon)
        self._icon_size = QSize(PrimaryButtonConfig.DEFAULT_ICON_SIZE, PrimaryButtonConfig.DEFAULT_ICON_SIZE)

    def _get_checked_text_color_key(self) -> str:
        """
        获取选中状态的文本颜色键。

        Returns:
            主题颜色键
        """
        return 'primary.text.normal'

    def _build_stylesheet(self, theme: Theme) -> str:
        bg_normal = self.get_style_color(theme, 'primary.background.normal', QColor(0, 120, 212))
        bg_hover = self.get_style_color(theme, 'primary.background.hover', QColor(0, 100, 192))
        bg_pressed = self.get_style_color(theme, 'primary.background.pressed', QColor(0, 80, 172))
        bg_disabled = self.get_style_color(theme, 'primary.background.disabled', QColor(100, 100, 100))

        text_color = self.get_style_color(theme, 'primary.text.normal', QColor(255, 255, 255))
        text_disabled = self.get_style_color(theme, 'primary.text.disabled', QColor(180, 180, 180))

        border_radius = self.get_style_value(theme, 'primary.border_radius', PrimaryButtonConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'primary.padding', PrimaryButtonConfig.DEFAULT_PADDING)

        qss = f"""
        PrimaryPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: none;
            border-radius: {border_radius}px;
            padding: {padding};
        }}
        PrimaryPushButton:hover {{
            background-color: {bg_hover.name()};
        }}
        PrimaryPushButton:pressed {{
            background-color: {bg_pressed.name()};
        }}
        PrimaryPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
        }}
        """

        return qss

    def setIcon(self, icon: Union[QIcon, str]) -> None:
        """
        Set the button icon.

        Args:
            icon: QIcon, icon name, or SVG string
        """
        if isinstance(icon, str):
            self.set_icon(icon)
        else:
            super().setIcon(icon)
