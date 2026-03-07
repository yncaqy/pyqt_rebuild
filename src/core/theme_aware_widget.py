"""
主题感知组件基类

提供自动资源清理和主题感知的基础组件类。

功能特性:
- 组件销毁时自动调用 cleanup 方法
- 统一的主题管理器引用
- 可选的主题订阅管理
"""

import logging
from typing import Optional
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget

from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class ThemeAwareWidget(QWidget):
    """
    主题感知组件基类，提供自动资源清理功能。
    
    此基类确保组件在销毁时自动调用 cleanup 方法，
    防止资源泄漏（如主题订阅、定时器、动画等）。
    
    使用方式:
        class MyButton(ThemeAwareWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._theme_mgr.subscribe(self, self._on_theme_changed)
            
            def cleanup(self) -> None:
                self._theme_mgr.unsubscribe(self)
                # 其他清理逻辑...
    
    注意:
        - 子类应重写 cleanup() 方法实现清理逻辑
        - cleanup() 会在组件销毁时自动调用
        - 也可以手动调用 cleanup() 进行提前清理
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化主题感知组件。
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_called: bool = False
        
        self.destroyed.connect(self._on_destroyed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
    
    def _on_destroyed(self) -> None:
        """
        组件销毁时的回调，自动调用 cleanup。
        """
        if not self._cleanup_called:
            self._do_cleanup()
    
    def _do_cleanup(self) -> None:
        """
        执行清理操作的内部方法。
        """
        try:
            self.cleanup()
        except Exception as e:
            logger.error(f"清理组件时出错: {e}")
        finally:
            self._cleanup_called = True
    
    def cleanup(self) -> None:
        """
        清理组件资源。
        
        子类应重写此方法以实现自定义清理逻辑。
        典型的清理操作包括:
        - 取消主题订阅
        - 清除缓存
        - 停止定时器和动画
        - 释放其他资源
        
        注意:
            - 此方法会在组件销毁时自动调用
            - 也可以手动调用以提前释放资源
            - 重写时应确保方法可以安全地多次调用
        """
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
        
        self._current_theme = None
    
    def force_cleanup(self) -> None:
        """
        强制执行清理（用于手动清理场景）。
        
        此方法会立即执行清理，即使已经清理过。
        """
        self._cleanup_called = False
        self._do_cleanup()


class ThemeAwareObject(QObject):
    """
    主题感知 QObject 基类，用于非 QWidget 的主题感知对象。
    
    此基类为非控件对象提供类似的自动清理功能，
    适用于需要主题感知但不继承 QWidget 的场景。
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化主题感知对象。
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_called: bool = False
        
        self.destroyed.connect(self._on_destroyed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
    
    def _on_destroyed(self) -> None:
        """对象销毁时的回调。"""
        if not self._cleanup_called:
            self._do_cleanup()
    
    def _do_cleanup(self) -> None:
        """执行清理操作的内部方法。"""
        try:
            self.cleanup()
        except Exception as e:
            logger.error(f"清理对象时出错: {e}")
        finally:
            self._cleanup_called = True
    
    def cleanup(self) -> None:
        """
        清理对象资源。
        
        子类应重写此方法以实现自定义清理逻辑。
        """
        if hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache.clear()
        
        self._current_theme = None
