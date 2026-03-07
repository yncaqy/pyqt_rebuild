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
import time
from typing import Optional
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class PillConfig:
    """胶囊按钮行为和样式的配置常量。"""

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_PADDING = '6px 12px'
    DEFAULT_HEIGHT = 28
    DEFAULT_BORDER_RADIUS = DEFAULT_HEIGHT // 2


class PillPushButton(QPushButton, StyleOverrideMixin, StylesheetCacheMixin):
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

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, icon_name: str = ""):
        """
        初始化胶囊按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(
            PillConfig.DEFAULT_HORIZONTAL_POLICY,
            PillConfig.DEFAULT_VERTICAL_POLICY
        )
        self.setFixedHeight(PillConfig.DEFAULT_HEIGHT)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._icon_name = icon_name
        self._icon_size = QSize(14, 14)
        self._icon_color_role = 'button.icon.normal'

        self.setCheckable(True)
        self.toggled.connect(self._on_toggled)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
        else:
            if icon_name:
                self._update_icon()

        logger.debug(f"PillPushButton 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def _on_toggled(self, checked: bool) -> None:
        """
        处理按钮状态变化。

        Args:
            checked: 新的选中状态
        """
        if self._current_theme:
            self._apply_theme(self._current_theme)
        self._update_icon()
        logger.debug(f"PillPushButton 状态改变: {checked}")

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
            logger.error(f"应用主题到 PillPushButton 时出错: {e}")

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
        
        cache_key = (theme_name, self.isChecked())

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme),
            theme_name
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (缓存大小: {self._get_cache_size()}, 耗时 {elapsed_time:.3f}s)")

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
                                             theme.get_color('button.border.normal', QColor(68, 68, 68)))
        border_hover = self.get_style_color(theme, 'pill.border.hover', 
                                            theme.get_color('button.border.hover', QColor(93, 173, 226)))
        border_disabled = self.get_style_color(theme, 'pill.border.disabled', 
                                               theme.get_color('button.border.disabled', QColor(51, 51, 51)))
        border_checked = self.get_style_color(theme, 'pill.border.checked', 
                                              theme.get_color('button.border.checked', QColor(93, 173, 226)))

        padding = self.get_style_value(theme, 'pill.padding', PillConfig.DEFAULT_PADDING)
        border_radius = PillConfig.DEFAULT_BORDER_RADIUS

        qss = f"""
        PillPushButton {{
            background-color: {bg_normal.name()};
            color: {text_normal.name()};
            border: 1px solid {border_normal.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            text-align: center;
        }}
        PillPushButton:hover {{
            background-color: {bg_hover.name()};
            border: 1px solid {border_hover.name()};
        }}
        PillPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid {border_disabled.name()};
        }}
        PillPushButton:checked {{
            background-color: {bg_checked.name()};
            color: {text_checked.name()};
            border: 1px solid {border_checked.name()};
        }}
        PillPushButton:checked:hover {{
            background-color: {bg_checked_hover.name()};
            border: 1px solid {border_checked.name()};
        }}
        PillPushButton:checked:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid {border_disabled.name()};
        }}
        """

        return qss

    def set_theme(self, name: str) -> None:
        """
        通过名称设置当前主题。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）
        """
        logger.debug(f"设置主题: {name}")
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
            padding: 内边距值，如 '6px 12px' 或 '8px'
        """
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('pill.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("PillPushButton 已取消主题订阅")

        self._clear_stylesheet_cache()
        self.clear_overrides()

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
            
            if self.isChecked():
                color = self._current_theme.get_color('pill.text.checked', 
                                                      self._current_theme.get_color('button.text.checked', QColor(255, 255, 255)))
            else:
                color = self._current_theme.get_color(self._icon_color_role, QColor(50, 50, 50))
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

    def set_tooltip(self, tooltip: str) -> None:
        """
        设置按钮工具提示。

        Args:
            tooltip: 悬停时显示的提示文本
        """
        from components.tooltips.tooltip_manager import install_tooltip
        install_tooltip(self, tooltip)
        logger.debug(f"工具提示设置为: {tooltip}")

    def remove_tooltip(self) -> None:
        """移除按钮的工具提示。"""
        from components.tooltips.tooltip_manager import remove_tooltip
        remove_tooltip(self)
