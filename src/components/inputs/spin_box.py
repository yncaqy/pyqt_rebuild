"""
数值输入组件

提供整数和浮点数输入功能，具有以下特性：
- 数值范围限制
- 步长调整
- 递增/递减按钮控制
- 直接输入验证
- 焦点状态处理
- 键盘操作支持（箭头键调整数值）
- 主题集成，自动更新样式
- 响应式设计
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QValidator, QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QToolButton,
    QSizePolicy, QFrame
)
from core.theme_manager import ThemeManager, Theme
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin

logger = logging.getLogger(__name__)


class SpinBoxConfig:
    """SpinBox 行为和样式的配置常量。"""
    
    DEFAULT_MIN_WIDTH = 80
    DEFAULT_HEIGHT = 32
    DEFAULT_BUTTON_WIDTH = 20
    DEFAULT_BORDER_RADIUS = 4
    DEFAULT_STEP = 1
    DEFAULT_REPEAT_DELAY = 300
    DEFAULT_REPEAT_INTERVAL = 50


class SpinBoxLineEdit(QLineEdit):
    """SpinBox 使用的行编辑器，支持键盘事件处理。"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._spin_box: Optional['SpinBoxBase'] = None
    
    def set_spin_box(self, spin_box: 'SpinBoxBase'):
        self._spin_box = spin_box
    
    def keyPressEvent(self, event):
        if self._spin_box:
            if event.key() == Qt.Key.Key_Up:
                self._spin_box.stepUp()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Down:
                self._spin_box.stepDown()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                self._spin_box._commit_value()
                event.accept()
                return
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        if self._spin_box:
            self._spin_box._commit_value()
        super().focusOutEvent(event)


class SpinButton(QToolButton):
    """递增/递减按钮，支持持续按下重复触发。"""
    
    def __init__(self, direction: int, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._direction = direction
        self._repeat_timer = QTimer(self)
        self._repeat_timer.timeout.connect(self._on_repeat)
        self._is_pressed = False
        self._color: Optional[QColor] = None
        
        self.setFixedSize(SpinBoxConfig.DEFAULT_BUTTON_WIDTH, SpinBoxConfig.DEFAULT_HEIGHT // 2)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)
    
    def set_color(self, color: QColor):
        self._color = color
        self.update()
    
    def _on_pressed(self):
        self._is_pressed = True
        self.clicked.emit()
        self._repeat_timer.start(SpinBoxConfig.DEFAULT_REPEAT_DELAY)
    
    def _on_released(self):
        self._is_pressed = False
        self._repeat_timer.stop()
    
    def _on_repeat(self):
        if self._is_pressed:
            self._repeat_timer.setInterval(SpinBoxConfig.DEFAULT_REPEAT_INTERVAL)
            self.clicked.emit()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        
        if self._color:
            color = self._color
        else:
            color = self.palette().color(self.foregroundRole())
        
        if self.underMouse():
            color = color.darker(110)
        
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        arrow_size = 4
        if self._direction > 0:
            painter.drawLine(center_x - arrow_size, center_y + 1, center_x, center_y - 2)
            painter.drawLine(center_x, center_y - 2, center_x + arrow_size, center_y + 1)
        else:
            painter.drawLine(center_x - arrow_size, center_y - 1, center_x, center_y + 2)
            painter.drawLine(center_x, center_y + 2, center_x + arrow_size, center_y - 1)
        
        painter.end()


class SpinBoxBase(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """SpinBox 基类，提供通用功能。"""
    
    valueChanged = pyqtSignal(object)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_style_override()
        self._init_stylesheet_cache(max_size=50)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        self._cleanup_done: bool = False
        
        self._minimum: float = 0
        self._maximum: float = 99
        self._value: float = 0
        self._single_step: float = SpinBoxConfig.DEFAULT_STEP
        self._is_focused: bool = False
        
        self._setup_ui()
        self._connect_signals()
        self._apply_initial_theme()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        self.destroyed.connect(self._on_widget_destroyed)
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(SpinBoxConfig.DEFAULT_MIN_WIDTH)
        self.setFixedHeight(SpinBoxConfig.DEFAULT_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def _setup_ui(self):
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._container = QFrame()
        self._container.setObjectName("spinBoxContainer")
        container_layout = QHBoxLayout(self._container)
        container_layout.setContentsMargins(4, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self._line_edit = SpinBoxLineEdit()
        self._line_edit.set_spin_box(self)
        self._line_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._line_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._button_container = QWidget()
        button_layout = QVBoxLayout(self._button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        
        self._up_button = SpinButton(1)
        self._up_button.clicked.connect(self.stepUp)
        
        self._down_button = SpinButton(-1)
        self._down_button.clicked.connect(self.stepDown)
        
        button_layout.addWidget(self._up_button)
        button_layout.addWidget(self._down_button)
        
        container_layout.addWidget(self._line_edit, 1)
        container_layout.addWidget(self._button_container)
        
        self._main_layout.addWidget(self._container)
    
    def _connect_signals(self):
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self._line_edit:
            if event.type() == event.Type.FocusIn:
                self._is_focused = True
                self._update_style()
            elif event.type() == event.Type.FocusOut:
                self._is_focused = False
                self._update_style()
                self._commit_value()
        return super().eventFilter(obj, event)
    
    def _on_text_changed(self, text: str):
        pass
    
    def _commit_value(self):
        pass
    
    def _apply_initial_theme(self):
        theme = self._theme_mgr.current_theme()
        if theme:
            self._on_theme_changed(theme)
    
    def _on_theme_changed(self, theme: Theme):
        if not theme:
            return
        
        self._current_theme = theme
        self._update_style()
    
    def _update_style(self):
        if not self._current_theme:
            return
        
        theme = self._current_theme
        
        bg = self.get_style_color(theme, 'input.background.normal', QColor(255, 255, 255))
        bg_hover = self.get_style_color(theme, 'input.background.hover', bg)
        border_focus = self.get_style_color(theme, 'input.border.focus', QColor(52, 152, 219))
        text_color = self.get_style_color(theme, 'input.text.normal', QColor(51, 51, 51))
        text_disabled = self.get_style_color(theme, 'input.text.disabled', QColor(150, 150, 150))
        
        is_dark = getattr(theme, 'is_dark', False)
        
        if is_dark:
            border_normal = "rgba(255, 255, 255, 25)"
        else:
            border_normal = "rgba(0, 0, 0, 15)"
        
        if self._is_focused:
            border_style = f"1px solid {border_focus.name()}"
        else:
            border_style = f"1px solid {border_normal}"
        
        border_radius = SpinBoxConfig.DEFAULT_BORDER_RADIUS
        
        style = f"""
            QFrame#spinBoxContainer {{
                background-color: {bg.name()};
                border: {border_style};
                border-radius: {border_radius}px;
            }}
            
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {text_color.name()};
                padding: 0 4px;
                font-size: 13px;
            }}
            
            QLineEdit:disabled {{
                color: {text_disabled.name()};
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
            }}
            
            QToolButton:hover {{
                background-color: {bg_hover.name()};
            }}
        """
        
        self._container.setStyleSheet(style)
        self._line_edit.setStyleSheet(f"color: {text_color.name()};")
        
        self._up_button.set_color(text_color)
        self._down_button.set_color(text_color)
    
    def _on_widget_destroyed(self):
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.stepUp()
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.stepDown()
            event.accept()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self._commit_value()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.stepUp()
        elif delta < 0:
            self.stepDown()
        event.accept()
    
    def stepUp(self):
        new_value = self._value + self._single_step
        if new_value <= self._maximum:
            self.setValue(new_value)
    
    def stepDown(self):
        new_value = self._value - self._single_step
        if new_value >= self._minimum:
            self.setValue(new_value)
    
    def value(self) -> float:
        return self._value
    
    def setValue(self, value: float):
        value = max(self._minimum, min(self._maximum, value))
        if value != self._value:
            self._value = value
            self._update_display()
            self.valueChanged.emit(value)
    
    def _update_display(self):
        pass
    
    def minimum(self) -> float:
        return self._minimum
    
    def setMinimum(self, minimum: float):
        self._minimum = minimum
        if self._value < minimum:
            self.setValue(minimum)
    
    def maximum(self) -> float:
        return self._maximum
    
    def setMaximum(self, maximum: float):
        self._maximum = maximum
        if self._value > maximum:
            self.setValue(maximum)
    
    def setRange(self, minimum: float, maximum: float):
        self._minimum = minimum
        self._maximum = maximum
        value = max(minimum, min(maximum, self._value))
        if value != self._value:
            self.setValue(value)
    
    def singleStep(self) -> float:
        return self._single_step
    
    def setSingleStep(self, step: float):
        if step > 0:
            self._single_step = step
    
    def setReadOnly(self, read_only: bool):
        self._line_edit.setReadOnly(read_only)
        self._up_button.setEnabled(not read_only)
        self._down_button.setEnabled(not read_only)
        self._update_style()
    
    def setEnabled(self, enabled: bool):
        self._container.setEnabled(enabled)
        self._line_edit.setEnabled(enabled)
        self._up_button.setEnabled(enabled)
        self._down_button.setEnabled(enabled)
        self._update_style()
    
    def cleanup(self):
        if self._cleanup_done:
            return
        self._cleanup_done = True
        self._theme_mgr.unsubscribe(self)


class SpinBox(SpinBoxBase):
    """
    整数输入组件。
    
    特性：
    - 整数范围限制
    - 步长调整
    - 递增/递减按钮控制
    - 直接输入验证
    - 焦点状态处理
    - 键盘操作支持（箭头键调整数值）
    - 鼠标滚轮支持
    - 主题集成
    
    信号：
        valueChanged(int): 当值改变时发出
    
    示例：
        spin = SpinBox()
        spin.setRange(0, 100)
        spin.setValue(50)
        spin.valueChanged.connect(lambda v: print(f"Value: {v}"))
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._display_prefix: str = ""
        self._display_suffix: str = ""
        super().__init__(parent)
        
        validator = QIntValidator(self)
        self._line_edit.setValidator(validator)
        
        self._update_display()
    
    def _update_display(self):
        text = f"{self._display_prefix}{int(self._value)}{self._display_suffix}"
        self._line_edit.setText(text)
    
    def _commit_value(self):
        text = self._line_edit.text().strip()
        
        if self._display_prefix and text.startswith(self._display_prefix):
            text = text[len(self._display_prefix):]
        if self._display_suffix and text.endswith(self._display_suffix):
            text = text[:-len(self._display_suffix)]
        
        try:
            value = int(text)
            self.setValue(value)
        except ValueError:
            self._update_display()
    
    def value(self) -> int:
        return int(self._value)
    
    def setValue(self, value: int):
        super().setValue(int(value))
    
    def setRange(self, minimum: int, maximum: int):
        super().setRange(int(minimum), int(maximum))
    
    def setMinimum(self, minimum: int):
        super().setMinimum(int(minimum))
    
    def setMaximum(self, maximum: int):
        super().setMaximum(int(maximum))
    
    def setSingleStep(self, step: int):
        super().setSingleStep(int(step))
    
    def prefix(self) -> str:
        return self._display_prefix
    
    def setPrefix(self, prefix: str):
        self._display_prefix = prefix
        self._update_display()
    
    def suffix(self) -> str:
        return self._display_suffix
    
    def setSuffix(self, suffix: str):
        self._display_suffix = suffix
        self._update_display()
    
    def stepUp(self):
        self.setValue(self._value + int(self._single_step))
    
    def stepDown(self):
        self.setValue(self._value - int(self._single_step))


class DoubleSpinBox(SpinBoxBase):
    """
    浮点数输入组件。
    
    特性：
    - 浮点数范围限制
    - 步长调整
    - 小数位数控制
    - 递增/递减按钮控制
    - 直接输入验证
    - 焦点状态处理
    - 键盘操作支持（箭头键调整数值）
    - 鼠标滚轮支持
    - 主题集成
    
    信号：
        valueChanged(float): 当值改变时发出
    
    示例：
        spin = DoubleSpinBox()
        spin.setRange(0.0, 100.0)
        spin.setValue(50.5)
        spin.setDecimals(2)
        spin.valueChanged.connect(lambda v: print(f"Value: {v}"))
    """
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._decimals: int = 2
        self._display_prefix: str = ""
        self._display_suffix: str = ""
        super().__init__(parent)
        
        self._update_validator()
        self._update_display()
    
    def _update_validator(self):
        validator = QDoubleValidator(self._minimum, self._maximum, self._decimals, self)
        self._line_edit.setValidator(validator)
    
    def _update_display(self):
        format_str = f"{{:.{self._decimals}f}}"
        text = f"{self._display_prefix}{format_str.format(self._value)}{self._display_suffix}"
        self._line_edit.setText(text)
    
    def _commit_value(self):
        text = self._line_edit.text().strip()
        
        if self._display_prefix and text.startswith(self._display_prefix):
            text = text[len(self._display_prefix):]
        if self._display_suffix and text.endswith(self._display_suffix):
            text = text[:-len(self._display_suffix)]
        
        try:
            value = float(text)
            self.setValue(value)
        except ValueError:
            self._update_display()
    
    def value(self) -> float:
        return round(self._value, self._decimals)
    
    def setValue(self, value: float):
        value = round(value, self._decimals)
        super().setValue(value)
    
    def decimals(self) -> int:
        return self._decimals
    
    def setDecimals(self, decimals: int):
        self._decimals = max(0, decimals)
        self._update_validator()
        self._update_display()
    
    def setRange(self, minimum: float, maximum: float):
        super().setRange(minimum, maximum)
        self._update_validator()
    
    def setMinimum(self, minimum: float):
        super().setMinimum(minimum)
        self._update_validator()
    
    def setMaximum(self, maximum: float):
        super().setMaximum(maximum)
        self._update_validator()
    
    def prefix(self) -> str:
        return self._display_prefix
    
    def setPrefix(self, prefix: str):
        self._display_prefix = prefix
        self._update_display()
    
    def suffix(self) -> str:
        return self._display_suffix
    
    def setSuffix(self, suffix: str):
        self._display_suffix = suffix
        self._update_display()

