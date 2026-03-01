"""
可编辑组合框组件

提供可编辑的组合框，具有以下特性：
- 继承自 QLineEdit，允许用户编辑当前选项
- 按下回车可添加新选项
- 点击下拉按钮弹出 RoundMenu 下拉列表
- 主题集成，自动更新样式
- 支持正常、悬停、聚焦、禁用状态
- 支持自动补全
"""

import logging
import time
from typing import Optional, Dict, Tuple, Any, List
from PyQt6.QtCore import QSize, QPoint, Qt, pyqtSignal, QRect, QStringListModel
from PyQt6.QtGui import QColor, QIcon, QPainter, QKeyEvent
from PyQt6.QtWidgets import QLineEdit, QWidget, QSizePolicy, QCompleter
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager
from core.style_override import StyleOverrideMixin
from components.menus.round_menu import RoundMenu, MenuConfig

logger = logging.getLogger(__name__)


class EditableComboBoxConfig:
    """
    可编辑组合框行为和样式的配置常量。

    Attributes:
        DEFAULT_HORIZONTAL_POLICY: 默认水平尺寸策略
        DEFAULT_VERTICAL_POLICY: 默认垂直尺寸策略
        DEFAULT_PADDING: 默认内边距
        DEFAULT_BORDER_RADIUS: 默认边框圆角
        DEFAULT_ARROW_SIZE: 下拉箭头尺寸
        DEFAULT_ARROW_MARGIN: 箭头与文本间距
        DEFAULT_MIN_WIDTH: 默认最小宽度
        DEFAULT_MIN_HEIGHT: 默认最小高度
        MAX_STYLESHEET_CACHE_SIZE: 样式缓存最大数量
    """

    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Preferred
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    DEFAULT_PADDING = '8px 32px 8px 12px'
    DEFAULT_BORDER_RADIUS = 6
    DEFAULT_ARROW_SIZE = 12
    DEFAULT_ARROW_MARGIN = 10
    DEFAULT_MIN_WIDTH = 200
    DEFAULT_MIN_HEIGHT = 36
    MAX_STYLESHEET_CACHE_SIZE = 100


class EditableComboBox(QLineEdit, StyleOverrideMixin):
    """
    可编辑组合框组件，继承自 QLineEdit。

    特性：
    - 允许用户编辑当前选项
    - 按下回车可添加新选项
    - 点击下拉按钮弹出下拉列表
    - 主题集成，自动响应主题切换
    - 支持正常、悬停、聚焦、禁用状态
    - 优化的样式缓存机制
    - 内存安全，支持正确的清理机制
    - 本地样式覆盖，不影响共享主题
    - 支持自动补全

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
        """
        初始化可编辑组合框。

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._init_style_override()

        self.setMinimumSize(
            EditableComboBoxConfig.DEFAULT_MIN_WIDTH,
            EditableComboBoxConfig.DEFAULT_MIN_HEIGHT
        )

        self.setSizePolicy(
            EditableComboBoxConfig.DEFAULT_HORIZONTAL_POLICY,
            EditableComboBoxConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._icon_mgr = IconManager.instance()
        self._current_theme: Optional[Theme] = None

        self._items: List[Dict[str, Any]] = []
        self._current_index: int = -1

        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        self._menu: Optional[RoundMenu] = None
        self._arrow_icon: Optional[QIcon] = None

        self._completer: Optional[QCompleter] = None
        self._completer_enabled: bool = True

        self._theme_mgr.subscribe(self, self._on_theme_changed)

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

    def sizeHint(self) -> QSize:
        """
        返回组合框的建议尺寸。

        确保宽度足够容纳最长文本和下拉箭头。
        """
        base_size = super().sizeHint()

        arrow_space = EditableComboBoxConfig.DEFAULT_ARROW_SIZE + EditableComboBoxConfig.DEFAULT_ARROW_MARGIN * 2

        max_text_width = 0
        for item in self._items:
            text_width = self.fontMetrics().boundingRect(item.get('text', '')).width()
            max_text_width = max(max_text_width, text_width)

        width = max(EditableComboBoxConfig.DEFAULT_MIN_WIDTH, max_text_width + arrow_space + 24)

        return QSize(width, base_size.height())

    def _on_text_edited(self, text: str) -> None:
        """
        处理文本编辑事件。

        Args:
            text: 编辑后的文本
        """
        index = self.findText(text)
        if index >= 0:
            self._current_index = index
        else:
            self._current_index = -1

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        处理键盘事件。

        回车键添加新选项或确认当前选项。

        Args:
            event: 键盘事件
        """
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

    def mousePressEvent(self, event) -> None:
        """处理鼠标按下事件。"""
        arrow_rect = self._get_arrow_rect()
        if arrow_rect.contains(event.pos()):
            self._toggle_menu()
            return

        super().mousePressEvent(event)

    def _get_arrow_rect(self) -> QRect:
        """
        获取下拉箭头的矩形区域。

        Returns:
            箭头区域的 QRect
        """
        arrow_size = EditableComboBoxConfig.DEFAULT_ARROW_SIZE
        arrow_margin = EditableComboBoxConfig.DEFAULT_ARROW_MARGIN
        return QRect(
            self.width() - arrow_size - arrow_margin - 4,
            (self.height() - arrow_size) // 2 - 4,
            arrow_size + 8,
            arrow_size + 8
        )

    def _toggle_menu(self) -> None:
        """切换下拉菜单显示状态。"""
        if self._menu and self._menu.isVisible():
            self._menu.hide()
        else:
            self._show_menu()

    def _show_menu(self) -> None:
        """显示下拉列表。"""
        if not self._items:
            return

        self._menu = RoundMenu()

        for i, item in enumerate(self._items):
            text = item.get('text', '')
            icon = item.get('icon')
            callback = lambda idx=i: self._on_item_selected(idx)
            self._menu.addAction(text, callback, icon=icon)

        margin = MenuConfig.DEFAULT_MARGIN
        global_pos = self.mapToGlobal(QPoint(-margin, self.height() + 4))
        self._menu.exec(global_pos)

    def _on_item_selected(self, index: int) -> None:
        """
        处理菜单项选中事件。

        Args:
            index: 选中的项索引
        """
        self.setCurrentIndex(index)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题管理器发出的主题变化通知。

        Args:
            theme: 新的主题对象
        """
        try:
            self._apply_theme(theme)
        except Exception as e:
            logger.error(f"应用主题到 EditableComboBox 时出错: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到组合框，支持缓存和性能监控。

        Args:
            theme: 包含颜色和样式定义的主题对象
        """
        start_time = time.time()

        if not theme:
            logger.debug("主题为空，跳过应用")
            return

        self._current_theme = theme
        theme_name = getattr(theme, 'name', 'unnamed')

        cache_key = (theme_name,)

        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            qss = self._build_stylesheet(theme)
            if len(self._stylesheet_cache) < EditableComboBoxConfig.MAX_STYLESHEET_CACHE_SIZE:
                self._stylesheet_cache[cache_key] = qss

        self.setStyleSheet(qss)
        self.style().unpolish(self)
        self.style().polish(self)

        self._update_arrow_icon()

        elapsed_time = time.time() - start_time
        logger.debug(f"主题已应用: {theme_name} (缓存大小: {len(self._stylesheet_cache)}, 耗时 {elapsed_time:.3f}s)")

    def _build_stylesheet(self, theme: Theme) -> str:
        """
        构建组合框的样式表。

        Args:
            theme: 主题对象

        Returns:
            完整的 QSS 样式表字符串
        """
        bg_normal = self.get_style_color(theme, 'combobox.background.normal',
                                         theme.get_color('input.background.normal', QColor(58, 58, 58)))
        bg_hover = self.get_style_color(theme, 'combobox.background.hover',
                                        theme.get_color('input.background.normal', QColor(58, 58, 58)))
        bg_focus = self.get_style_color(theme, 'combobox.background.focus',
                                        theme.get_color('input.background.normal', QColor(58, 58, 58)))
        bg_disabled = self.get_style_color(theme, 'combobox.background.disabled',
                                           theme.get_color('input.background.disabled', QColor(42, 42, 42)))

        text_normal = self.get_style_color(theme, 'combobox.text.normal',
                                           theme.get_color('input.text.normal', QColor(224, 224, 224)))
        text_disabled = self.get_style_color(theme, 'combobox.text.disabled',
                                             theme.get_color('input.text.disabled', QColor(102, 102, 102)))
        placeholder_color = self.get_style_color(theme, 'combobox.text.placeholder',
                                                 theme.get_color('input.text.placeholder', QColor(170, 170, 170)))

        border_normal = self.get_style_color(theme, 'combobox.border.normal',
                                             theme.get_color('input.border.normal', QColor(68, 68, 68)))
        border_hover = self.get_style_color(theme, 'combobox.border.hover',
                                            theme.get_color('input.border.focus', QColor(93, 173, 226)))
        border_focus = self.get_style_color(theme, 'combobox.border.focus',
                                            theme.get_color('input.border.focus', QColor(93, 173, 226)))
        border_disabled = self.get_style_color(theme, 'combobox.border.disabled',
                                               theme.get_color('input.border.disabled', QColor(51, 51, 51)))

        padding = self.get_style_value(theme, 'combobox.padding', EditableComboBoxConfig.DEFAULT_PADDING)
        border_radius = self.get_style_value(theme, 'combobox.border_radius', EditableComboBoxConfig.DEFAULT_BORDER_RADIUS)

        qss = f"""
        EditableComboBox {{
            background-color: {bg_normal.name()};
            color: {text_normal.name()};
            border: 1px solid {border_normal.name()};
            border-radius: {border_radius}px;
            padding: {padding};
            selection-background-color: rgba(93, 173, 226, 0.3);
        }}
        EditableComboBox:hover {{
            background-color: {bg_hover.name()};
            border: 1px solid {border_hover.name()};
        }}
        EditableComboBox:focus {{
            background-color: {bg_focus.name()};
            border: 1px solid {border_focus.name()};
        }}
        EditableComboBox:disabled {{
            background-color: {bg_disabled.name()};
            color: {text_disabled.name()};
            border: 1px solid {border_disabled.name()};
        }}
        EditableComboBox::placeholder {{
            color: {placeholder_color.name()};
        }}
        """

        return qss

    def _update_arrow_icon(self) -> None:
        """更新下拉箭头图标。"""
        if not self._current_theme:
            return

        arrow_color = self._current_theme.get_color('combobox.arrow.normal',
                                                    self._current_theme.get_color('button.icon.normal', QColor(200, 200, 200)))

        theme_type = "dark" if self._current_theme.is_dark else "light"
        arrow_name = self._icon_mgr.resolve_icon_name("ChevronDown", theme_type)

        self._arrow_icon = self._icon_mgr.get_colored_icon(arrow_name, arrow_color, EditableComboBoxConfig.DEFAULT_ARROW_SIZE)
        self.update()

    def paintEvent(self, event) -> None:
        """重写绘制事件，绘制下拉箭头。"""
        super().paintEvent(event)

        if self._arrow_icon and not self._arrow_icon.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            arrow_size = EditableComboBoxConfig.DEFAULT_ARROW_SIZE
            arrow_margin = EditableComboBoxConfig.DEFAULT_ARROW_MARGIN

            x = self.width() - arrow_size - arrow_margin
            y = (self.height() - arrow_size) // 2

            self._arrow_icon.paint(painter, x, y, arrow_size, arrow_size)

    # ========== QComboBox 接口实现 ==========

    def addItem(self, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        """
        添加一个项目到组合框。

        Args:
            text: 项目文本
            icon: 可选图标
            userData: 可选用户数据
        """
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.append(item)

        self._update_completer_model()

        if self._current_index < 0:
            self.setCurrentIndex(0)

        logger.debug(f"添加项目: '{text}'")

    def addItems(self, texts: List[str]) -> None:
        """
        添加多个项目到组合框。

        Args:
            texts: 项目文本列表
        """
        for text in texts:
            item = {'text': text, 'icon': None, 'userData': None}
            self._items.append(item)

        self._update_completer_model()

        if self._current_index < 0:
            self.setCurrentIndex(0)

        logger.debug(f"添加 {len(texts)} 个项目")

    def insertItem(self, index: int, text: str, icon: Optional[QIcon] = None, userData: Any = None) -> None:
        """
        在指定位置插入项目。

        Args:
            index: 插入位置
            text: 项目文本
            icon: 可选图标
            userData: 可选用户数据
        """
        item = {'text': text, 'icon': icon, 'userData': userData}
        self._items.insert(index, item)

        self._update_completer_model()

        if self._current_index < 0:
            self.setCurrentIndex(0)
        elif index <= self._current_index:
            self._current_index += 1

        logger.debug(f"在位置 {index} 插入项目: '{text}'")

    def insertItems(self, index: int, texts: List[str]) -> None:
        """
        在指定位置插入多个项目。

        Args:
            index: 插入位置
            texts: 项目文本列表
        """
        for i, text in enumerate(texts):
            self.insertItem(index + i, text)

        logger.debug(f"在位置 {index} 插入 {len(texts)} 个项目")

    def removeItem(self, index: int) -> None:
        """
        移除指定位置的项目。

        Args:
            index: 项目索引
        """
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
        """
        获取项目数量。

        Returns:
            项目数量
        """
        return len(self._items)

    def currentIndex(self) -> int:
        """
        获取当前选中索引。

        Returns:
            当前索引，如果没有选中则返回 -1
        """
        return self._current_index

    def setCurrentIndex(self, index: int) -> None:
        """
        设置当前选中索引。

        Args:
            index: 要选中的索引
        """
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
        """
        获取当前选中文本。

        Returns:
            当前选中文本
        """
        return self.text()

    def setCurrentText(self, text: str) -> None:
        """
        设置当前选中文本。

        Args:
            text: 要选中的文本
        """
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                self.setCurrentIndex(i)
                return

        self.setText(text)

    def itemText(self, index: int) -> str:
        """
        获取指定索引的项目文本。

        Args:
            index: 项目索引

        Returns:
            项目文本
        """
        if 0 <= index < len(self._items):
            return self._items[index].get('text', '')
        return ""

    def setItemText(self, index: int, text: str) -> None:
        """
        设置指定索引的项目文本。

        Args:
            index: 项目索引
            text: 新文本
        """
        if 0 <= index < len(self._items):
            self._items[index]['text'] = text
            self._update_completer_model()
            if index == self._current_index:
                self.setText(text)

    def itemIcon(self, index: int) -> Optional[QIcon]:
        """
        获取指定索引的项目图标。

        Args:
            index: 项目索引

        Returns:
            项目图标
        """
        if 0 <= index < len(self._items):
            return self._items[index].get('icon')
        return None

    def setItemIcon(self, index: int, icon: QIcon) -> None:
        """
        设置指定索引的项目图标。

        Args:
            index: 项目索引
            icon: 新图标
        """
        if 0 <= index < len(self._items):
            self._items[index]['icon'] = icon

    def itemData(self, index: int) -> Any:
        """
        获取指定索引的项目用户数据。

        Args:
            index: 项目索引

        Returns:
            用户数据
        """
        if 0 <= index < len(self._items):
            return self._items[index].get('userData')
        return None

    def setItemData(self, index: int, userData: Any) -> None:
        """
        设置指定索引的项目用户数据。

        Args:
            index: 项目索引
            userData: 用户数据
        """
        if 0 <= index < len(self._items):
            self._items[index]['userData'] = userData

    def findText(self, text: str) -> int:
        """
        查找包含指定文本的项目索引。

        Args:
            text: 要查找的文本

        Returns:
            项目索引，如果未找到则返回 -1
        """
        for i, item in enumerate(self._items):
            if item.get('text') == text:
                return i
        return -1

    def findData(self, data: Any) -> int:
        """
        查找包含指定用户数据的项目索引。

        Args:
            data: 要查找的用户数据

        Returns:
            项目索引，如果未找到则返回 -1
        """
        for i, item in enumerate(self._items):
            if item.get('userData') == data:
                return i
        return -1

    def setCompleterEnabled(self, enabled: bool) -> None:
        """
        设置是否启用自动补全。

        Args:
            enabled: 是否启用
        """
        self._completer_enabled = enabled
        if enabled:
            self._update_completer_model()
        else:
            self.setCompleter(None)

    def isCompleterEnabled(self) -> bool:
        """
        获取是否启用自动补全。

        Returns:
            是否启用自动补全
        """
        return self._completer_enabled

    def set_global_theme(self, name: str) -> None:
        """
        设置全局主题。

        注意：此方法会改变整个应用程序的主题，而不仅仅是此组件。

        Args:
            name: 主题名称（如 'dark', 'light', 'default'）
        """
        logger.debug(f"设置全局主题: {name}")
        self._theme_mgr.set_theme(name)

    def get_theme(self) -> Optional[str]:
        """
        获取当前主题名称。

        Returns:
            当前主题名称，如果未设置主题则返回 None
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

    def set_padding(self, padding: str) -> None:
        """
        设置组合框内边距。

        Args:
            padding: 内边距值，如 '8px 12px' 或 '8px'
        """
        if not isinstance(padding, str) or not padding.strip():
            logger.warning(f"无效的内边距值: {padding}")
            return

        logger.debug(f"设置内边距: {padding}")
        self.override_style('combobox.padding', padding)
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def cleanup(self) -> None:
        """
        清理资源。

        取消主题订阅，清空缓存，释放资源。
        """
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            logger.debug("EditableComboBox 已取消主题订阅")

        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
            logger.debug("样式缓存已清空")

        self.clear_overrides()

    def __del__(self) -> None:
        """析构函数，自动清理资源。"""
        try:
            self.cleanup()
        except Exception:
            pass

    def showPopup(self) -> None:
        """显示下拉列表（公开方法）。"""
        if self._items:
            self._show_menu()

    def hidePopup(self) -> None:
        """隐藏下拉列表。"""
        if self._menu:
            self._menu.hide()
