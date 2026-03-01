"""
自定义按钮组件

提供现代化的主题按钮，具有以下特性：
- 主题集成，自动更新样式
- 支持正常、悬停、按下、禁用四种状态
- 可自定义圆角和内边距
- 优化的样式缓存机制，提升性能
- 支持本地样式覆盖，无需修改共享主题
"""

import logging
import time
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin

logger = logging.getLogger(__name__)


class ButtonConfig:
    """
    按钮行为和样式的配置常量。
    
    Attributes:
        DEFAULT_HORIZONTAL_POLICY: 默认水平尺寸策略
        DEFAULT_VERTICAL_POLICY: 默认垂直尺寸策略
        DEFAULT_BORDER_RADIUS: 默认边框圆角（像素）
        DEFAULT_PADDING: 默认内边距
        MAX_STYLESHEET_CACHE_SIZE: 样式缓存最大数量
    """

    # 水平尺寸策略：Minimum 表示按钮宽度根据内容自动调整，不会主动扩展填充可用空间
    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    
    # 垂直尺寸策略：Fixed 表示按钮高度固定，不会随布局自动调整
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed

    # 默认边框圆角半径（单位：像素），用于按钮的圆角效果
    DEFAULT_BORDER_RADIUS = 6
    
    # 默认内边距（格式：'上下 左右'），控制按钮文本与边框之间的间距
    DEFAULT_PADDING = '8px 16px'

    # 样式表缓存最大数量，防止内存泄漏，超过此数量后不再缓存新样式
    MAX_STYLESHEET_CACHE_SIZE = 100


class CustomPushButton(QPushButton, StyleOverrideMixin):
    """
    主题化按钮组件，支持现代样式和自动主题更新。

    特性：
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、按下、禁用四种状态
    - 可自定义圆角和内边距
    - 优化的样式缓存机制，避免重复计算
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题

    示例:
        button = CustomPushButton("点击我")
        button.set_theme('dark')
        button.clicked.connect(lambda: print("已点击!"))
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
        
        # 初始化样式覆盖系统
        self._init_style_override()

        # 设置尺寸策略：水平方向根据内容自动调整，垂直方向固定
        self.setSizePolicy(
            ButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            ButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        # 初始化管理器和状态
        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        # 图标相关属性
        self._icon_name = icon_name
        self._icon_size = QSize(16, 16)
        self._icon_color_role = 'button.icon.normal'

        # 样式缓存：避免重复计算相同的样式表
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # 订阅主题变化通知
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        # 应用初始主题
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
        else:
            # 如果没有当前主题，仅更新图标
            if icon_name:
                self._update_icon()

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
            self._update_icon()
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

        # 创建优化的缓存键：包含所有影响样式的因素
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

        # 检查缓存：如果已缓存则直接使用，避免重复构建样式表
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            # 构建新的样式表
            qss = self._build_stylesheet(theme)

            # 缓存样式表（有数量限制，防止内存泄漏）
            if len(self._stylesheet_cache) < ButtonConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss

        # 智能刷新：仅当样式表实际变化时才更新
        current_stylesheet = self.styleSheet()
        if current_stylesheet != qss:
            self.setStyleSheet(qss)
            # 强制刷新样式，确保 Qt 重新应用
            self.style().unpolish(self)
            self.style().polish(self)
            logger.debug("样式表已更新并刷新")
        else:
            logger.debug("样式表未变化，跳过刷新")

        elapsed_time = time.time() - start_time
        logger.info(f"主题已应用: {getattr(theme, 'name', 'unnamed')} (缓存大小: {len(self._stylesheet_cache)}, 耗时 {elapsed_time:.3f}s)")

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
        if self._icon_name:
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

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        应在组件销毁前调用。
        """
        # 取消主题订阅
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("CustomPushButton 已取消主题订阅")

        # 清空样式缓存
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("样式缓存已清空")
        
        # 清空样式覆盖
        self.clear_overrides()

    def _update_icon(self) -> None:
        """
        更新按钮图标。

        根据当前设置从图标管理器获取图标并应用到按钮。
        支持主题感知的图标颜色。
        """
        if not self._icon_name:
            # 没有图标名称时清空图标
            self.setIcon(QIcon())
            # 重置样式表以移除图标相关的内边距
            if self._current_theme:
                qss = self._build_stylesheet(self._current_theme)
                self.setStyleSheet(qss)
            return
        
        # 从图标管理器获取图标
        icon_size = self._icon_size.width()
        if self._current_theme:
            # 从主题获取图标颜色
            color = self._current_theme.get_color(self._icon_color_role, QColor(50, 50, 50))
            icon = self._icon_mgr.get_colored_icon(self._icon_name, color, icon_size)
        else:
            # 使用默认图标（无颜色覆盖）
            icon = self._icon_mgr.get_icon(self._icon_name, icon_size)
        
        # 应用图标到按钮
        self.setIcon(icon)
        self.setIconSize(self._icon_size)
        
        logger.debug(f"图标尺寸设置为: {icon_size}x{icon_size}")
        
        # 在图标和文本之间添加间距
        if self.text():
            # 移除现有的前导空格
            original_text = self.text().lstrip()
            # 在文本前添加一个空格，创建图标后的间距
            self.setText(f" {original_text}")
        
        # 设置基础样式表
        if self._current_theme:
            base_qss = self._build_stylesheet(self._current_theme)
            self.setStyleSheet(base_qss)
        
        logger.debug(f"图标已更新: {self._icon_name}, 尺寸: {self._icon_size.width()}x{self._icon_size.height()}")
    
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

        图标颜色将从主题中根据指定的角色键获取。

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
