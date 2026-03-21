"""
主题管理模块

为 PyQt 组件提供全局主题注册表和动态主题切换功能。
"""
import logging
import weakref
from typing import Dict, Any, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class Theme:
    """
    不可变主题数据容器。

    存储样式参数（颜色、字体、边框等），支持嵌套键访问
    （如 'button.hover.background'）。
    """

    def __init__(self, name: str, style_data: Dict[str, Any]):
        """
        初始化主题对象。

        Args:
            name: 主题名称/标识符
            style_data: 样式数据字典
        """
        super().__init__()
        self._name = name
        # 复制数据以避免外部修改影响主题
        self._style_data = style_data.copy() if style_data else {}

    @property
    def name(self) -> str:
        """主题名称/标识符。"""
        return self._name
    
    @property
    def is_dark(self) -> bool:
        """
        判断是否为暗色主题。

        直接读取主题配置中的 'is_dark' 字段。

        Returns:
            如果是暗色主题返回 True，否则返回 False
        """
        # 直接从配置读取 is_dark 字段
        is_dark_value = self._get_nested_value('is_dark')
        if is_dark_value is not None:
            return bool(is_dark_value)
        
        # 如果配置中没有 is_dark 字段，默认返回 True（暗色主题）
        # 建议在主题配置中明确设置 is_dark 字段
        return True

    def get_color(self, key: str, default: QColor = None) -> QColor:
        """
        通过键路径获取颜色值。

        Args:
            key: 点分隔的路径（如 'button.background.hover'）
            default: 未找到时的默认颜色

        Returns:
            QColor 颜色值或默认值
        """
        if default is None:
            default = QColor()

        value = self._get_nested_value(key)
        if isinstance(value, QColor):
            return value

        # 将各种格式转换为 QColor
        return self._to_color(value, default)

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        通过键路径获取任意主题值。

        Args:
            key: 点分隔的路径
            default: 未找到时的默认值

        Returns:
            主题值或默认值
        """
        value = self._get_nested_value(key)
        return value if value is not None else default

    def _get_nested_value(self, key: str) -> Any:
        """
        使用点号语法获取嵌套值。

        Args:
            key: 点分隔的键路径

        Returns:
            找到的值，如果不存在则返回 None
        """
        parts = key.split('.')
        value = self._style_data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None
        return value

    def _to_color(self, value: Any, default: QColor) -> QColor:
        """
        将各种颜色格式转换为 QColor。

        支持的格式：
        - QColor 对象
        - 十六进制字符串（如 '#FF0000'）
        - 颜色名称（如 'red'）
        - RGB 元组 (r, g, b)
        - RGBA 元组 (r, g, b, a)

        Args:
            value: 要转换的值
            default: 转换失败时的默认颜色

        Returns:
            QColor 对象
        """
        if isinstance(value, QColor):
            return value
        elif isinstance(value, str):
            # 十六进制颜色或命名颜色
            color = QColor(value)
            return color if color.isValid() else default
        elif isinstance(value, (tuple, list)) and len(value) >= 3:
            # RGB 或 RGBA 元组
            if len(value) == 3:
                return QColor(int(value[0]), int(value[1]), int(value[2]))
            elif len(value) == 4:
                return QColor(int(value[0]), int(value[1]), int(value[2]), int(value[3]))
        return default

    def to_dict(self) -> Dict[str, Any]:
        """
        返回完整的主题数据副本。

        Returns:
            主题数据字典的副本
        """
        return self._style_data.copy()

    def with_override(self, key: str, value: Any) -> 'Theme':
        """
        创建一个带有单个值覆盖的新主题。

        此方法返回一个新的 Theme 实例，保持原主题的不可变性。

        Args:
            key: 点分隔的路径（如 'button.border_radius'）
            value: 要设置的值

        Returns:
            应用了覆盖的新 Theme 实例
        """
        new_data = self._copy_with_override(self._style_data, key.split('.'), value)
        return Theme(f"{self._name}_override", new_data)
    
    def _copy_with_override(self, data: Dict, keys: list, value: Any) -> Dict:
        """
        递归复制数据结构并应用覆盖（惰性复制）。

        只复制键路径上的字典，其他部分保持引用，节省内存和时间。

        Args:
            data: 原始数据字典
            keys: 键路径列表（如 ['button', 'border_radius']）
            value: 要设置的值

        Returns:
            复制后的新字典

        示例:
            输入 data:
            {
                'button': {
                    'background': '#3c3c3c',
                    'border_radius': 6
                },
                'label': {
                    'color': '#ffffff'
                }
            }
            
            调用: _copy_with_override(data, ['button', 'border_radius'], 10)
            
            输出 result:
            {
                'button': {                    # 新字典（复制）
                    'background': '#3c3c3c',   # 引用原值
                    'border_radius': 10        # 新值（覆盖）
                },
                'label': { ... }               # 引用原字典（未复制）
            }
        """
        # 浅拷贝当前层级
        result = data.copy()
        
        if len(keys) == 1:
            # 到达目标键，直接设置值
            result[keys[0]] = value
        else:
            # 需要继续深入
            current_key = keys[0]
            if current_key in result and isinstance(result[current_key], dict):
                # 递归复制下一层级（惰性：只复制路径上的字典）
                result[current_key] = self._copy_with_override(result[current_key], keys[1:], value)
            else:
                # 路径不存在，创建新字典
                result[current_key] = {}
                self._set_nested(result[current_key], keys[1:], value)
        return result
    
    def _set_nested(self, data: Dict, keys: list, value: Any) -> None:
        """
        在字典中设置嵌套值（原地修改）。

        递归创建不存在的中间字典，直到到达目标键。

        Args:
            data: 目标字典
            keys: 键路径列表（如 ['button', 'border_radius']）
            value: 要设置的值

        示例:
            输入 data:
            {}
            
            调用: _set_nested(data, ['button', 'border_radius'], 10)
            
            输出 data（原地修改）:
            {
                'button': {
                    'border_radius': 10
                }
            }
            
            再调用: _set_nested(data, ['button', 'padding'], '8px')
            
            输出 data:
            {
                'button': {
                    'border_radius': 10,
                    'padding': '8px'
                }
            }

            # 调用: _set_nested(data, ['is_dark'], True)
            # keys = ['is_dark']
            # len(keys) = 1，✅ 直接触发
            # data['is_dark'] = True
            # 结果: data = {'is_dark': True}
        """
        if len(keys) == 1:
            data[keys[0]] = value
        else:
            if keys[0] not in data:
                data[keys[0]] = {}
            self._set_nested(data[keys[0]], keys[1:], value)

    def __repr__(self) -> str:
        return f"Theme(name='{self._name}')"


class ThemeManager(QObject):
    """
    全局主题注册表和管理器（单例模式）。

    职责：
    - 按名称注册和检索主题
    - 向组件应用主题
    - 通知所有订阅者主题变化
    - 提供 QSS 扩展支持

    使用示例:
        theme_mgr = ThemeManager.instance()
        theme_mgr.register_theme_dict('dark', DARK_THEME)
        theme_mgr.set_theme('dark')
    """

    _instance: Optional['ThemeManager'] = None

    themeChanged = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化主题管理器。

        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._subscribers: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
        
        self._batch_timer: Optional['QTimer'] = None
        self._pending_theme: Optional[Theme] = None
        self._is_batching = False
        self._global_stylesheet_cache: Dict[str, str] = {}
        self._use_global_stylesheet = True

    @classmethod
    def instance(cls) -> 'ThemeManager':
        """
        获取单例实例。

        Returns:
            ThemeManager 的唯一实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_theme(self, theme: Theme) -> None:
        """
        注册主题对象。

        Args:
            theme: 要注册的 Theme 实例
        """
        self._themes[theme.name] = theme

    def register_theme_dict(self, name: str, style_data: Dict[str, Any]) -> Theme:
        """
        从字典创建并注册主题。

        Args:
            name: 主题名称
            style_data: 样式值字典

        Returns:
            创建的 Theme 实例
        """
        theme = Theme(name, style_data)
        self.register_theme(theme)
        return theme

    def register_theme_file(self, name: str, file_path: str) -> Theme:
        """
        从 Python 文件加载并注册主题。

        文件应包含 THEME_DATA 字典。

        Args:
            name: 主题名称
            file_path: 主题文件路径

        Returns:
            创建的 Theme 实例

        Raises:
            ValueError: 如果文件不包含 THEME_DATA 字典
        """
        import importlib.util
        import sys
        # Python 的 动态导入机制 ，用于在运行时从文件路径加载 Python 模块。
        spec = importlib.util.spec_from_file_location(f"theme_{name}", file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"theme_{name}"] = module
        spec.loader.exec_module(module)

        if hasattr(module, 'THEME_DATA'):
            return self.register_theme_dict(name, module.THEME_DATA)
        else:
            raise ValueError(f"主题文件 '{file_path}' 必须包含 THEME_DATA 字典")

    def get_theme(self, name: str) -> Optional[Theme]:
        """
        按名称检索主题。

        Args:
            name: 主题名称

        Returns:
            Theme 实例，如果未找到则返回 None
        """
        return self._themes.get(name)

    def set_theme(self, theme_name: str) -> None:
        """
        设置当前主题并通知所有订阅者。

        Args:
            theme_name: 要激活的主题名称

        Raises:
            ValueError: 如果主题未注册

        示例:
            ThemeManager.instance().set_theme('dark')
        """
        logger.debug(f"set_theme 调用: {theme_name}")
        theme = self._themes.get(theme_name)
        if not theme:
            raise ValueError(f"主题 '{theme_name}' 未注册")

        import time
        start_time = time.perf_counter()

        logger.debug(f"找到主题: {theme.name if hasattr(theme, 'name') else 'Unknown'}")
        self._current_theme = theme
        self.themeChanged.emit(theme_name)

        if self._use_global_stylesheet:
            self._apply_global_stylesheet(theme)
            self._apply_palette(theme)

        self._schedule_batch_notify()

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.info(f"主题切换耗时: {elapsed:.2f}ms")

    def _apply_global_stylesheet(self, theme: Theme) -> None:
        """应用全局样式表到 QApplication。"""
        from PyQt6.QtWidgets import QApplication
        
        if not QApplication.instance():
            return

        theme_name = theme.name
        if theme_name not in self._global_stylesheet_cache:
            self._global_stylesheet_cache[theme_name] = self._build_global_stylesheet(theme)
        
        global_qss = self._global_stylesheet_cache[theme_name]
        QApplication.instance().setStyleSheet(global_qss)
        logger.debug(f"全局样式表已应用: {len(global_qss)} 字节")

    def _build_global_stylesheet(self, theme: Theme) -> str:
        """
        构建全局样式表。

        Args:
            theme: 主题对象

        Returns:
            全局样式表字符串
        """
        parts = []

        bg_primary = theme.get_color('background.primary', QColor(35, 35, 35))
        bg_secondary = theme.get_color('background.secondary', QColor(45, 45, 45))
        bg_tertiary = theme.get_color('background.tertiary', QColor(30, 30, 30))
        text_primary = theme.get_color('text.primary', QColor(230, 230, 230))
        text_secondary = theme.get_color('text.secondary', QColor(180, 180, 180))
        text_disabled = theme.get_color('text.disabled', QColor(120, 120, 120))
        border_default = theme.get_color('border.default', QColor(60, 60, 60))
        primary_color = theme.get_color('primary.main', QColor(0, 120, 212))

        def _color(c: QColor) -> str:
            return c.name(QColor.NameFormat.HexArgb)

        parts.append(f"""
/* Global Base Styles */
QWidget {{
    color: {_color(text_primary)};
    font-family: "Segoe UI Variable", "Segoe UI", "Microsoft YaHei UI", sans-serif;
}}

QMainWindow, QDialog {{
    background-color: {_color(bg_primary)};
}}

QLabel {{
    color: {_color(text_primary)};
    background: transparent;
}}

QLabel:disabled {{
    color: {_color(text_disabled)};
}}

/* ScrollBar */
QScrollBar:vertical {{
    background: {_color(bg_secondary)};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {_color(text_secondary)};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {_color(bg_secondary)};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {_color(text_secondary)};
    min-width: 30px;
    border-radius: 5px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ToolTip */
QToolTip {{
    background-color: {_color(bg_secondary)};
    color: {_color(text_primary)};
    border: 1px solid {_color(border_default)};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* Menu */
QMenu {{
    background-color: {_color(bg_secondary)};
    border: 1px solid {_color(border_default)};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {_color(primary_color)};
}}

QMenu::separator {{
    height: 1px;
    background: {_color(border_default)};
    margin: 4px 8px;
}}

/* Slider */
QSlider::groove:horizontal {{
    background: {_color(bg_tertiary)};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {_color(primary_color)};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

/* ProgressBar */
QProgressBar {{
    background: {_color(bg_tertiary)};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: {_color(primary_color)};
    border-radius: 4px;
}}
""")

        return "\n".join(parts)

    def _apply_palette(self, theme: Theme) -> None:
        """
        应用 QPalette 到 QApplication。

        QPalette 比样式表更高效，适用于基本颜色设置。

        Args:
            theme: 主题对象
        """
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPalette
        
        app = QApplication.instance()
        if not app:
            return

        bg_primary = theme.get_color('background.primary', QColor(35, 35, 35))
        bg_secondary = theme.get_color('background.secondary', QColor(45, 45, 45))
        text_primary = theme.get_color('text.primary', QColor(230, 230, 230))
        text_secondary = theme.get_color('text.secondary', QColor(180, 180, 180))
        text_disabled = theme.get_color('text.disabled', QColor(120, 120, 120))
        primary_color = theme.get_color('primary.main', QColor(0, 120, 212))
        accent_color = theme.get_color('accent.primary', QColor(0, 120, 212))
        border_default = theme.get_color('border.default', QColor(60, 60, 60))

        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, bg_primary)
        palette.setColor(QPalette.ColorRole.WindowText, text_primary)
        palette.setColor(QPalette.ColorRole.Base, bg_secondary)
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_primary)
        palette.setColor(QPalette.ColorRole.ToolTipBase, bg_secondary)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_primary)
        palette.setColor(QPalette.ColorRole.Text, text_primary)
        palette.setColor(QPalette.ColorRole.Button, bg_secondary)
        palette.setColor(QPalette.ColorRole.ButtonText, text_primary)
        palette.setColor(QPalette.ColorRole.BrightText, text_primary)
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, primary_color)
        palette.setColor(QPalette.ColorRole.PlaceholderText, text_secondary)

        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, text_disabled)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, text_disabled)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, text_disabled)

        app.setPalette(palette)
        logger.debug("QPalette 已应用")

    def _schedule_batch_notify(self) -> None:
        """调度批量通知，延迟执行以合并多次主题变化。"""
        if self._batch_timer is None:
            from PyQt6.QtCore import QTimer
            self._batch_timer = QTimer(self)
            self._batch_timer.setSingleShot(True)
            self._batch_timer.timeout.connect(self._do_batch_notify)
        
        if not self._batch_timer.isActive():
            self._batch_timer.start(16)

    def _do_batch_notify(self) -> None:
        """执行批量通知。"""
        if not self._current_theme:
            return
        
        logger.debug(f"批量通知 {len(self._subscribers)} 个订阅者")
        self._notify_subscribers()

    def set_current_theme(self, theme_name: str) -> None:
        """
        设置当前主题（便捷方法）。

        这是 set_theme() 的别名，用于向后兼容。

        Args:
            theme_name: 要激活的主题名称

        Raises:
            ValueError: 如果主题未注册
        """
        self.set_theme(theme_name)

    def _notify_subscribers(self) -> None:
        """
        通知所有订阅者主题已变化。

        注意：WeakKeyDictionary 会自动移除已删除的组件，
        因此无需手动清理垃圾回收的组件。
        """
        if not self._current_theme:
            return

        visible_subscribers = []
        hidden_subscribers = []
        non_widget_subscribers = []

        for widget, callback in list(self._subscribers.items()):
            try:
                if isinstance(widget, QWidget):
                    if widget.isVisible():
                        visible_subscribers.append((widget, callback))
                    else:
                        hidden_subscribers.append((widget, callback))
                else:
                    non_widget_subscribers.append((widget, callback))
            except RuntimeError:
                pass

        for widget, callback in non_widget_subscribers:
            try:
                callback(self._current_theme)
            except RuntimeError:
                pass
            except Exception as e:
                logger.warning(f"{widget.__class__.__name__} 主题回调出错: {e}")

        for widget, callback in visible_subscribers:
            try:
                callback(self._current_theme)
            except RuntimeError:
                pass
            except Exception as e:
                logger.warning(f"{widget.__class__.__name__} 主题回调出错: {e}")

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._notify_hidden_subscribers(hidden_subscribers))

    def _notify_hidden_subscribers(self, subscribers: list) -> None:
        """延迟通知隐藏的订阅者。"""
        if not self._current_theme:
            return
            
        for widget, callback in subscribers:
            try:
                callback(self._current_theme)
            except RuntimeError:
                pass
            except Exception as e:
                logger.warning(f"{widget.__class__.__name__} 主题回调出错: {e}")

    def current_theme(self) -> Optional[Theme]:
        """
        获取当前激活的主题。

        Returns:
            当前 Theme 实例，如果未设置则返回 None
        """
        return self._current_theme

    def subscribe(self, widget: QWidget, callback: Callable[[Theme], None]) -> None:
        """
        订阅组件到主题变化通知。

        当主题切换时，回调函数会被自动调用。

        Args:
            widget: 要订阅的组件
            callback: 主题变化时调用的回调函数
        """
        self._subscribers[widget] = callback
        # 立即应用当前主题
        if self._current_theme:
            callback(self._current_theme)

    def unsubscribe(self, widget: QWidget) -> None:
        """
        取消组件的主题变化订阅。

        Args:
            widget: 要取消订阅的组件
        """
        self._subscribers.pop(widget, None)

    def apply_to_widget(self, widget: QWidget, theme_name: Optional[str] = None) -> None:
        """
        将主题应用到组件。

        这是基础实现。子类应重写 _generate_qss 以提供
        特定主题的 QSS 生成逻辑。

        Args:
            widget: 要应用主题的组件
            theme_name: 主题名称（为 None 时使用当前主题）
        """
        theme = self._themes.get(theme_name) if theme_name else self._current_theme
        if not theme:
            return

        # 从主题生成 QSS（子类可重写以自定义行为）
        qss = self._generate_qss(theme, widget)

        # 在组件属性中存储主题名称
        widget.setProperty("_theme", theme.name)

        # 应用样式表
        widget.setStyleSheet(qss)

        # 强制刷新样式（动态样式必须执行此步骤）
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _generate_qss(self, theme: Theme, widget: QWidget) -> str:
        """
        从主题数据生成 QSS 字符串。

        这是一个模板方法，可被子类重写以自定义 QSS 生成。
        基础实现返回空字符串。

        Args:
            theme: 要生成 QSS 的主题
            widget: 目标组件

        Returns:
            QSS 字符串
        """
        return ""
