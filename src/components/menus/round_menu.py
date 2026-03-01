"""
圆角菜单组件

提供现代 Fluent Design 风格的弹出菜单，具有以下特性：
- 圆角和阴影效果
- 平滑的悬停动画
- 主题集成
- 图标支持
- 键盘导航
- 子菜单支持

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
    QGraphicsDropShadowEffect
)

from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager

logger = logging.getLogger(__name__)


class MenuConfig:
    """圆角菜单配置常量。"""

    # 默认边框圆角半径（单位：像素）
    DEFAULT_BORDER_RADIUS = 8
    
    # 默认菜单外边距（单位：像素）
    DEFAULT_MARGIN = 8
    
    # 默认菜单项高度（单位：像素）
    DEFAULT_ITEM_HEIGHT = 36
    
    # 默认菜单项内边距（单位：像素）
    DEFAULT_ITEM_PADDING = 12
    
    # 默认图标尺寸（单位：像素）
    DEFAULT_ICON_SIZE = 16
    
    # 默认最小宽度（单位：像素）
    DEFAULT_MIN_WIDTH = 150
    
    # 默认最大宽度（单位：像素）
    DEFAULT_MAX_WIDTH = 300

    # 动画持续时间（单位：毫秒）
    ANIMATION_DURATION = 150
    
    # 阴影模糊半径（单位：像素）
    SHADOW_BLUR_RADIUS = 20
    
    # 阴影偏移量（单位：像素）
    SHADOW_OFFSET = 4

    # 分隔线高度（单位：像素）
    SEPARATOR_HEIGHT = 9
    
    # 分隔线边距（单位：像素）
    SEPARATOR_MARGIN = 8

    # 子菜单箭头尺寸（单位：像素）
    SUBMENU_ARROW_SIZE = 12
    
    # 子菜单显示延迟（单位：毫秒）
    SUBMENU_DELAY = 200


class MenuActionItem(QWidget):
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
        super().__init__(parent)

        self._text = text
        self._shortcut = shortcut
        self._checkable = checkable
        self._checked = checked
        self._enabled = True
        self._icon: Optional[QIcon] = None
        self._icon_name: Optional[str] = None
        self._is_hovered = False
        self._hover_opacity = 0.0

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self.setFixedHeight(MenuConfig.DEFAULT_ITEM_HEIGHT)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if icon:
            self._set_icon_internal(icon)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        self._current_theme = theme
        self.update()

    def _set_icon_internal(self, icon: Union[QIcon, str]) -> None:
        """内部设置图标方法。"""
        if isinstance(icon, str):
            self._icon_name = icon
            if self._current_theme:
                text_color = self._current_theme.get_color('menu.item.text', QColor(200, 200, 200))
                self._icon = self._icon_mgr.get_colored_icon(icon, text_color, MenuConfig.DEFAULT_ICON_SIZE)
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

    def enterEvent(self, event: QEvent) -> None:
        """鼠标进入事件处理。"""
        if self._enabled:
            self._is_hovered = True
            self._animate_hover(True)
            self.hovered.emit(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """鼠标离开事件处理。"""
        self._is_hovered = False
        self._animate_hover(False)
        self.hovered.emit(False)
        super().leaveEvent(event)

    def _animate_hover(self, hover: bool) -> None:
        """播放悬停动画。"""
        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(MenuConfig.ANIMATION_DURATION)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0 if hover else 0.0)
        self._hover_animation.start()

    def getHoverOpacity(self) -> float:
        """获取悬停透明度（用于动画）。"""
        return self._hover_opacity

    def setHoverOpacity(self, opacity: float) -> None:
        """设置悬停透明度（用于动画）。"""
        self._hover_opacity = opacity
        self.update()

    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件处理。"""
        if event.button() == Qt.MouseButton.LeftButton and self._enabled:
            if self._checkable:
                self._checked = not self._checked
            self.clicked.emit()

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制事件处理。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = self._current_theme
        if not theme:
            return

        rect = self.rect()

        if self._is_hovered and self._enabled:
            hover_color = theme.get_color('menu.item.hover', QColor(50, 50, 50))
            hover_color.setAlphaF(self._hover_opacity * hover_color.alphaF() if hover_color.alphaF() > 0 else self._hover_opacity * 0.3)
            
            border_radius = theme.get_value('menu.border_radius', MenuConfig.DEFAULT_BORDER_RADIUS)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), border_radius, border_radius)
            painter.fillPath(path, hover_color)

        text_color = theme.get_color(
            'menu.item.text.disabled' if not self._enabled else 'menu.item.text',
            QColor(150, 150, 150) if not self._enabled else QColor(200, 200, 200)
        )

        icon_rect = QRect(
            MenuConfig.DEFAULT_ITEM_PADDING,
            (rect.height() - MenuConfig.DEFAULT_ICON_SIZE) // 2,
            MenuConfig.DEFAULT_ICON_SIZE,
            MenuConfig.DEFAULT_ICON_SIZE
        )

        if self._checkable and self._checked:
            check_color = theme.get_color('menu.item.check', QColor(52, 152, 219))
            painter.setPen(QPen(check_color, 2))
            path = QPainterPath()
            path.moveTo(icon_rect.left() + 3, icon_rect.center().y())
            path.lineTo(icon_rect.center().x(), icon_rect.bottom() - 3)
            path.lineTo(icon_rect.right() - 3, icon_rect.top() + 3)
            painter.drawPath(path)
        elif self._icon and not self._icon.isNull():
            self._icon.paint(painter, icon_rect)

        text_left = icon_rect.right() + MenuConfig.DEFAULT_ITEM_PADDING
        text_rect = QRect(
            text_left,
            0,
            rect.width() - text_left - (len(self._shortcut) * 8 + MenuConfig.DEFAULT_ITEM_PADDING if self._shortcut else MenuConfig.DEFAULT_ITEM_PADDING),
            rect.height()
        )

        font = QFont()
        font.setPixelSize(13)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._text)

        if self._shortcut:
            shortcut_color = theme.get_color('menu.item.shortcut', QColor(120, 120, 120))
            painter.setPen(shortcut_color)
            shortcut_rect = QRect(
                rect.width() - len(self._shortcut) * 8 - MenuConfig.DEFAULT_ITEM_PADDING,
                0,
                len(self._shortcut) * 8,
                rect.height()
            )
            painter.drawText(shortcut_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, self._shortcut)

    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class MenuSeparator(QFrame):
    """菜单分隔线。"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(MenuConfig.SEPARATOR_HEIGHT)
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        self._current_theme = theme
        separator_color = theme.get_color('menu.separator', QColor(60, 60, 60))
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

    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class RoundMenu(QWidget):
    """
    现代 Fluent Design 风格弹出菜单。

    功能特性:
    - 圆角和阴影效果
    - 平滑动画
    - 主题集成
    - 图标支持
    - 键盘导航
    - 子菜单支持

    使用方式（类似 QMenu）:
        menu = RoundMenu(parent)
        menu.addAction('新建', callback)
        menu.addAction('打开', callback, icon='folder_open')
        menu.addSeparator()
        menu.addAction('退出', callback)

        # 在指定位置显示
        menu.exec(QPoint(100, 100))

        # 或连接 aboutToShow 信号
        menu.aboutToShow.connect(lambda: print('菜单显示中'))
    """

    aboutToShow = pyqtSignal()
    aboutToHide = pyqtSignal()
    triggered = pyqtSignal(object)

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._items: List[Union[MenuActionItem, MenuSeparator]] = []
        self._actions: List[QAction] = []
        self._current_hover_index = -1
        self._submenu: Optional['RoundMenu'] = None
        self._parent_menu: Optional['RoundMenu'] = None

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        self.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self._init_ui()

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _init_ui(self) -> None:
        """初始化 UI 布局。"""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(8, 8, 8, 8)
        self._main_layout.setSpacing(0)

        self._container = QWidget()
        self._container.setObjectName("menuContainer")
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 4, 0, 4)
        self._container_layout.setSpacing(0)

        self._main_layout.addWidget(self._container)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._apply_theme(theme)
        for item in self._items:
            if isinstance(item, MenuActionItem):
                if item._icon_name and theme:
                    text_color = theme.get_color('menu.item.text', QColor(200, 200, 200))
                    item._icon = self._icon_mgr.get_colored_icon(
                        item._icon_name, text_color, MenuConfig.DEFAULT_ICON_SIZE
                    )

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            return

        self._current_theme = theme

        bg_color = theme.get_color('menu.background', QColor(45, 45, 45))
        border_color = theme.get_color('menu.border', QColor(60, 60, 60))
        border_radius = theme.get_value('menu.border_radius', MenuConfig.DEFAULT_BORDER_RADIUS)

        cache_key = (bg_color.name(), border_color.name(), border_radius)

        if cache_key not in self._stylesheet_cache:
            qss = f"""
                #menuContainer {{
                    background-color: {bg_color.name()};
                    border: 1px solid {border_color.name()};
                    border-radius: {border_radius}px;
                }}
            """
            self._stylesheet_cache[cache_key] = qss

        self._container.setStyleSheet(self._stylesheet_cache[cache_key])

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
        """
        添加菜单项。

        Args:
            text: 菜单项文本
            callback: 触发时的回调函数
            icon: 图标（QIcon 或图标名称字符串）
            shortcut: 快捷键文本（如 "Ctrl+N"）
            checkable: 是否可选中
            checked: 初始选中状态

        Returns:
            创建的 MenuActionItem
        """
        item = MenuActionItem(text, self, icon, shortcut, checkable, checked)

        if callback:
            item.clicked.connect(callback)

        item.clicked.connect(lambda: self._on_item_clicked(item))

        self._items.append(item)
        self._container_layout.addWidget(item)

        self._adjust_size()

        return item

    def addMenu(self, title: str, icon: Optional[Union[QIcon, str]] = None) -> 'RoundMenu':
        """
        添加子菜单。

        Args:
            title: 子菜单标题
            icon: 可选图标

        Returns:
            创建的子菜单
        """
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
            self.setFixedSize(MenuConfig.DEFAULT_MIN_WIDTH, 50)
            return

        # Calculate width based on text content
        max_text_width = 0
        for item in self._items:
            if isinstance(item, MenuActionItem):
                text_width = item.fontMetrics().boundingRect(item.text()).width()
                shortcut_width = len(item.shortcut()) * 8 if item.shortcut() else 0
                total_width = text_width + shortcut_width + MenuConfig.DEFAULT_ICON_SIZE + MenuConfig.DEFAULT_ITEM_PADDING * 4
                max_text_width = max(max_text_width, total_width)

        width = max(MenuConfig.DEFAULT_MIN_WIDTH, min(max_text_width + 16, MenuConfig.DEFAULT_MAX_WIDTH))

        # Set item widths first
        item_width = width - 16
        
        for item in self._items:
            if isinstance(item, MenuActionItem):
                item.setFixedWidth(item_width)
            elif isinstance(item, MenuSeparator):
                item.setFixedWidth(item_width)

        # Calculate height - use fixed heights since items may not be visible yet
        height = 16  # Top + bottom margin
        for item in self._items:
            if isinstance(item, MenuActionItem):
                height += MenuConfig.DEFAULT_ITEM_HEIGHT
            elif isinstance(item, MenuSeparator):
                height += MenuConfig.SEPARATOR_HEIGHT

        self.setFixedSize(width, height)

    def exec(self, pos: QPoint) -> None:
        """
        在指定位置执行菜单。

        Args:
            pos: 显示菜单的全局坐标
        """
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

        self.show()
        self.setFocus()

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
        self.aboutToHide.emit()
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
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

        for item in self._items:
            if isinstance(item, (MenuActionItem, MenuSeparator)):
                item.cleanup()

        if self._submenu:
            self._submenu.cleanup()

    def deleteLater(self) -> None:
        self.cleanup()
        super().deleteLater()
