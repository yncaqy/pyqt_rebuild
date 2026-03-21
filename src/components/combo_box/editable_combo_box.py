"""
WinUI3 风格可编辑组合框组件

遵循 WinUI3 设计规范，提供可编辑的组合框。
特性：
- 继承自 QLineEdit，允许用户编辑当前选项
- 按下回车可添加新选项
- 点击下拉按钮弹出下拉列表
- 占位符文本支持
- 选中项指示器
- 平滑动画效果
- 自动补全支持
- 主题集成

参考文档:
https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/combo-box
"""

import logging
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import (
    Qt, QSize, QPoint, pyqtSignal, QRect, QStringListModel,
    QPropertyAnimation, QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QFont, QKeyEvent, QFocusEvent
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy, QCompleter
try:
    from core.theme_manager import ThemeManager, Theme
    from core.style_override import StyleOverrideMixin
    from core.stylesheet_cache_mixin import StylesheetCacheMixin
    from core.icon_manager import IconManager
    from themes.colors import FONT_CONFIG
    from .config import ComboBoxConfig, ComboBoxMenuConfig, ComboBoxAnimationConfig
    from .combo_box_menu import ComboBoxMenu
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.style_override import StyleOverrideMixin
    from ...core.stylesheet_cache_mixin import StylesheetCacheMixin
    from ...core.icon_manager import IconManager
    from ...themes.colors import FONT_CONFIG
    from .config import ComboBoxConfig, ComboBoxMenuConfig, ComboBoxAnimationConfig
    from .combo_box_menu import ComboBoxMenu

logger = logging.getLogger(__name__)


class EditableComboBox(QLineEdit, StyleOverrideMixin, StylesheetCacheMixin):
    """
    WinUI3 风格可编辑组合框组件。
    
    遵循 WinUI3 设计规范，提供可编辑的组合框。
    
    特性：
    - 允许用户编辑当前选项
    - 按下回车可添加新选项
    - 点击下拉按钮弹出下拉列表
    - 占位符文本支持
    - 选中项指示器
    - 平滑动画效果
    - 自动补全支持
    - 主题集成

    信号:
        currentIndexChanged: 当前索引改变时发出
        currentTextChanged: 当前文本改变时发出
        itemAdded: 新项目添加时发出

    示例:
        combo = EditableComboBox()
        combo.addItem("选项1")
        combo.addItem("选项2")
        combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(lambda index: print(f"选中: {index}"))
    """

    currentIndexChanged = pyqtSignal(int)
    currentTextChanged = pyqtSignal(str)
    itemAdded = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache(max_size=100)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(ComboBoxConfig.MIN_HEIGHT)
        self.setMinimumWidth(ComboBoxConfig.MIN_WIDTH)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False

        self._items: List[Dict[str, Any]] = []
        self._current_index: int = -1
        self._placeholder_text: str = ""

        self._menu: Optional[ComboBoxMenu] = None
        self._is_popup_visible: bool = False
        self._is_focused: bool = False
        self._is_hovered: bool = False
        
        self._arrow_icon_normal: Optional[QIcon] = None
        self._arrow_icon_hover: Optional[QIcon] = None

        self._hover_progress: float = 0.0
        self._hover_animation: Optional[QPropertyAnimation] = None

        self._colors: Dict[str, QColor] = {}
        
        self._bg_normal: QColor = QColor(255, 255, 255, 9)
        self._bg_hover: QColor = QColor(255, 255, 255, 14)
        self._bg_pressed: QColor = QColor(255, 255, 255, 6)
        self._bg_disabled: QColor = QColor(255, 255, 255, 4)
        self._bg_focused: QColor = QColor(255, 255, 255, 9)
        
        self._border_normal: QColor = QColor(255, 255, 255, 0)
        self._border_hover: QColor = QColor(255, 255, 255, 0)
        self._border_pressed: QColor = QColor(255, 255, 255, 0)
        self._border_disabled: QColor = QColor(255, 255, 255, 0)
        self._border_focused: QColor = QColor(255, 255, 255, 0)
        
        self._text_normal: QColor = QColor(255, 255, 255)
        self._text_placeholder: QColor = QColor(255, 255, 255, 135)
        self._text_disabled: QColor = QColor(255, 255, 255, 92)
        
        self._arrow_normal: QColor = QColor(255, 255, 255, 153)
        self._arrow_hover: QColor = QColor(255, 255, 255, 204)
        self._arrow_disabled: QColor = QColor(255, 255, 255, 92)

        self._completer: Optional[QCompleter] = None
        self._completer_enabled: bool = True

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self._setup_completer()
        self.textEdited.connect(self._on_text_edited)

        logger.debug("EditableComboBox 初始化完成")

    def _setup_completer(self) -> None:
        """设置自动补全器。"""
        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self._completer)

    def _update_completer_model(self) -> None:
        """更新自动补全模型。"""
        if self._completer and self._completer_enabled:
            texts = [item.get('text', '') for item in self._items]
            self._completer.setModel(QStringListModel(texts, self))

    def get_hover_progress(self) -> float:
        return self._hover_progress

    def set_hover_progress(self, value: float) -> None:
        self._hover_progress = value
        self.update()

    hover_progress = pyqtProperty(float, get_hover_progress, set_hover_progress)

    def _start_hover_animation(self, forward: bool) -> None:
        """启动悬停动画。"""
        if self._hover_animation:
            self._hover_animation.stop()

        self._hover_animation = QPropertyAnimation(self, b"hover_progress")
        self._hover_animation.setDuration(ComboBoxAnimationConfig.HOVER_DURATION)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0 if forward else 0.0)
        self._hover_animation.start()

    def sizeHint(self) -> QSize:
        """返回组合框的建议尺寸。"""
        base_size = super().sizeHint()
        arrow_space = ComboBoxConfig.ARROW_SIZE + ComboBoxConfig.ARROW_MARGIN * 2
        max_text_width = 0
        for item in self._items:
            text_width = self.fontMetrics().boundingRect(item.get('text', '')).width()
            max_text_width = max(max_text_width, text_width)
        width = max(ComboBoxConfig.MIN_WIDTH, max_text_width + arrow_space + 24)
        return QSize(width, base_size.height())

    def _on_text_edited(self, text: str) -> None:
        """处理文本编辑事件。"""
        index = self.findText(text)
        if index >= 0:
            self._current_index = index
        else:
            self._current_index = -1

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """处理键盘事件。"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            text = self.text().strip()
            if text:
                index = self.findText(text)
                if index < 0:
                    self.addItem(text)
                    self.setCurrentIndex(len(self._items) - 1)
                    self.itemAdded.emit(text)
                else:
                    self.setCurrentIndex(index)
            return

        super().keyPressEvent(event)

    def enterEvent(self, event) -> None:
        """处理鼠标进入事件。"""
        self._is_hovered = True
        if self.isEnabled():
            self._start_hover_animation(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """处理鼠标离开事件。"""
        self._is_hovered = False
        if self.isEnabled():
            self._start_hover_animation(False)
        super().leaveEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """处理焦点进入事件。"""
        self._is_focused = True
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """处理焦点离开事件。"""
        self._is_focused = False
        self.update()
        super().focusOutEvent(event)

    def mousePressEvent(self, event) -> None:
        """处理鼠标按下事件。"""
        arrow_rect = self._get_arrow_rect()
        if arrow_rect.contains(event.pos()):
            self._toggle_menu()
            return
        super().mousePressEvent(event)

    def _get_arrow_rect(self) -> QRect:
        """获取下拉箭头的矩形区域。"""
        arrow_size = ComboBoxConfig.ARROW_SIZE
        arrow_margin = ComboBoxConfig.ARROW_MARGIN
        return QRect(
            self.width() - arrow_size - arrow_margin - 4,
            (self.height() - arrow_size) // 2 - 4,
            arrow_size + 8,
            arrow_size + 8
        )

    def _toggle_menu(self) -> None:
        """切换下拉菜单显示状态。"""
        if self._menu and self._is_popup_visible:
            self._menu.hide()
        else:
            self._show_menu()

    def _show_menu(self) -> None:
        """显示下拉列表。"""
        if not self._items:
            return

        self._menu = ComboBoxMenu()

        for i, item in enumerate(self._items):
            text = item.get('text', '')
            icon = item.get('icon')
            user_data = item.get('userData')
            self._menu.addItem(text, icon, user_data)

        if self._current_theme:
            self._menu._apply_theme(self._current_theme)

        self._menu.setCurrentIndex(self._current_index)

        self._menu.aboutToHide.connect(self._on_menu_hidden)

        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._menu.show_at(global_pos, self.width())
        self._is_popup_visible = True

    def _on_menu_hidden(self) -> None:
        """处理菜单隐藏事件。"""
        self._is_popup_visible = False
        if self._menu:
            new_index = self._menu.currentIndex()
            if new_index >= 0 and new_index != self._current_index:
                self.setCurrentIndex(new_index)
            self._menu.deleteLater()
            self._menu = None

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 EditableComboBox 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        if not theme:
            logger.debug("主题为空，跳过应用")
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')
        is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True

        self._colors = ComboBoxConfig.get_colors(is_dark)
        
        self._bg_normal = self._colors['background_normal']
        self._bg_hover = self._colors['background_hover']
        self._bg_pressed = self._colors['background_pressed']
        self._bg_disabled = self._colors['background_disabled']
        self._bg_focused = self._colors['background_focused']
        
        self._border_normal = self._colors['border_normal']
        self._border_hover = self._colors['border_hover']
        self._border_pressed = self._colors['border_pressed']
        self._border_disabled = self._colors['border_disabled']
        self._border_focused = self._colors['border_focused']
        
        self._text_normal = self._colors['text_normal']
        self._text_placeholder = self._colors['text_placeholder']
        self._text_disabled = self._colors['text_disabled']
        
        self._arrow_normal = self._colors['arrow_normal']
        self._arrow_hover = self._colors['arrow_hover']
        self._arrow_disabled = self._colors['arrow_disabled']

        self._update_arrow_icon()

        if self._menu:
            self._menu._apply_theme(theme)

        self.update()

        logger.debug(f"主题已应用: {theme_name}")

    def _update_arrow_icon(self) -> None:
        """更新下拉箭头图标。"""
        if not self._current_theme:
            return

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon_normal = self._icon_mgr.get_colored_icon(
            arrow_name, self._arrow_normal, ComboBoxConfig.ARROW_SIZE
        )
        self._arrow_icon_hover = self._icon_mgr.get_colored_icon(
            arrow_name, self._arrow_hover, ComboBoxConfig.ARROW_SIZE
        )

        self.update()

    def paintEvent(self, event) -> None:
        """重写绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)

        is_disabled = not self.isEnabled()
        is_focused = self._is_focused

        if is_disabled:
            bg_color = self._bg_disabled
            border_color = self._border_disabled
            text_color = self._text_disabled
            arrow_color = self._arrow_disabled
        elif is_focused:
            bg_color = self._bg_focused
            border_color = self._border_focused
            text_color = self._text_normal
            arrow_color = self._arrow_hover
        elif self._is_hovered:
            t = self._hover_progress
            bg_color = self._lerp_color(self._bg_normal, self._bg_hover, t)
            border_color = self._lerp_color(self._border_normal, self._border_hover, t)
            text_color = self._text_normal
            arrow_color = self._lerp_color(self._arrow_normal, self._arrow_hover, t)
        else:
            bg_color = self._bg_normal
            border_color = self._border_normal
            text_color = self._text_normal
            arrow_color = self._arrow_normal

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, ComboBoxConfig.BORDER_RADIUS, ComboBoxConfig.BORDER_RADIUS)
        
        if border_color.alpha() > 0:
            border_width = 2 if is_focused else 1
            painter.setPen(QPen(border_color, border_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, ComboBoxConfig.BORDER_RADIUS, ComboBoxConfig.BORDER_RADIUS)

        painter.end()
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                padding: {ComboBoxConfig.PADDING_V}px {ComboBoxConfig.ARROW_SIZE + ComboBoxConfig.ARROW_MARGIN * 2}px {ComboBoxConfig.PADDING_V}px {ComboBoxConfig.PADDING_H}px;
                color: {text_color.name()};
                selection-background-color: rgba(89, 89, 89, 0.3);
            }}
        """)
        
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self._arrow_icon_normal and self._arrow_icon_hover:
            arrow_icon = self._arrow_icon_hover if self._is_hovered or is_focused else self._arrow_icon_normal
            if is_disabled:
                theme_type = "dark" if not self._current_theme or self._current_theme.is_dark else "light"
                arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)
                arrow_icon = self._icon_mgr.get_colored_icon(
                    arrow_name, 
                    self._arrow_disabled, 
                    ComboBoxConfig.ARROW_SIZE
                )
            
            arrow_size = ComboBoxConfig.ARROW_SIZE
            arrow_margin = ComboBoxConfig.ARROW_MARGIN
            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2
            arrow_icon.paint(painter, x, y, arrow_size, arrow_size)

    def _lerp_color(self, c1: QColor, c2: QColor, t: float) -> QColor:
        """线性插值两个颜色。"""
        if not c1.isValid() or not c2.isValid():
            return c2
        
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        
        return QColor(
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b)),
            max(0, min(255, a))
        )

    def _on_widget_destroyed(self) -> None:
        """处理组件销毁事件。"""
        self._cleanup()

    def _cleanup(self) -> None:
        """清理资源。"""
        if self._cleanup_done:
            return

        self._cleanup_done = True

        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation = None

        try:
            self._theme_mgr.unsubscribe(self)
        except Exception as e:
            logger.debug(f"取消主题订阅时出错: {e}")

        logger.debug("EditableComboBox 资源已清理")

    # ========== QComboBox 接口实现 ==========

    def addItem(self, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        """添加一个项目到组合框。"""
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.append(item)
        self._update_completer_model()
        if self._current_index < 0:
            self.setCurrentIndex(0)
        logger.debug(f"添加项目: '{text}'")

    def addItems(self, texts: List[str]) -> None:
        """添加多个项目到组合框。"""
        for text in texts:
            item = {'text': text, 'icon': None, 'userData': None}
            self._items.append(item)
        self._update_completer_model()
        if self._current_index < 0:
            self.setCurrentIndex(0)
        logger.debug(f"添加 {len(texts)} 个项目")

    def insertItem(self, index: int, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        """在指定位置插入项目。"""
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.insert(index, item)
        self._update_completer_model()
        if self._current_index < 0:
            self.setCurrentIndex(0)
        elif index <= self._current_index:
            self._current_index += 1
        logger.debug(f"在位置 {index} 插入项目: '{text}'")

    def insertItems(self, index: int, texts: List[str]) -> None:
        """在指定位置插入多个项目。"""
        for i, text in enumerate(texts):
            self.insertItem(index + i, text)
        logger.debug(f"在位置 {index} 插入 {len(texts)} 个项目")

    def removeItem(self, index: int) -> None:
        """移除指定位置的项目。"""
        if index < 0 or index >= len(self._items):
            return
        del self._items[index]
        self._update_completer_model()
        if len(self._items) == 0:
            self._current_index = -1
            self.setText("")
        elif index < self._current_index:
            self._current_index -= 1
        elif index == self._current_index:
            if self._current_index >= len(self._items):
                self._current_index = len(self._items) - 1
            if self._current_index >= 0:
                self.setText(self._items[self._current_index].get('text', ''))
        logger.debug(f"移除位置 {index} 的项目")

    def clear(self) -> None:
        """清空所有项目。"""
        self._items.clear()
        self._current_index = -1
        self.setText("")
        self._update_completer_model()
        logger.debug("清空所有项目")

    def count(self) -> int:
        """获取项目数量。"""
        return len(self._items)

    def currentIndex(self) -> int:
        """获取当前选中索引。"""
        return self._current_index

    def setCurrentIndex(self, index: int) -> None:
        """设置当前选中索引。"""
        if index < -1 or index >= len(self._items):
            return
        old_index = self._current_index
        self._current_index = index
        if index >= 0:
            text = self._items[index].get('text', '')
            self.setText(text)
        else:
            self.setText("")
        if old_index != index:
            self.currentIndexChanged.emit(index)
            if index >= 0:
                self.currentTextChanged.emit(self._items[index].get('text', ''))
        logger.debug(f"设置当前索引: {index}")

    def currentText(self) -> str:
        """获取当前选中文本。"""
        return self.text()

    def setCurrentText(self, text: str) -> None:
        """设置当前选中文本。"""
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                self.setCurrentIndex(i)
                return
        self.setText(text)

    def itemText(self, index: int) -> str:
        """获取指定索引的项目文本。"""
        if 0 <= index < len(self._items):
            return self._items[index].get('text', '')
        return ""

    def setItemText(self, index: int, text: str) -> None:
        """设置指定索引的项目文本。"""
        if 0 <= index < len(self._items):
            self._items[index]['text'] = text
            self._update_completer_model()
            if index == self._current_index:
                self.setText(text)

    def itemIcon(self, index: int) -> Optional[QIcon]:
        """获取指定索引的项目图标。"""
        if 0 <= index < len(self._items):
            return self._items[index].get('icon')
        return None

    def setItemIcon(self, index: int, icon: QIcon) -> None:
        """设置指定索引的项目图标。"""
        if 0 <= index < len(self._items):
            self._items[index]['icon'] = icon

    def itemData(self, index: int) -> Any:
        """获取指定索引的项目用户数据。"""
        if 0 <= index < len(self._items):
            return self._items[index].get('userData')
        return None

    def setItemData(self, index: int, userData: Any) -> None:
        """设置指定索引的项目用户数据。"""
        if 0 <= index < len(self._items):
            self._items[index]['userData'] = userData

    def findText(self, text: str) -> int:
        """查找包含指定文本的项目索引。"""
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                return i
        return -1

    def findData(self, data: Any) -> int:
        """查找包含指定用户数据的项目索引。"""
        for i, item in enumerate(self._items):
            if item.get('userData') == data:
                return i
        return -1

    def setPlaceholderText(self, text: str) -> None:
        """设置占位符文本。"""
        self._placeholder_text = text
        self.update()

    def placeholderText(self) -> str:
        """获取占位符文本。"""
        return self._placeholder_text

    def setCompleterEnabled(self, enabled: bool) -> None:
        """设置是否启用自动补全。"""
        self._completer_enabled = enabled
        if not enabled:
            self.setCompleter(None)
        else:
            self.setCompleter(self._completer)
            self._update_completer_model()

    def completerEnabled(self) -> bool:
        """获取是否启用自动补全。"""
        return self._completer_enabled
