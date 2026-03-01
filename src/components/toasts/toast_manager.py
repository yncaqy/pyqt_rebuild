"""
Toast 管理器

提供 Toast 通知的集中管理，支持多个 Toast 的自动定位和堆叠显示。
"""

from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .toast import Toast, ToastPosition, ToastType


class ToastManager(QObject):
    """
    Toast 通知管理器，支持多个 Toast 的自动定位。

    功能特性:
    - 单例模式，全局统一管理
    - 多个 Toast 自动堆叠
    - 便捷的类型方法（info, success, warning, error）
    - 可配置默认位置和持续时间
    - 预热机制，消除首次显示延迟

    使用示例:
        manager = ToastManager.get_instance()
        manager.success("操作成功")
        manager.error("操作失败")
    """

    instance = None
    _prewarmed = False

    @classmethod
    def get_instance(cls) -> 'ToastManager':
        """
        获取单例实例。

        Returns:
            ToastManager 单例实例
        """
        if cls.instance is None:
            cls.instance = ToastManager()
        return cls.instance

    def __init__(self):
        """初始化 Toast 管理器。"""
        super().__init__()
        self._active_toasts: List[Toast] = []
        self._default_position = ToastPosition.TOP_CENTER
        self._default_duration = 3000
        self._spacing = 10

    @classmethod
    def prewarm(cls) -> None:
        """
        预热 Toast 系统以防止首次显示延迟。

        创建并立即销毁一个隐藏的 Toast 来初始化所有 Qt 子系统
        （动画、图形效果、样式表等）。

        在应用程序启动时调用以获得最佳性能。

        使用示例:
            ToastManager.prewarm()  # 在应用启动时调用
        """
        if cls._prewarmed:
            return

        try:
            temp_toast = Toast("prewarm", ToastType.INFO, 0)
            temp_toast.setStyleSheet(temp_toast.styleSheet())
            temp_toast.update()

            temp_toast.cleanup()
            temp_toast.deleteLater()

            cls._prewarmed = True
            print("Toast system pre-warmed")
        except Exception as e:
            print(f"Warning: Failed to pre-warm toast system: {e}")

    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = None,
        position: ToastPosition = None,
        parent: QWidget = None,
        show_close_button: bool = None
    ) -> Toast:
        """
        显示 Toast 通知。

        Args:
            message: Toast 消息文本
            toast_type: Toast 类型（info, success, warning, error）
            duration: 自动隐藏持续时间（毫秒）
            position: Toast 显示位置
            parent: 父控件
            show_close_button: 是否显示关闭按钮

        Returns:
            创建的 Toast 实例
        """
        if duration is None:
            duration = self._default_duration
        if position is None:
            position = self._default_position
        
        toast = Toast(message, toast_type, duration, show_close_button, parent)

        offset = self._calculate_offset(position)
        toast._position_offset = offset

        toast.destroyed.connect(lambda: self._remove_toast(toast))

        self._active_toasts.append(toast)

        toast.show(position, parent)

        return toast

    def info(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None, show_close_button: bool = None) -> Toast:
        """
        显示信息类型 Toast。

        Args:
            message: Toast 消息文本
            duration: 自动隐藏持续时间（毫秒）
            position: Toast 显示位置
            parent: 父控件
            show_close_button: 是否显示关闭按钮

        Returns:
            创建的 Toast 实例
        """
        return self.show(message, ToastType.INFO, duration, position, parent, show_close_button)
    
    def success(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None, show_close_button: bool = None) -> Toast:
        """
        显示成功类型 Toast。

        Args:
            message: Toast 消息文本
            duration: 自动隐藏持续时间（毫秒）
            position: Toast 显示位置
            parent: 父控件
            show_close_button: 是否显示关闭按钮

        Returns:
            创建的 Toast 实例
        """
        return self.show(message, ToastType.SUCCESS, duration, position, parent, show_close_button)
    
    def warning(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None, show_close_button: bool = None) -> Toast:
        """
        显示警告类型 Toast。

        Args:
            message: Toast 消息文本
            duration: 自动隐藏持续时间（毫秒）
            position: Toast 显示位置
            parent: 父控件
            show_close_button: 是否显示关闭按钮

        Returns:
            创建的 Toast 实例
        """
        return self.show(message, ToastType.WARNING, duration, position, parent, show_close_button)
    
    def error(self, message: str, duration: int = None, position: ToastPosition = None, parent: QWidget = None, show_close_button: bool = None) -> Toast:
        """
        显示错误类型 Toast。

        Args:
            message: Toast 消息文本
            duration: 自动隐藏持续时间（毫秒）
            position: Toast 显示位置
            parent: 父控件
            show_close_button: 是否显示关闭按钮

        Returns:
            创建的 Toast 实例
        """
        return self.show(message, ToastType.ERROR, duration, position, parent, show_close_button)

    def _calculate_offset(self, position: ToastPosition) -> int:
        """
        计算 Toast 堆叠时的垂直偏移量。

        Args:
            position: Toast 位置

        Returns:
            垂直偏移量（像素）
        """
        count = 0
        for toast in self._active_toasts:
            if hasattr(toast, '_position'):
                if toast._position == position:
                    count += 1

        return count * (100 + self._spacing)

    def _remove_toast(self, toast: Toast) -> None:
        """
        从活动列表中移除 Toast。

        Args:
            toast: 要移除的 Toast
        """
        if toast in self._active_toasts:
            self._active_toasts.remove(toast)

    def clear_all(self) -> None:
        """关闭所有活动的 Toast。"""
        for toast in self._active_toasts[:]:
            toast.close()
        self._active_toasts.clear()

    def set_default_position(self, position: ToastPosition) -> None:
        """
        设置新 Toast 的默认位置。

        Args:
            position: 默认位置
        """
        self._default_position = position

    def set_default_duration(self, duration: int) -> None:
        """
        设置新 Toast 的默认持续时间。

        Args:
            duration: 默认持续时间（毫秒）
        """
        self._default_duration = duration

    def set_spacing(self, spacing: int) -> None:
        """
        设置堆叠 Toast 之间的间距。

        Args:
            spacing: 间距（像素）
        """
        self._spacing = spacing
