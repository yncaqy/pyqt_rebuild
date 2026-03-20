"""
WinUI3 ComboBox 配置常量

遵循 WinUI3 设计规范定义 ComboBox 组件的尺寸、颜色和动画参数。

参考文档:
https://learn.microsoft.com/zh-cn/windows/apps/develop/ui/controls/combo-box
"""

from PyQt6.QtGui import QColor
from typing import Dict

try:
    from themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG
except ImportError:
    from ...themes.colors import WINUI3_CONTROL_SIZING, FONT_CONFIG


class ComboBoxConfig:
    """ComboBox 配置常量，严格遵循 WinUI3 设计规范。"""
    
    MIN_HEIGHT = WINUI3_CONTROL_SIZING['dropdown']['min_height']
    MIN_WIDTH = 120
    
    PADDING_H = WINUI3_CONTROL_SIZING['dropdown']['padding_h']
    PADDING_V = WINUI3_CONTROL_SIZING['dropdown']['padding_v']
    BORDER_RADIUS = WINUI3_CONTROL_SIZING['dropdown']['border_radius']
    
    ARROW_SIZE = WINUI3_CONTROL_SIZING['dropdown']['arrow_size']
    ARROW_MARGIN = WINUI3_CONTROL_SIZING['dropdown']['arrow_margin']
    
    DARK_COLORS = {
        'background_normal': QColor(255, 255, 255, 9),
        'background_hover': QColor(255, 255, 255, 14),
        'background_pressed': QColor(255, 255, 255, 6),
        'background_disabled': QColor(255, 255, 255, 4),
        'background_focused': QColor(255, 255, 255, 9),
        
        'border_normal': QColor(255, 255, 255, 0),
        'border_hover': QColor(255, 255, 255, 0),
        'border_pressed': QColor(255, 255, 255, 0),
        'border_disabled': QColor(255, 255, 255, 0),
        'border_focused': QColor(255, 255, 255, 0),
        
        'text_normal': QColor(255, 255, 255),
        'text_placeholder': QColor(255, 255, 255, 135),
        'text_disabled': QColor(255, 255, 255, 92),
        
        'arrow_normal': QColor(255, 255, 255, 153),
        'arrow_hover': QColor(255, 255, 255, 204),
        'arrow_disabled': QColor(255, 255, 255, 92),
    }
    
    LIGHT_COLORS = {
        'background_normal': QColor(0, 0, 0, 6),
        'background_hover': QColor(0, 0, 0, 11),
        'background_pressed': QColor(0, 0, 0, 4),
        'background_disabled': QColor(0, 0, 0, 3),
        'background_focused': QColor(0, 0, 0, 6),
        
        'border_normal': QColor(0, 0, 0, 0),
        'border_hover': QColor(0, 0, 0, 0),
        'border_pressed': QColor(0, 0, 0, 0),
        'border_disabled': QColor(0, 0, 0, 0),
        'border_focused': QColor(0, 0, 0, 0),
        
        'text_normal': QColor(0, 0, 0, 228),
        'text_placeholder': QColor(0, 0, 0, 114),
        'text_disabled': QColor(0, 0, 0, 92),
        
        'arrow_normal': QColor(0, 0, 0, 153),
        'arrow_hover': QColor(0, 0, 0, 204),
        'arrow_disabled': QColor(0, 0, 0, 92),
    }
    
    @classmethod
    def get_colors(cls, is_dark: bool) -> Dict[str, QColor]:
        return cls.DARK_COLORS if is_dark else cls.LIGHT_COLORS


class ComboBoxMenuConfig:
    """ComboBox 下拉菜单配置常量。"""
    
    MAX_VISIBLE_ITEMS = 10
    ITEM_HEIGHT = 36
    ITEM_PADDING_H = 12
    ITEM_PADDING_V = 8
    ITEM_BORDER_RADIUS = 4
    
    BORDER_RADIUS = 8
    BORDER_WIDTH = 1
    
    INDICATOR_WIDTH = 3
    INDICATOR_MARGIN = 4
    
    SHADOW_OFFSET = 4
    SHADOW_BLUR = 16
    SHADOW_COLOR_DARK = QColor(0, 0, 0, 80)
    SHADOW_COLOR_LIGHT = QColor(0, 0, 0, 40)
    
    ANIMATION_DURATION = 167
    
    DARK_COLORS = {
        'background': QColor(44, 44, 44),
        'border': QColor(255, 255, 255, 0),
        
        'item_background_normal': QColor(255, 255, 255, 0),
        'item_background_hover': QColor(255, 255, 255, 18),
        'item_background_selected': QColor(255, 255, 255, 12),
        
        'item_text_normal': QColor(255, 255, 255),
        'item_text_hover': QColor(255, 255, 255),
        'item_text_selected': QColor(255, 255, 255),
        'item_text_disabled': QColor(255, 255, 255, 92),
        
        'checkmark': QColor('#60CDFF'),
    }
    
    LIGHT_COLORS = {
        'background': QColor(252, 252, 252),
        'border': QColor(0, 0, 0, 0),
        
        'item_background_normal': QColor(0, 0, 0, 0),
        'item_background_hover': QColor(0, 0, 0, 12),
        'item_background_selected': QColor(0, 0, 0, 8),
        
        'item_text_normal': QColor(0, 0, 0, 228),
        'item_text_hover': QColor(0, 0, 0, 228),
        'item_text_selected': QColor(0, 0, 0, 228),
        'item_text_disabled': QColor(0, 0, 0, 92),
        
        'checkmark': QColor('#595959'),
    }
    
    @classmethod
    def get_colors(cls, is_dark: bool) -> Dict[str, QColor]:
        return cls.DARK_COLORS if is_dark else cls.LIGHT_COLORS


class ComboBoxAnimationConfig:
    """ComboBox 动画配置常量，严格遵循 WinUI3 动画规范。"""
    
    HOVER_DURATION = 167
    PRESS_DURATION = 83
    MENU_OPEN_DURATION = 167
    MENU_CLOSE_DURATION = 167
    
    DIRECT_ENTER_EASING = (0, 0, 0, 1)
    GENTLE_EXIT_EASING = (1, 0, 1, 1)
    MINIMAL_EASING = (0, 0, 1, 1)
