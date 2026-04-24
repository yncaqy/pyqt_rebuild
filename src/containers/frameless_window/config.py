"""
无边框窗口配置常量和枚举

提供无边框窗口组件的配置常量、默认值和位置枚举。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class WindowConfig:
    """无边框窗口行为配置常量。"""

    # 边缘检测
    DEFAULT_EDGE_MARGIN = 6  # 像素
    TITLEBAR_EDGE_MARGIN = 6  # 像素

    # 标题栏尺寸
    TITLEBAR_HEIGHT = 40
    TITLEBAR_BUTTON_WIDTH = 46
    TITLEBAR_BUTTON_HEIGHT = 40
    TITLEBAR_ICON_SIZE = 24
    TITLEBAR_ICON_SPACING = 12  # 图标和标题之间的间距
    TITLEBAR_LAYOUT_MARGIN_LEFT = 10  # 标题栏布局左边距

    # 自定义组件区域配置
    CUSTOM_WIDGET_SPACING = 8  # 自定义组件之间的间距
    CUSTOM_WIDGET_MARGIN = 4  # 自定义组件与边界的间距

    # 图标尺寸
    BUTTON_ICON_SOURCE_SIZE = 32  # 加载时的源尺寸（HiDPI 支持）
    BUTTON_ICON_DISPLAY_SIZE = 20  # 按钮上的显示尺寸
    BUTTON_COLORED_ICON_SOURCE_SIZE = 32  # 彩色图标的源尺寸

    # 窗口约束
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300

    # 性能调优
    EVENT_FILTER_THRESHOLD_MS = 16  # 约 60fps
    MAX_EDGE_CACHE_SIZE = 1000

    # 内容边距
    CONTENT_MARGIN = 10

    # 默认颜色值（主题不可用时的回退值）
    DEFAULT_TITLEBAR_TEXT_COLOR = QColor(220, 220, 220)
    DEFAULT_TITLEBAR_BG_COLOR = QColor(30, 30, 30)
    DEFAULT_BUTTON_HOVER_COLOR = QColor(50, 50, 50)
    DEFAULT_CLOSE_HOVER_COLOR = QColor(231, 76, 60)
    DEFAULT_WINDOW_BG_COLOR = QColor(25, 25, 25)
    DEFAULT_BORDER_COLOR = QColor(40, 40, 40)

    # 边缘调整大小的光标
    CURSOR_MAP = {
        'top': Qt.CursorShape.SizeVerCursor,
        'bottom': Qt.CursorShape.SizeVerCursor,
        'left': Qt.CursorShape.SizeHorCursor,
        'right': Qt.CursorShape.SizeHorCursor,
        'top-left': Qt.CursorShape.SizeFDiagCursor,
        'top-right': Qt.CursorShape.SizeBDiagCursor,
        'bottom-left': Qt.CursorShape.SizeBDiagCursor,
        'bottom-right': Qt.CursorShape.SizeFDiagCursor,
        'none': Qt.CursorShape.ArrowCursor
    }


class TitleBarPosition:
    """标题栏自定义组件位置枚举。"""
    LEFT = 'left'  # 图标和标题之间
    CENTER = 'center'  # 标题和控制按钮之间
    RIGHT = 'right'  # 控制按钮左侧
