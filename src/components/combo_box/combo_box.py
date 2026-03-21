"""
WinUI3 风格组合框组件

遵循 WinUI3 设计规范，提供带下拉列表选择的组合框。
特性：
- 点击弹出下拉列表
- 占位符文本支持
- 选中项指示器
- 平滑动画效果
- 键盘导航支持
- 主题集成

参考文档:
https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/combo-box
"""

import logging
import time
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import (
    Qt, QSize, QPoint, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QFont, QFocusEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
try:
    from core.theme_manager import ThemeManager, Theme
    from core.style_override import StyleOverrideMixin
    from core.stylesheet_cache_mixin import StylesheetCacheMixin
    from core.icon_manager import IconManager
    from core.font_manager import FontManager
    from .config import ComboBoxConfig, ComboBoxAnimationConfig
    from .combo_box_menu import ComboBoxMenu
except ImportError:
    from ...core.theme_manager import ThemeManager, Theme
    from ...core.style_override import StyleOverrideMixin
    from ...core.stylesheet_cache_mixin import StylesheetCacheMixin
    from ...core.icon_manager import IconManager
    from ...core.font_manager import FontManager
    from .config import ComboBoxConfig, ComboBoxAnimationConfig
    from .combo_box_menu import ComboBoxMenu

logger = logging.getLogger(__name__)


class ComboBox(QPushButton, StyleOverrideMixin, StylesheetCacheMixin):
    """
    WinUI3 风格组合框组件。
    
    遵循 WinUI3 设计规范，提供带下拉列表选择的组合框。
    
    特性：
    - 点击弹出下拉列表
    - 占位符文本支持
    - 选中项指示器
    - 平滑动画效果
    - 键盘导航支持
    - 主题集成

    信号:
        currentIndexChanged: 当前索引改变时发出
        currentTextChanged: 当前文本改变时发出

    示例:
        combo = ComboBox()
        combo.addItem("选项1")
        combo.addItem("选项2")
        combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(lambda index: print(f"选中: {index}"))
    """

    currentIndexChanged = pyqtSignal(int)
    currentTextChanged = pyqtSignal(str)

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
        
        self._arrow_icon_normal: Optional[QIcon] = None
        self._arrow_icon_hover: Optional[QIcon] = None
        self._arrow_icon_disabled: Optional[QIcon] = None
        
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._hover_animation: Optional[QPropertyAnimation] = None
        self._press_animation: Optional[QPropertyAnimation] = None
        
        self._bg_normal = QColor(0, 0, 0, 0)
        self._bg_hover = QColor(0, 0, 0, 0)
        self._bg_pressed = QColor(0, 0, 0, 0)
        self._bg_disabled = QColor(0, 0, 0, 0)
        self._bg_focused = QColor(0, 0, 0, 0)
        
        self._border_normal = QColor(0, 0, 0, 0)
        self._border_hover = QColor(0, 0, 0, 0)
        self._border_pressed = QColor(0, 0, 0, 0)
        self._border_disabled = QColor(0, 0, 0, 0)
        self._border_focused = QColor(0, 0, 0, 0)
        
        self._text_normal = QColor(0, 0, 0, 0)
        self._text_placeholder = QColor(0, 0, 0, 0)
        self._text_disabled = QColor(0, 0, 0, 0)
        
        self._arrow_normal = QColor(0, 0, 0, 0)
        self._arrow_hover = QColor(0, 0, 0, 0)
        self._arrow_disabled = QColor(0, 0, 0, 0)

        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug("ComboBox 初始化完成")

    def get_hover_progress(self) -> float:
        return self._hover_progress
    
    def set_hover_progress(self, value: float) -> None:
        self._hover_progress = value
        self.update()
    
    hoverProgress = pyqtProperty(float, get_hover_progress, set_hover_progress)
    
    def get_press_progress(self) -> float:
        return self._press_progress
    
    def set_press_progress(self, value: float) -> None:
        self._press_progress = value
        self.update()
    
    pressProgress = pyqtProperty(float, get_press_progress, set_press_progress)
    
    def _start_hover_animation(self, target: float) -> None:
        if self._hover_animation:
            self._hover_animation.stop()
        
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress")
        self._hover_animation.setDuration(ComboBoxAnimationConfig.HOVER_DURATION)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.start()
    
    def _start_press_animation(self, target: float) -> None:
        if self._press_animation:
            self._press_animation.stop()
        
        self._press_animation = QPropertyAnimation(self, b"pressProgress")
        self._press_animation.setDuration(ComboBoxAnimationConfig.PRESS_DURATION)
        self._press_animation.setStartValue(self._press_progress)
        self._press_animation.setEndValue(target)
        self._press_animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._press_animation.start()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        if self.isEnabled():
            self._start_hover_animation(1.0)
    
    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        if self.isEnabled():
            self._start_hover_animation(0.0)
    
    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if self.isEnabled():
            self._start_press_animation(1.0)
    
    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if self.isEnabled() and not self._is_popup_visible:
            self._start_press_animation(0.0)
    
    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self._is_focused = True
        self.update()
    
    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        self._is_focused = False
        self.update()
    
    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if not self._is_popup_visible:
                self._show_menu()
            return
        
        if event.key() == Qt.Key.Key_Down:
            if not self._is_popup_visible:
                self._show_menu()
            return
        
        if event.key() == Qt.Key.Key_Escape:
            if self._is_popup_visible and self._menu:
                self._menu.hide()
            return
        
        super().keyPressEvent(event)

    def sizeHint(self) -> QSize:
        base_size = super().sizeHint()

        arrow_space = ComboBoxConfig.ARROW_SIZE + ComboBoxConfig.ARROW_MARGIN * 2

        max_text_width = 0
        for item in self._items:
            text_width = self.fontMetrics().boundingRect(item.get('text', '')).width()
            max_text_width = max(max_text_width, text_width)

        width = max(ComboBoxConfig.MIN_WIDTH, max_text_width + arrow_space + 24)

        return QSize(width, max(base_size.height(), ComboBoxConfig.MIN_HEIGHT))

    def _on_clicked(self) -> None:
        if self._is_popup_visible:
            if self._menu:
                self._menu.hide()
        else:
            self._show_menu()

    def _show_menu(self) -> None:
        if not self._items:
            return

        self._menu = ComboBoxMenu()
        
        for item in self._items:
            self._menu.addItem(
                item.get('text', ''),
                item.get('icon'),
                item.get('userData')
            )
        
        self._menu.setCurrentIndex(self._current_index)
        self._menu.itemClicked.connect(self._on_menu_item_clicked)
        self._menu.aboutToHide.connect(self._on_menu_hidden)
        
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._menu.show_at(global_pos, self.width())
        
        self._is_popup_visible = True
        self._start_press_animation(1.0)

    def _on_menu_item_clicked(self, index: int) -> None:
        self.setCurrentIndex(index)
    
    def _on_menu_hidden(self) -> None:
        if self._is_popup_visible:
            self._is_popup_visible = False
            self._start_press_animation(0.0)

    def _on_theme_changed(self, theme: Theme) -> None:
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 ComboBox 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        start_time = time.time()

        if not theme:
            logger.debug("主题为空，跳过应用")
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')
        is_dark = theme.is_dark if hasattr(theme, 'is_dark') else True
        colors = ComboBoxConfig.get_colors(is_dark)
        
        self._bg_normal = self.get_style_color(theme, 'combobox.background.normal', colors['background_normal'])
        self._bg_hover = self.get_style_color(theme, 'combobox.background.hover', colors['background_hover'])
        self._bg_pressed = self.get_style_color(theme, 'combobox.background.pressed', colors['background_pressed'])
        self._bg_disabled = self.get_style_color(theme, 'combobox.background.disabled', colors['background_disabled'])
        self._bg_focused = self.get_style_color(theme, 'combobox.background.focused', colors['background_focused'])
        
        self._border_normal = self.get_style_color(theme, 'combobox.border.normal', colors['border_normal'])
        self._border_hover = self.get_style_color(theme, 'combobox.border.hover', colors['border_hover'])
        self._border_pressed = self.get_style_color(theme, 'combobox.border.pressed', colors['border_pressed'])
        self._border_disabled = self.get_style_color(theme, 'combobox.border.disabled', colors['border_disabled'])
        self._border_focused = self.get_style_color(theme, 'combobox.border.focused', colors['border_focused'])
        
        self._text_normal = self.get_style_color(theme, 'combobox.text.normal', colors['text_normal'])
        self._text_placeholder = self.get_style_color(theme, 'combobox.text.placeholder', colors['text_placeholder'])
        self._text_disabled = self.get_style_color(theme, 'combobox.text.disabled', colors['text_disabled'])
        
        self._arrow_normal = self.get_style_color(theme, 'combobox.arrow.normal', colors['arrow_normal'])
        self._arrow_hover = self.get_style_color(theme, 'combobox.arrow.hover', colors['arrow_hover'])
        self._arrow_disabled = self.get_style_color(theme, 'combobox.arrow.disabled', colors['arrow_disabled'])

        self.setStyleSheet(self._build_stylesheet())
        
        font = FontManager.get_body_font()
        self.setFont(font)
        
        self._update_arrow_icon()

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (耗时 {elapsed_time:.3f}s)")

    def _build_stylesheet(self) -> str:
        return f"""
        ComboBox {{
            background-color: transparent;
            border: none;
            padding: {ComboBoxConfig.PADDING_V}px {ComboBoxConfig.PADDING_H + ComboBoxConfig.ARROW_SIZE + ComboBoxConfig.ARROW_MARGIN}px {ComboBoxConfig.PADDING_V}px {ComboBoxConfig.PADDING_H}px;
            text-align: left;
        }}
        """

    def _update_arrow_icon(self) -> None:
        if not self._current_theme:
            return

        is_dark = self._current_theme.is_dark if hasattr(self._current_theme, 'is_dark') else True
        theme_type = "dark" if is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon_normal = self._icon_mgr.get_colored_icon(
            arrow_name, self._arrow_normal, ComboBoxConfig.ARROW_SIZE
        )
        self._arrow_icon_hover = self._icon_mgr.get_colored_icon(
            arrow_name, self._arrow_hover, ComboBoxConfig.ARROW_SIZE
        )
        self._arrow_icon_disabled = self._icon_mgr.get_colored_icon(
            arrow_name, self._arrow_disabled, ComboBoxConfig.ARROW_SIZE
        )
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        
        is_enabled = self.isEnabled()
        is_hovered = self._hover_progress > 0
        is_pressed = self._press_progress > 0 or self._is_popup_visible
        is_focused = self._is_focused
        
        if not is_enabled:
            bg_color = self._bg_disabled
            border_color = self._border_disabled
            text_color = self._text_disabled
        elif is_focused:
            bg_color = self._bg_focused
            border_color = self._border_focused
            text_color = self._text_normal
        elif is_pressed:
            bg_color = self._bg_pressed
            border_color = self._border_pressed
            text_color = self._text_normal
        elif is_hovered:
            bg_color = self._lerp_color(self._bg_normal, self._bg_hover, self._hover_progress)
            border_color = self._lerp_color(self._border_normal, self._border_hover, self._hover_progress)
            text_color = self._text_normal
        else:
            bg_color = self._bg_normal
            border_color = self._border_normal
            text_color = self._text_normal
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, ComboBoxConfig.BORDER_RADIUS, ComboBoxConfig.BORDER_RADIUS)
        
        if border_color.alpha() > 0:
            border_width = 2 if is_focused else 1
            painter.setPen(QPen(border_color, border_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, ComboBoxConfig.BORDER_RADIUS, ComboBoxConfig.BORDER_RADIUS)
        
        text = self.text()
        if text:
            is_placeholder = (self._current_index < 0 and self._placeholder_text)
            display_text_color = self._text_placeholder if is_placeholder else text_color
            
            text_rect = rect.adjusted(
                ComboBoxConfig.PADDING_H, 
                0, 
                -(ComboBoxConfig.ARROW_SIZE + ComboBoxConfig.ARROW_MARGIN * 2), 
                0
            )
            painter.setPen(display_text_color)
            painter.setFont(self.font())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        
        arrow_icon = None
        if not is_enabled:
            arrow_icon = self._arrow_icon_disabled
        elif is_pressed or is_hovered:
            arrow_icon = self._arrow_icon_hover
        else:
            arrow_icon = self._arrow_icon_normal
        
        if arrow_icon and not arrow_icon.isNull():
            arrow_size = ComboBoxConfig.ARROW_SIZE
            arrow_margin = ComboBoxConfig.ARROW_MARGIN

            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2
            
            arrow_icon.paint(painter, x, y, arrow_size, arrow_size)
    
    def _lerp_color(self, c1: QColor, c2: QColor, t: float) -> QColor:
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        return QColor(r, g, b, a)

    def _update_display_text(self) -> None:
        if self._current_index >= 0 and self._current_index < len(self._items):
            text = self._items[self._current_index].get('text', '')
            self.setText(text)
        elif self._placeholder_text:
            self.setText(self._placeholder_text)
        else:
            self.setText("")

    def addItem(self, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.append(item)

        if self._current_index < 0:
            self.setCurrentIndex(0)
        else:
            self._update_display_text()

        logger.debug(f"添加项目: '{text}'")

    def addItems(self, texts: List[str]) -> None:
        for text in texts:
            self.addItem(text)

        logger.debug(f"添加 {len(texts)} 个项目")

    def insertItem(self, index: int, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.insert(index, item)

        if self._current_index < 0:
            self.setCurrentIndex(0)
        elif index <= self._current_index:
            self._current_index += 1
            self._update_display_text()

        logger.debug(f"在位置 {index} 插入项目: '{text}'")

    def insertItems(self, index: int, texts: List[str]) -> None:
        for i, text in enumerate(texts):
            self.insertItem(index + i, text)

        logger.debug(f"在位置 {index} 插入 {len(texts)} 个项目")

    def removeItem(self, index: int) -> None:
        if index < 0 or index >= len(self._items):
            return

        del self._items[index]

        if len(self._items) == 0:
            self._current_index = -1
        elif index < self._current_index:
            self._current_index -= 1
        elif index == self._current_index:
            if self._current_index >= len(self._items):
                self._current_index = len(self._items) - 1

        self._update_display_text()

        logger.debug(f"移除位置 {index} 的项目")

    def clear(self) -> None:
        self._items.clear()
        self._current_index = -1
        self._update_display_text()

        logger.debug("清空所有项目")

    def count(self) -> int:
        return len(self._items)

    def currentIndex(self) -> int:
        return self._current_index

    def setCurrentIndex(self, index: int) -> None:
        if index < -1 or index >= len(self._items):
            return

        old_index = self._current_index
        self._current_index = index

        self._update_display_text()

        if old_index != index:
            self.currentIndexChanged.emit(index)
            if index >= 0:
                self.currentTextChanged.emit(self._items[index].get('text', ''))

        logger.debug(f"设置当前索引: {index}")

    def currentText(self) -> str:
        if self._current_index >= 0 and self._current_index < len(self._items):
            return self._items[self._current_index].get('text', '')
        return ""

    def setCurrentText(self, text: str) -> None:
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                self.setCurrentIndex(i)
                return

    def itemText(self, index: int) -> str:
        if 0 <= index < len(self._items):
            return self._items[index].get('text', '')
        return ""

    def setItemText(self, index: int, text: str) -> None:
        if 0 <= index < len(self._items):
            self._items[index]['text'] = text
            if index == self._current_index:
                self._update_display_text()

    def itemIcon(self, index: int) -> Optional[QIcon]:
        if 0 <= index < len(self._items):
            return self._items[index].get('icon')
        return None

    def setItemIcon(self, index: int, icon: QIcon) -> None:
        if 0 <= index < len(self._items):
            self._items[index]['icon'] = icon

    def itemData(self, index: int) -> Any:
        if 0 <= index < len(self._items):
            return self._items[index].get('userData')
        return None

    def setItemData(self, index: int, userData: Any) -> None:
        if 0 <= index < len(self._items):
            self._items[index]['userData'] = userData

    def findText(self, text: str) -> int:
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                return i
        return -1

    def findData(self, data: Any) -> int:
        for i, item in enumerate(self._items):
            if item.get('userData') == data:
                return i
        return -1

    def placeholderText(self) -> str:
        return self._placeholder_text

    def setPlaceholderText(self, text: str) -> None:
        self._placeholder_text = text
        if self._current_index < 0:
            self._update_display_text()

    def set_global_theme(self, name: str) -> None:
        logger.debug(f"设置全局主题: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        try:
            if self._current_theme is not None:
                theme_name = getattr(self._current_theme, 'name', None)
                if theme_name is not None:
                    return str(theme_name)
            return None
        except Exception as e:
            logger.warning(f"获取主题名称时出错: {e}")
            return None

    def _on_widget_destroyed(self) -> None:
        if not self._cleanup_done:
            self.cleanup()

    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("ComboBox 已取消主题订阅")

        self._clear_stylesheet_cache()
        self.clear_overrides()
        
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.deleteLater()
            self._hover_animation = None
        
        if self._press_animation:
            self._press_animation.stop()
            self._press_animation.deleteLater()
            self._press_animation = None

    def showPopup(self) -> None:
        if self._items:
            self._show_menu()

    def hidePopup(self) -> None:
        if self._menu:
            self._menu.hide()
