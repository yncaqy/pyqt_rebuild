"""
主题化组件基类

提供统一的主题化组件基类，整合 StyleOverrideMixin 和 StylesheetCacheMixin，
确保所有主题化组件遵循一致的设计模式。

功能特性:
- 统一的主题订阅和管理
- 统一的样式覆盖和缓存机制
- 统一的清理方法
- 常用工具方法封装
"""

import logging
from typing import Optional, Dict, Any, Tuple, Callable

from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QColor, QPainter, QIcon, QFont
from PyQt6.QtWidgets import (
    QWidget, QStyledItemDelegate, QSlider, QLineEdit, QTextEdit,
    QPlainTextEdit, QPushButton, QCheckBox, QGroupBox, QTreeWidget,
    QTableWidget, QHeaderView
)

from src.core.theme_manager import ThemeManager, Theme
from src.core.style_override import StyleOverrideMixin
from src.core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class ThemedComponentBase(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    主题化组件基类。

    所有需要主题支持的组件都应继承此类，以获得：
    - 自动主题订阅和取消订阅
    - 样式覆盖能力
    - 样式表缓存
    - 统一的清理机制

    使用示例:
        class MyButton(ThemedComponentBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._setup_ui()
                self._apply_initial_theme()

            def _setup_ui(self):
                # 创建UI
                pass

            def _apply_theme(self, theme: Optional[Theme] = None):
                theme = theme or self._theme_mgr.current_theme()
                if not theme:
                    return
                # 应用主题样式
                bg = self.get_style_color(theme, 'button.background', QColor(60, 60, 60))
                # ...

            def cleanup(self):
                # 自定义清理逻辑
                super().cleanup()

    属性:
        _theme_mgr: 主题管理器实例
        _current_theme: 当前主题
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._ui_initialized: bool = False

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _apply_initial_theme(self) -> None:
        """
        应用初始主题。

        子类应在完成 UI 初始化后调用此方法。
        """
        self._ui_initialized = True
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        主题变化回调。

        子类可重写此方法以自定义主题切换行为。
        默认行为是调用 _apply_theme 方法。

        Args:
            theme: 新主题
        """
        self._current_theme = theme
        if self._ui_initialized:
            self._apply_theme(theme)

    def _apply_theme(self, theme: Optional[Theme] = None) -> None:
        """
        应用主题样式。

        子类必须重写此方法以实现具体的样式应用逻辑。

        Args:
            theme: 要应用的主题，如果为 None 则使用当前主题
        """
        pass

    def get_theme_color(
        self,
        path: str,
        default: QColor = QColor(128, 128, 128)
    ) -> QColor:
        """
        从当前主题获取颜色值。

        Args:
            path: 颜色路径，使用点号分隔（如 'button.background.normal'）
            default: 默认颜色

        Returns:
            颜色值
        """
        if not self._current_theme:
            return default

        return self.get_style_color(self._current_theme, path, default)

    def get_theme_value(
        self,
        path: str,
        default: Any = None
    ) -> Any:
        """
        从当前主题获取值。

        Args:
            path: 值路径，使用点号分隔
            default: 默认值

        Returns:
            主题值
        """
        if not self._current_theme:
            return default

        return self.get_style_value(self._current_theme, path, default)

    def get_cached_stylesheet(
        self,
        cache_key: Tuple,
        builder: Callable[[], str]
    ) -> str:
        """
        获取缓存的样式表。

        Args:
            cache_key: 缓存键
            builder: 样式表构建函数

        Returns:
            样式表字符串
        """
        return self._get_cached_stylesheet(cache_key, builder)

    def cleanup(self) -> None:
        """
        清理资源。

        子类应重写此方法以清理自定义资源，并调用 super().cleanup()。
        """
        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class ThemedObjectBase(QObject, StyleOverrideMixin, StylesheetCacheMixin):
    """
    主题化 QObject 基类。

    用于需要继承 QObject 但不是 QWidget 的场景（如 Delegate）。
    """

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._ui_initialized: bool = False

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _apply_initial_theme(self) -> None:
        """应用初始主题。"""
        self._ui_initialized = True
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._current_theme = theme
        if self._ui_initialized:
            self._apply_theme(theme)

    def _apply_theme(self, theme: Optional[Theme] = None) -> None:
        pass

    def get_theme_color(
        self,
        path: str,
        default: QColor = QColor(128, 128, 128)
    ) -> QColor:
        if not self._current_theme:
            return default
        return self.get_style_color(self._current_theme, path, default)

    def get_theme_value(
        self,
        path: str,
        default: Any = None
    ) -> Any:
        if not self._current_theme:
            return default
        return self.get_style_value(self._current_theme, path, default)

    def get_cached_stylesheet(
        self,
        cache_key: Tuple,
        builder: Callable[[], str]
    ) -> str:
        return self._get_cached_stylesheet(cache_key, builder)

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class ThemedMixin(StyleOverrideMixin, StylesheetCacheMixin):
    """
    主题化混入类。

    可用于任何继承自 QWidget 或其子类的组件，提供主题管理功能。
    与 ThemedComponentBase 不同，此类不继承 QWidget，因此可以与任何 Qt 控件组合使用。

    使用示例:
        class MySlider(QSlider, ThemedMixin):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._init_theme()
                self._apply_initial_theme()

            def _apply_theme(self, theme):
                # 应用主题样式
                pass

    注意:
        - 必须在 __init__ 中调用 self._init_theme() 初始化主题系统
        - 必须在 UI 初始化完成后调用 self._apply_initial_theme()
        - 必须实现 self._apply_theme(theme) 方法
    """

    def _init_theme(self) -> None:
        """
        初始化主题系统。

        必须在组件的 __init__ 方法中调用此方法。
        """
        self._init_style_override()
        self._init_stylesheet_cache()

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._ui_initialized: bool = False

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _apply_initial_theme(self) -> None:
        """
        应用初始主题。

        子类应在完成 UI 初始化后调用此方法。
        """
        self._ui_initialized = True
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        主题变化回调。

        子类可重写此方法以自定义主题切换行为。
        默认行为是调用 _apply_theme 方法。

        Args:
            theme: 新主题
        """
        self._current_theme = theme
        if self._ui_initialized:
            self._apply_theme(theme)

    def _apply_theme(self, theme: Optional[Theme] = None) -> None:
        """
        应用主题样式。

        子类必须重写此方法以实现具体的样式应用逻辑。

        Args:
            theme: 要应用的主题，如果为 None 则使用当前主题
        """
        pass

    def get_theme_color(
        self,
        path: str,
        default: QColor = QColor(128, 128, 128)
    ) -> QColor:
        """
        从当前主题获取颜色值。

        Args:
            path: 颜色路径，使用点号分隔（如 'button.background.normal'）
            default: 默认颜色

        Returns:
            颜色值
        """
        if not self._current_theme:
            return default

        return self.get_style_color(self._current_theme, path, default)

    def get_theme_value(
        self,
        path: str,
        default: Any = None
    ) -> Any:
        """
        从当前主题获取值。

        Args:
            path: 值路径，使用点号分隔
            default: 默认值

        Returns:
            主题值
        """
        if not self._current_theme:
            return default

        return self.get_style_value(self._current_theme, path, default)

    def get_cached_stylesheet(
        self,
        cache_key: Tuple,
        builder: Callable[[], str]
    ) -> str:
        """
        获取缓存的样式表。

        Args:
            cache_key: 缓存键
            builder: 样式表构建函数

        Returns:
            样式表字符串
        """
        return self._get_cached_stylesheet(cache_key, builder)

    def cleanup_theme(self) -> None:
        """
        清理主题资源。

        子类应重写此方法以清理自定义资源，并调用 super().cleanup_theme()。
        """
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class ThemedSliderBase(QSlider, ThemedMixin):
    """
    主题化滑块基类。

    用于需要主题支持的滑块控件。
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self._init_theme()


class ThemedLineEditBase(QLineEdit, ThemedMixin):
    """
    主题化单行输入框基类。

    用于需要主题支持的单行文本输入控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedTextEditBase(QTextEdit, ThemedMixin):
    """
    主题化多行文本编辑器基类。

    用于需要主题支持的多行文本编辑控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedPlainTextEditBase(QPlainTextEdit, ThemedMixin):
    """
    主题化纯文本编辑器基类。

    用于需要主题支持的纯文本编辑控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedComboBoxBase(QPushButton, ThemedMixin):
    """
    主题化组合框基类。

    用于需要主题支持的下拉选择控件。
    注意：继承自 QPushButton 以支持自定义样式。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedCheckBoxBase(QCheckBox, ThemedMixin):
    """
    主题化复选框基类。

    用于需要主题支持的复选框控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedGroupBoxBase(QGroupBox, ThemedMixin):
    """
    主题化分组框基类。

    用于需要主题支持的分组框控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedTreeWidgetBase(QTreeWidget, ThemedMixin):
    """
    主题化树形控件基类。

    用于需要主题支持的树形列表控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedTableWidgetBase(QTableWidget, ThemedMixin):
    """
    主题化表格控件基类。

    用于需要主题支持的表格控件。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_theme()


class ThemedHeaderViewBase(QHeaderView, ThemedMixin):
    """
    主题化表头基类。

    用于需要主题支持的表头控件。
    """

    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self._init_theme()


class ThemedDelegateBase(QStyledItemDelegate, StyleOverrideMixin, StylesheetCacheMixin):
    """
    主题化委托基类。

    用于自定义绘制委托（Delegate），提供主题支持。
    继承自 QStyledItemDelegate 以支持 Qt 的委托系统。
    """

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._init_style_override()
        self._init_stylesheet_cache()

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._ui_initialized: bool = False

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme

        self._theme_mgr.subscribe(self, self._on_theme_changed)

    def _apply_initial_theme(self) -> None:
        """应用初始主题。"""
        self._ui_initialized = True
        if self._current_theme:
            self._apply_theme(self._current_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        self._current_theme = theme
        if self._ui_initialized:
            self._apply_theme(theme)

    def _apply_theme(self, theme: Optional[Theme] = None) -> None:
        pass

    def get_theme_color(
        self,
        path: str,
        default: QColor = QColor(128, 128, 128)
    ) -> QColor:
        if not self._current_theme:
            return default
        return self.get_style_color(self._current_theme, path, default)

    def get_theme_value(
        self,
        path: str,
        default: Any = None
    ) -> Any:
        if not self._current_theme:
            return default
        return self.get_style_value(self._current_theme, path, default)

    def get_cached_stylesheet(
        self,
        cache_key: Tuple,
        builder: Callable[[], str]
    ) -> str:
        return self._get_cached_stylesheet(cache_key, builder)

    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()
