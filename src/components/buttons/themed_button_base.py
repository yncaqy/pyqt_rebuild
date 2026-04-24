"""
主题化按钮基类

提供统一的按钮主题化基础设施，消除按钮组件间的代码重复。

功能特性:
- 统一的主题订阅和管理
- 统一的样式缓存机制
- 统一的图标管理
- 统一的清理机制
- 可扩展的样式构建接口
"""

import logging
import time
from abc import abstractmethod
from typing import Optional, Tuple, Any

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy

from src.core.theme_manager import ThemeManager, Theme
from src.core.icon_manager import IconManager
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.core.shadow_manager import ShadowMixin, ShadowDepth

logger = logging.getLogger(__name__)


class ThemedButtonBase(QPushButton, StyleOverrideMixin, StylesheetCacheMixin, ShadowMixin):
    """
    主题化按钮基类。

    所有需要主题支持的按钮都应继承此类，以获得：
    - 自动主题订阅和取消订阅
    - 样式覆盖能力
    - 样式表缓存
    - 统一的图标管理
    - 统一的清理机制

    子类需要实现：
    - `_build_stylesheet(theme)`: 构建样式表
    - `_get_cache_key(theme)`: 获取缓存键（可选，有默认实现）

    使用示例:
        class MyButton(ThemedButtonBase):
            def _build_stylesheet(self, theme: Theme) -> str:
                bg = self.get_style_color(theme, 'button.background.normal', QColor(60, 60, 60))
                return f"MyButton {{ background-color: {bg.name()}; }}"
    """

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None,
        icon_name: str = "",
        checkable: bool = False
    ):
        """
        初始化主题化按钮基类。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
            checkable: 是否可切换状态
        """
        super().__init__(text, parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)
        self._init_shadow()

        self._setup_size_policy()

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._icon_name = icon_name
        self._icon_size = QSize(16, 16)
        self._icon_color_role = 'button.icon.normal'
        self._is_svg_icon = False

        if checkable:
            self.setCheckable(True)
            self.toggled.connect(self._on_toggled)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        if icon_name and not checkable:
            self._update_icon()

        logger.debug(f"{self.__class__.__name__} 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def _setup_size_policy(self) -> None:
        """设置尺寸策略。子类可重写此方法以自定义尺寸策略。"""
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )

    def _on_toggled(self, checked: bool) -> None:
        """
        处理按钮状态变化。

        Args:
            checked: 新的选中状态
        """
        if self._current_theme:
            self._apply_theme(self._current_theme)
        self._update_icon()
        logger.debug(f"{self.__class__.__name__} 状态改变: {checked}")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        Args:
            theme: 新的主题对象
        """
        try:
            self._apply_theme(theme)
            self._update_icon()
            is_dark = theme.is_dark if theme else True
            self._update_shadow_color(is_dark)
        except Exception as e:
            logger.error(f"应用主题到 {self.__class__.__name__} 时出错: {e}")

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

        cache_key = self._get_cache_key(theme)

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

    def _get_cache_key(self, theme: Theme) -> Tuple[Any, ...]:
        """
        获取样式表缓存键。

        子类可重写此方法以自定义缓存键。
        默认实现返回主题名称和选中状态。

        Args:
            theme: 主题对象

        Returns:
            缓存键元组
        """
        theme_name = getattr(theme, 'name', 'unnamed')
        return (theme_name, self.isChecked())

    @abstractmethod
    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        子类必须实现此方法以定义自己的样式。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        pass

    def _build_border_style(self, border_color: QColor) -> str:
        """
        构建边框样式（WinUI 3 风格）。

        始终保持 1px 边框宽度，避免状态切换时按钮大小变化。

        Args:
            border_color: 边框颜色

        Returns:
            边框样式字符串
        """
        return f"1px solid {border_color.name(QColor.NameFormat.HexArgb)}"

    def set_theme(self, name: str) -> None:
        """
        通过名称设置当前主题。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）
        """
        logger.info(f"设置主题: {name}")
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

    def set_border_radius(self, radius: int) -> None:
        """
        设置按钮边框圆角。

        Args:
            radius: 圆角半径（像素），必须为非负整数
        """
        if not isinstance(radius, int) or radius < 0:
            logger.warning(f"无效的边框圆角值: {radius}")
            return

        logger.debug(f"设置边框圆角: {radius}px")
        self.override_style('button.border_radius', radius)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def set_padding(self, padding: str) -> None:
        """
        设置按钮内边距。

        Args:
            padding: 内边距值，如 '8px 16px' 或 '10px'
        """
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('button.padding', padding)
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
            logger.debug(f"{self.__class__.__name__} 已取消主题订阅")

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

        if self._is_svg_icon:
            if self._current_theme:
                if self.isChecked() and self.isCheckable():
                    checked_color_key = self._get_checked_text_color_key()
                    color = self._current_theme.get_color(
                        checked_color_key,
                        self._current_theme.get_color('button.text.checked', QColor(255, 255, 255))
                    )
                else:
                    text_color = self._current_theme.get_color('button.text.normal', QColor(224, 224, 224))
                    color = self._current_theme.get_color(self._icon_color_role, text_color)

                colored_svg = self._colorize_svg(self._icon_name, color)
                icon = self._icon_mgr.get_icon_from_svg(colored_svg, icon_size)
            else:
                icon = self._icon_mgr.get_icon_from_svg(self._icon_name, icon_size)
        else:
            if self._current_theme:
                theme_type = "dark" if self._current_theme.is_dark else "light"
                resolved_name = self._icon_mgr.resolve_icon_name(self._icon_name, theme_type)

                if self.isChecked() and self.isCheckable():
                    checked_color_key = self._get_checked_text_color_key()
                    color = self._current_theme.get_color(
                        checked_color_key,
                        self._current_theme.get_color('button.text.checked', QColor(255, 255, 255))
                    )
                else:
                    text_color = self._current_theme.get_color('button.text.normal', QColor(224, 224, 224))
                    color = self._current_theme.get_color(self._icon_color_role, text_color)
                icon = self._icon_mgr.get_colored_icon(resolved_name, color, icon_size)
            else:
                icon = self._icon_mgr.get_icon(self._icon_name, icon_size)

        self.setIcon(icon)
        self.setIconSize(self._icon_size)
        logger.debug(f"图标已更新: {self._icon_name}")

    def _colorize_svg(self, svg_content: str, color: QColor) -> str:
        """
        给 SVG 内容上色。

        Args:
            svg_content: SVG 内容字符串
            color: 目标颜色

        Returns:
            上色后的 SVG 内容
        """
        import re
        color_hex = color.name(QColor.NameFormat.HexRgb)

        svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color_hex}"', svg_content)
        svg_content = re.sub(r'fill="[^"]*"', f'fill="{color_hex}"', svg_content)
        svg_content = re.sub(r'stroke:[^;"]*', f'stroke:{color_hex}', svg_content)
        svg_content = re.sub(r'fill:[^;"]*', f'fill:{color_hex}', svg_content)

        return svg_content

    def _get_checked_text_color_key(self) -> str:
        """
        获取选中状态的文本颜色键。

        子类可重写此方法以自定义选中状态的文本颜色键。

        Returns:
            主题颜色键
        """
        return 'button.text.checked'

    def set_icon(self, icon_name: str) -> None:
        """
        设置按钮图标。

        Args:
            icon_name: 图标名称（不带扩展名）或 SVG 字符串
        """
        is_svg = icon_name.strip().startswith('<svg')

        if self._icon_name != icon_name or self._is_svg_icon != is_svg:
            self._icon_name = icon_name
            self._is_svg_icon = is_svg
            self._update_icon()
            logger.debug(f"图标设置为: {'SVG' if is_svg else icon_name}")

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
        from src.components.tooltips.tooltip_manager import install_tooltip
        install_tooltip(self, tooltip)
        logger.debug(f"工具提示设置为: {tooltip}")

    def get_tooltip(self) -> str:
        """
        获取当前工具提示文本。

        Returns:
            当前工具提示文本
        """
        return self.toolTip()

    def remove_tooltip(self) -> None:
        """移除按钮的工具提示。"""
        from src.components.tooltips.tooltip_manager import remove_tooltip
        remove_tooltip(self)
        logger.debug("工具提示已移除")

    def deleteLater(self) -> None:
        """
        安排组件延迟删除，并自动执行清理。

        重写 Qt 的 deleteLater 方法，确保正确清理资源。
        """
        self.remove_tooltip()
        self.cleanup()
        super().deleteLater()
        logger.debug(f"{self.__class__.__name__} 已安排删除")
