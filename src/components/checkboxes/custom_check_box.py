"""
WinUI 3 风格复选框组件

提供符合 Microsoft WinUI 3 设计规范的复选框控件，具有以下特性：
- 严格遵循 WinUI 3 设计规范
- 支持多种状态：默认、悬停、按下、选中、部分选中（三态）、禁用
- 平滑的状态过渡动画
- 主题集成，自动响应主题切换
- 自定义勾选标记绘制
- 键盘导航和可访问性支持
- 内存安全，正确清理资源

WinUI 3 CheckBox 设计规范：
- 指示器尺寸：20x20 像素
- 边框圆角：4 像素
- 边框宽度：1 像素
- 选中状态：使用系统强调色填充背景
- 勾选标记：白色，平滑绘制
- 三态支持：部分选中显示横线
- 动画：状态切换时平滑过渡（约 167ms）

Dark Theme 颜色规范：
- 未选中边框：#87FFFFFF (53% 白色)
- 未选中背景：透明
- 悬停边框：#9EFFFFFF (62% 白色)
- 悬停背景：#0FFFFFF (6% 白色)
- 按下边框：#87FFFFFF (53% 白色)
- 按下背景：#0FFFFFF (6% 白色)
- 选中背景：#0078D4 (系统强调色)
- 选中悬停背景：#006CBD (强调色悬停)
- 禁用边框：#5CFFFFFF (36% 白色)
- 禁用背景：透明

Light Theme 颜色规范：
- 未选中边框：#72000000 (45% 黑色)
- 未选中背景：透明
- 悬停边框：#9E000000 (62% 黑色)
- 悬停背景：#0A000000 (4% 黑色)
- 按下边框：#72000000 (45% 黑色)
- 按下背景：#0A000000 (4% 黑色)
- 选中背景：#0078D4 (系统强调色)
- 选中悬停背景：#006CBD (强调色悬停)
- 禁用边框：#5C000000 (36% 黑色)
- 禁用背景：透明

使用方式：
    checkbox = CustomCheckBox("接受条款")
    checkbox.setChecked(True)
    checkbox.stateChanged.connect(lambda state: print(f"状态: {state}"))
"""

import logging
from typing import Optional, Any
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QPaintEvent, QFont
from PyQt6.QtWidgets import QCheckBox, QWidget, QStyle, QStyleOptionButton, QSizePolicy

from core.themed_component_base import ThemedMixin
from core.animation import AnimationManager
from themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG

logger = logging.getLogger(__name__)


class CheckBoxConfig:
    """
    复选框配置常量，严格遵循 WinUI 3 设计规范。
    """
    DEFAULT_SIZE = WINUI3_CONTROL_SIZING['checkbox']['size']
    DEFAULT_BORDER_RADIUS = WINUI3_CONTROL_SIZING['checkbox']['border_radius']
    DEFAULT_CHECKMARK_SIZE = WINUI3_CONTROL_SIZING['checkbox']['checkmark_size']
    
    INDICATOR_MARGIN = 2
    CHECKMARK_PEN_WIDTH = 2.0
    INDETERMINATE_PEN_WIDTH = 2.0
    BORDER_WIDTH = 1.0
    
    SPACING = 8
    
    ANIMATION_DURATION = 167
    
    DARK_COLORS = {
        'border_normal': QColor(255, 255, 255, 35),
        'border_hover': QColor(255, 255, 255, 35),
        'border_pressed': QColor(255, 255, 255, 60),
        'border_disabled': QColor(255, 255, 255, 25),
        'background_normal': QColor(0, 0, 0, 0),
        'background_hover': QColor(0, 0, 0, 0),
        'background_pressed': QColor(255, 255, 255, 18),
        'background_disabled': QColor(0, 0, 0, 0),
        'accent': QColor('#595959'),
        'accent_hover': QColor('#6B6B6B'),
        'accent_pressed': QColor('#4A4A4A'),
        'checkmark': QColor(255, 255, 255),
        'text': QColor(255, 255, 255),
        'text_disabled': QColor(255, 255, 255, 92),
    }
    
    LIGHT_COLORS = {
        'border_normal': QColor(0, 0, 0, 35),
        'border_hover': QColor(0, 0, 0, 35),
        'border_pressed': QColor(0, 0, 0, 60),
        'border_disabled': QColor(0, 0, 0, 25),
        'background_normal': QColor(0, 0, 0, 0),
        'background_hover': QColor(0, 0, 0, 0),
        'background_pressed': QColor(0, 0, 0, 12),
        'background_disabled': QColor(0, 0, 0, 0),
        'accent': QColor('#595959'),
        'accent_hover': QColor('#6B6B6B'),
        'accent_pressed': QColor('#4A4A4A'),
        'checkmark': QColor(255, 255, 255),
        'text': QColor(0, 0, 0, 228),
        'text_disabled': QColor(0, 0, 0, 92),
    }
    
    @staticmethod
    def get_colors(is_dark: bool) -> dict:
        return CheckBoxConfig.DARK_COLORS if is_dark else CheckBoxConfig.LIGHT_COLORS


class CustomCheckBox(QCheckBox, ThemedMixin):
    """
    WinUI 3 风格复选框组件。
    
    功能特性:
    - 严格遵循 WinUI 3 设计规范
    - 支持多种状态：默认、悬停、按下、选中、部分选中、禁用
    - 平滑的状态过渡动画
    - 主题集成，自动响应主题切换
    - 自定义勾选标记绘制
    - 三态支持（部分选中）
    - 键盘导航支持
    - 内存安全，正确清理资源
    
    使用示例:
        checkbox = CustomCheckBox("接受条款")
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda state: print(f"状态: {state}"))
        
        # 三态模式
        checkbox.setTristate(True)
    """
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._init_theme()
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._check_progress = 0.0
        
        self._hover_animation: Optional[QPropertyAnimation] = None
        self._press_animation: Optional[QPropertyAnimation] = None
        self._check_animation: Optional[QPropertyAnimation] = None
        
        self._is_pressed = False
        self._animation_manager = AnimationManager.instance()
        
        self._setup_font()
        self._apply_initial_theme()
        
        logger.debug(f"CustomCheckBox initialized with text: '{text}'")
    
    def _setup_font(self) -> None:
        """设置字体，遵循 WinUI 3 设计规范。"""
        font = QFont()
        font.setFamilies([FONT_CONFIG['family'], FONT_CONFIG.get('fallback', 'Microsoft YaHei UI')])
        font.setPixelSize(FONT_CONFIG['size']['body'])
        self.setFont(font)
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        """应用主题样式。"""
        if not self._current_theme:
            return
        
        is_dark = self._current_theme.is_dark if hasattr(self._current_theme, 'is_dark') else True
        colors = CheckBoxConfig.get_colors(is_dark)
        
        self._border_color = self.get_theme_color('checkbox.border.normal', colors['border_normal'])
        self._border_hover_color = self.get_theme_color('checkbox.border.hover', colors['border_hover'])
        self._border_pressed_color = self.get_theme_color('checkbox.border.pressed', colors['border_pressed'])
        self._border_disabled_color = self.get_theme_color('checkbox.border.disabled', colors['border_disabled'])
        
        self._background_color = self.get_theme_color('checkbox.background.normal', colors['background_normal'])
        self._background_hover_color = self.get_theme_color('checkbox.background.hover', colors['background_hover'])
        self._background_pressed_color = self.get_theme_color('checkbox.background.pressed', colors['background_pressed'])
        self._background_disabled_color = self.get_theme_color('checkbox.background.disabled', colors['background_disabled'])
        
        self._accent_color = self.get_theme_color('primary.main', colors['accent'])
        self._accent_hover_color = self.get_theme_color('primary.hover', colors['accent_hover'])
        self._accent_pressed_color = self.get_theme_color('primary.pressed', colors['accent_pressed'])
        
        self._checkmark_color = self.get_theme_color('checkbox.checkmark', colors['checkmark'])
        self._text_color = self.get_theme_color('checkbox.text.normal', colors['text'])
        self._text_disabled_color = self.get_theme_color('checkbox.text.disabled', colors['text_disabled'])
        
        self._size = self.get_theme_value('checkbox.size', CheckBoxConfig.DEFAULT_SIZE)
        self._border_radius = self.get_theme_value('checkbox.border_radius', CheckBoxConfig.DEFAULT_BORDER_RADIUS)
        
        self.setStyleSheet(self._build_stylesheet())
        self.update()
    
    def _build_stylesheet(self) -> str:
        """构建样式表。"""
        return f"""
            CustomCheckBox {{
                spacing: {CheckBoxConfig.SPACING}px;
                color: {self._text_color.name()};
                background: transparent;
            }}
            CustomCheckBox:disabled {{
                color: {self._text_disabled_color.name()};
            }}
            CustomCheckBox::indicator {{
                width: {self._size}px;
                height: {self._size}px;
                background: transparent;
                border: none;
            }}
        """
    
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
    
    def get_check_progress(self) -> float:
        return self._check_progress
    
    def set_check_progress(self, value: float) -> None:
        self._check_progress = value
        self.update()
    
    checkProgress = pyqtProperty(float, get_check_progress, set_check_progress)
    
    def _animate_hover(self, enter: bool) -> None:
        """悬停动画。"""
        if not self._animation_manager.should_animate():
            self._hover_progress = 1.0 if enter else 0.0
            self.update()
            return
        
        if self._hover_animation:
            self._hover_animation.stop()
        
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress")
        duration = self._animation_manager.get_scaled_duration(CheckBoxConfig.ANIMATION_DURATION)
        self._hover_animation.setDuration(duration)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0 if enter else 0.0)
        self._hover_animation.start()
    
    def _animate_press(self, pressed: bool) -> None:
        """按下动画。"""
        if not self._animation_manager.should_animate():
            self._press_progress = 1.0 if pressed else 0.0
            self.update()
            return
        
        if self._press_animation:
            self._press_animation.stop()
        
        self._press_animation = QPropertyAnimation(self, b"pressProgress")
        duration = self._animation_manager.get_scaled_duration(int(CheckBoxConfig.ANIMATION_DURATION * 0.6))
        self._press_animation.setDuration(duration)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._press_animation.setStartValue(self._press_progress)
        self._press_animation.setEndValue(1.0 if pressed else 0.0)
        self._press_animation.start()
    
    def _animate_check(self, checked: bool) -> None:
        """选中动画。"""
        if not self._animation_manager.should_animate():
            self._check_progress = 1.0 if checked else 0.0
            self.update()
            return
        
        if self._check_animation:
            self._check_animation.stop()
        
        self._check_animation = QPropertyAnimation(self, b"checkProgress")
        duration = self._animation_manager.get_scaled_duration(CheckBoxConfig.ANIMATION_DURATION)
        self._check_animation.setDuration(duration)
        self._check_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._check_animation.setStartValue(self._check_progress)
        self._check_animation.setEndValue(1.0 if checked else 0.0)
        self._check_animation.start()
    
    def enterEvent(self, event) -> None:
        """鼠标进入事件。"""
        if self.isEnabled():
            self._animate_hover(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件。"""
        if self.isEnabled():
            self._animate_hover(False)
            if self._is_pressed:
                self._is_pressed = False
                self._animate_press(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件。"""
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._is_pressed = True
            self._animate_press(True)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件。"""
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._is_pressed = False
            self._animate_press(False)
        super().mouseReleaseEvent(event)
    
    def setChecked(self, checked: bool) -> None:
        """设置选中状态。"""
        old_checked = self.isChecked()
        super().setChecked(checked)
        if old_checked != checked:
            self._animate_check(checked)
    
    def setCheckState(self, state: Qt.CheckState) -> None:
        """设置选中状态（支持三态）。"""
        old_state = self.checkState()
        super().setCheckState(state)
        if old_state != state:
            if state == Qt.CheckState.Checked:
                self._animate_check(True)
            elif state == Qt.CheckState.Unchecked:
                self._animate_check(False)
            else:
                self._check_progress = 1.0
                self.update()
    
    def nextCheckState(self) -> None:
        """下一个选中状态。"""
        if self.isTristate():
            if self.checkState() == Qt.CheckState.Unchecked:
                self.setCheckState(Qt.CheckState.PartiallyChecked)
            elif self.checkState() == Qt.CheckState.PartiallyChecked:
                self.setCheckState(Qt.CheckState.Checked)
            else:
                self.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.setChecked(not self.isChecked())
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        style = self.style()
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        
        indicator_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, opt, self
        )
        
        self._draw_indicator(painter, indicator_rect)
        
        text_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxContents, opt, self
        )
        
        if self.text():
            text_color = self._text_color if self.isEnabled() else self._text_disabled_color
            painter.setPen(text_color)
            painter.setFont(self.font())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
    
    def _draw_indicator(self, painter: QPainter, rect: QRectF) -> None:
        """绘制指示器。"""
        is_checked = self.isChecked() or self.checkState() == Qt.CheckState.Checked
        is_partially_checked = self.checkState() == Qt.CheckState.PartiallyChecked
        is_enabled = self.isEnabled()
        is_hovered = self._hover_progress > 0
        is_pressed = self._press_progress > 0
        
        indicator_rect = QRectF(rect.x(), rect.y(), self._size, self._size)
        indicator_rect.moveCenter(QPointF(rect.center()))
        
        border_rect = indicator_rect.adjusted(0.5, 0.5, -0.5, -0.5)
        
        if not is_enabled:
            bg_color = self._background_disabled_color
            border_color = self._border_disabled_color
            
            painter.setPen(QPen(border_color, CheckBoxConfig.BORDER_WIDTH))
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(border_rect, self._border_radius, self._border_radius)
            
            if is_checked or is_partially_checked:
                self._draw_disabled_checkmark(painter, indicator_rect, is_partially_checked)
        elif is_checked or is_partially_checked:
            if is_pressed:
                bg_color = self._accent_pressed_color
            elif is_hovered:
                bg_color = self._accent_hover_color
            else:
                bg_color = self._accent_color
            
            if self._check_progress < 1.0 and not is_partially_checked:
                animated_color = QColor(bg_color)
                animated_color.setAlpha(int(bg_color.alpha() * self._check_progress))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(animated_color))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(bg_color))
            
            painter.drawRoundedRect(border_rect, self._border_radius, self._border_radius)
            
            if is_partially_checked:
                self._draw_indeterminate_mark(painter, indicator_rect)
            elif self._check_progress > 0:
                self._draw_checkmark(painter, indicator_rect)
        else:
            if is_pressed:
                bg_color = self._background_pressed_color
                border_color = self._border_pressed_color
            elif is_hovered:
                bg_color = self._background_hover_color
                border_color = self._border_hover_color
            else:
                bg_color = self._background_color
                border_color = self._border_color
            
            painter.setPen(QPen(border_color, CheckBoxConfig.BORDER_WIDTH))
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(border_rect, self._border_radius, self._border_radius)
    
    def _draw_disabled_checkmark(self, painter: QPainter, rect: QRectF, is_indeterminate: bool = False) -> None:
        """绘制禁用状态的勾选标记。"""
        disabled_color = self._border_disabled_color
        
        if is_indeterminate:
            margin = CheckBoxConfig.INDICATOR_MARGIN + 3
            line_rect = rect.adjusted(margin, 0, -margin, 0)
            line_y = rect.center().y()
            
            pen = QPen(disabled_color, CheckBoxConfig.INDETERMINATE_PEN_WIDTH)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(line_rect.left()), int(line_y), int(line_rect.right()), int(line_y))
        else:
            margin = CheckBoxConfig.INDICATOR_MARGIN + 1
            check_rect = rect.adjusted(margin, margin, -margin, -margin)
            
            pen = QPen(disabled_color, CheckBoxConfig.CHECKMARK_PEN_WIDTH)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            
            start_x = check_rect.left() + check_rect.width() * 0.15
            start_y = check_rect.top() + check_rect.height() * 0.5
            mid_x = check_rect.left() + check_rect.width() * 0.4
            mid_y = check_rect.bottom() - check_rect.height() * 0.15
            end_x = check_rect.right() - check_rect.width() * 0.15
            end_y = check_rect.top() + check_rect.height() * 0.25
            
            path = QPainterPath()
            path.moveTo(start_x, start_y)
            path.lineTo(mid_x, mid_y)
            path.lineTo(end_x, end_y)
            painter.drawPath(path)
    
    def _draw_checkmark(self, painter: QPainter, rect: QRectF) -> None:
        """绘制勾选标记。"""
        margin = CheckBoxConfig.INDICATOR_MARGIN + 1
        check_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        pen = QPen(self._checkmark_color, CheckBoxConfig.CHECKMARK_PEN_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        progress = self._check_progress
        
        start_x = check_rect.left() + check_rect.width() * 0.15
        start_y = check_rect.top() + check_rect.height() * 0.5
        mid_x = check_rect.left() + check_rect.width() * 0.4
        mid_y = check_rect.bottom() - check_rect.height() * 0.15
        end_x = check_rect.right() - check_rect.width() * 0.15
        end_y = check_rect.top() + check_rect.height() * 0.25
        
        if progress <= 0.5:
            t = progress * 2
            current_x = start_x + (mid_x - start_x) * t
            current_y = start_y + (mid_y - start_y) * t
            
            path = QPainterPath()
            path.moveTo(start_x, start_y)
            path.lineTo(current_x, current_y)
            painter.drawPath(path)
        else:
            t = (progress - 0.5) * 2
            current_x = mid_x + (end_x - mid_x) * t
            current_y = mid_y + (end_y - mid_y) * t
            
            path = QPainterPath()
            path.moveTo(start_x, start_y)
            path.lineTo(mid_x, mid_y)
            path.lineTo(current_x, current_y)
            painter.drawPath(path)
    
    def _draw_indeterminate_mark(self, painter: QPainter, rect: QRectF) -> None:
        """绘制部分选中标记（横线）。"""
        margin = CheckBoxConfig.INDICATOR_MARGIN + 3
        line_rect = rect.adjusted(margin, 0, -margin, 0)
        line_y = rect.center().y()
        
        pen = QPen(self._checkmark_color, CheckBoxConfig.INDETERMINATE_PEN_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(int(line_rect.left()), int(line_y), int(line_rect.right()), int(line_y))
    
    def sizeHint(self) -> Any:
        """建议尺寸。"""
        from PyQt6.QtCore import QSize
        text_width = self.fontMetrics().horizontalAdvance(self.text()) if self.text() else 0
        width = self._size + CheckBoxConfig.SPACING + text_width + 4
        height = max(self._size, self.fontMetrics().height())
        return QSize(width, height)
    
    def cleanup_theme(self) -> None:
        """清理主题资源。"""
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation = None
        if self._press_animation:
            self._press_animation.stop()
            self._press_animation = None
        if self._check_animation:
            self._check_animation.stop()
            self._check_animation = None
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()
    
    def deleteLater(self) -> None:
        """计划删除组件。"""
        self.cleanup_theme()
        super().deleteLater()
