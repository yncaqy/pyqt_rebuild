"""
下拉按钮组件

遵循 Microsoft WinUI 3 DropDownButton 设计规范实现。
DropDownButton 是一个带有下拉箭头的按钮，用于打开附加的弹出面板。

设计规范参考:
https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/buttons#example---drop-down-button

核心特性:
- 点击自动打开下拉菜单
- 下拉箭头作为视觉指示器
- 支持正常、悬停、按下、禁用状态
- 主题集成，自动响应主题切换
- 键盘导航支持
- 可访问性支持
- 菜单放置位置可配置

使用场景:
- 当按钮具有包含更多选项的浮出控件时使用
- 默认的下拉箭头以视觉方式提示用户，此按钮包含下拉菜单
"""

import logging
from enum import Enum
from typing import Optional, List

from PyQt6.QtCore import QSize, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QKeyEvent, QAction, QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget, QMenu

from core.theme_manager import Theme
from components.buttons.themed_button_base import ThemedButtonBase
from components.menus.round_menu import RoundMenu, MenuConfig
from themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG, FALLBACK_COLORS, FALLBACK_COLORS_LIGHT

logger = logging.getLogger(__name__)

TRANSPARENT_COLOR = QColor(0, 0, 0, 0)


class MenuPlacement(Enum):
    """菜单放置位置枚举，对应 WinUI 3 Placement 模式。"""
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"


class DropDownConfig:
    """下拉按钮配置常量，遵循 WinUI 3 设计规范。"""

    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['dropdown']['border_radius']
    DEFAULT_ARROW_SIZE = WINUI3_CONTROL_SIZING['dropdown']['arrow_size']
    DEFAULT_ARROW_MARGIN = WINUI3_CONTROL_SIZING['dropdown']['arrow_margin']
    DEFAULT_MIN_HEIGHT = WINUI3_CONTROL_SIZING['dropdown']['min_height']
    MENU_OFFSET_Y = 2

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

    @staticmethod
    def get_padding() -> str:
        """获取按钮内边距，遵循 WinUI 3 设计规范。"""
        padding_v = WINUI3_CONTROL_SIZING['dropdown']['padding_v']
        padding_h = WINUI3_CONTROL_SIZING['dropdown']['padding_h']
        return f"{padding_v}px {padding_h}px"


class DropDownPushButton(ThemedButtonBase):
    """
    下拉按钮组件，遵循 Microsoft WinUI 3 DropDownButton 设计规范。

    DropDownButton 是一个带有下拉箭头的按钮，用于打开附加的弹出面板。
    默认的下拉箭头以视觉方式提示用户，此按钮包含下拉菜单。

    特性:
    - 点击自动打开下拉菜单
    - 下拉箭头作为视觉指示器
    - 支持正常、悬停、按下、禁用状态
    - 主题集成，自动响应主题切换
    - 键盘导航支持 (Enter/Space/Down 打开菜单)
    - 可访问性支持
    - 菜单放置位置可配置
    - 优化的样式缓存机制
    - 内存安全，支持正确的清理机制

    示例:
        button = DropDownPushButton("文件")
        menu = RoundMenu()
        menu.addAction("新建", lambda: print("新建"))
        menu.addAction("打开", lambda: print("打开"))
        menu.addSeparator()
        menu.addAction("退出", lambda: print("退出"))
        button.setMenu(menu)

    属性:
        menuPlacement: 菜单放置位置，默认为 BOTTOM_LEFT

    信号:
        aboutToShow: 菜单即将显示时发出
        aboutToHide: 菜单即将隐藏时发出
    """

    aboutToShow = pyqtSignal()
    aboutToHide = pyqtSignal()

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None,
        icon_name: str = "",
        placement: MenuPlacement = MenuPlacement.BOTTOM_LEFT
    ):
        """
        初始化下拉按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
            placement: 菜单放置位置，默认为左下角对齐
        """
        super().__init__(text, parent, icon_name)

        self._menu: Optional[RoundMenu] = None
        self._arrow_icon: Optional[QIcon] = None
        self._menu_placement: MenuPlacement = placement
        self._is_menu_open: bool = False
        self._icon_size = QSize(
            WINUI3_CONTROL_SIZING['dropdown']['icon_size'],
            WINUI3_CONTROL_SIZING['dropdown']['icon_size']
        )

        self._setup_font()

        self.clicked.connect(self._on_clicked)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if self._current_theme:
            self._update_arrow_icon()

        logger.debug(f"DropDownPushButton 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def _setup_font(self) -> None:
        """设置按钮字体，遵循 WinUI 3 设计规范。"""
        font = QFont()
        font.setFamilies([FONT_CONFIG['family'], FONT_CONFIG.get('fallback', 'Microsoft YaHei UI')])
        font.setPixelSize(FONT_CONFIG['size']['body'])
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

    def sizeHint(self) -> QSize:
        """返回推荐尺寸，遵循 WinUI 3 设计规范。"""
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text()) if self.text() else 0
        
        padding_h = WINUI3_CONTROL_SIZING['dropdown']['padding_h']
        arrow_size = DropDownConfig.DEFAULT_ARROW_SIZE
        arrow_margin = DropDownConfig.DEFAULT_ARROW_MARGIN
        
        icon_width = 0
        if not self.icon().isNull():
            icon_width = self._icon_size.width() + 8
        
        width = text_width + icon_width + arrow_size + arrow_margin + padding_h * 2
        height = DropDownConfig.DEFAULT_MIN_HEIGHT
        
        return QSize(max(width, 80), height)

    def minimumSizeHint(self) -> QSize:
        """返回最小尺寸。"""
        return self.sizeHint()

    def _on_clicked(self) -> None:
        """处理点击事件，自动打开下拉菜单。"""
        if self._menu:
            self._show_menu()

    def _show_menu(self) -> None:
        """显示下拉菜单，根据配置的放置位置定位。"""
        if not self._menu:
            return

        self.aboutToShow.emit()
        self._is_menu_open = True

        global_pos = self._calculate_menu_position()
        self._menu.exec(global_pos)

        self._is_menu_open = False
        self.aboutToHide.emit()

    def _calculate_menu_position(self) -> QPoint:
        """计算菜单显示位置，基于放置模式。"""
        margin = MenuConfig.DEFAULT_MARGIN

        if self._menu_placement == MenuPlacement.BOTTOM_LEFT:
            return self.mapToGlobal(
                QPoint(-margin, self.height() + DropDownConfig.MENU_OFFSET_Y)
            )
        elif self._menu_placement == MenuPlacement.BOTTOM_RIGHT:
            menu_width = self._menu.sizeHint().width() if self._menu else 0
            return self.mapToGlobal(
                QPoint(self.width() - menu_width - margin * 2, self.height() + DropDownConfig.MENU_OFFSET_Y)
            )
        elif self._menu_placement == MenuPlacement.TOP_LEFT:
            menu_height = self._menu.sizeHint().height() if self._menu else 0
            return self.mapToGlobal(
                QPoint(-margin, -menu_height - DropDownConfig.MENU_OFFSET_Y)
            )
        elif self._menu_placement == MenuPlacement.TOP_RIGHT:
            menu_width = self._menu.sizeHint().width() if self._menu else 0
            menu_height = self._menu.sizeHint().height() if self._menu else 0
            return self.mapToGlobal(
                QPoint(self.width() - menu_width - margin * 2, -menu_height - DropDownConfig.MENU_OFFSET_Y)
            )

        return self.mapToGlobal(QPoint(-margin, self.height() + DropDownConfig.MENU_OFFSET_Y))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        处理键盘事件，支持键盘导航。

        - Enter/Space: 打开菜单
        - Down: 打开菜单并聚焦第一个菜单项
        - Up: 打开菜单并聚焦最后一个菜单项
        - Escape: 关闭菜单
        """
        if self._menu:
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Space, Qt.Key.Key_Down):
                self._show_menu()
                event.accept()
                return
            elif key == Qt.Key.Key_Up:
                self._show_menu()
                event.accept()
                return
            elif key == Qt.Key.Key_Escape:
                if self._is_menu_open:
                    self._menu.hide()
                    event.accept()
                    return

        super().keyPressEvent(event)

    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变更，更新样式和箭头图标。"""
        super()._on_theme_changed(theme)
        self._update_arrow_icon()

    def _build_stylesheet(self, theme: Theme) -> str:
        """构建样式表，使用主题颜色。"""
        is_dark = theme.is_dark if theme else True
        
        bg_normal = self.get_style_color(
            theme, 'dropdown.background.normal',
            theme.get_color('button.background.normal', DropDownConfig.get_fallback_bg_normal(is_dark))
        )
        bg_hover = self.get_style_color(
            theme, 'dropdown.background.hover',
            theme.get_color('button.background.hover', DropDownConfig.get_fallback_bg_hover(is_dark))
        )
        bg_pressed = self.get_style_color(
            theme, 'dropdown.background.pressed',
            theme.get_color('button.background.pressed', DropDownConfig.get_fallback_bg_pressed(is_dark))
        )
        bg_disabled = self.get_style_color(
            theme, 'dropdown.background.disabled',
            theme.get_color('button.background.disabled', DropDownConfig.get_fallback_bg_disabled(is_dark))
        )

        text_normal = self.get_style_color(
            theme, 'dropdown.text.normal',
            theme.get_color('button.text.normal', DropDownConfig.get_fallback_text_normal(is_dark))
        )
        text_disabled = self.get_style_color(
            theme, 'dropdown.text.disabled',
            theme.get_color('button.text.disabled', DropDownConfig.get_fallback_text_disabled(is_dark))
        )

        border_normal = self.get_style_color(
            theme, 'dropdown.border.normal',
            theme.get_color('button.border.normal', TRANSPARENT_COLOR)
        )
        border_hover = self.get_style_color(
            theme, 'dropdown.border.hover',
            theme.get_color('button.border.hover', TRANSPARENT_COLOR)
        )
        border_pressed = self.get_style_color(
            theme, 'dropdown.border.pressed',
            theme.get_color('button.border.pressed', TRANSPARENT_COLOR)
        )
        border_disabled = self.get_style_color(
            theme, 'dropdown.border.disabled',
            theme.get_color('button.border.disabled', TRANSPARENT_COLOR)
        )

        padding = self.get_style_value(theme, 'dropdown.padding', DropDownConfig.get_padding())
        border_radius = self.get_style_value(theme, 'dropdown.border_radius', DropDownConfig.DEFAULT_BORDER_RADIUS)

        border_style_normal = self._build_border_style(border_normal)
        border_style_hover = self._build_border_style(border_hover)
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
            border: none;
        }}
        DropDownPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: {border_style_disabled};
        }}
        """

        return qss

    def _update_arrow_icon(self) -> None:
        """更新箭头图标，使用主题颜色。"""
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color(
            'dropdown.arrow.normal',
            self._current_theme.get_color('button.text.normal', QColor(255, 255, 255))
        )

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon = self._icon_mgr.get_colored_icon(
            arrow_name, arrow_color, DropDownConfig.DEFAULT_ARROW_SIZE
        )
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制按钮，包含箭头指示器。"""
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

        Raises:
            TypeError: 如果 menu 不是 RoundMenu 类型
        """
        if not isinstance(menu, RoundMenu):
            raise TypeError("菜单必须是 RoundMenu 或其子类")

        self._menu = menu
        logger.debug(f"下拉菜单已设置: {menu.title()}")

    def menu(self) -> Optional[RoundMenu]:
        """返回当前关联的菜单。"""
        return self._menu

    def setMenuPlacement(self, placement: MenuPlacement) -> None:
        """
        设置菜单放置位置。

        Args:
            placement: MenuPlacement 枚举值
        """
        self._menu_placement = placement
        logger.debug(f"菜单放置位置已设置: {placement.value}")

    def menuPlacement(self) -> MenuPlacement:
        """返回当前菜单放置位置。"""
        return self._menu_placement

    def isMenuOpen(self) -> bool:
        """返回菜单是否打开。"""
        return self._is_menu_open

    def showMenu(self) -> None:
        """公开方法：显示下拉菜单。"""
        self._show_menu()

    def hideMenu(self) -> None:
        """公开方法：隐藏下拉菜单。"""
        if self._menu:
            self._menu.hide()

    def set_padding(self, padding: str) -> None:
        """
        设置按钮内边距。

        Args:
            padding: CSS 格式的内边距字符串，如 "8px 12px"
        """
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('dropdown.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def add_action(self, text: str, callback=None, icon_name: str = "") -> None:
        """
        快捷方法：向菜单添加操作项。

        如果菜单不存在，会自动创建一个新菜单。

        Args:
            text: 操作文本
            callback: 点击回调函数
            icon_name: 图标名称（可选）
        """
        if not self._menu:
            self._menu = RoundMenu(self)

        self._menu.addAction(text, callback, icon_name)

    def add_separator(self) -> None:
        """快捷方法：向菜单添加分隔线。"""
        if not self._menu:
            self._menu = RoundMenu(self)

        self._menu.addSeparator()

    def clear_menu(self) -> None:
        """清空菜单中的所有项。"""
        if self._menu:
            self._menu.clear()
