"""
圆角菜单组件

提供现代 Fluent Design 风格的弹出菜单，具有以下特性：
- 圆角和阴影效果
- 平滑的悬停动画
- 主题集成
- 图标支持
- 键盘导航
- 子菜单支持
- 统一的 ThemedComponentBase 基类

使用方式（类似 QMenu）:
    menu = RoundMenu(parent)
    menu.addAction('新建', lambda: print('新建'))
    menu.addAction('打开', callback, icon='folder_open')
    menu.addSeparator()
    menu.addAction('退出', lambda: app.quit())
    menu.exec(pos)
"""

import logging
from typing import Optional, List, Callable, Union, Dict, Any, Tuple
from PyQt6.QtCore import (
    Qt, QPoint, QPointF, QRect, QRectF, QSize, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer, QEvent, pyqtProperty
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QIcon, QAction, QFont,
    QCursor, QPaintEvent, QMouseEvent, QKeyEvent, QPainterPath
)
from PyQt6.QtWidgets import (
    QWidget, QMenu, QApplication, QStyle, QStyleOptionMenuItem,
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)

from src.core.themed_component_base import ThemedComponentBase
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin
from src.core.theme_manager import ThemeManager
from src.core.icon_manager import IconManager
from src.core.font_manager import FontManager
from src.core.animation import AnimatableMixin, AnimationPreset, AnimationManager
from src.themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG, FALLBACK_COLORS, FALLBACK_COLORS_LIGHT

try:
    from components.combo_box.config import ComboBoxMenuConfig
except ImportError:
    from ..combo_box.config import ComboBoxMenuConfig

logger = logging.getLogger(__name__)


class MenuConfig:
    """圆角菜单配置常量，遵循 WinUI 3 设计规范。"""

    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['menu']['border_radius']
    DEFAULT_MARGIN = WINUI3_CONTROL_SIZING['spacing']['small']
    DEFAULT_ITEM_HEIGHT = WINUI3_CONTROL_SIZING['menu']['item_height']
    DEFAULT_ITEM_PADDING = WINUI3_CONTROL_SIZING['menu']['padding_h']
    DEFAULT_ICON_SIZE = WINUI3_CONTROL_SIZING['menu']['icon_size']
    DEFAULT_MIN_WIDTH = 120
    DEFAULT_MAX_WIDTH = 280
    ANIMATION_DURATION = 100
    SHOW_ANIMATION_DURATION = 150
    HIDE_ANIMATION_DURATION = 100
    SHADOW_BLUR_RADIUS = 12
    SHADOW_OFFSET = 2
    SEPARATOR_HEIGHT = 9
    SEPARATOR_MARGIN = 8
    SUBMENU_ARROW_SIZE = 10
    SUBMENU_DELAY = 200

    @staticmethod
    def get_fallback_text(is_dark: bool = True) -> QColor:
        colors = ComboBoxMenuConfig.get_colors(is_dark)
        return colors['item_text_normal']

    @staticmethod
    def get_fallback_text_disabled(is_dark: bool = True) -> QColor:
        colors = ComboBoxMenuConfig.get_colors(is_dark)
        return colors['item_text_disabled']

    @staticmethod
    def get_fallback_hover(is_dark: bool = True) -> QColor:
        colors = ComboBoxMenuConfig.get_colors(is_dark)
        return colors['item_background_hover']

    @staticmethod
    def get_fallback_separator(is_dark: bool = True) -> QColor:
        return QColor(FALLBACK_COLORS['border']['default'] if is_dark else FALLBACK_COLORS_LIGHT['border']['default'])

    @staticmethod
    def get_fallback_accent(is_dark: bool = True) -> QColor:
        colors = ComboBoxMenuConfig.get_colors(is_dark)
        return colors['checkmark']

    @staticmethod
    def get_fallback_background(is_dark: bool = True) -> QColor:
        colors = ComboBoxMenuConfig.get_colors(is_dark)
        return colors['background']


class MenuActionItem(ThemedComponentBase):
    """
    单个菜单项控件。

    功能特性:
    - 图标和文本显示
    - 悬停状态动画
    - 可选中支持
    - 快捷键显示
    """

    clicked = pyqtSignal()
    hovered = pyqtSignal(bool)

    def __init__(
        self,
        text: str,
        parent: Optional[QWidget] = None,
        icon: Optional[Union[QIcon, str]] = None,
        shortcut: str = "",
        checkable: bool = False,
        checked: bool = False
    ):
        self._text = text
        self._shortcut = shortcut
        self._checkable = checkable
        self._checked = checked
        self._enabled = True
        self._icon: Optional[QIcon] = None
        self._icon_name: Optional[str] = None
        self._is_hovered = False
        self._hover_opacity = 0.0
        self._has_submenu = False

        self._icon_mgr = IconManager.instance()

        super().__init__(parent)

        self.setFixedHeight(MenuConfig.DEFAULT_ITEM_HEIGHT)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if icon:
            self._set_icon_internal(icon)

        self._apply_initial_theme()

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式。"""
        is_dark = theme.is_dark if theme else True
        if self._icon_name and self._current_theme:
            theme_type = "dark" if self._current_theme.is_dark else "light"
            resolved_name = self._icon_mgr.resolve_icon_name(self._icon_name, theme_type)
            text_color = self.get_theme_color('menu.item.text', MenuConfig.get_fallback_text(is_dark))
            self._icon = self._icon_mgr.get_colored_icon(
                resolved_name, text_color, MenuConfig.DEFAULT_ICON_SIZE
            )
        self.update()

    def _set_icon_internal(self, icon: Union[QIcon, str]) -> None:
        """内部设置图标方法。"""
        is_dark = self._current_theme.is_dark if self._current_theme else True
        if isinstance(icon, str):
            self._icon_name = icon
            if self._current_theme:
                theme_type = "dark" if self._current_theme.is_dark else "light"
                resolved_name = self._icon_mgr.resolve_icon_name(icon, theme_type)
                text_color = self.get_theme_color('menu.item.text', MenuConfig.get_fallback_text(is_dark))
                self._icon = self._icon_mgr.get_colored_icon(resolved_name, text_color, MenuConfig.DEFAULT_ICON_SIZE)
            else:
                self._icon = self._icon_mgr.get_icon(icon, MenuConfig.DEFAULT_ICON_SIZE)
        else:
            self._icon = icon
            self._icon_name = None

    def setIcon(self, icon: Union[QIcon, str]) -> None:
        """设置图标。"""
        self._set_icon_internal(icon)
        self.update()

    def icon(self) -> Optional[QIcon]:
        """获取图标。"""
        return self._icon

    def text(self) -> str:
        """获取文本。"""
        return self._text

    def setText(self, text: str) -> None:
        """设置文本。"""
        self._text = text
        self.update()

    def shortcut(self) -> str:
        """获取快捷键文本。"""
        return self._shortcut

    def setShortcut(self, shortcut: str) -> None:
        """设置快捷键文本。"""
        self._shortcut = shortcut
        self.update()

    def isCheckable(self) -> bool:
        """是否可选中。"""
        return self._checkable

    def setCheckable(self, checkable: bool) -> None:
        """设置是否可选中。"""
        self._checkable = checkable
        self.update()

    def isChecked(self) -> bool:
        """是否已选中。"""
        return self._checked

    def setChecked(self, checked: bool) -> None:
        """设置选中状态。"""
        if self._checkable:
            self._checked = checked
            self.update()

    def toggle(self) -> None:
        """切换选中状态。"""
        if self._checkable:
            self.setChecked(not self._checked)

    def isEnabled(self) -> bool:
        """是否启用。"""
        return self._enabled

    def setEnabled(self, enabled: bool) -> None:
        """设置启用状态。"""
        self._enabled = enabled
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if enabled
            else Qt.CursorShape.ForbiddenCursor
        )
        self.update()

    def setHovered(self, hovered: bool) -> None:
        """设置悬停状态。"""
        if self._is_hovered != hovered:
            self._is_hovered = hovered
            self.hovered.emit(hovered)
            self.update()

    def getHoverOpacity(self) -> float:
        """获取悬停透明度。"""
        return self._hover_opacity

    def setHoverOpacity(self, opacity: float) -> None:
        """设置悬停透明度。"""
        self._hover_opacity = opacity
        self.update()

    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)

    def enterEvent(self, event) -> None:
        """鼠标进入事件。"""
        if self._enabled:
            self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """鼠标离开事件。"""
        self._animate_hover(False)
        super().leaveEvent(event)

    def _animate_hover(self, hovered: bool) -> None:
        """悬停动画。"""
        self._is_hovered = hovered

        animation = QPropertyAnimation(self, b"hoverOpacity")
        animation.setDuration(MenuConfig.ANIMATION_DURATION)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(self._hover_opacity)
        animation.setEndValue(1.0 if hovered else 0.0)
        animation.start()

    def mousePressEvent(self, event) -> None:
        """鼠标按下事件。"""
        if event.button() == Qt.MouseButton.LeftButton and self._enabled:
            if self._checkable:
                self.toggle()
            self.clicked.emit()

    def paintEvent(self, event) -> None:
        """绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        is_dark = self._current_theme.is_dark if self._current_theme else True

        if self._is_hovered and self._enabled:
            hover_color = self.get_theme_color('menu.item.hover', MenuConfig.get_fallback_hover(is_dark))
            hover_color.setAlpha(int(255 * self._hover_opacity))
            painter.fillRect(rect, hover_color)

        icon_size = MenuConfig.DEFAULT_ICON_SIZE
        padding = MenuConfig.DEFAULT_ITEM_PADDING

        if self._icon and not self._icon.isNull():
            icon_rect = QRect(padding, (rect.height() - icon_size) // 2, icon_size, icon_size)
            self._icon.paint(painter, icon_rect)

        if self._checkable:
            check_rect = QRect(padding + 2, (rect.height() - 12) // 2, 12, 12)
            check_color = self.get_theme_color('primary.main', MenuConfig.get_fallback_accent(is_dark))
            if self._checked:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(check_color)
                painter.drawRoundedRect(QRectF(check_rect), 2, 2)

        text_x = padding + icon_size + padding
        text_width = rect.width() - text_x - padding

        if self._shortcut:
            text_width -= len(self._shortcut) * 8 + padding

        if self._has_submenu:
            text_width -= MenuConfig.SUBMENU_ARROW_SIZE + padding

        text_color = self.get_theme_color(
            'menu.item.text' if self._enabled else 'menu.item.disabled',
            MenuConfig.get_fallback_text(is_dark) if self._enabled else MenuConfig.get_fallback_text_disabled(is_dark)
        )
        painter.setPen(text_color)
        font = FontManager.get_menu_font()
        painter.setFont(font)

        text_rect = QRect(text_x, 0, text_width, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._text)

        if self._shortcut:
            shortcut_color = self.get_theme_color('menu.item.shortcut', MenuConfig.get_fallback_text_disabled(is_dark))
            painter.setPen(shortcut_color)
            shortcut_x = rect.width() - padding - len(self._shortcut) * 8
            if self._has_submenu:
                shortcut_x -= MenuConfig.SUBMENU_ARROW_SIZE + padding
            shortcut_rect = QRect(shortcut_x, 0, len(self._shortcut) * 8, rect.height())
            painter.drawText(shortcut_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._shortcut)

        if self._has_submenu:
            arrow_color = self.get_theme_color('menu.item.text', MenuConfig.get_fallback_text(is_dark))
            painter.setPen(arrow_color)
            arrow_size = MenuConfig.SUBMENU_ARROW_SIZE
            arrow_x = rect.width() - padding - arrow_size
            arrow_y = (rect.height() - arrow_size) // 2

            from PyQt6.QtGui import QPolygonF
            arrow = QPolygonF([
                QPointF(arrow_x, arrow_y),
                QPointF(arrow_x + arrow_size, arrow_y + arrow_size // 2),
                QPointF(arrow_x, arrow_y + arrow_size)
            ])
            painter.drawPolyline(arrow)


class MenuSeparator(ThemedComponentBase):
    """菜单分隔线。"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(MenuConfig.SEPARATOR_HEIGHT)

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式，遵循 WinUI 3 设计规范。"""
        is_dark = theme.is_dark if theme else True
        separator_color = self.get_theme_color('menu.separator', MenuConfig.get_fallback_separator(is_dark))
        self.setStyleSheet(f"""
            MenuSeparator {{
                background: transparent;
                border: none;
                border-top: 1px solid {separator_color.name()};
                margin-left: {MenuConfig.SEPARATOR_MARGIN}px;
                margin-right: {MenuConfig.SEPARATOR_MARGIN}px;
                margin-top: {(MenuConfig.SEPARATOR_HEIGHT - 1) // 2}px;
            }}
        """)


class RoundMenu(QWidget, StyleOverrideMixin, StylesheetCacheMixin, AnimatableMixin):
    """
    现代 Fluent Design 风格弹出菜单。

    功能特性:
    - 圆角和阴影效果
    - 平滑动画
    - 主题集成
    - 图标支持
    - 键盘导航
    - 子菜单支持
    - Style override 支持
    - Stylesheet caching

    使用方式（类似 QMenu）:
        menu = RoundMenu(parent)
        menu.addAction('新建', callback)
        menu.addAction('打开', callback, icon='folder_open')
        menu.addSeparator()
        menu.addAction('退出', callback)

        # 在指定位置显示
        menu.exec(QPoint(100, 100))
    """

    aboutToShow = pyqtSignal()
    aboutToHide = pyqtSignal()
    triggered = pyqtSignal(object)

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._title = title
        self._items: List[Union[MenuActionItem, MenuSeparator]] = []
        self._actions: List[QAction] = []
        self._current_hover_index = -1
        self._submenu: Optional['RoundMenu'] = None
        self._parent_menu: Optional['RoundMenu'] = None

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        self._icon_mgr = IconManager.instance()

        self._animation_manager = AnimationManager.instance()

        self.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self._init_ui()
        self.setup_animation(AnimationPreset.FLYOUT, AnimationPreset.FLYOUT_HIDE)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        """初始化 UI 布局，遵循 WinUI 3 设计规范。"""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(4, 4, 4, 4)
        self._main_layout.setSpacing(0)

        self._container = QWidget()
        self._container.setObjectName("menuContainer")
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 2, 0, 2)
        self._container_layout.setSpacing(0)

        self._main_layout.addWidget(self._container)

    def _on_theme_changed(self, theme: Any) -> None:
        """主题变化回调。"""
        self._current_theme = theme
        self._apply_theme(theme)
        is_dark = theme.is_dark if theme else True
        for item in self._items:
            if isinstance(item, MenuActionItem):
                if item._icon_name and theme:
                    theme_type = "dark" if theme.is_dark else "light"
                    resolved_name = self._icon_mgr.resolve_icon_name(item._icon_name, theme_type)
                    text_color = self.get_style_color(theme, 'menu.item.text', MenuConfig.get_fallback_text(is_dark))
                    item._icon = self._icon_mgr.get_colored_icon(
                        resolved_name, text_color, MenuConfig.DEFAULT_ICON_SIZE
                    )

    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式，遵循 WinUI 3 设计规范。"""
        if not self._current_theme:
            return

        is_dark = self._current_theme.is_dark if self._current_theme else True
        bg_color = self.get_style_color(self._current_theme, 'menu.background', MenuConfig.get_fallback_background(is_dark))
        border_radius = self.get_style_value(self._current_theme, 'menu.border_radius', MenuConfig.DEFAULT_BORDER_RADIUS)

        cache_key: Tuple[str, str, int] = (bg_color.name(), '', border_radius)

        def build_stylesheet() -> str:
            return f"""
                #menuContainer {{
                    background-color: {bg_color.name()};
                    border: none;
                    border-radius: {border_radius}px;
                }}
            """

        qss = self._get_cached_stylesheet(cache_key, build_stylesheet)
        self._container.setStyleSheet(qss)

    def title(self) -> str:
        """获取菜单标题。"""
        return self._title

    def setTitle(self, title: str) -> None:
        """设置菜单标题。"""
        self._title = title

    def addAction(
        self,
        text: str,
        callback: Optional[Callable] = None,
        icon: Optional[Union[QIcon, str]] = None,
        shortcut: str = "",
        checkable: bool = False,
        checked: bool = False
    ) -> MenuActionItem:
        """添加菜单项。"""
        item = MenuActionItem(text, self, icon, shortcut, checkable, checked)

        if callback:
            item.clicked.connect(callback)

        item.clicked.connect(lambda: self._on_item_clicked(item))

        self._items.append(item)
        self._container_layout.addWidget(item)

        self._adjust_size()

        return item

    def addMenu(self, title: str, icon: Optional[Union[QIcon, str]] = None) -> 'RoundMenu':
        """添加子菜单。"""
        submenu = RoundMenu(title, self)
        submenu._parent_menu = self

        item = MenuActionItem(title, self, icon)
        item._has_submenu = True
        item.clicked.connect(lambda: self._show_submenu(submenu, item))

        self._items.append(item)
        self._container_layout.addWidget(item)

        self._adjust_size()

        return submenu

    def addSeparator(self) -> MenuSeparator:
        """添加分隔线到菜单。"""
        separator = MenuSeparator(self)
        self._items.append(separator)
        self._container_layout.addWidget(separator)
        return separator

    def insertAction(self, before: MenuActionItem, text: str, **kwargs) -> MenuActionItem:
        """在指定菜单项之前插入新菜单项。"""
        index = self._items.index(before) if before in self._items else 0
        item = MenuActionItem(text, self, **kwargs)
        self._items.insert(index, item)
        self._container_layout.insertWidget(index, item)
        self._adjust_size()
        return item

    def removeAction(self, action: MenuActionItem) -> None:
        """从菜单移除指定菜单项。"""
        if action in self._items:
            self._items.remove(action)
            self._container_layout.removeWidget(action)
            action.cleanup()
            action.deleteLater()
            self._adjust_size()

    def clear(self) -> None:
        """清空菜单中的所有项目。"""
        for item in self._items:
            if isinstance(item, (MenuActionItem, MenuSeparator)):
                item.cleanup()
                item.deleteLater()
        self._items.clear()
        self._adjust_size()

    def _on_item_clicked(self, item: MenuActionItem) -> None:
        """菜单项点击处理。"""
        self.triggered.emit(item)
        self.hide()
        if self._parent_menu:
            self._parent_menu.hide()

    def _show_submenu(self, submenu: 'RoundMenu', item: MenuActionItem) -> None:
        """显示子菜单。"""
        if self._submenu and self._submenu != submenu:
            self._submenu.hide()

        self._submenu = submenu

        global_pos = item.mapToGlobal(QPoint(item.width(), 0))
        submenu.exec(global_pos)

    def _adjust_size(self) -> None:
        """根据内容调整菜单尺寸。"""
        item_count = len(self._items)

        if item_count == 0:
            self.setFixedSize(MenuConfig.DEFAULT_MIN_WIDTH, 40)
            return

        max_text_width = 0
        for item in self._items:
            if isinstance(item, MenuActionItem):
                text_width = item.fontMetrics().boundingRect(item.text()).width()
                shortcut_width = len(item.shortcut()) * 7 if item.shortcut() else 0
                total_width = text_width + shortcut_width + MenuConfig.DEFAULT_ICON_SIZE + MenuConfig.DEFAULT_ITEM_PADDING * 4
                max_text_width = max(max_text_width, total_width)

        width = max(MenuConfig.DEFAULT_MIN_WIDTH, min(max_text_width + 12, MenuConfig.DEFAULT_MAX_WIDTH))

        item_width = width - 8

        for item in self._items:
            if isinstance(item, MenuActionItem):
                item.setFixedWidth(item_width)
            elif isinstance(item, MenuSeparator):
                item.setFixedWidth(item_width)

        height = 8
        for item in self._items:
            if isinstance(item, MenuActionItem):
                height += MenuConfig.DEFAULT_ITEM_HEIGHT
            elif isinstance(item, MenuSeparator):
                height += MenuConfig.SEPARATOR_HEIGHT

        self.setFixedSize(width, height)

    def exec(self, pos: QPoint) -> None:
        """在指定位置执行菜单，带有 Flyout 动画效果。"""
        self.aboutToShow.emit()

        self._adjust_size()

        menu_width = self.width()
        menu_height = self.height()

        screen = QApplication.screenAt(pos)
        if screen:
            screen_rect = screen.availableGeometry()

            x = pos.x()
            y = pos.y()

            if x + menu_width > screen_rect.right():
                x = screen_rect.right() - menu_width - 8

            if y + menu_height > screen_rect.bottom():
                y = pos.y() - menu_height

            if x < screen_rect.left():
                x = screen_rect.left() + 8

            if y < screen_rect.top():
                y = screen_rect.top() + 8

            self.move(x, y)

        self._start_show_animation()

    def _start_show_animation(self) -> None:
        """启动显示动画，遵循 WinUI 3 Flyout 动画规范。"""
        self.show()
        self.animate_show()
        self.setFocus()

    def hide(self) -> None:
        """隐藏菜单，带有 Flyout 动画效果。"""
        self._start_hide_animation()

    def _start_hide_animation(self) -> None:
        """启动隐藏动画，遵循 WinUI 3 Flyout 动画规范。"""
        if self.is_animating():
            self.stop_animation()
        self.animate_hide()
        QTimer.singleShot(
            self._animation_manager.get_scaled_duration(AnimationPreset.FLYOUT_HIDE.duration),
            self._on_hide_animation_finished
        )

    def _on_hide_animation_finished(self) -> None:
        """隐藏动画完成后的回调。"""
        self.aboutToHide.emit()
        super().hide()

    def exec_(self, pos: QPoint) -> None:
        """兼容旧版本的方法名。"""
        self.exec(pos)

    def popup(self, pos: QPoint) -> None:
        """在指定位置显示菜单（exec 的别名）。"""
        self.exec(pos)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._current_hover_index = -1

    def hideEvent(self, event) -> None:
        if self._submenu:
            self._submenu.hide()
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return

        if event.key() == Qt.Key.Key_Up:
            self._navigate(-1)
            return

        if event.key() == Qt.Key.Key_Down:
            self._navigate(1)
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._activate_current()
            return

        super().keyPressEvent(event)

    def _navigate(self, direction: int) -> None:
        """在菜单项之间导航。"""
        visible_items = [
            (i, item) for i, item in enumerate(self._items)
            if isinstance(item, MenuActionItem) and item.isEnabled() and item.isVisible()
        ]

        if not visible_items:
            return

        current_idx = -1
        for i, (orig_idx, item) in enumerate(visible_items):
            if orig_idx == self._current_hover_index:
                current_idx = i
                break

        new_idx = current_idx + direction
        if new_idx < 0:
            new_idx = len(visible_items) - 1
        elif new_idx >= len(visible_items):
            new_idx = 0

        if self._current_hover_index >= 0 and self._current_hover_index < len(self._items):
            old_item = self._items[self._current_hover_index]
            if isinstance(old_item, MenuActionItem):
                old_item._is_hovered = False
                old_item.update()

        self._current_hover_index = visible_items[new_idx][0]
        new_item = visible_items[new_idx][1]
        new_item._is_hovered = True
        new_item._hover_opacity = 1.0
        new_item.update()

    def _activate_current(self) -> None:
        """激活当前选中的菜单项。"""
        if 0 <= self._current_hover_index < len(self._items):
            item = self._items[self._current_hover_index]
            if isinstance(item, MenuActionItem) and item.isEnabled():
                item.clicked.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.rect().contains(event.pos()):
            self.hide()
            return
        super().mousePressEvent(event)

    def focusOutEvent(self, event) -> None:
        if not self.isHidden():
            QTimer.singleShot(100, self._check_hide)

    def _check_hide(self) -> None:
        if not self.hasFocus() and not self.underMouse():
            self.hide()

    def cleanup(self) -> None:
        """清理资源。"""
        self._theme_mgr.unsubscribe(self)

        self.stop_animation()
        self.cleanup_animation()

        for item in self._items:
            if isinstance(item, (MenuActionItem, MenuSeparator)):
                item.cleanup()

        if self._submenu:
            self._submenu.cleanup()

        self._clear_stylesheet_cache()
        self.clear_overrides()

    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
