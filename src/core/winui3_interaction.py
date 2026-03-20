"""
WinUI3 统一交互模式基类

提供所有组件共享的交互行为和视觉反馈。
确保一致的悬停、按下、聚焦和禁用状态处理。

遵循 WinUI3 设计规范:
- 悬停：背景变亮，边框变亮
- 按下：背景变暗
- 聚焦：蓝色边框（2px）
- 禁用：降低不透明度
"""

import logging
from typing import Optional, Dict, Any, Tuple
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFocusEvent
from PyQt6.QtWidgets import QWidget

try:
    from themes.colors import WINUI3_ANIMATION
except ImportError:
    from ...themes.colors import WINUI3_ANIMATION

logger = logging.getLogger(__name__)


class WinUI3InteractionMixin:
    """
    WinUI3 交互模式混入类。
    
    提供统一的交互行为：
    - 悬停动画（167ms，direct enter 缓动）
    - 按下动画（83ms，minimal 缓动）
    - 聚焦状态（蓝色边框）
    - 禁用状态（降低不透明度）
    """
    
    _hover_progress: float = 0.0
    _press_progress: float = 0.0
    _is_focused: bool = False
    _hover_animation: Optional[QPropertyAnimation] = None
    _press_animation: Optional[QPropertyAnimation] = None
    
    def _init_interaction(self) -> None:
        """初始化交互状态。"""
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._is_focused = False
        self._hover_animation = None
        self._press_animation = None
    
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
    
    def _create_direct_enter_easing(self) -> QEasingCurve:
        """创建 direct enter 缓动曲线（cubic-bezier(0, 0, 0, 1)）。"""
        return QEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _create_gentle_exit_easing(self) -> QEasingCurve:
        """创建 gentle exit 缓动曲线（cubic-bezier(1, 0, 1, 1)）。"""
        return QEasingCurve(QEasingCurve.Type.InCubic)
    
    def _create_minimal_easing(self) -> QEasingCurve:
        """创建 minimal 缓动曲线（linear）。"""
        return QEasingCurve(QEasingCurve.Type.Linear)
    
    def _start_hover_animation(self, target: float) -> None:
        """启动悬停动画。"""
        if self._hover_animation:
            self._hover_animation.stop()
        
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress")
        self._hover_animation.setDuration(WINUI3_ANIMATION['durations']['normal'])
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.setEasingCurve(self._create_direct_enter_easing())
        self._hover_animation.start()
    
    def _start_press_animation(self, target: float) -> None:
        """启动按下动画。"""
        if self._press_animation:
            self._press_animation.stop()
        
        self._press_animation = QPropertyAnimation(self, b"pressProgress")
        self._press_animation.setDuration(WINUI3_ANIMATION['durations']['fast'])
        self._press_animation.setStartValue(self._press_progress)
        self._press_animation.setEndValue(target)
        self._press_animation.setEasingCurve(self._create_minimal_easing())
        self._press_animation.start()
    
    def _handle_enter_event(self, event) -> None:
        """处理进入事件。"""
        if self.isEnabled():
            self._start_hover_animation(1.0)
    
    def _handle_leave_event(self, event) -> None:
        """处理离开事件。"""
        if self.isEnabled():
            self._start_hover_animation(0.0)
    
    def _handle_mouse_press(self, event) -> None:
        """处理鼠标按下事件。"""
        if self.isEnabled():
            self._start_press_animation(1.0)
    
    def _handle_mouse_release(self, event) -> None:
        """处理鼠标释放事件。"""
        if self.isEnabled():
            self._start_press_animation(0.0)
    
    def _handle_focus_in(self, event: QFocusEvent) -> None:
        """处理聚焦事件。"""
        self._is_focused = True
        self.update()
    
    def _handle_focus_out(self, event: QFocusEvent) -> None:
        """处理失焦事件。"""
        self._is_focused = False
        self.update()
    
    def _lerp_color(self, c1: QColor, c2: QColor, t: float) -> QColor:
        """线性插值两个颜色。"""
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
        return QColor(r, g, b, a)
    
    def _get_interaction_state(self) -> Dict[str, Any]:
        """
        获取当前交互状态。
        
        Returns:
            包含状态信息的字典：
            - is_enabled: 是否启用
            - is_hovered: 是否悬停
            - is_pressed: 是否按下
            - is_focused: 是否聚焦
            - hover_progress: 悬停进度（0.0-1.0）
            - press_progress: 按下进度（0.0-1.0）
        """
        return {
            'is_enabled': self.isEnabled(),
            'is_hovered': self._hover_progress > 0,
            'is_pressed': self._press_progress > 0,
            'is_focused': self._is_focused,
            'hover_progress': self._hover_progress,
            'press_progress': self._press_progress,
        }
    
    def _cleanup_interaction(self) -> None:
        """清理交互动画资源。"""
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.deleteLater()
            self._hover_animation = None
        
        if self._press_animation:
            self._press_animation.stop()
            self._press_animation.deleteLater()
            self._press_animation = None


class WinUI3StateColors:
    """
    WinUI3 状态颜色管理器。
    
    根据交互状态计算正确的颜色值。
    """
    
    @staticmethod
    def get_background_color(
        state: Dict[str, Any],
        colors: Dict[str, QColor]
    ) -> QColor:
        """获取背景颜色。"""
        if not state['is_enabled']:
            return colors.get('background_disabled', QColor(0, 0, 0, 0))
        
        if state['is_focused']:
            return colors.get('background_focused', colors.get('background_normal', QColor(0, 0, 0, 0)))
        
        if state['is_pressed']:
            return colors.get('background_pressed', QColor(0, 0, 0, 0))
        
        if state['is_hovered']:
            normal = colors.get('background_normal', QColor(0, 0, 0, 0))
            hover = colors.get('background_hover', QColor(0, 0, 0, 0))
            t = state['hover_progress']
            return WinUI3InteractionMixin._lerp_color(None, normal, hover, t)
        
        return colors.get('background_normal', QColor(0, 0, 0, 0))
    
    @staticmethod
    def get_border_color(
        state: Dict[str, Any],
        colors: Dict[str, QColor]
    ) -> QColor:
        """获取边框颜色。"""
        if not state['is_enabled']:
            return colors.get('border_disabled', QColor(0, 0, 0, 0))
        
        if state['is_focused']:
            return colors.get('border_focused', QColor('#595959'))
        
        if state['is_pressed']:
            return colors.get('border_pressed', QColor(0, 0, 0, 0))
        
        if state['is_hovered']:
            normal = colors.get('border_normal', QColor(0, 0, 0, 0))
            hover = colors.get('border_hover', QColor(0, 0, 0, 0))
            t = state['hover_progress']
            return WinUI3InteractionMixin._lerp_color(None, normal, hover, t)
        
        return colors.get('border_normal', QColor(0, 0, 0, 0))
    
    @staticmethod
    def get_text_color(
        state: Dict[str, Any],
        colors: Dict[str, QColor],
        is_placeholder: bool = False
    ) -> QColor:
        """获取文本颜色。"""
        if not state['is_enabled']:
            return colors.get('text_disabled', QColor(0, 0, 0, 0))
        
        if is_placeholder:
            return colors.get('text_placeholder', QColor(0, 0, 0, 0))
        
        return colors.get('text_normal', QColor(0, 0, 0, 0))
    
    @staticmethod
    def get_border_width(state: Dict[str, Any]) -> int:
        """获取边框宽度。"""
        return 2 if state['is_focused'] else 1
    
    @staticmethod
    def get_opacity(state: Dict[str, Any]) -> float:
        """获取不透明度。"""
        if not state['is_enabled']:
            return 0.4
        return 1.0
