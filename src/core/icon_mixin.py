"""
图标管理混入类

提供统一的图标管理接口，让所有需要图标的组件使用相同的方式设置和管理图标。

功能特性:
- 统一的图标设置接口
- 自动主题适配（黑/白版本切换）
- 自动图标着色
- 主题切换自动更新（需组件配合）
- 支持多种图标来源

使用示例:
    class MyButton(QPushButton, IconMixin):
        def __init__(self):
            super().__init__()
            self._init_icon_mixin()
            
            # 设置图标
            self.setIconSource("Play", size=24)
            
            # 设置带颜色的图标
            self.setIconSource("Close", color=QColor(255, 0, 0))
"""

from typing import Optional, Union
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtCore import QSize

from core.icon_manager import IconManager


class IconMixin:
    """
    为组件提供统一图标管理能力的混入类。
    
    此混入类提供统一的图标设置接口，自动处理主题切换和图标着色。
    
    注意：此混入类不会独立订阅主题，组件需要在 _on_theme_changed 中
    调用 _update_icon() 来更新图标。
    
    使用方式:
        1. 在 __init__ 中调用 _init_icon_mixin()
        2. 使用 setIconSource() 设置图标
        3. 在 _on_theme_changed 中调用 _update_icon()
        4. 在 cleanup() 中调用 _cleanup_icon_mixin()
    
    属性:
        _icon_source: 当前图标来源名称
        _icon_size: 图标尺寸
        _icon_color: 图标颜色（可选）
        _icon_theme_aware: 是否主题感知
    """
    
    def _init_icon_mixin(self) -> None:
        """
        初始化图标管理系统。
        
        必须在组件的 __init__ 方法中调用此方法。
        注意：此方法不会订阅主题，组件需要自行订阅并在主题变化时调用 _update_icon()。
        """
        self._icon_mgr = IconManager.instance()
        
        self._icon_source: Optional[str] = None
        self._icon_size: int = 24
        self._icon_color: Optional[QColor] = None
        self._icon_theme_aware: bool = True
        self._current_icon: Optional[QIcon] = None
    
    def _update_icon_with_theme(self, theme) -> None:
        """
        主题变化时更新图标。
        
        组件应在 _on_theme_changed 中调用此方法。
        
        Args:
            theme: 新主题对象
        """
        if self._icon_source and self._icon_theme_aware:
            self._update_icon(theme)
    
    def _update_icon(self, theme=None) -> None:
        """
        内部方法：根据当前设置更新图标。
        
        Args:
            theme: 当前主题，如果为 None 则尝试获取
        """
        if not self._icon_source:
            return
        
        if theme is None:
            if hasattr(self, '_current_theme'):
                theme = self._current_theme
            elif hasattr(self, '_theme'):
                theme = self._theme
        
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
            default_color = theme.get_color('icon.normal', QColor(255, 255, 255))
            self._current_icon = self._icon_mgr.get_colored_icon(
                icon_name, default_color, self._icon_size
            )
        else:
            self._current_icon = self._icon_mgr.get_icon(icon_name, self._icon_size)
        
        self._apply_icon(self._current_icon)
    
    def _apply_icon(self, icon: QIcon) -> None:
        """
        应用图标到组件。子类应重写此方法。
        
        Args:
            icon: 要应用的图标
        
        默认实现:
            - 如果组件有 setIcon 方法（如 QPushButton），调用它
            - 子类可以重写此方法实现自定义行为（如直接绘制）
        """
        if hasattr(self, 'setIcon') and callable(self.setIcon):
            self.setIcon(icon)
    
    def setIconSource(
        self,
        source: str,
        size: Optional[int] = None,
        color: Optional[QColor] = None,
        theme_aware: bool = True
    ) -> None:
        """
        设置图标来源。
        
        Args:
            source: 图标名称（不含扩展名）
            size: 图标尺寸（像素），None 表示保持当前尺寸
            color: 图标颜色，None 表示使用主题默认颜色
            theme_aware: 是否根据主题自动切换图标变体
        """
        self._icon_source = source
        if size is not None:
            self._icon_size = size
        self._icon_color = color
        self._icon_theme_aware = theme_aware
        
        self._update_icon()
    
    def setIconSize(self, size: int) -> None:
        """
        设置图标尺寸。
        
        Args:
            size: 图标尺寸（像素）
        """
        if self._icon_size != size:
            self._icon_size = size
            if self._icon_source:
                self._update_icon()
    
    def setIconColor(self, color: Optional[QColor]) -> None:
        """
        设置图标颜色。
        
        Args:
            color: 图标颜色，None 表示使用主题默认颜色
        """
        self._icon_color = color
        if self._icon_source:
            self._update_icon()
    
    def setIconThemeAware(self, aware: bool) -> None:
        """
        设置是否主题感知。
        
        Args:
            aware: True 表示根据主题自动切换图标变体
        """
        self._icon_theme_aware = aware
        if self._icon_source:
            self._update_icon()
    
    def iconSource(self) -> Optional[str]:
        """
        获取当前图标来源名称。
        
        Returns:
            图标名称，如果未设置则返回 None
        """
        return self._icon_source
    
    def iconSize(self) -> int:
        """
        获取当前图标尺寸。
        
        Returns:
            图标尺寸（像素）
        """
        return self._icon_size
    
    def iconColor(self) -> Optional[QColor]:
        """
        获取当前图标颜色。
        
        Returns:
            图标颜色，如果使用主题默认颜色则返回 None
        """
        return self._icon_color
    
    def getIcon(self) -> Optional[QIcon]:
        """
        获取当前图标。
        
        Returns:
            当前图标，如果未设置则返回 None
        """
        return self._current_icon
    
    def getIconPixmap(self, size: Optional[int] = None) -> Optional[QPixmap]:
        """
        获取当前图标的像素图。
        
        Args:
            size: 像素图尺寸，None 表示使用当前图标尺寸
        
        Returns:
            图标像素图，如果未设置图标则返回 None
        """
        if not self._current_icon:
            return None
        
        size = size or self._icon_size
        return self._current_icon.pixmap(size, size)
    
    def clearIcon(self) -> None:
        """
        清除当前图标。
        """
        self._icon_source = None
        self._current_icon = None
        self._apply_icon(QIcon())
    
    def reloadIcon(self) -> None:
        """
        强制重新加载图标。
        """
        if self._icon_source:
            self._update_icon()
    
    def _cleanup_icon_mixin(self) -> None:
        """
        清理图标管理资源。
        
        应在组件的 cleanup() 方法中调用此方法。
        """
        self._current_icon = None

    def setStandardIcon(
        self,
        source: str,
        size_category: str = "medium",
        color: Optional[QColor] = None,
        theme_aware: bool = True
    ) -> None:
        """
        设置图标使用 WinUI 3 标准尺寸类别。

        WinUI 3 标准图标尺寸:
        - small: 12px - 非常小的 UI 元素
        - medium: 16px - 标准控件（按钮、菜单、工具栏）
        - large: 20px - 导航项、列表项
        - xlarge: 24px - 大图标、磁贴
        - xxlarge: 32px - 超大图标
        - xxxlarge: 48px - 英雄图标、应用图标

        Args:
            source: 图标名称（不含扩展名）
            size_category: 尺寸类别
            color: 图标颜色，None 表示使用主题默认颜色
            theme_aware: 是否根据主题自动切换图标变体

        Example:
            # 设置标准按钮图标 (16px)
            button.setStandardIcon("Play", "medium")
            
            # 设置导航图标 (20px)
            nav_item.setStandardIcon("Home", "large")
        """
        from themes.colors import WINUI3_CONTROL_SIZING
        
        sizes = WINUI3_CONTROL_SIZING.get('icon', {})
        size = sizes.get(size_category, 16)
        
        self.setIconSource(source, size, color, theme_aware)

    def setControlIcon(
        self,
        source: str,
        control_type: str = "button",
        color: Optional[QColor] = None,
        theme_aware: bool = True
    ) -> None:
        """
        设置控件图标，自动使用推荐尺寸。

        根据控件类型自动选择合适的图标尺寸:
        - button, menu, toolbar, tab: 16px
        - navigation, list: 20px
        - tile: 24px

        Args:
            source: 图标名称
            control_type: 控件类型
            color: 图标颜色
            theme_aware: 是否主题感知

        Example:
            # 设置按钮图标
            button.setControlIcon("Play", "button")
            
            # 设置导航图标
            nav_item.setControlIcon("Home", "navigation")
        """
        from core.icon_manager import IconSize
        
        size = IconSize.for_control(control_type)
        self.setIconSource(source, size, color, theme_aware)
