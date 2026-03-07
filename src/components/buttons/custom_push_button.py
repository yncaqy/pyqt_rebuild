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
import time
from typing import Optional, Tuple, Any
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.icon_mixin import IconMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_aware_widget import ThemeAwareWidget

logger = logging.getLogger(__name__)


class ButtonConfig:
    """
    按钮行为和样式的配置常量。
    
    Attributes:
        DEFAULT_HORIZONTAL_POLICY: 默认水平尺寸策略
        DEFAULT_VERTICAL_POLICY: 默认垂直尺寸策略
        DEFAULT_BORDER_RADIUS: 默认边框圆角（像素）
        DEFAULT_PADDING: 默认内边距
    """

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_BORDER_RADIUS = 6
    DEFAULT_PADDING = '8px 16px'


class CustomPushButton(QPushButton, StyleOverrideMixin, IconMixin, StylesheetCacheMixin):
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
        button.setIconSource("Play", size=16)
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None, icon_name: str = ""):
        """
        初始化主题化按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
            icon_name: 图标名称（不带扩展名）
        """
        super().__init__(text, parent)
        
        self._init_style_override()
        self._init_icon_mixin()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(
            ButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            ButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._icon_color_role: str = 'button.icon.normal'

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        if icon_name:
            self.setIconSource(icon_name, size=16)

        logger.debug(f"CustomPushButton 初始化完成: 文本='{text}', 图标='{icon_name}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        当全局主题切换时，此方法会被自动调用。

        Args:
            theme: 新的主题对象
        """
        try:
            self._apply_theme(theme)
            self._update_icon_with_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 CustomPushButton 时出错: {e}")
            import traceback
            traceback.print_exc()

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
        cache_key = (
            theme_name,
            theme.get_color('button.background.normal', QColor(230, 230, 230)).name(),
            theme.get_color('button.background.hover', QColor(200, 200, 200)).name(),
            theme.get_color('button.background.pressed', QColor(180, 180, 180)).name(),
            theme.get_color('button.background.disabled', QColor(240, 240, 240)).name(),
            theme.get_color('button.text.normal', QColor(50, 50, 50)).name(),
            theme.get_color('button.text.disabled', QColor(150, 150, 150)).name(),
            theme.get_color('button.border.normal', QColor(150, 150, 150)).name(),
            theme.get_color('button.border.hover', QColor(100, 100, 100)).name(),
            theme.get_color('button.border.pressed', QColor(80, 80, 80)).name(),
            theme.get_color('button.border.disabled', QColor(200, 200, 200)).name(),
            theme.get_value('button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS),
            theme.get_value('button.padding', ButtonConfig.DEFAULT_PADDING),
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme),
            theme_name
        )

        current_stylesheet = self.styleSheet()
        if current_stylesheet != qss:
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (缓存大小: {self._get_cache_size()}, 耗时 {elapsed_time:.3f}s)")

    def _needs_style_refresh(self, new_qss: str) -> bool:
        """
        判断是否需要刷新样式。

        Args:
            new_qss: 新的样式表

        Returns:
            如果需要刷新返回 True，否则返回 False
        """
        current_qss = self.styleSheet()
        return current_qss != new_qss

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建按钮的样式表。

        根据主题数据生成完整的 QSS 样式表，包含所有状态样式。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        # 获取背景颜色（四种状态）
        bg_normal = self.get_style_color(theme, 'button.background.normal', QColor(230, 230, 230))
        bg_hover = self.get_style_color(theme, 'button.background.hover', QColor(200, 200, 200))
        bg_pressed = self.get_style_color(theme, 'button.background.pressed', QColor(180, 180, 180))
        bg_disabled = self.get_style_color(theme, 'button.background.disabled', QColor(240, 240, 240))

        # 获取文本颜色
        text_color = self.get_style_color(theme, 'button.text.normal', QColor(50, 50, 50))
        text_disabled = self.get_style_color(theme, 'button.text.disabled', QColor(150, 150, 150))

        # 获取边框颜色（四种状态）
        border_color = self.get_style_color(theme, 'button.border.normal', QColor(150, 150, 150))
        border_hover = self.get_style_color(theme, 'button.border.hover', QColor(100, 100, 100))
        border_pressed = self.get_style_color(theme, 'button.border.pressed', QColor(80, 80, 80))
        border_disabled = self.get_style_color(theme, 'button.border.disabled', QColor(200, 200, 200))

        # 获取布局相关属性
        border_radius = self.get_style_value(theme, 'button.border_radius', ButtonConfig.DEFAULT_BORDER_RADIUS)
        padding = self.get_style_value(theme, 'button.padding', ButtonConfig.DEFAULT_PADDING)

        # 构建 QSS 样式表
        qss = f"""
        CustomPushButton {{
            background-color: {bg_normal.name()};
            color: {text_color.name()};
            border: 2px solid {border_color.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            font-weight: bold;
            text-align: center;
        }}
        CustomPushButton:hover {{
            background-color: {bg_hover.name()};
            border: 2px solid {border_hover.name()};
        }}
        CustomPushButton:pressed {{
            background-color: {bg_pressed.name()};
            border: 2px solid {border_pressed.name()};
        }}
        CustomPushButton:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 2px solid {border_disabled.name()};
        }}
        """

        # 图标按钮的额外样式（预留扩展）
        if self._icon_source:
            qss += ""

        return qss

    def set_theme(self, name: str) -> None:
        """
        通过名称设置当前主题。

        这是一个便捷方法，委托给主题管理器执行。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）

        示例:
            button.set_theme('dark')
        """
        logger.info(f"设置主题: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        获取当前主题名称。

        Returns:
            当前主题名称，如果未设置主题则返回 None

        示例:
            current_theme = button.get_theme()
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

        使用本地样式覆盖，不影响共享主题。

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

        使用本地样式覆盖，不影响共享主题。

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
            logger.debug("CustomPushButton 已取消主题订阅")

        self._clear_stylesheet_cache()
        self.clear_overrides()
        self._cleanup_icon_mixin()

    def _apply_icon(self, icon: QIcon) -> None:
        """
        应用图标到按钮（重写 IconMixin 方法）。
        
        Args:
            icon: 要应用的图标
        """
        self.setIcon(icon)
        self.setIconSize(QSize(self._icon_size, self._icon_size))
        
        if self.text():
            original_text = self.text().lstrip()
            self.setText(f" {original_text}")
        
        if self._current_theme:
            base_qss = self._build_stylesheet(self._current_theme)
            self.setStyleSheet(base_qss)
        
        logger.debug(f"图标已应用: {self._icon_source}, 尺寸: {self._icon_size}x{self._icon_size}")

    def _update_icon(self, theme=None) -> None:
        """
        更新按钮图标（重写 IconMixin 方法）。
        
        使用按钮特定的颜色角色获取图标颜色。
        
        Args:
            theme: 当前主题，如果为 None 则使用 _current_theme
        """
        if not self._icon_source:
            self.setIcon(QIcon())
            if self._current_theme:
                qss = self._build_stylesheet(self._current_theme)
                self.setStyleSheet(qss)
            return
        
        if theme is None:
            theme = self._current_theme
        
        icon_name = self._icon_source
        
        if self._icon_theme_aware and theme:
            theme_type = 'dark' if theme.is_dark else 'light'
            icon_name = self._icon_mgr.resolve_icon_name(self._icon_source, theme_type)
        
        is_colored = self._icon_mgr.is_colored_icon(icon_name)
        
        if is_colored:
            self._current_icon = self._icon_mgr.get_icon(icon_name, self._icon_size)
        elif self._icon_color:
            self._current_icon = self._icon_mgr.get_colored_icon(
                icon_name, self._icon_color, self._icon_size
            )
        elif theme:
            color = theme.get_color(self._icon_color_role, QColor(50, 50, 50))
            self._current_icon = self._icon_mgr.get_colored_icon(
                icon_name, color, self._icon_size
            )
        else:
            self._current_icon = self._icon_mgr.get_icon(icon_name, self._icon_size)
        
        self._apply_icon(self._current_icon)

    def set_icon(self, icon_name: str) -> None:
        """
        设置按钮图标（兼容旧接口）。

        Args:
            icon_name: 图标名称（不带扩展名）
        """
        self.setIconSource(icon_name, size=self._icon_size)
        logger.debug(f"图标设置为: {icon_name}")
            
    def get_icon(self) -> str:
        """
        获取当前图标名称（兼容旧接口）。

        Returns:
            当前图标名称
        """
        return self._icon_source or ""
        
    def set_icon_size(self, size: QSize) -> None:
        """
        设置图标尺寸（兼容旧接口）。

        Args:
            size: 图标尺寸（QSize 对象）
        """
        self.setIconSize(size.width())
        logger.debug(f"图标尺寸设置为: {size.width()}x{size.height()}")
            
    def get_icon_size(self) -> QSize:
        """
        获取当前图标尺寸（兼容旧接口）。

        Returns:
            当前图标尺寸（QSize 对象）
        """
        return QSize(self._icon_size, self._icon_size)
        
    def set_icon_color_role(self, role: str) -> None:
        """
        设置图标颜色的主题角色。

        图标颜色将从主题中根据指定的角色键获取。

        Args:
            role: 主题颜色角色（如 'button.icon.normal'）
        """
        if self._icon_color_role != role:
            self._icon_color_role = role
            if self._icon_source:
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

    def get_tooltip(self) -> str:
        """
        获取当前工具提示文本。

        Returns:
            当前工具提示文本
        """
        return self.toolTip()

    def remove_tooltip(self) -> None:
        """
        移除按钮的工具提示。
        """
        from components.tooltips.tooltip_manager import remove_tooltip
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
        logger.debug("CustomPushButton 已安排删除")
