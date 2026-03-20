"""
WinUI3 设计系统配置

严格遵循 WinUI3 设计规范定义的设计令牌。
包括颜色、字体、间距、动画、阴影等所有设计元素。

参考文档:
https://learn.microsoft.com/zh-cn/windows/apps/design/
"""

from PyQt6.QtGui import QColor
from typing import Dict, Any

WINUI3_DESIGN_TOKENS = {
    'typography': {
        'font_family': 'Segoe UI Variable',
        'font_family_fallback': ['Segoe UI', 'Microsoft YaHei UI', 'Arial'],
        'type_ramp': {
            'caption': {'size': 12, 'line_height': 16, 'weight': 'Regular'},
            'body': {'size': 14, 'line_height': 20, 'weight': 'Regular'},
            'body_strong': {'size': 14, 'line_height': 20, 'weight': 'SemiBold'},
            'body_large': {'size': 18, 'line_height': 24, 'weight': 'Regular'},
            'subtitle': {'size': 20, 'line_height': 28, 'weight': 'SemiBold'},
            'title': {'size': 28, 'line_height': 36, 'weight': 'SemiBold'},
            'title_large': {'size': 40, 'line_height': 52, 'weight': 'SemiBold'},
            'display': {'size': 68, 'line_height': 92, 'weight': 'SemiBold'},
        },
        'weight_values': {
            'Light': 300,
            'SemiLight': 350,
            'Regular': 400,
            'SemiBold': 600,
            'Bold': 700,
        }
    },
    
    'animation': {
        'durations': {
            'instant': 0,
            'fast': 83,
            'normal': 167,
            'slow': 250,
            'slower': 333,
        },
        'easing': {
            'direct_enter': 'cubic-bezier(0, 0, 0, 1)',
            'existing_element': 'cubic-bezier(0.55, 0.55, 0, 1)',
            'direct_exit': 'cubic-bezier(0, 0, 0, 1)',
            'gentle_exit': 'cubic-bezier(1, 0, 1, 1)',
            'minimal': 'linear',
        },
        'presets': {
            'hover': {'duration': 167, 'easing': 'cubic-bezier(0, 0, 0, 1)'},
            'press': {'duration': 83, 'easing': 'linear'},
            'focus': {'duration': 167, 'easing': 'cubic-bezier(0, 0, 0, 1)'},
            'expand': {'duration': 167, 'easing': 'cubic-bezier(0, 0, 0, 1)'},
            'collapse': {'duration': 167, 'easing': 'cubic-bezier(1, 0, 1, 1)'},
            'page_transition': {'duration': 250, 'easing': 'cubic-bezier(0.55, 0.55, 0, 1)'},
        }
    },
    
    'spacing': {
        'xsmall': 4,
        'small': 8,
        'medium': 12,
        'large': 16,
        'xlarge': 24,
        'xxlarge': 32,
        'xxxlarge': 48,
    },
    
    'sizing': {
        'control_height': {
            'compact': 24,
            'normal': 32,
            'comfortable': 40,
        },
        'border_radius': {
            'small': 4,
            'medium': 6,
            'large': 8,
            'xlarge': 12,
        },
        'icon': {
            'xsmall': 12,
            'small': 16,
            'medium': 20,
            'large': 24,
            'xlarge': 32,
            'xxlarge': 48,
        }
    },
    
    'colors': {
        'accent': '#595959',
        'accent_light': '#808080',
        'accent_dark': '#404040',
        
        'dark_theme': {
            'background': {
                'mica': '#1C1C1C',
                'solid_base': '#202020',
                'secondary': '#1C1C1C',
                'tertiary': '#282828',
                'elevated': '#2D2D2D',
                'card': '#2D2D2D',
            },
            'text': {
                'primary': '#FFFFFF',
                'secondary': QColor(255, 255, 255, 197),
                'tertiary': QColor(255, 255, 255, 135),
                'disabled': QColor(255, 255, 255, 92),
                'placeholder': QColor(255, 255, 255, 135),
            },
            'control': {
                'background': QColor(255, 255, 255, 9),
                'background_hover': QColor(255, 255, 255, 14),
                'background_pressed': QColor(255, 255, 255, 6),
                'background_disabled': QColor(255, 255, 255, 4),
                'border': QColor(255, 255, 255, 24),
                'border_hover': QColor(255, 255, 255, 39),
                'border_pressed': QColor(255, 255, 255, 24),
                'border_disabled': QColor(255, 255, 255, 12),
                'border_focused': '#595959',
            },
            'surface': {
                'stroke': QColor(255, 255, 255, 15),
                'stroke_card': QColor(255, 255, 255, 9),
                'stroke_surface': QColor(0, 0, 0, 15),
            },
            'overlay': {
                'hover': QColor(255, 255, 255, 24),
                'pressed': QColor(255, 255, 255, 16),
                'selected': QColor(255, 255, 255, 18),
            }
        },
        
        'light_theme': {
            'background': {
                'mica': '#F3F3F3',
                'solid_base': '#F3F3F3',
                'secondary': '#EEEEEE',
                'tertiary': '#F9F9F9',
                'elevated': '#FFFFFF',
                'card': '#FFFFFF',
            },
            'text': {
                'primary': QColor(0, 0, 0, 228),
                'secondary': QColor(0, 0, 0, 158),
                'tertiary': QColor(0, 0, 0, 114),
                'disabled': QColor(0, 0, 0, 92),
                'placeholder': QColor(0, 0, 0, 114),
            },
            'control': {
                'background': QColor(0, 0, 0, 6),
                'background_hover': QColor(0, 0, 0, 11),
                'background_pressed': QColor(0, 0, 0, 4),
                'background_disabled': QColor(0, 0, 0, 3),
                'border': QColor(0, 0, 0, 24),
                'border_hover': QColor(0, 0, 0, 39),
                'border_pressed': QColor(0, 0, 0, 24),
                'border_disabled': QColor(0, 0, 0, 12),
                'border_focused': '#595959',
            },
            'surface': {
                'stroke': QColor(0, 0, 0, 10),
                'stroke_card': QColor(0, 0, 0, 6),
                'stroke_surface': QColor(0, 0, 0, 13),
            },
            'overlay': {
                'hover': QColor(0, 0, 0, 10),
                'pressed': QColor(0, 0, 0, 6),
                'selected': QColor(0, 0, 0, 8),
            }
        }
    },
    
    'shadows': {
        'dark_theme': {
            'card': {'offset': (0, 4), 'blur': 16, 'color': QColor(0, 0, 0, 80)},
            'tooltip': {'offset': (0, 8), 'blur': 24, 'color': QColor(0, 0, 0, 100)},
            'flyout': {'offset': (0, 8), 'blur': 32, 'color': QColor(0, 0, 0, 120)},
        },
        'light_theme': {
            'card': {'offset': (0, 4), 'blur': 16, 'color': QColor(0, 0, 0, 40)},
            'tooltip': {'offset': (0, 8), 'blur': 24, 'color': QColor(0, 0, 0, 50)},
            'flyout': {'offset': (0, 8), 'blur': 32, 'color': QColor(0, 0, 0, 60)},
        }
    },
    
    'states': {
        'normal': {
            'opacity': 1.0,
            'scale': 1.0,
        },
        'hover': {
            'opacity': 1.0,
            'scale': 1.0,
        },
        'pressed': {
            'opacity': 0.9,
            'scale': 0.98,
        },
        'disabled': {
            'opacity': 0.4,
            'scale': 1.0,
        },
        'focused': {
            'opacity': 1.0,
            'scale': 1.0,
        }
    }
}

WINUI3_CONTROL_STANDARDS = {
    'button': {
        'height': 32,
        'min_width': 80,
        'padding_h': 12,
        'padding_v': 6,
        'border_radius': 4,
        'icon_size': 16,
        'icon_text_spacing': 8,
    },
    'button_compact': {
        'height': 24,
        'min_width': 0,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 4,
        'icon_size': 14,
        'icon_text_spacing': 6,
    },
    'dropdown': {
        'height': 32,
        'min_width': 120,
        'padding_h': 12,
        'padding_v': 6,
        'border_radius': 4,
        'arrow_size': 12,
        'arrow_margin': 8,
        'icon_size': 16,
    },
    'dropdown_compact': {
        'height': 24,
        'min_width': 100,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 4,
        'arrow_size': 10,
        'arrow_margin': 6,
        'icon_size': 14,
    },
    'input': {
        'height': 32,
        'min_width': 120,
        'padding_h': 12,
        'padding_v': 6,
        'border_radius': 4,
        'border_width': 1,
    },
    'checkbox': {
        'size': 20,
        'border_radius': 4,
        'checkmark_size': 12,
        'label_spacing': 8,
    },
    'radiobutton': {
        'size': 20,
        'border_radius': 10,
        'indicator_size': 10,
        'label_spacing': 8,
    },
    'switch': {
        'width': 40,
        'height': 20,
        'handle_size': 12,
        'border_radius': 10,
    },
    'slider': {
        'groove_height': 4,
        'handle_size': 20,
        'handle_radius': 10,
        'groove_radius': 2,
    },
    'tab': {
        'height': 40,
        'min_width': 80,
        'padding_h': 12,
        'padding_v': 8,
        'indicator_height': 3,
    },
    'menu': {
        'item_height': 32,
        'min_width': 120,
        'padding_h': 12,
        'padding_v': 6,
        'border_radius': 8,
        'icon_size': 16,
        'icon_text_spacing': 8,
    },
    'list_item': {
        'height': 40,
        'padding_h': 12,
        'padding_v': 8,
        'icon_size': 20,
        'icon_text_spacing': 12,
    },
    'card': {
        'padding': 16,
        'border_radius': 8,
        'border_width': 1,
        'shadow_blur': 16,
    },
    'tooltip': {
        'padding_h': 8,
        'padding_v': 4,
        'border_radius': 4,
        'max_width': 320,
    },
}

def get_design_token(path: str, is_dark: bool = True) -> Any:
    """
    获取设计令牌值。
    
    Args:
        path: 令牌路径，使用点号分隔（如 'colors.dark_theme.text.primary'）
        is_dark: 是否为暗色主题
        
    Returns:
        令牌值
    """
    parts = path.split('.')
    value = WINUI3_DESIGN_TOKENS
    
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
            if value is None:
                return None
        else:
            return None
    
    return value

def get_control_standard(control_type: str, compact: bool = False) -> Dict[str, Any]:
    """
    获取控件标准配置。
    
    Args:
        control_type: 控件类型
        compact: 是否使用紧凑模式
        
    Returns:
        控件配置字典
    """
    key = f"{control_type}_compact" if compact else control_type
    return WINUI3_CONTROL_STANDARDS.get(key, {})

def get_animation_preset(preset_name: str) -> Dict[str, Any]:
    """
    获取动画预设。
    
    Args:
        preset_name: 预设名称
        
    Returns:
        动画配置字典
    """
    return WINUI3_DESIGN_TOKENS['animation']['presets'].get(preset_name, {})

def get_color_token(category: str, name: str, is_dark: bool = True) -> QColor:
    """
    获取颜色令牌。
    
    Args:
        category: 颜色类别（如 'text', 'control', 'background'）
        name: 颜色名称
        is_dark: 是否为暗色主题
        
    Returns:
        QColor 对象
    """
    theme = 'dark_theme' if is_dark else 'light_theme'
    colors = WINUI3_DESIGN_TOKENS['colors'].get(theme, {})
    category_colors = colors.get(category, {})
    return category_colors.get(name, QColor(128, 128, 128))
