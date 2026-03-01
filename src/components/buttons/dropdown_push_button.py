"""
下拉按钮组件

提供带下拉菜单的按钮，具有以下特性：
- 点击弹出 RoundMenu 下拉菜单
- 主题集成，自动更新样式
- 支持正常、悬停、按下、禁用状态
- 支持文本和图标显示
- 下拉箭头图标指示器
"""

import logging
import time
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import QSize, QPoint
from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin
from components.menus.round_menu import RoundMenu, MenuConfig

logger = logging.getLogger(__name__)


class DropDownConfig:
    """
    下拉按钮行为和样式的配置常量。

    Attributes:
        DEFAULT_HORIZONTAL_POLICY: 默认水平尺寸策略
        DEFAULT_VERTICAL_POLICY: 默认垂直尺寸策略
        DEFAULT_PADDING: 默认内边距
        DEFAULT_BORDER_RADIUS: 默认边框圆角
        DEFAULT_ARROW_SIZE: 下拉箭头尺寸
        DEFAULT_ARROW_MARGIN: 箭头与文本间距
        MAX_STYLESHEET_CACHE_SIZE: 样式缓存最大数量
    """

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_PADDING = '8px 32px 8px 12px'
    DEFAULT_BORDER_RADIUS = 6
    DEFAULT_ARROW_SIZE = 12
    DEFAULT_ARROW_MARGIN = 10
    MAX_STYLESHEET_CACHE_SIZE = 100


class DropDownPushButton(QPushButton, StyleOverrideMixin):
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
        super().__init__(text, parent)

        self._init_style_override()

        self.setSizePolicy(
            DropDownConfig.DEFAULT_HORIZONTAL_POLICY,
            DropDownConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self._icon_name = icon_name
        self._icon_size = QSize(16, 16)
        self._icon_color_role = 'button.icon.normal'

        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        self._menu: Optional[RoundMenu] = None
        self._arrow_icon: Optional[QIcon] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
        else:
            if icon_name:
                self._update_icon()

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
        try:
            self._apply_theme(theme)
            self._update_icon()
        except Exception as e:
            logger.error(f"应用主题到 DropDownPushButton 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到按钮，支持缓存和性能监控。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        start_time = time.time()

        if not theme:
            logger.debug("主题为空，跳过应用")
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')

        cache_key = (theme_name,)

        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            qss = self._build_stylesheet(theme)
            if len(self._stylesheet_cache) < DropDownConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)
        
        self._update_arrow_icon()

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (缓存大小: {len(self._stylesheet_cache)}, 耗时 {elapsed_time:.3f}s)")

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
                                             theme.get_color('button.border.normal', QColor(68, 68, 68)))
        border_hover = self.get_style_color(theme, 'dropdown.border.hover',
                                            theme.get_color('button.border.hover', QColor(93, 173, 226)))
        border_pressed = self.get_style_color(theme, 'dropdown.border.pressed',
                                              theme.get_color('button.border.pressed', QColor(52, 152, 219)))
        border_disabled = self.get_style_color(theme, 'dropdown.border.disabled',
                                               theme.get_color('button.border.disabled', QColor(51, 51, 51)))

        padding = self.get_style_value(theme, 'dropdown.padding', DropDownConfig.DEFAULT_PADDING)
        border_radius = self.get_style_value(theme, 'dropdown.border_radius', DropDownConfig.DEFAULT_BORDER_RADIUS)

        qss = f"""
        DropDownPushButton {{
            background-color: {bg_normal.name()};
            color: {text_normal.name()};
            border: 1px solid {border_normal.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: left;
        }}
        DropDownPushButton:hover {{
            background-color: {bg_hover.name()};
            border: 1px solid {border_hover.name()};
        }}
        DropDownPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: 1px solid {border_pressed.name()};
        }}
        DropDownPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid {border_disabled.name()};
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

    def set_global_theme(self, name: str) -> None:
        """
        设置全局主题。

        注意：此方法会改变整个应用程序的主题，而不仅仅是此按钮。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）
        """
        logger.debug(f"设置全局主题: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        获取当前主题名称。

        Returns:
            当前主题名称，如果未设置主题则返回 None
        """
        try:
            if self._current_theme is not None:
                theme_name = getattr(self._current_theme, 'name', None)
                if theme_name is not None:
                    return str(theme_name)
            return None
        except Exception as e:
            logger.warning(f"获取主题名称时出错: {e}")
            return None

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

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        """
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("DropDownPushButton 已取消主题订阅")

        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("样式缓存已清空")

        self.clear_overrides()

    def __del__(self) -> None:
        """析构函数，自动清理资源。"""
        try:
            self.cleanup()
        except Exception:
            pass

    def _update_icon(self) -> None:
        """
        更新按钮图标。

        根据当前设置从图标管理器获取图标并应用到按钮。
        """
        if not self._icon_name:
            self.setIcon(QIcon())
            return

        icon_size = self._icon_size.width()
        if self._current_theme:
            theme_type = "dark" if self._current_theme.is_dark else "light"
            resolved_name = self._icon_mgr.resolve_icon_name(self._icon_name, theme_type)
            color = self._current_theme.get_color(self._icon_color_role, QColor(200, 200, 200))
            icon = self._icon_mgr.get_colored_icon(resolved_name, color, icon_size)
        else:
            icon = self._icon_mgr.get_icon(self._icon_name, icon_size)

        self.setIcon(icon)
        self.setIconSize(self._icon_size)
        logger.debug(f"图标已更新: {self._icon_name}")

    def set_icon(self, icon_name: str) -> None:
        """
        设置按钮图标。

        Args:
            icon_name: 图标名称（不带扩展名）
        """
        if self._icon_name != icon_name:
            self._icon_name = icon_name
            self._update_icon()
            logger.debug(f"图标设置为: {icon_name}")

    def get_icon(self) -> str:
        """
        获取当前图标名称。

        Returns:
            当前图标名称
        """
        return self._icon_name

    def set_icon_size(self, size: QSize) -> None:
        """
        设置图标尺寸。

        Args:
            size: 图标尺寸（QSize 对象）
        """
        if self._icon_size != size:
            self._icon_size = size
            self._update_icon()
            logger.debug(f"图标尺寸设置为: {size.width()}x{size.height()}")

    def get_icon_size(self) -> QSize:
        """
        获取当前图标尺寸。

        Returns:
            当前图标尺寸（QSize 对象）
        """
        return self._icon_size

    def set_icon_color_role(self, role: str) -> None:
        """
        设置图标颜色的主题角色。

        Args:
            role: 主题颜色角色（如 'button.icon.normal'）
        """
        if self._icon_color_role != role:
            self._icon_color_role = role
            if self._current_theme:
                self._update_icon()
            logger.debug(f"图标颜色角色设置为: {role}")

    def get_icon_color_role(self) -> str:
        """
        获取当前图标颜色角色。

        Returns:
            当前图标颜色角色
        """
        return self._icon_color_role

    def showMenu(self) -> None:
        """显示下拉菜单（公开方法）。"""
        self._show_menu()

    def hideMenu(self) -> None:
        """隐藏下拉菜单。"""
        if self._menu:
            self._menu.hide()
