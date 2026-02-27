"""
图标卡片组件

用于在图标库中展示单个图标的卡片容器。
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStyle
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QFontMetrics

from components.widgets.icon_widget import IconWidget, IconSize
from components.labels.themed_label import ThemedLabel
from components.containers.themed_widget import ThemedWidget
from components.tooltips.tooltip_manager import TooltipManager
from core.theme_manager import ThemeManager, Theme
from core.icon_manager import IconManager


class IconCard(ThemedWidget):
    """
    主题化的图标卡片组件。
    
    用于在图标库中展示单个图标，支持主题切换和点击复制功能。
    
    Signals:
        clicked: 点击卡片时发出，携带图标名称
    """
    
    clicked = pyqtSignal(str)
    
    def __init__(
        self,
        icon_name: str,
        size: IconSize = IconSize.XLARGE,
        parent: Optional[QWidget] = None
    ):
        self._icon_name = icon_name
        self._base_icon_name = self._extract_base_name(icon_name)
        self._icon_size = size
        self._bg_color: Optional[QColor] = None
        self._border_color: Optional[QColor] = None
        self._text_color: Optional[QColor] = None
        self._hover_bg_color: Optional[QColor] = None
        self._hover_border_color: Optional[QColor] = None
        self._is_hovered = False
        
        super().__init__(parent)
        
        self._setup_ui()
        self._apply_theme()
        
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        TooltipManager().install_tooltip(self, self._base_icon_name)
    
    def _extract_base_name(self, icon_name: str) -> str:
        """提取图标基础名称（移除 _black/_white 后缀）"""
        if icon_name.endswith('_white') or icon_name.endswith('_black'):
            return icon_name[:-6]
        return icon_name
    
    def _setup_ui(self) -> None:
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        self._icon = IconWidget(self._base_icon_name, size=self._icon_size, theme_aware=True)
        layout.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        self._name_label = ThemedLabel(self._base_icon_name, font_role='small')
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setWordWrap(False)
        layout.addWidget(self._name_label)
        
        self.setFixedSize(120, 75)
        
        QTimer.singleShot(0, self._elide_text)
    
    def _elide_text(self) -> None:
        """省略过长的文本"""
        fm = QFontMetrics(self._name_label.font())
        available_width = self.width() - 12
        elided = fm.elidedText(self._base_icon_name, Qt.TextElideMode.ElideRight, available_width)
        self._name_label.setText(elided)
    
    def _apply_theme(self, theme: Optional[Theme] = None) -> None:
        """应用主题"""
        theme = theme or self._theme_mgr.current_theme()
        if not theme:
            return
        
        self._bg_color = theme.get_color('card.background', QColor(255, 255, 255, 25))
        self._border_color = theme.get_color('card.border', QColor(255, 255, 255, 25))
        self._text_color = theme.get_color('text.secondary', QColor(255, 255, 255, 178))
        
        hover_alpha = min(self._bg_color.alpha() + 15, 255)
        self._hover_bg_color = QColor(self._bg_color)
        self._hover_bg_color.setAlpha(hover_alpha)
        
        self._hover_border_color = QColor(self._border_color)
        self._hover_border_color.setAlpha(min(self._border_color.alpha() + 25, 255))
        
        self._update_style()
    
    def _update_style(self) -> None:
        """更新样式"""
        bg = self._hover_bg_color if self._is_hovered else self._bg_color
        border = self._hover_border_color if self._is_hovered else self._border_color
        
        if bg and border:
            self.setStyleSheet(f"""
                IconCard {{
                    background-color: rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg.alpha()});
                    border-radius: 8px;
                    border: 1px solid rgba({border.red()}, {border.green()}, {border.blue()}, {border.alpha()});
                }}
            """)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题切换响应"""
        super()._on_theme_changed(theme)
        self._apply_theme(theme)
    
    def enterEvent(self, event) -> None:
        """鼠标进入事件"""
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开事件"""
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self._base_icon_name)
            self.clicked.emit(self._base_icon_name)
        super().mousePressEvent(event)
    
    def icon_name(self) -> str:
        """获取图标名称"""
        return self._base_icon_name
