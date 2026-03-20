"""
下拉按钮组件

提供带下拉菜单的按钮，具有以下特性：
- 点击弹出 RoundMenu 下拉菜单
- 主题集成，自动更新样式
- 支持正常、悬停、按下、禁用状态
- 支持文本和图标显示
- 下拉箭头图标指示器
- 自动资源清理机制
"""

import logging
from typing import Optional

from PyQt6.QtCore import QSize, QPoint
from PyQt6.QtGui import QColor, QIcon, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase
from components.menus.round_menu import RoundMenu, MenuConfig
from themes.colors import WINUI3_CONTROL_SIZING

logger = logging.getLogger(__name__)

TRANSPARENT_COLOR = QColor(0, 0, 0, 0)


class DropDownConfig:
    """下拉按钮行为和样式的配置常量。"""

    DEFAULT_PADDING = f"{WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h'] + WINUI3_CONTROL_SIZING['button']['icon_size'] + 8}px {WINUI3_CONTROL_SIZING['button']['padding_v']}px {WINUI3_CONTROL_SIZING['button']['padding_h']}px"
    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['button']['border_radius']
    DEFAULT_ARROW_SIZE = WINUI3_CONTROL_SIZING['button']['icon_size']
    DEFAULT_ARROW_MARGIN = WINUI3_CONTROL_SIZING['spacing']['small']
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['button']['min_height']
    MENU_OFFSET_Y = 4
    
    FALLBACK_BG_NORMAL = QColor(45, 45, 45)
    FALLBACK_BG_HOVER = QColor(61, 61, 61)
    FALLBACK_BG_PRESSED = QColor(29, 29, 29)
    FALLBACK_BG_DISABLED = QColor(28, 28, 28)
    FALLBACK_TEXT_NORMAL = QColor(255, 255, 255)
    FALLBACK_TEXT_DISABLED = QColor(255, 255, 255, 92)


class DropDownPushButton(ThemedButtonBase):
    """
    带下拉菜单的按钮组件，点击弹出 RoundMenu。

    特性：
    - 点击弹出 RoundMenu 及其子类
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、按下、禁用状态
    - 优化的样式缓存机制
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 支持文本和图标显示
    - 下拉箭头图标指示器
    - 自动资源清理

    示例:
        button = DropDownPushButton("文件")
        menu = RoundMenu()
        menu.addAction("新建", lambda: print("新建"))
        menu.addAction("打开", lambda: print("打开"))
        menu.addSeparator()
        menu.addAction("退出", lambda: print("退出"))
        button.setMenu(menu)
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, icon_name: str = ""):
        """
        初始化下拉按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent, icon_name)
        
        self._menu: Optional[RoundMenu] = None
        self._arrow_icon: Optional[QIcon] = None
        self._icon_size = QSize(WINUI3_CONTROL_SIZING['button']['icon_size'], WINUI3_CONTROL_SIZING['button']['icon_size'])
        
        self.clicked.connect(self._on_clicked)
        
        if self._current_theme:
            self._update_arrow_icon()

        logger.debug(f"DropDownPushButton 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def sizeHint(self) -> QSize:
        base_size = super().sizeHint()
        
        arrow_space = DropDownConfig.DEFAULT_ARROW_SIZE + DropDownConfig.DEFAULT_ARROW_MARGIN * 2
        
        return QSize(base_size.width() + arrow_space, base_size.height())

    def _on_clicked(self) -> None:
        if self._menu:
            self._show_menu()

    def _show_menu(self) -> None:
        if not self._menu:
            return

        margin = MenuConfig.DEFAULT_MARGIN
        global_pos = self.mapToGlobal(QPoint(-margin, self.height() + DropDownConfig.MENU_OFFSET_Y))
        self._menu.exec(global_pos)

    def _on_theme_changed(self, theme: Theme) -> None:
        super()._on_theme_changed(theme)
        self._update_arrow_icon()

    def _build_stylesheet(self, theme: Theme) -> str:
        bg_normal = self.get_style_color(theme, 'dropdown.background.normal',
                                         theme.get_color('button.background.normal', DropDownConfig.FALLBACK_BG_NORMAL))
        bg_hover = self.get_style_color(theme, 'dropdown.background.hover',
                                        theme.get_color('button.background.hover', DropDownConfig.FALLBACK_BG_HOVER))
        bg_pressed = self.get_style_color(theme, 'dropdown.background.pressed',
                                          theme.get_color('button.background.pressed', DropDownConfig.FALLBACK_BG_PRESSED))
        bg_disabled = self.get_style_color(theme, 'dropdown.background.disabled',
                                           theme.get_color('button.background.disabled', DropDownConfig.FALLBACK_BG_DISABLED))

        text_normal = self.get_style_color(theme, 'dropdown.text.normal',
                                           theme.get_color('button.text.normal', DropDownConfig.FALLBACK_TEXT_NORMAL))
        text_disabled = self.get_style_color(theme, 'dropdown.text.disabled',
                                             theme.get_color('button.text.disabled', DropDownConfig.FALLBACK_TEXT_DISABLED))

        border_normal = self.get_style_color(theme, 'dropdown.border.normal',
                                             theme.get_color('button.border.normal', TRANSPARENT_COLOR))
        border_hover = self.get_style_color(theme, 'dropdown.border.hover',
                                            theme.get_color('button.border.hover', TRANSPARENT_COLOR))
        border_pressed = self.get_style_color(theme, 'dropdown.border.pressed',
                                              theme.get_color('button.border.pressed', TRANSPARENT_COLOR))
        border_disabled = self.get_style_color(theme, 'dropdown.border.disabled',
                                               theme.get_color('button.border.disabled', TRANSPARENT_COLOR))

        padding = self.get_style_value(theme, 'dropdown.padding', DropDownConfig.DEFAULT_PADDING)
        border_radius = self.get_style_value(theme, 'dropdown.border_radius', DropDownConfig.DEFAULT_BORDER_RADIUS)

        border_style_normal = self._build_border_style(border_normal)
        border_style_hover = self._build_border_style(border_hover)
        border_style_pressed = self._build_border_style(border_pressed)
        border_style_disabled = self._build_border_style(border_disabled)

        qss = f"""
        DropDownPushButton {{
            background-color: {bg_normal.name()};
            color: {text_normal.name()};
            border: {border_style_normal};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: left;
            min-height: {DropDownConfig.DEFAULT_MIN_HEIGHT}px;
        }}
        DropDownPushButton:hover {{
            background-color: {bg_hover.name()};
            border: {border_style_hover};
        }}
        DropDownPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: {border_style_pressed};
        }}
        DropDownPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss

    def _update_arrow_icon(self) -> None:
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color('dropdown.arrow.normal', 
                                                    self._current_theme.get_color('button.text.normal', QColor(255, 255, 255)))
        
        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)
        
        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, DropDownConfig.DEFAULT_ARROW_SIZE)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        
        if self._arrow_icon and not self._arrow_icon.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            arrow_size = DropDownConfig.DEFAULT_ARROW_SIZE
            arrow_margin = DropDownConfig.DEFAULT_ARROW_MARGIN
            
            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2
            
            self._arrow_icon.paint(painter, x, y, arrow_size, arrow_size)

    def setMenu(self, menu: RoundMenu) -> None:
        if not isinstance(menu, RoundMenu):
            logger.warning("菜单必须是 RoundMenu 或其子类")
            return

        self._menu = menu
        logger.debug(f"下拉菜单已设置: {menu.title()}")

    def menu(self) -> Optional[RoundMenu]:
        return self._menu

    def set_padding(self, padding: str) -> None:
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('dropdown.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def showMenu(self) -> None:
        self._show_menu()

    def hideMenu(self) -> None:
        if self._menu:
            self._menu.hide()
