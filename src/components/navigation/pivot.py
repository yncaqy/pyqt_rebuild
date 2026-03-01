"""
Pivot 组件

Fluent Design 风格的枢轴/分段控件，用于类似标签页的导航。

功能特性:
- 切换标签时的平滑下划线动画
- 水平布局，项目自动调整大小
- 键盘导航支持
- 主题集成
- 动态添加/删除项目
"""

from typing import Optional, List, Dict, Any, Union
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QTimer, QEvent, pyqtProperty
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor

from core.theme_manager import ThemeManager, Theme


class PivotConfig:
    """Pivot 组件配置常量。"""
    
    # 项目水平内边距（单位：像素）
    ITEM_PADDING_H = 16
    
    # 项目垂直内边距（单位：像素）
    ITEM_PADDING_V = 8
    
    # 项目之间的间距（单位：像素）
    ITEM_SPACING = 4
    
    # 下划线高度（单位：像素）
    UNDERLINE_HEIGHT = 3
    
    # 下划线与文本的偏移量（单位：像素）
    UNDERLINE_OFFSET = 4
    
    # 字体大小（单位：像素）
    FONT_SIZE = 14
    
    # 正常状态字体粗细
    FONT_WEIGHT_NORMAL = 400
    
    # 选中状态字体粗细
    FONT_WEIGHT_SELECTED = 600
    
    # 动画持续时间（单位：毫秒）
    ANIMATION_DURATION = 200
    
    # 项目最小宽度（单位：像素）
    MIN_ITEM_WIDTH = 60
    
    # 项目最大宽度（单位：像素）
    MAX_ITEM_WIDTH = 200


class PivotItem(QWidget):
    """
    单个 Pivot 项目控件。
    
    功能特性:
    - 文本显示，支持悬停状态
    - 选中状态样式
    - 点击处理
    """
    
    clicked = pyqtSignal()
    
    def __init__(
        self, 
        text: str, 
        parent: Optional[QWidget] = None,
        item_key: Optional[str] = None
    ):
        super().__init__(parent)
        
        self._text = text
        self._key = item_key or text
        self._selected = False
        self._hovered = False
        self._hover_opacity = 0.0
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        self._current_theme = theme
        self.update()
    
    def text(self) -> str:
        """获取显示文本。"""
        return self._text
    
    def setText(self, text: str) -> None:
        """设置显示文本。"""
        self._text = text
        self.update()
        self._update_size()
    
    def key(self) -> str:
        """获取项目键。"""
        return self._key
    
    def setKey(self, key: str) -> None:
        """设置项目键。"""
        self._key = key
    
    def isSelected(self) -> bool:
        """是否选中。"""
        return self._selected
    
    def setSelected(self, selected: bool) -> None:
        """设置选中状态。"""
        if self._selected != selected:
            self._selected = selected
            self.update()
    
    def _update_size(self) -> None:
        """根据文本更新控件大小。"""
        font = QFont()
        font.setPixelSize(PivotConfig.FONT_SIZE)
        font.setWeight(
            PivotConfig.FONT_WEIGHT_SELECTED if self._selected 
            else PivotConfig.FONT_WEIGHT_NORMAL
        )
        
        from PyQt6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self._text)
        
        width = max(
            PivotConfig.MIN_ITEM_WIDTH,
            min(text_width + PivotConfig.ITEM_PADDING_H * 2, PivotConfig.MAX_ITEM_WIDTH)
        )
        height = fm.height() + PivotConfig.ITEM_PADDING_V * 2
        
        self.setFixedHeight(height)
        self.setMinimumWidth(int(width))
        self.setMaximumWidth(int(PivotConfig.MAX_ITEM_WIDTH))
    
    def sizeHint(self) -> QSize:
        """返回推荐尺寸。"""
        self._update_size()
        return super().sizeHint()
    
    def minimumSizeHint(self) -> QSize:
        """返回最小尺寸。"""
        self._update_size()
        return super().minimumSizeHint()
    
    def getHoverOpacity(self) -> float:
        """获取悬停透明度（用于动画）。"""
        return self._hover_opacity
    
    def setHoverOpacity(self, opacity: float) -> None:
        """设置悬停透明度（用于动画）。"""
        self._hover_opacity = opacity
        self.update()
    
    hoverOpacity = pyqtProperty(float, getHoverOpacity, setHoverOpacity)
    
    def _animate_hover(self, hover: bool) -> None:
        """播放悬停动画。"""
        self._hover_animation = QPropertyAnimation(self, b"hoverOpacity")
        self._hover_animation.setDuration(PivotConfig.ANIMATION_DURATION)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0 if hover else 0.0)
        self._hover_animation.start()
    
    def enterEvent(self, event: QEvent) -> None:
        """鼠标进入事件处理。"""
        self._hovered = True
        self._animate_hover(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent) -> None:
        """鼠标离开事件处理。"""
        self._hovered = False
        self._animate_hover(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件处理。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    def paintEvent(self, event) -> None:
        """绘制事件处理。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self._current_theme
        if not theme:
            return
        
        rect = self.rect()
        
        # 绘制悬停背景
        if self._hovered and not self._selected:
            hover_color = theme.get_color('pivot.item.hover', QColor(255, 255, 255, 30))
            hover_color.setAlphaF(self._hover_opacity * 0.3)
            painter.fillRect(rect, hover_color)
        
        # 绘制文本
        font = QFont()
        font.setPixelSize(PivotConfig.FONT_SIZE)
        font.setWeight(
            PivotConfig.FONT_WEIGHT_SELECTED if self._selected 
            else PivotConfig.FONT_WEIGHT_NORMAL
        )
        painter.setFont(font)
        
        if self._selected:
            text_color = theme.get_color('pivot.item.text_selected', QColor(255, 255, 255))
        else:
            text_color = theme.get_color('pivot.item.text', QColor(180, 180, 180))
        
        painter.setPen(text_color)
        painter.drawText(
            rect, 
            Qt.AlignmentFlag.AlignCenter, 
            self._text
        )
    
    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class PivotUnderline(QWidget):
    """
    Pivot 的动画下划线控件。
    
    功能特性:
    - 平滑的位置和宽度动画
    - 主题感知样式
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._target_rect = QRect(0, 0, 0, PivotConfig.UNDERLINE_HEIGHT)
        self._current_rect = QRect(0, 0, 0, PivotConfig.UNDERLINE_HEIGHT)
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        self._current_theme = theme
        self.update()
    
    def setGeometryFromParent(self, parent_rect: QRect) -> None:
        """设置几何位置以覆盖父控件。"""
        self.setGeometry(parent_rect)
    
    def animate_to(self, x: int, width: int) -> None:
        """动画移动下划线到新位置。"""
        y = self.height() - PivotConfig.UNDERLINE_HEIGHT - PivotConfig.UNDERLINE_OFFSET // 2
        
        self._target_rect = QRect(int(x), int(y), int(width), PivotConfig.UNDERLINE_HEIGHT)
        
        # 位置动画
        self._pos_animation = QPropertyAnimation(self, b"underlineRect")
        self._pos_animation.setDuration(PivotConfig.ANIMATION_DURATION)
        self._pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pos_animation.setStartValue(self._current_rect)
        self._pos_animation.setEndValue(self._target_rect)
        self._pos_animation.start()
    
    def getUnderlineRect(self) -> QRect:
        """获取下划线矩形。"""
        return self._current_rect
    
    def setUnderlineRect(self, rect: QRect) -> None:
        """设置下划线矩形。"""
        self._current_rect = rect
        self.update()
    
    underlineRect = pyqtProperty(QRect, getUnderlineRect, setUnderlineRect)
    
    def paintEvent(self, event) -> None:
        """绘制事件处理。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self._current_theme
        if not theme:
            return
        
        # 从主题获取下划线颜色
        underline_color = theme.get_color('pivot.underline', QColor(52, 152, 219))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(underline_color)
        painter.drawRoundedRect(self._current_rect, 2, 2)
    
    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)


class Pivot(QWidget):
    """
    Fluent Design 风格的 Pivot 控件，用于类似标签页的导航。
    
    功能特性:
    - 切换标签时的平滑下划线动画
    - 水平布局，项目自动调整大小
    - 键盘导航支持
    - 主题集成
    - 动态添加/删除项目
    
    使用示例:
        pivot = Pivot()
        pivot.addItem("首页", "home")
        pivot.addItem("设置", "settings")
        pivot.addItem("关于", "about")
        
        pivot.currentChanged.connect(lambda key: print(f"选中: {key}"))
        
        # 连接到 QStackedWidget
        stacked = QStackedWidget()
        pivot.currentChanged.connect(lambda key: stacked.setCurrentIndex(...))
    """
    
    currentChanged = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items: List[PivotItem] = []
        self._item_keys: Dict[str, PivotItem] = {}
        self._current_index = -1
        self._current_key: Optional[str] = None
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None
        
        self.setFixedHeight(40)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self._init_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)
    
    def _init_ui(self) -> None:
        """初始化 UI 布局。"""
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(PivotConfig.ITEM_SPACING)
        self._main_layout.addStretch()
        
        # 创建下划线控件（定位在底部）
        self._underline = PivotUnderline(self)
        self._underline.hide()
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        self._current_theme = theme
        self.update()
    
    def addItem(
        self, 
        text: str, 
        key: Optional[str] = None,
        select: bool = False
    ) -> PivotItem:
        """
        添加新项目到 Pivot。
        
        Args:
            text: 显示文本
            key: 可选的唯一键（默认为文本）
            select: 是否立即选中此项
            
        Returns:
            创建的 PivotItem
        """
        item_key = key or text
        
        if item_key in self._item_keys:
            return self._item_keys[item_key]
        
        item = PivotItem(text, self, item_key)
        item.clicked.connect(lambda: self._on_item_clicked(item))
        
        self._items.append(item)
        self._item_keys[item_key] = item
        
        # 插入到 stretch 之前
        self._main_layout.insertWidget(self._main_layout.count() - 1, item)
        
        # 默认选中第一个项目或按请求选中
        if len(self._items) == 1 or select:
            self.setCurrentItem(item_key)
        
        return item
    
    def removeItem(self, key: str) -> bool:
        """
        从 Pivot 移除项目。
        
        Args:
            key: 要移除的项目键
            
        Returns:
            移除成功返回 True，未找到返回 False
        """
        if key not in self._item_keys:
            return False
        
        item = self._item_keys[key]
        index = self._items.index(item)
        
        # 如需要则更新选中状态
        if self._current_index == index:
            if len(self._items) > 1:
                new_index = min(index, len(self._items) - 2)
                self.setCurrentIndex(new_index)
            else:
                self._current_index = -1
                self._current_key = None
                self._underline.hide()
        elif self._current_index > index:
            self._current_index -= 1
        
        self._items.remove(item)
        del self._item_keys[key]
        self._main_layout.removeWidget(item)
        item.cleanup()
        item.deleteLater()
        
        return True
    
    def clear(self) -> None:
        """移除所有项目。"""
        for item in self._items[:]:
            self._main_layout.removeWidget(item)
            item.cleanup()
            item.deleteLater()
        
        self._items.clear()
        self._item_keys.clear()
        self._current_index = -1
        self._current_key = None
        self._underline.hide()
    
    def count(self) -> int:
        """返回项目数量。"""
        return len(self._items)
    
    def itemAt(self, index: int) -> Optional[PivotItem]:
        """获取指定索引的项目。"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def item(self, key: str) -> Optional[PivotItem]:
        """通过键获取项目。"""
        return self._item_keys.get(key)
    
    def currentIndex(self) -> int:
        """返回当前项目的索引。"""
        return self._current_index
    
    def setCurrentIndex(self, index: int) -> None:
        """通过索引设置当前项目。"""
        if 0 <= index < len(self._items) and index != self._current_index:
            self._select_item(index)
    
    def currentKey(self) -> Optional[str]:
        """返回当前项目的键。"""
        return self._current_key
    
    def setCurrentItem(self, key: str) -> None:
        """通过键设置当前项目。"""
        if key in self._item_keys:
            index = self._items.index(self._item_keys[key])
            self.setCurrentIndex(index)
    
    def currentText(self) -> str:
        """返回当前项目的文本。"""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index].text()
        return ""
    
    def _on_item_clicked(self, item: PivotItem) -> None:
        """处理项目点击。"""
        index = self._items.index(item)
        self._select_item(index)
    
    def _select_item(self, index: int) -> None:
        """选中指定索引的项目。"""
        if not (0 <= index < len(self._items)):
            return
        
        old_index = self._current_index
        self._current_index = index
        
        # 更新项目状态
        for i, item in enumerate(self._items):
            item.setSelected(i == index)
        
        # 更新当前键
        self._current_key = self._items[index].key()
        
        # 动画移动下划线
        self._animate_underline(index)
        
        # 触发信号
        if old_index != index:
            self.currentChanged.emit(self._current_key)
    
    def _animate_underline(self, index: int) -> None:
        """动画移动下划线到指定索引的项目。"""
        if not (0 <= index < len(self._items)):
            return
        
        item = self._items[index]
        item_rect = item.geometry()
        
        # 计算下划线位置（文本下方居中）
        underline_width = min(item_rect.width() - 16, 60)
        underline_x = item_rect.x() + (item_rect.width() - underline_width) // 2
        
        # 更新下划线几何位置以覆盖 Pivot
        self._underline.setGeometryFromParent(self.rect())
        self._underline.show()
        self._underline.raise_()
        self._underline.animate_to(underline_x, underline_width)
    
    def resizeEvent(self, event) -> None:
        """大小改变事件处理。"""
        super().resizeEvent(event)
        
        # 重新定位下划线
        if 0 <= self._current_index < len(self._items):
            self._animate_underline(self._current_index)
    
    def keyPressEvent(self, event) -> None:
        """键盘导航处理。"""
        if event.key() == Qt.Key.Key_Left:
            if self._current_index > 0:
                self.setCurrentIndex(self._current_index - 1)
            elif len(self._items) > 0:
                self.setCurrentIndex(len(self._items) - 1)
            return
        
        if event.key() == Qt.Key.Key_Right:
            if self._current_index < len(self._items) - 1:
                self.setCurrentIndex(self._current_index + 1)
            elif len(self._items) > 0:
                self.setCurrentIndex(0)
            return
        
        if event.key() == Qt.Key.Key_Home:
            if len(self._items) > 0:
                self.setCurrentIndex(0)
            return
        
        if event.key() == Qt.Key.Key_End:
            if len(self._items) > 0:
                self.setCurrentIndex(len(self._items) - 1)
            return
        
        super().keyPressEvent(event)
    
    def cleanup(self) -> None:
        """清理资源。"""
        for item in self._items:
            item.cleanup()
        
        if hasattr(self, '_underline') and self._underline:
            self._underline.cleanup()
        
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
