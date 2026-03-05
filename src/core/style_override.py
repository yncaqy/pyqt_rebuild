"""
样式覆盖混入类

提供组件本地覆盖主题值的机制，无需修改共享的 Theme 对象。

这确保了主题的不可变性，同时允许针对单个组件进行自定义。
"""

from typing import Dict, Any, Optional, Callable
from PyQt6.QtGui import QColor, QPainter, QIcon
from PyQt6.QtCore import QRect, QRectF, Qt

from core.theme_manager import Theme


class StyleOverrideMixin:
    """
    为主题化组件提供本地样式覆盖能力的混入类。
    
    此混入类允许组件自定义其外观，而无需修改共享的 Theme 对象，
    从而保持主题的不可变性。
    
    使用示例:
        class MyButton(QPushButton, StyleOverrideMixin):
            def __init__(self):
                super().__init__()
                self._init_style_override()
            
            def set_custom_radius(self, radius: int):
                self.override_style('button.border_radius', radius)
            
            def _build_stylesheet(self, theme: Theme) -> str:
                # 使用 get_style_value 获取合并后的值
                bg = self.get_style_value(theme, 'button.background.normal', QColor(60, 60, 60))
                radius = self.get_style_value(theme, 'button.border_radius', 6)
                # ...
    
    属性:
        _style_overrides: 本地样式覆盖的字典
    """
    
    def _init_style_override(self) -> None:
        """
        初始化样式覆盖系统。
        
        必须在组件的 __init__ 方法中调用此方法。
        """
        self._style_overrides: Dict[str, Any] = {}
    
    def override_style(self, key: str, value: Any) -> None:
        """
        设置本地样式覆盖。
        
        此覆盖优先于主题值，但不会修改主题本身。
        
        Args:
            key: 样式键（如 'button.border_radius'）
            value: 覆盖值
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        self._style_overrides[key] = value
    
    def remove_override(self, key: str) -> None:
        """
        移除本地样式覆盖。
        
        Args:
            key: 要移除的样式键
        """
        if hasattr(self, '_style_overrides') and key in self._style_overrides:
            del self._style_overrides[key]
    
    def clear_overrides(self) -> None:
        """
        清除所有本地样式覆盖。
        """
        if hasattr(self, '_style_overrides'):
            self._style_overrides.clear()
    
    def get_style_value(self, theme: Optional[Theme], key: str, default: Any = None) -> Any:
        """
        获取样式值，覆盖值优先。
        
        如果设置了覆盖值则返回覆盖值，否则返回主题值。
        优先级：覆盖值 > 主题值 > 默认值
        
        Args:
            theme: 要获取值的主题对象
            key: 样式键
            default: 未找到时的默认值
            
        Returns:
            样式值（覆盖值 > 主题值 > 默认值）
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        
        # 首先检查本地覆盖
        if key in self._style_overrides:
            return self._style_overrides[key]
        
        # 然后从主题获取
        if theme:
            return theme.get_value(key, default)
        
        return default
    
    def get_style_color(self, theme: Optional[Theme], key: str, default: QColor = None) -> QColor:
        """
        获取颜色值，覆盖值优先。
        
        Args:
            theme: 要获取颜色的主题对象
            key: 样式键
            default: 未找到时的默认颜色
            
        Returns:
            QColor 颜色值（覆盖值 > 主题值 > 默认值）
        """
        if not hasattr(self, '_style_overrides'):
            self._style_overrides = {}
        
        # 首先检查本地覆盖
        if key in self._style_overrides:
            value = self._style_overrides[key]
            if isinstance(value, QColor):
                return value
            elif isinstance(value, str):
                return QColor(value)
            return default if default else QColor()
        
        # 然后从主题获取
        if theme:
            return theme.get_color(key, default)
        
        return default if default else QColor()
    
    def has_override(self, key: str) -> bool:
        """
        检查是否存在指定的样式覆盖。
        
        Args:
            key: 要检查的样式键
            
        Returns:
            如果存在覆盖则返回 True
        """
        return hasattr(self, '_style_overrides') and key in self._style_overrides
    
    def get_all_overrides(self) -> Dict[str, Any]:
        """
        获取所有本地样式覆盖。
        
        Returns:
            覆盖字典的副本
        """
        if hasattr(self, '_style_overrides'):
            return self._style_overrides.copy()
        return {}
    
    def apply_overrides_to_theme(self, theme: Theme) -> Theme:
        """
        创建一个应用了所有覆盖的新主题。
        
        当需要一个包含覆盖的完整 Theme 对象时，此方法很有用。
        
        Args:
            theme: 要应用覆盖的基础主题
            
        Returns:
            应用了覆盖的新 Theme 实例
        """
        result_theme = theme
        for key, value in self._style_overrides.items():
            result_theme = result_theme.with_override(key, value)
        return result_theme

    @staticmethod
    def setup_painter_for_icon(painter: QPainter) -> None:
        """
        为图标绘制配置 QPainter 的渲染提示。

        此方法设置必要的渲染提示以消除图标锯齿，确保所有组件
        在绘制图标时获得一致的渲染效果。

        应在 paintEvent 中绘制图标之前调用此方法：
            def paintEvent(self, event):
                painter = QPainter(self)
                StyleOverrideMixin.setup_painter_for_icon(painter)
                # 或使用实例方法
                self.setup_painter_for_icon(painter)
                # ... 绘制图标

        Args:
            painter: 要配置的 QPainter 对象
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    def draw_icon(
        self,
        painter: QPainter,
        icon: QIcon,
        x: int,
        y: int,
        size: int
    ) -> None:
        """
        绘制图标并自动应用抗锯齿设置。

        此方法封装了图标绘制的最佳实践，确保图标渲染时
        自动应用正确的渲染提示，消除锯齿问题。

        使用示例：
            def paintEvent(self, event):
                painter = QPainter(self)
                # ... 其他绘制

                # 绘制图标（自动处理抗锯齿）
                self.draw_icon(painter, self._arrow_icon, x, y, 12)

        Args:
            painter: 用于绘制的 QPainter 对象
            icon: 要绘制的图标
            x: 绘制位置的 X 坐标
            y: 绘制位置的 Y 坐标
            size: 图标大小（宽度和高度相同）
        """
        if icon is None or icon.isNull():
            return

        self.setup_painter_for_icon(painter)
        icon.paint(painter, x, y, size, size)

    def draw_icon_rect(
        self,
        painter: QPainter,
        icon: QIcon,
        rect: QRect
    ) -> None:
        """
        在指定矩形区域内绘制图标并自动应用抗锯齿设置。

        此方法是 draw_icon 的变体，接受 QRect 参数，
        适用于需要将图标绘制在特定矩形区域的场景。

        使用示例：
            def paintEvent(self, event):
                painter = QPainter(self)
                icon_rect = QRect(10, 10, 24, 24)
                self.draw_icon_rect(painter, self._icon, icon_rect)

        Args:
            painter: 用于绘制的 QPainter 对象
            icon: 要绘制的图标
            rect: 图标绘制的矩形区域
        """
        if icon is None or icon.isNull():
            return

        self.setup_painter_for_icon(painter)
        icon.paint(painter, rect)
