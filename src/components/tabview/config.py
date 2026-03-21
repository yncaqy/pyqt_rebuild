"""
TabView 配置常量

严格遵循 WinUI3 TabView 设计规范。
参考: https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/tab-view
"""

from PyQt6.QtGui import QFont
from themes.colors import FONT_CONFIG, WINUI3_CONTROL_SIZING


class TabViewConfig:
    """
    TabView 配置常量类。
    
    基于 WinUI3 TabView 设计规范:
    - TabViewItem: Header, IconSource, IsClosable, CloseButton
    - TabView: TabStrip, LeftHeader, RightHeader, AddTabButton
    - 键盘导航: Ctrl+Tab 切换, Ctrl+F4 关闭, 箭头键移动焦点
    - 视觉: 选中标签背景高亮，与内容区域无缝连接
    """
    
    TAB_HEIGHT = 40
    TAB_MIN_WIDTH = 80
    TAB_MAX_WIDTH = 240
    TAB_PADDING_H = 12
    TAB_PADDING_V = 8
    TAB_SPACING = 0
    TAB_RADIUS = 8
    
    CLOSE_BUTTON_SIZE = 16
    CLOSE_BUTTON_MARGIN = 4
    CLOSE_BUTTON_RADIUS = 3
    ICON_SIZE = 16
    ICON_TEXT_SPACING = 8
    
    ADD_BUTTON_SIZE = 36
    SCROLL_BUTTON_SIZE = 24
    
    FONT_SIZE = FONT_CONFIG['size']['caption']
    FONT_WEIGHT_NORMAL = QFont.Weight.Normal
    FONT_WEIGHT_SELECTED = QFont.Weight.DemiBold
    
    ANIMATION_DURATION = 167
    DRAG_THRESHOLD = 20
    
    FOCUS_BORDER_WIDTH = 2
    FOCUS_BORDER_OFFSET = 2


class TabViewColors:
    """
    TabView 颜色常量类。
    
    WinUI3 TabView 颜色规范:
    - 暗色主题: 深色背景，浅色文字
    - 亮色主题: 浅色背景，深色文字
    - 选中状态: 背景高亮
    - 悬停状态: 微妙的背景变化
    - 焦点状态: 焦点边框
    """
    
    DARK = {
        'tabstrip_background': '#1E1E1E',
        'tab_background_selected': '#2D2D2D',
        'tab_background_hover': (255, 255, 255, 25),
        'tab_background_pressed': (255, 255, 255, 40),
        'tab_text': (160, 160, 160),
        'tab_text_selected': (255, 255, 255),
        'tab_text_hover': (200, 200, 200),
        'close_icon': (140, 140, 140),
        'close_icon_hover': (255, 255, 255),
        'close_background_hover': (255, 255, 255, 40),
        'close_background_pressed': (255, 255, 255, 60),
        'add_icon': (150, 150, 150),
        'add_icon_hover': (200, 200, 200),
        'scroll_icon': (150, 150, 150),
        'focus_border': (255, 255, 255, 80),
    }
    
    LIGHT = {
        'tabstrip_background': '#F3F3F3',
        'tab_background_selected': '#FFFFFF',
        'tab_background_hover': (0, 0, 0, 15),
        'tab_background_pressed': (0, 0, 0, 25),
        'tab_text': (100, 100, 100),
        'tab_text_selected': (0, 0, 0),
        'tab_text_hover': (60, 60, 60),
        'close_icon': (120, 120, 120),
        'close_icon_hover': (0, 0, 0),
        'close_background_hover': (0, 0, 0, 20),
        'close_background_pressed': (0, 0, 0, 40),
        'add_icon': (100, 100, 100),
        'add_icon_hover': (60, 60, 60),
        'scroll_icon': (100, 100, 100),
        'focus_border': (0, 0, 0, 80),
    }


class TabViewVisualStates:
    """
    TabView 视觉状态常量类。
    
    WinUI3 TabViewItem 视觉状态:
    - Normal: 默认状态
    - PointerOver: 鼠标悬停
    - Pressed: 按下状态
    - Selected: 选中状态
    - PointerOverSelected: 选中时悬停
    - PressedSelected: 选中时按下
    - Focused: 焦点状态
    - PointerFocused: 指针焦点
    - Disabled: 禁用状态
    """
    
    NORMAL = 'Normal'
    POINTER_OVER = 'PointerOver'
    PRESSED = 'Pressed'
    SELECTED = 'Selected'
    POINTER_OVER_SELECTED = 'PointerOverSelected'
    PRESSED_SELECTED = 'PressedSelected'
    FOCUSED = 'Focused'
    POINTER_FOCUSED = 'PointerFocused'
    DISABLED = 'Disabled'


class TabViewWidthMode:
    """
    TabView 宽度模式常量类。
    
    WinUI3 TabViewWidthMode 枚举:
    - Equal: 每个标签宽度相同（默认）
    - SizeToContent: 每个标签根据内容调整宽度
    - Compact: 未选中的标签折叠为仅显示图标
    """
    
    EQUAL = 'Equal'
    SIZE_TO_CONTENT = 'SizeToContent'
    COMPACT = 'Compact'


class TabViewCloseButtonOverlayMode:
    """
    TabView 关闭按钮覆盖模式常量类。
    
    WinUI3 TabViewCloseButtonOverlayMode 枚举:
    - Auto: 自动（选中时始终显示，未选中时悬停显示）
    - OnPointerOver: 仅悬停时显示
    - Always: 始终显示
    """
    
    AUTO = 'Auto'
    ON_POINTER_OVER = 'OnPointerOver'
    ALWAYS = 'Always'
