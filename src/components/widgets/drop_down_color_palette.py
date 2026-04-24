"""
下拉颜色面板组件

提供现代 Fluent Design 风格的下拉颜色选择器，具有以下特性：
- 点击按钮显示颜色面板
- 预设颜色网格布局
- 当前选中颜色视觉指示
- 平滑的下拉/收起动画
- 主题集成
- 颜色选择信号
- 自动资源清理

使用方式:
    palette = DropDownColorPalette()
    palette.setCurrentColor(QColor(255, 0, 0))
    palette.colorChanged.connect(lambda c: print(f"选中颜色: {c.name()}"))
"""

import logging
from typing import Optional, List, Tuple
from PyQt6.QtCore import (
    Qt, QSize, QPoint, QRect, QRectF, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QEvent, pyqtProperty
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QIcon,
    QPaintEvent, QMouseEvent
)
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QGridLayout,
    QSizePolicy, QGraphicsOpacityEffect, QApplication
)

from src.core.theme_manager import ThemeManager, Theme
from src.core.icon_manager import IconManager
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class ColorPaletteConfig:
    """下拉颜色面板配置常量，遵循 WinUI3 设计规范。"""

    DEFAULT_BUTTON_WIDTH = 100
    DEFAULT_BUTTON_HEIGHT = 28
    DEFAULT_BUTTON_BORDER_RADIUS = 4
    COLOR_ITEM_SIZE = 20
    COLOR_ITEM_SPACING = 4
    COLOR_ITEM_BORDER_RADIUS = 4
    PANEL_BORDER_RADIUS = 8
    PANEL_PADDING = 8
    PANEL_MARGIN = 4
    COLUMNS = 8
    ANIMATION_DURATION = 150

    DEFAULT_COLORS = [
        "#E81123", "#FF8C00", "#FFF100", "#107C10",
        "#00BCF2", "#0078D4", "#5C2D91", "#C30052",
        "#D13438", "#FFB900", "#00CC6A", "#00B7C3",
        "#8764B8", "#E74856", "#FF6B6B", "#4ECDC4",
        "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD",
        "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
        "#FFFFFF", "#C0C0C0", "#808080", "#404040",
        "#000000", "#800000", "#008000", "#000080",
    ]

    DEFAULT_COLOR = '#5dade2'


class ColorItemWidget(QWidget):
    """
    单个颜色项控件。

    功能特性:
    - 颜色显示
    - 悬停效果
    - 选中指示
    """

    clicked = pyqtSignal(QColor)

    def __init__(
        self,
        color: QColor,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._color = color
        self._is_hovered = False
        self._is_selected = False
        self._hover_opacity = 0.0
        self._hover_animation: Optional[QPropertyAnimation] = None
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setFixedSize(
            ColorPaletteConfig.COLOR_ITEM_SIZE,
            ColorPaletteConfig.COLOR_ITEM_SIZE
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._current_theme = theme
        self.update()

    def color(self) -> QColor:
        return QColor(self._color)

    def setColor(self, color: QColor) -> None:
        self._color = color
        self.update()

    def isSelected(self) -> bool:
        return self._is_selected

    def setSelected(self, selected: bool) -> None:
        if self._is_selected != selected:
            self._is_selected = selected
            self.update()

    def enterEvent(self, event: QEvent) -> None:
        self._is_hovered = True
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._is_hovered = False
        self._animate_hover(False)
        super().leaveEvent(event)

    def _animate_hover(self, hover: bool) -> None:
        if self._hover_animation:
            self._hover_animation.stop()

        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(ColorPaletteConfig.ANIMATION_DURATION)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0 if hover else 0.0)
        self._hover_animation.start()

    def getHoverOpacity(self) -> float:
        return self._hover_opacity

    def setHoverOpacity(self, opacity: float) -> None:
        self._hover_opacity = opacity
        self.update()

    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._color)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        radius = ColorPaletteConfig.COLOR_ITEM_BORDER_RADIUS

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._color))
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        if self._is_selected:
            if self._current_theme:
                accent_color = self._current_theme.get_color('accent.primary', QColor(89, 89, 89))
            else:
                accent_color = QColor(89, 89, 89)
            pen = QPen(accent_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(rect).adjusted(1, 1, -1, -1), radius, radius)

        if self._is_hovered and not self._is_selected:
            hover_color = QColor(255, 255, 255, int(40 * self._hover_opacity))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(hover_color))
            painter.drawRoundedRect(QRectF(rect), radius, radius)

    def cleanup(self) -> None:
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.deleteLater()
            self._hover_animation = None
        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class ColorPalettePanel(QWidget):
    """
    颜色选择面板。

    功能特性:
    - 预设颜色网格布局
    - 当前选中颜色指示
    - 平滑动画
    """

    colorClicked = pyqtSignal(QColor)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        colors: Optional[List[str]] = None
    ):
        super().__init__(parent)

        self._colors = colors if colors else ColorPaletteConfig.DEFAULT_COLORS
        self._color_items: List[ColorItemWidget] = []
        self._current_color: Optional[QColor] = None
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None
        self._show_animation: Optional[QPropertyAnimation] = None
        self._hide_animation: Optional[QPropertyAnimation] = None

        self.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(
            ColorPaletteConfig.PANEL_PADDING,
            ColorPaletteConfig.PANEL_PADDING,
            ColorPaletteConfig.PANEL_PADDING,
            ColorPaletteConfig.PANEL_PADDING
        )

        self._container = QWidget()
        self._container.setObjectName("colorPaletteContainer")

        self._grid_layout = QGridLayout(self._container)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(ColorPaletteConfig.COLOR_ITEM_SPACING)

        self._setup_color_items()

        self._main_layout.addWidget(self._container)

        self._adjust_size()

    def _setup_color_items(self) -> None:
        for i, color_str in enumerate(self._colors):
            color = QColor(color_str)
            item = ColorItemWidget(color, self)
            item.clicked.connect(self._on_color_clicked)
            row = i // ColorPaletteConfig.COLUMNS
            col = i % ColorPaletteConfig.COLUMNS
            self._grid_layout.addWidget(item, row, col)
            self._color_items.append(item)

    def _adjust_size(self) -> None:
        total_items = len(self._colors)
        rows = (total_items + ColorPaletteConfig.COLUMNS - 1) // ColorPaletteConfig.COLUMNS

        item_total_size = ColorPaletteConfig.COLOR_ITEM_SIZE + ColorPaletteConfig.COLOR_ITEM_SPACING
        width = ColorPaletteConfig.COLUMNS * item_total_size - ColorPaletteConfig.COLOR_ITEM_SPACING
        width += ColorPaletteConfig.PANEL_PADDING * 2

        height = rows * item_total_size - ColorPaletteConfig.COLOR_ITEM_SPACING
        height += ColorPaletteConfig.PANEL_PADDING * 2

        self.setFixedSize(width, height)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        bg_color = theme.get_color('menu.background', QColor(45, 45, 45))
        border_color = theme.get_color('menu.border', QColor(60, 60, 60))
        border_radius = ColorPaletteConfig.PANEL_BORDER_RADIUS

        bg_hex = bg_color.name(QColor.NameFormat.HexArgb)
        border_hex = border_color.name(QColor.NameFormat.HexArgb)

        self._container.setStyleSheet(f"""
            #colorPaletteContainer {{
                background-color: {bg_hex};
                border: 1px solid {border_hex};
                border-radius: {border_radius}px;
            }}
        """)

    def _on_color_clicked(self, color: QColor) -> None:
        self.setCurrentColor(color)
        self.colorClicked.emit(color)

    def setCurrentColor(self, color: QColor) -> None:
        self._current_color = color
        for item in self._color_items:
            item.setSelected(item.color() == color)

    def currentColor(self) -> Optional[QColor]:
        return QColor(self._current_color) if self._current_color else None

    def show_panel(self, pos: QPoint) -> None:
        self.move(pos)
        self.show()
        self._animate_show()

    def hide_panel(self) -> None:
        self._animate_hide()

    def _animate_show(self) -> None:
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        self._show_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._show_animation.setDuration(ColorPaletteConfig.ANIMATION_DURATION)
        self._show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._show_animation.setStartValue(0.0)
        self._show_animation.setEndValue(1.0)
        self._show_animation.start()

    def _animate_hide(self) -> None:
        if self._opacity_effect:
            self._hide_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
            self._hide_animation.setDuration(ColorPaletteConfig.ANIMATION_DURATION)
            self._hide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._hide_animation.setStartValue(1.0)
            self._hide_animation.setEndValue(0.0)
            self._hide_animation.finished.connect(self.hide)
            self._hide_animation.start()
        else:
            self.hide()

    def setColors(self, colors: List[str]) -> None:
        for item in self._color_items:
            item.deleteLater()
        self._color_items.clear()

        self._colors = colors
        self._setup_color_items()
        self._adjust_size()

        if self._current_color:
            self.setCurrentColor(self._current_color)

    def cleanup(self) -> None:
        if self._show_animation:
            self._show_animation.stop()
            self._show_animation.deleteLater()
            self._show_animation = None

        if self._hide_animation:
            self._hide_animation.stop()
            self._hide_animation.deleteLater()
            self._hide_animation = None

        for item in self._color_items:
            item.cleanup()
            item.deleteLater()
        self._color_items.clear()

        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class DropDownColorPalette(QPushButton, StyleOverrideMixin, StylesheetCacheMixin):
    """
    下拉颜色面板组件。

    功能特性:
    - 点击按钮显示颜色面板
    - 预设颜色网格布局
    - 当前选中颜色视觉指示
    - 平滑的下拉/收起动画
    - 主题集成
    - 颜色选择信号
    - 自动资源清理

    信号:
        colorChanged: 颜色改变时发出
        currentColorChanged: 当前颜色改变时发出
    """

    colorChanged = pyqtSignal(QColor)
    currentColorChanged = pyqtSignal(QColor)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        colors: Optional[List[str]] = None
    ):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
        self.setFixedHeight(ColorPaletteConfig.DEFAULT_BUTTON_HEIGHT)
        self.setMinimumWidth(ColorPaletteConfig.DEFAULT_BUTTON_WIDTH)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._colors = colors if colors else ColorPaletteConfig.DEFAULT_COLORS
        self._current_color: QColor = QColor(ColorPaletteConfig.DEFAULT_COLOR)
        self._panel: Optional[ColorPalettePanel] = None
        self._arrow_icon: Optional[QIcon] = None
        self._is_panel_visible = False

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug("DropDownColorPalette 初始化完成")

    def sizeHint(self) -> QSize:
        return QSize(ColorPaletteConfig.DEFAULT_BUTTON_WIDTH, ColorPaletteConfig.DEFAULT_BUTTON_HEIGHT)

    def _on_clicked(self) -> None:
        if self._is_panel_visible:
            self._hide_panel()
        else:
            self._show_panel()

    def _show_panel(self) -> None:
        if not self._panel:
            self._panel = ColorPalettePanel(self, self._colors)
            self._panel.colorClicked.connect(self._on_color_selected)

        if self._current_color:
            self._panel.setCurrentColor(self._current_color)

        panel_size = self._panel.size()
        screen = QApplication.screenAt(self.mapToGlobal(QPoint(0, 0)))
        if not screen:
            screen = QApplication.primaryScreen()

        screen_rect = screen.availableGeometry()
        button_global_pos = self.mapToGlobal(QPoint(0, 0))

        below_y = button_global_pos.y() + self.height() + ColorPaletteConfig.PANEL_MARGIN

        if below_y + panel_size.height() <= screen_rect.bottom():
            global_pos = self.mapToGlobal(QPoint(0, self.height() + ColorPaletteConfig.PANEL_MARGIN))
        else:
            global_pos = self.mapToGlobal(QPoint(0, -panel_size.height() - ColorPaletteConfig.PANEL_MARGIN))

        if global_pos.x() + panel_size.width() > screen_rect.right():
            global_pos.setX(screen_rect.right() - panel_size.width() - 5)
        if global_pos.x() < screen_rect.left():
            global_pos.setX(screen_rect.left() + 5)

        self._panel.show_panel(global_pos)
        self._is_panel_visible = True

    def _hide_panel(self) -> None:
        if self._panel:
            self._panel.hide_panel()
        self._is_panel_visible = False

    def _on_color_selected(self, color: QColor) -> None:
        self.setCurrentColor(color)
        self._hide_panel()

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 DropDownColorPalette 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')

        qss = self._get_cached_stylesheet(
            (theme_name,),
            lambda: self._build_stylesheet(theme)
        )

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        self._update_arrow_icon()

        logger.debug(f"主题已应用: {theme_name}")

    def _build_stylesheet(self, theme: Theme) -> str:
        is_dark = getattr(theme, 'is_dark', True)

        bg_normal = self.get_style_color(theme, 'colorpalette.background.normal',
                                         QColor(255, 255, 255, 9) if is_dark else QColor(0, 0, 0, 6))
        bg_hover = self.get_style_color(theme, 'colorpalette.background.hover',
                                        QColor(255, 255, 255, 15) if is_dark else QColor(0, 0, 0, 12))
        bg_pressed = self.get_style_color(theme, 'colorpalette.background.pressed',
                                          QColor(255, 255, 255, 20) if is_dark else QColor(0, 0, 0, 18))
        bg_disabled = self.get_style_color(theme, 'colorpalette.background.disabled',
                                           QColor(255, 255, 255, 4) if is_dark else QColor(0, 0, 0, 3))

        border_normal = self.get_style_color(theme, 'colorpalette.border.normal',
                                             QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24))
        border_hover = self.get_style_color(theme, 'colorpalette.border.hover',
                                            QColor(255, 255, 255, 40) if is_dark else QColor(0, 0, 0, 40))
        border_pressed = self.get_style_color(theme, 'colorpalette.border.pressed',
                                              QColor(255, 255, 255, 50) if is_dark else QColor(0, 0, 0, 50))
        border_disabled = self.get_style_color(theme, 'colorpalette.border.disabled',
                                               QColor(255, 255, 255, 12) if is_dark else QColor(0, 0, 0, 12))

        border_radius = self.get_style_value(theme, 'colorpalette.border_radius',
                                             ColorPaletteConfig.DEFAULT_BUTTON_BORDER_RADIUS)

        bg_normal_hex = bg_normal.name(QColor.NameFormat.HexArgb)
        bg_hover_hex = bg_hover.name(QColor.NameFormat.HexArgb)
        bg_pressed_hex = bg_pressed.name(QColor.NameFormat.HexArgb)
        bg_disabled_hex = bg_disabled.name(QColor.NameFormat.HexArgb)
        border_normal_hex = border_normal.name(QColor.NameFormat.HexArgb)
        border_hover_hex = border_hover.name(QColor.NameFormat.HexArgb)
        border_pressed_hex = border_pressed.name(QColor.NameFormat.HexArgb)
        border_disabled_hex = border_disabled.name(QColor.NameFormat.HexArgb)

        qss = f"""
        DropDownColorPalette {{
            background-color: {bg_normal_hex};
            border: 1px solid {border_normal_hex};
            border-radius: {border_radius}px;
            padding: 4px 28px 4px 4px;
            text-align: left;
        }}
        DropDownColorPalette:hover {{
            background-color: {bg_hover_hex};
            border: 1px solid {border_hover_hex};
        }}
        DropDownColorPalette:pressed {{
            background-color: {bg_pressed_hex};
            border: 1px solid {border_pressed_hex};
        }}
        DropDownColorPalette:disabled {{
            background-color: {bg_disabled_hex};
            border: 1px solid {border_disabled_hex};
        }}
        """

        return qss

    def _update_arrow_icon(self) -> None:
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color('colorpalette.arrow.normal',
                                                    self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200)))

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, 12)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        color_preview_size = self.height() - 10
        color_preview_rect = QRect(5, 5, color_preview_size, color_preview_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._current_color))
        painter.drawRoundedRect(QRectF(color_preview_rect), 3, 3)

        arrow_size = 10
        arrow_margin = 8
        x = self.width() - arrow_size - arrow_margin
        y = (self.height() - arrow_size) // 2
        self.draw_icon(painter, self._arrow_icon, x, y, arrow_size)

    def currentColor(self) -> QColor:
        return QColor(self._current_color)

    def setCurrentColor(self, color: QColor) -> None:
        if self._current_color != color:
            self._current_color = QColor(color)
            self.update()
            self.colorChanged.emit(self._current_color)
            self.currentColorChanged.emit(self._current_color)
            logger.debug(f"颜色已设置: {color.name()}")

    def colors(self) -> List[str]:
        return self._colors.copy()

    def setColors(self, colors: List[str]) -> None:
        self._colors = colors
        if self._panel:
            self._panel.setColors(colors)
        logger.debug(f"颜色列表已更新: {len(colors)} 个颜色")

    def addColor(self, color: str) -> None:
        if color not in self._colors:
            self._colors.append(color)
            if self._panel:
                self._panel.setColors(self._colors)

    def removeColor(self, color: str) -> None:
        if color in self._colors:
            self._colors.remove(color)
            if self._panel:
                self._panel.setColors(self._colors)

    def clearColors(self) -> None:
        self._colors.clear()
        if self._panel:
            self._panel.setColors(self._colors)

    def showPanel(self) -> None:
        self._show_panel()

    def hidePanel(self) -> None:
        self._hide_panel()

    def isPanelVisible(self) -> bool:
        return self._is_panel_visible

    def _on_widget_destroyed(self) -> None:
        """组件销毁时自动调用清理。"""
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        """
        清理资源。
        此方法会在组件销毁时自动调用，也可以手动调用。
        """
        if self._cleanup_done:
            return

        self._cleanup_done = True

        if self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

        if self._panel:
            self._panel.cleanup()
            self._panel.deleteLater()
            self._panel = None

        self._clear_stylesheet_cache()
        self.clear_overrides()
