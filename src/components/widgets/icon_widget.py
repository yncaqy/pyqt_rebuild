"""
图标控件组件

可复用的图标显示控件，具有以下特性：
- 多种图标来源（SVG、PNG、字体图标、原始 SVG 字符串）
- 统一的尺寸控制，支持标准尺寸
- 自定义颜色和样式支持
- 延迟加载，优化性能
- 错误处理，提供备用图标
- 主题集成

功能特性:
- 任意分辨率下的高质量渲染
- 平滑缩放，支持抗锯齿
- 悬停和点击效果
- 无障碍设计
- 内存高效，支持缓存

参考: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
"""

import logging
from typing import Optional, Union
from enum import Enum
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QEvent
from PyQt6.QtGui import QPainter, QColor, QPixmap, QIcon, QEnterEvent, QMouseEvent

from src.core.theme_manager import ThemeManager, Theme
from src.core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class IconSize(Enum):
    """标准图标尺寸，确保应用程序中的一致性。"""
    TINY = 12
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    XLARGE = 32
    XXLARGE = 48
    HUGE = 64


class IconSource:
    """图标来源配置。"""

    def __init__(
        self,
        name: Optional[str] = None,
        svg_content: Optional[str] = None,
        icon: Optional[QIcon] = None,
        pixmap: Optional[QPixmap] = None
    ):
        self.name = name
        self.svg_content = svg_content
        self.icon = icon
        self.pixmap = pixmap

    @classmethod
    def from_name(cls, name: str) -> 'IconSource':
        """从图标名称创建图标来源。"""
        return cls(name=name)

    @classmethod
    def from_svg(cls, svg_content: str) -> 'IconSource':
        """从 SVG 内容字符串创建图标来源。"""
        return cls(svg_content=svg_content)

    @classmethod
    def from_icon(cls, icon: QIcon) -> 'IconSource':
        """从 QIcon 创建图标来源。"""
        return cls(icon=icon)

    @classmethod
    def from_pixmap(cls, pixmap: QPixmap) -> 'IconSource':
        """从 QPixmap 创建图标来源。"""
        return cls(pixmap=pixmap)


class IconWidgetConfig:
    """IconWidget 配置常量。"""

    DEFAULT_SIZE = IconSize.MEDIUM.value
    DEFAULT_BORDER_RADIUS = 4
    PRESSED_SCALE = 0.9
    ANIMATION_DURATION = 100
    LAZY_LOAD_DELAY = 100


class IconWidget(QWidget):
    """
    可复用的图标显示控件，功能全面。

    功能特性:
    - 多种图标来源（SVG、PNG、字体图标、原始 SVG 字符串）
    - 统一的尺寸控制，支持标准尺寸
    - 自定义颜色和样式支持
    - 延迟加载，优化性能
    - 错误处理，提供备用图标
    - 主题集成
    - 悬停和点击效果

    信号:
        clicked: 点击图标时发出
        doubleClicked: 双击图标时发出

    使用示例:
        # 从图标名称创建
        icon_widget = IconWidget("Play_white", size=IconSize.LARGE)

        # 使用自定义颜色
        icon_widget = IconWidget("Play_white", color=QColor(255, 0, 0))

        # 从 SVG 内容创建
        svg = '<svg viewBox="0 0 24 24">...</svg>'
        icon_widget = IconWidget.from_svg(svg, size=IconSize.MEDIUM)

        # 从 QIcon 创建
        icon = QIcon("path/to/icon.png")
        icon_widget = IconWidget.from_icon(icon)
    """

    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def __init__(
        self,
        source: Optional[Union[str, IconSource]] = None,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None,
        *,
        clickable: bool = False,
        hover_effect: bool = False,
        lazy_load: bool = False,
        theme_aware: bool = True
    ):
        """
        初始化 IconWidget。

        Args:
            source: 图标来源（名称、IconSource 或 None 用于延迟加载）
            size: 图标尺寸（int 或 IconSize 枚举）
            color: 可选的颜色应用到图标
            parent: 父控件
            clickable: 图标是否响应点击
            hover_effect: 是否显示悬停动画
            lazy_load: 是否延迟加载图标
            theme_aware: 是否根据主题自动切换图标变体
        """
        super().__init__(parent)

        self._icon_mgr = IconManager.instance()
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._size = size.value if isinstance(size, IconSize) else size
        self._color = color
        self._source: Optional[IconSource] = None
        self._base_icon_name: Optional[str] = None
        self._pixmap: Optional[QPixmap] = None
        self._fallback_pixmap: Optional[QPixmap] = None
        self._is_loaded = False
        self._load_error = False

        self._clickable = clickable
        self._hover_effect = hover_effect
        self._lazy_load = lazy_load
        self._theme_aware = theme_aware

        self._is_hovered = False
        self._is_pressed = False
        self._scale = 1.0
        self._opacity = 1.0

        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        if source is not None:
            if isinstance(source, str):
                self._source = IconSource.from_name(source)
            else:
                self._source = source

            if lazy_load:
                QTimer.singleShot(IconWidgetConfig.LAZY_LOAD_DELAY, self._load_icon)
            else:
                self._load_icon()

    def _setup_ui(self) -> None:
        """初始化 UI 属性。"""
        self._base_size = self._size
        self._max_display_size = self._size
        self.setMinimumSize(self._max_display_size, self._max_display_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        if self._clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _on_theme_changed(self, theme: Theme) -> None:
        """处理主题变化。"""
        self._current_theme = theme
        if self._source and self._source.name:
            self._load_icon()
        self.update()

    def _load_icon(self) -> None:
        """从来源加载图标。"""
        if self._source is None:
            return

        try:
            self._load_error = False

            if self._source.pixmap:
                self._pixmap = self._source.pixmap
            elif self._source.icon:
                self._pixmap = self._source.icon.pixmap(self._size, self._size)
            elif self._source.svg_content:
                self._pixmap = self._icon_mgr.create_pixmap_from_svg(
                    self._source.svg_content, self._size
                )
            elif self._source.name:
                icon_name = self._source.name

                if self._theme_aware and self._current_theme:
                    theme_type = 'dark' if self._current_theme.is_dark else 'light'
                    resolved_name = self._icon_mgr.resolve_icon_name(icon_name, theme_type)
                    if resolved_name != icon_name:
                        icon_name = resolved_name

                is_colored = self._icon_mgr.is_colored_icon(icon_name)
                color = self._color

                if color is None and self._current_theme and not is_colored:
                    color = self._get_theme_color()

                if color and not is_colored:
                    icon = self._icon_mgr.get_colored_icon(
                        icon_name, color, self._size
                    )
                else:
                    icon = self._icon_mgr.get_icon(icon_name, self._size)

                self._pixmap = icon.pixmap(self._size, self._size)

            self._is_loaded = True
            self.update()

        except Exception as e:
            logger.error(f"Error loading icon: {e}")
            self._load_error = True
            self._pixmap = self._get_fallback_pixmap()
            self.update()

    def _get_theme_color(self) -> Optional[QColor]:
        """从当前主题获取图标颜色。"""
        if self._current_theme:
            return self._current_theme.get_color('icon.normal', QColor(255, 255, 255))
        return None

    def _get_fallback_pixmap(self) -> QPixmap:
        """获取错误情况下的备用像素图。"""
        if self._fallback_pixmap is None:
            self._fallback_pixmap = QPixmap(self._size, self._size)
            self._fallback_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(self._fallback_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(128, 128, 128))
            painter.drawEllipse(0, 0, self._size, self._size)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(0, 0, self._size, self._size,
                           Qt.AlignmentFlag.AlignCenter, "?")
            painter.end()

        return self._fallback_pixmap

    def get_scale(self) -> float:
        """获取缩放值。"""
        return self._scale

    def set_scale(self, value: float) -> None:
        """设置缩放值。"""
        self._scale = value
        self.update()

    scale = pyqtProperty(float, get_scale, set_scale)

    def get_opacity(self) -> float:
        """获取透明度。"""
        return self._opacity

    def set_opacity(self, value: float) -> None:
        """设置透明度。"""
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def _animate_press(self) -> None:
        """按下动画效果 - 缩小。"""
        if not self._hover_effect:
            return

        self._press_anim = QPropertyAnimation(self, b"scale")
        self._press_anim.setDuration(IconWidgetConfig.ANIMATION_DURATION)
        self._press_anim.setStartValue(self._scale)
        self._press_anim.setEndValue(IconWidgetConfig.PRESSED_SCALE)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._press_anim.start()

    def _animate_release(self) -> None:
        """释放动画效果 - 恢复正常大小。"""
        if not self._hover_effect:
            return

        self._release_anim = QPropertyAnimation(self, b"scale")
        self._release_anim.setDuration(IconWidgetConfig.ANIMATION_DURATION)
        self._release_anim.setStartValue(self._scale)
        self._release_anim.setEndValue(1.0)
        self._release_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._release_anim.start()

    def enterEvent(self, event: QEnterEvent) -> None:
        """鼠标进入事件。"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """鼠标离开事件。"""
        self._is_hovered = False
        self._is_pressed = False
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件。"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._animate_press()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放事件。"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self._animate_release()

            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """鼠标双击事件。"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event) -> None:
        """绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)

        pixmap = self._pixmap if self._pixmap else self._get_fallback_pixmap()

        widget_size = min(self.width(), self.height())
        icon_display_size = int(self._base_size * self._scale)
        x_offset = (self.width() - icon_display_size) // 2
        y_offset = (self.height() - icon_display_size) // 2

        if self._scale != 1.0:
            scaled_pixmap = pixmap.scaled(
                icon_display_size, icon_display_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            painter.drawPixmap(x_offset, y_offset, pixmap)

    def sizeHint(self) -> QSize:
        """返回建议尺寸。"""
        return QSize(self._max_display_size, self._max_display_size)

    def minimumSizeHint(self) -> QSize:
        """返回最小建议尺寸。"""
        return QSize(self._max_display_size, self._max_display_size)

    def setSource(self, source: Union[str, IconSource]) -> None:
        """
        设置图标来源。

        Args:
            source: 图标名称字符串或 IconSource 对象
        """
        if isinstance(source, str):
            self._source = IconSource.from_name(source)
        else:
            self._source = source

        self._is_loaded = False
        self._load_icon()

    def source(self) -> Optional[IconSource]:
        """获取当前图标来源。"""
        return self._source

    def setSize(self, size: Union[int, IconSize]) -> None:
        """
        设置图标尺寸。

        Args:
            size: 图标尺寸（int 或 IconSize 枚举）
        """
        new_size = size.value if isinstance(size, IconSize) else size
        if self._base_size != new_size:
            self._base_size = new_size
            self._size = new_size
            self._max_display_size = new_size
            self.setFixedSize(self._max_display_size, self._max_display_size)
            self._fallback_pixmap = None

            if self._source and self._is_loaded:
                self._load_icon()

    def size(self) -> int:
        """获取当前图标尺寸。"""
        return self._size

    def setColor(self, color: Optional[QColor]) -> None:
        """
        设置图标颜色。

        Args:
            color: 要应用的颜色，或 None 使用主题默认值
        """
        if self._color != color:
            self._color = color
            if self._source:
                self._load_icon()

    def color(self) -> Optional[QColor]:
        """获取当前图标颜色。"""
        return self._color

    def setClickable(self, clickable: bool) -> None:
        """
        设置图标是否响应点击。

        Args:
            clickable: True 启用点击响应
        """
        self._clickable = clickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable
            else Qt.CursorShape.ArrowCursor
        )

    def isClickable(self) -> bool:
        """检查图标是否可点击。"""
        return self._clickable

    def setHoverEffect(self, enabled: bool) -> None:
        """
        启用或禁用悬停动画效果。

        Args:
            enabled: True 启用悬停效果
        """
        self._hover_effect = enabled

    def hasHoverEffect(self) -> bool:
        """检查悬停效果是否启用。"""
        return self._hover_effect

    def isLoaded(self) -> bool:
        """检查图标是否已加载。"""
        return self._is_loaded

    def hasError(self) -> bool:
        """检查图标加载是否失败。"""
        return self._load_error

    def reload(self) -> None:
        """强制重新加载图标。"""
        self._is_loaded = False
        self._load_error = False
        self._load_icon()

    def clear(self) -> None:
        """清除图标。"""
        self._source = None
        self._pixmap = None
        self._is_loaded = False
        self._load_error = False
        self.update()

    @classmethod
    def from_name(
        cls,
        name: str,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        从图标名称创建 IconWidget。

        Args:
            name: 图标名称（不含扩展名）
            size: 图标尺寸
            color: 可选颜色
            parent: 父控件

        Returns:
            IconWidget 实例
        """
        return cls(IconSource.from_name(name), size, color, parent)

    @classmethod
    def from_svg(
        cls,
        svg_content: str,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        从 SVG 内容字符串创建 IconWidget。

        Args:
            svg_content: SVG 内容字符串
            size: 图标尺寸
            color: 可选颜色
            parent: 父控件

        Returns:
            IconWidget 实例
        """
        return cls(IconSource.from_svg(svg_content), size, color, parent)

    @classmethod
    def from_icon(
        cls,
        icon: QIcon,
        size: Union[int, IconSize] = IconSize.MEDIUM,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        从 QIcon 创建 IconWidget。

        Args:
            icon: QIcon 实例
            size: 图标尺寸
            parent: 父控件

        Returns:
            IconWidget 实例
        """
        return cls(IconSource.from_icon(icon), size, None, parent)

    @classmethod
    def from_pixmap(
        cls,
        pixmap: QPixmap,
        parent: Optional[QWidget] = None
    ) -> 'IconWidget':
        """
        从 QPixmap 创建 IconWidget。

        Args:
            pixmap: QPixmap 实例
            parent: 父控件

        Returns:
            IconWidget 实例
        """
        size = pixmap.width()
        return cls(IconSource.from_pixmap(pixmap), size, None, parent)

    def cleanup(self) -> None:
        """清理资源。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        self._pixmap = None
        self._fallback_pixmap = None
