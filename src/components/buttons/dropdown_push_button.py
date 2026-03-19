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
from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QWidget

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase
from components.menus.round_menu import RoundMenu, MenuConfig

logger = logging.getLogger(__name__)


class DropDownConfig:
    """下拉按钮行为和样式的配置常量。"""

    DEFAULT_PADDING = '5px 24px 5px 8px'
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_ARROW_SIZE = 12
    DEFAULT_ARROW_MARGIN = 6


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
        self._icon_size = QSize(16, 16)
        
        self.clicked.connect(self._on_clicked)

        logger.debug(f"DropDownPushButton 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def sizeHint(self) -> QSize:
        """
        返回按钮的建议尺寸。

        确保按钮宽度足够容纳文本、图标和下拉箭头。
        """
        base_size = super().sizeHint()
        
        arrow_space = DropDownConfig.DEFAULT_ARROW_SIZE + DropDownConfig.DEFAULT_ARROW_MARGIN * 2
        
        return QSize(base_size.width() + arrow_space, base_size.height())

    def _on_clicked(self) -> None:
        """处理按钮点击事件，显示下拉菜单。"""
        if self._menu:
            self._show_menu()

    def _show_menu(self) -> None:
        """显示下拉菜单。"""
        if not self._menu:
            return

        margin = MenuConfig.DEFAULT_MARGIN
        global_pos = self.mapToGlobal(QPoint(-margin, self.height() + 4))
        self._menu.exec(global_pos)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        Args:
            theme: 新的主题对象
        """
        super()._on_theme_changed(theme)
        self._update_arrow_icon()

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        bg_normal = self.get_style_color(theme, 'dropdown.background.normal',
                                         theme.get_color('button.background.normal', QColor(58, 58, 58)))
        bg_hover = self.get_style_color(theme, 'dropdown.background.hover',
                                        theme.get_color('button.background.hover', QColor(74, 74, 74)))
        bg_pressed = self.get_style_color(theme, 'dropdown.background.pressed',
                                          theme.get_color('button.background.pressed', QColor(85, 85, 85)))
        bg_disabled = self.get_style_color(theme, 'dropdown.background.disabled',
                                           theme.get_color('button.background.disabled', QColor(42, 42, 42)))

        text_normal = self.get_style_color(theme, 'dropdown.text.normal',
                                           theme.get_color('button.text.normal', QColor(224, 224, 224)))
        text_disabled = self.get_style_color(theme, 'dropdown.text.disabled',
                                             theme.get_color('button.text.disabled', QColor(102, 102, 102)))

        border_normal = self.get_style_color(theme, 'dropdown.border.normal',
                                             theme.get_color('button.border.normal', QColor('transparent')))
        border_hover = self.get_style_color(theme, 'dropdown.border.hover',
                                            theme.get_color('button.border.hover', QColor('transparent')))
        border_pressed = self.get_style_color(theme, 'dropdown.border.pressed',
                                              theme.get_color('button.border.pressed', QColor('transparent')))
        border_disabled = self.get_style_color(theme, 'dropdown.border.disabled',
                                               theme.get_color('button.border.disabled', QColor('transparent')))

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
            min-height: 28px;
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
        """更新下拉箭头图标。"""
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color('dropdown.arrow.normal',
                                                    self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200)))
        
        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)
        
        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, DropDownConfig.DEFAULT_ARROW_SIZE)
        self.update()

    def paintEvent(self, event) -> None:
        """重写绘制事件，绘制下拉箭头。"""
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
        """
        设置下拉菜单。

        Args:
            menu: RoundMenu 或其子类实例
        """
        if not isinstance(menu, RoundMenu):
            logger.warning("菜单必须是 RoundMenu 或其子类")
            return

        self._menu = menu
        logger.debug(f"下拉菜单已设置: {menu.title()}")

    def menu(self) -> Optional[RoundMenu]:
        """
        获取关联的下拉菜单。

        Returns:
            RoundMenu 实例，如果未设置则返回 None
        """
        return self._menu

    def set_padding(self, padding: str) -> None:
        """
        设置按钮内边距。

        Args:
            padding: 内边距值，如 '8px 12px' 或 '8px'
        """
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('dropdown.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def showMenu(self) -> None:
        """显示下拉菜单（公开方法）。"""
        self._show_menu()

    def hideMenu(self) -> None:
        """隐藏下拉菜单。"""
        if self._menu:
            self._menu.hide()
