"""
单选按钮组件

提供现代化的单选按钮，具有以下特性：
- 主题集成，自动更新样式
- 自定义圆形指示器绘制
- 支持正常、悬停、选中、禁用状态
- 优化的样式缓存机制
- 本地样式覆盖，不影响共享主题
- 使用方式与 QRadioButton 完全相同
- 自动资源清理机制
"""

import logging
from typing import Optional, Tuple
from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPaintEvent
from PyQt6.QtWidgets import QRadioButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class RadioButtonConfig:
    """单选按钮行为和样式的配置常量。"""

    DEFAULT_SIZE = 18
    DEFAULT_SPACING = 8
    INDICATOR_MARGIN = 2
    DEFAULT_INNER_RADIUS_RATIO = 0.4


class RadioButton(QRadioButton, StyleOverrideMixin, StylesheetCacheMixin):
    """
    单选按钮组件，用于在一组备选项中进行单选。

    特性：
    - 主题集成，自动响应主题切换
    - 自定义圆形指示器绘制
    - 支持正常、悬停、选中、禁用状态
    - 优化的样式缓存机制
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 使用方式与 QRadioButton 完全相同
    - 自动资源清理机制

    示例:
        radio1 = RadioButton("选项1")
        radio2 = RadioButton("选项2")
        radio1.setChecked(True)
        radio1.toggled.connect(lambda checked: print(f"选中: {checked}"))
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        """
        初始化单选按钮。

        Args:
            text: 按钮文本标签
            parent: 父组件
        """
        super().__init__(text, parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._indicator_color = QColor(52, 152, 219)
        self._indicator_disabled = QColor(176, 176, 176)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        logger.debug(f"RadioButton 初始化完成: 文本='{text}'")

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        Args:
            theme: 新的主题对象
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 RadioButton 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到单选按钮。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        if not theme:
            return

        self._current_theme = theme

        indicator_color = self.get_style_color(theme, 'radiobutton.indicator', QColor(52, 152, 219))
        indicator_disabled = self.get_style_color(theme, 'radiobutton.indicator.disabled', QColor(176, 176, 176))

        text_color = self.get_style_color(theme, 'radiobutton.text.normal', QColor(50, 50, 50))
        text_disabled = self.get_style_color(theme, 'radiobutton.text.disabled', QColor(150, 150, 150))

        self._indicator_color = indicator_color
        self._indicator_disabled = indicator_disabled

        size = self.get_style_value(theme, 'radiobutton.size', RadioButtonConfig.DEFAULT_SIZE)

        indicator_width = size + 8

        cache_key = (
            text_color.name(),
            text_disabled.name(),
            indicator_width
        )

        qss = self._get_cached_stylesheet(
            cache_key,
            lambda: self._build_stylesheet(theme, text_color, text_disabled, indicator_width)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        self.update()

    def _build_stylesheet(self, theme: Theme, text_color: QColor, text_disabled: QColor, indicator_width: int) -> str:
        """构建样式表。"""
        return f"""
        RadioButton {{
            spacing: 8px;
            padding-left: {indicator_width}px;
            color: {text_color.name()};
            background: transparent;
            border: none;
            outline: none;
        }}
        RadioButton::indicator {{
            width: 0px;
            height: 0px;
            subcontrol-position: left center;
        }}
        RadioButton:hover {{
            color: {text_color.name()};
            background: transparent;
        }}
        RadioButton:disabled {{
            color: {text_disabled.name()};
            background: transparent;
        }}
        RadioButton:focus {{
            outline: none;
            background: transparent;
        }}
        """

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        重写绘制事件，绘制自定义圆形指示器。

        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        size = self.get_style_value(theme, 'radiobutton.size', RadioButtonConfig.DEFAULT_SIZE)

        indicator_rect = self._get_indicator_rect(size)

        is_checked = self.isChecked()
        is_enabled = self.isEnabled()
        is_hover = self.underMouse() and is_enabled

        if is_enabled:
            bg_color = self.get_style_color(theme, 'radiobutton.background.hover' if is_hover else 'radiobutton.background.normal',
                                            QColor(Qt.GlobalColor.transparent))

            if is_checked:
                border_color = self.get_style_color(theme, 'radiobutton.border.checked', QColor(52, 152, 219))
            elif is_hover:
                border_color = self.get_style_color(theme, 'radiobutton.border.focus', QColor(52, 152, 219))
            else:
                border_color = self.get_style_color(theme, 'radiobutton.border.normal', QColor(176, 176, 176))

            indicator_color = self._indicator_color
            text_color = self.get_style_color(theme, 'radiobutton.text.normal', QColor(50, 50, 50))
        else:
            bg_color = self.get_style_color(theme, 'radiobutton.background.disabled', QColor(Qt.GlobalColor.transparent))
            border_color = self.get_style_color(theme, 'radiobutton.border.disabled', QColor(224, 224, 224))
            indicator_color = self._indicator_disabled
            text_color = self.get_style_color(theme, 'radiobutton.text.disabled', QColor(150, 150, 150))

        if bg_color.alpha() > 0:
            painter.setBrush(QBrush(bg_color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(indicator_rect)

        if is_checked:
            inner_radius = size * RadioButtonConfig.DEFAULT_INNER_RADIUS_RATIO
            inner_rect = QRectF(
                indicator_rect.center().x() - inner_radius,
                indicator_rect.center().y() - inner_radius,
                inner_radius * 2,
                inner_radius * 2
            )
            painter.setBrush(QBrush(indicator_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(inner_rect)

        text = self.text()
        if text:
            painter.setPen(QPen(text_color))
            text_x = indicator_rect.right() + 8
            text_y = (self.height() + painter.fontMetrics().height()) // 2 - painter.fontMetrics().descent()
            painter.drawText(int(text_x), int(text_y), text)

    def _get_indicator_rect(self, size: int) -> QRectF:
        """
        获取指示器的矩形区域。

        Args:
            size: 指示器尺寸

        Returns:
            指示器区域的 QRectF
        """
        y_offset = (self.height() - size) // 2

        return QRectF(
            RadioButtonConfig.INDICATOR_MARGIN,
            y_offset,
            size,
            size
        )

    def sizeHint(self) -> QSize:
        """
        返回按钮的建议尺寸。

        Returns:
            建议尺寸
        """
        theme = self._current_theme
        size = self.get_style_value(theme, 'radiobutton.size', RadioButtonConfig.DEFAULT_SIZE) if theme else RadioButtonConfig.DEFAULT_SIZE

        text_width = self.fontMetrics().boundingRect(self.text()).width()
        indicator_width = size + 8
        spacing = 8

        return QSize(
            indicator_width + spacing + text_width + RadioButtonConfig.INDICATOR_MARGIN * 2,
            max(size, self.fontMetrics().height()) + RadioButtonConfig.INDICATOR_MARGIN * 2
        )

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
            logger.debug("RadioButton 已取消主题订阅")

        self._clear_stylesheet_cache()
        self.clear_overrides()
