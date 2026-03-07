"""
暗色主题定义

使用 colors.py 中定义的颜色变量，确保颜色一致性。
"""

from PyQt6.QtGui import QColor
from .colors import COLORS, DARK_COLORS, FONT_CONFIG, WINDOW_CONFIG

C = COLORS
D = DARK_COLORS
F = FONT_CONFIG
W = WINDOW_CONFIG

DARK_THEME = {
    'name': 'dark',
    'is_dark': True,
    
    'window': {
        'background': D['background']['primary'],
        'border': D['border']['default'],
        'border_radius': W['border_radius'],
    },
    
    'titlebar': {
        'background': D['titlebar']['background'],
        'text': D['text']['primary'],
        'height': W['titlebar_height'],
        'button': {
            'hover': D['titlebar']['button_hover'],
            'close_hover': D['titlebar']['close_hover'],
        },
    },
    
    'label': {
        'text': {
            'title': D['text']['primary'],
            'header': D['text']['primary'],
            'subtitle': D['text']['primary'],
            'body': D['text']['primary'],
            'small': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'background': 'transparent',
    },
    
    'button': {
        'background': {
            'normal': D['button']['background'],
            'hover': D['button']['background_hover'],
            'pressed': D['button']['background_pressed'],
            'disabled': D['button']['background_disabled'],
            'checked': C['primary']['main'],
            'checked_hover': C['primary']['dark'],
            'checked_pressed': C['primary']['active'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
            'checked': D['text']['primary'],
        },
        'icon': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': D['border']['light'],
            'hover': C['primary']['main'],
            'pressed': C['primary']['dark'],
            'disabled': D['border']['default'],
            'checked': C['primary']['main'],
        },
        'border_radius': 6,
        'padding': '8px 16px',
    },
    
    'pill': {
        'background': {
            'normal': D['button']['background'],
            'hover': D['button']['background_hover'],
            'disabled': D['button']['background_disabled'],
            'checked': C['primary']['main'],
            'checked_hover': C['primary']['dark'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
            'checked': D['text']['primary'],
        },
        'border': {
            'normal': D['border']['light'],
            'hover': C['primary']['main'],
            'disabled': D['border']['default'],
            'checked': C['primary']['main'],
        },
        'padding': '6px 12px',
    },
    
    'dropdown': {
        'background': {
            'normal': D['button']['background'],
            'hover': D['button']['background_hover'],
            'pressed': D['button']['background_pressed'],
            'disabled': D['button']['background_disabled'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': D['border']['light'],
            'hover': C['primary']['main'],
            'pressed': C['primary']['dark'],
            'disabled': D['border']['default'],
        },
        'arrow': {
            'normal': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 6,
        'padding': '8px 12px',
    },
    
    'combobox': {
        'background': {
            'normal': D['button']['background'],
            'hover': D['button']['background_hover'],
            'pressed': D['button']['background_pressed'],
            'disabled': D['button']['background_disabled'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': D['border']['light'],
            'hover': C['primary']['main'],
            'pressed': C['primary']['dark'],
            'disabled': D['border']['default'],
        },
        'arrow': {
            'normal': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 6,
        'padding': '8px 12px',
    },
    
    'primary': {
        'background': {
            'normal': C['primary']['main'],
            'hover': C['primary']['dark'],
            'pressed': C['primary']['active'],
            'disabled': D['button']['background_disabled'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 6,
        'padding': '8px 16px',
    },
    
    'link': {
        'normal': C['primary']['main'],
        'hover': C['primary']['dark'],
    },
    
    'input': {
        'background': {
            'normal': D['input']['background'],
            'disabled': D['input']['background_disabled'],
            'readonly': '#252525',
            'error': '#3a2525',
        },
        'text': {
            'normal': D['text']['primary'],
            'placeholder': D['text']['placeholder'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': D['input']['border'],
            'focus': D['input']['border_focus'],
            'error': C['error']['main'],
            'disabled': D['border']['default'],
        },
        'border_radius': 4,
        'padding': '8px 12px',
        'selection': {
            'background': C['primary']['main'],
            'text': '#ffffff',
        },
    },
    
    'textedit': {
        'background': D['input']['background'],
        'background_readonly': '#252525',
        'current_line': {
            'background': QColor(40, 55, 40),
        },
        'line_number': {
            'color': QColor(100, 100, 100),
            'background': QColor(30, 30, 30),
            'current': QColor(180, 180, 180),
        },
        'toolbar': {
            'background': QColor(45, 45, 45),
            'border': QColor(55, 55, 55),
            'text': QColor(200, 200, 200),
            'hover': QColor(60, 60, 60),
            'pressed': QColor(70, 70, 70),
            'checked': QColor(50, 70, 90),
        },
        'padding': 8,
    },
    
    'checkbox': {
        'background': {
            'normal': 'transparent',
            'hover': 'transparent',
            'checked': C['primary']['main'],
            'disabled': 'transparent',
        },
        'border': {
            'normal': D['checkbox']['border'],
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': D['border']['default'],
        },
        'checkmark': D['checkbox']['checkmark'],
        'checkmark_disabled': D['text']['disabled'],
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 4,
        'size': 18,
    },
    
    'radiobutton': {
        'background': {
            'normal': 'transparent',
            'hover': 'transparent',
            'disabled': 'transparent',
        },
        'border': {
            'normal': D['border']['light'],
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': D['border']['default'],
        },
        'indicator': C['primary']['main'],
        'indicator_disabled': D['text']['disabled'],
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 9,
        'size': 18,
    },
    
    'switch': {
        'track': {
            'off': D['border']['light'],
            'on': C['primary']['main'],
            'disabled': D['border']['default'],
        },
        'handle': '#ffffff',
        'handle_disabled': D['text']['disabled'],
    },
    
    'datepicker': {
        'background': D['input']['background'],
        'background_disabled': D['input']['background_disabled'],
        'border': D['input']['border'],
        'border_focus': D['input']['border_focus'],
        'text': D['text']['primary'],
        'text_disabled': D['text']['disabled'],
        'border_radius': 4,
    },
    
    'timepicker': {
        'background': D['input']['background'],
        'background_disabled': D['input']['background_disabled'],
        'border': D['input']['border'],
        'border_focus': D['input']['border_focus'],
        'text': D['text']['primary'],
        'text_disabled': D['text']['disabled'],
        'border_radius': 4,
        'icon': {
            'normal': D['text']['secondary'],
            'hover': D['text']['primary'],
        },
    },
    
    'timewheel': {
        'selection': {
            'background': D['background']['tertiary'],
        },
        'text': {
            'normal': D['text']['secondary'],
            'selected': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
    },
    
    'calendar': {
        'background': D['background']['secondary'],
        'border': D['border']['default'],
        'header': {
            'background': D['background']['tertiary'],
            'text': D['text']['primary'],
        },
        'item': {
            'normal': D['text']['primary'],
            'selected': '#ffffff',
            'hover': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'selection': C['primary']['main'],
        'border_radius': 8,
    },
    
    'slider': {
        'groove': {
            'background': D['slider']['groove'],
            'disabled': D['background']['tertiary'],
            'height': 6,
        },
        'handle': {
            'background': D['slider']['handle'],
            'hover': D['slider']['handle_hover'],
            'pressed': C['primary']['dark'],
            'disabled': D['slider']['handle_disabled'],
            'size': 18,
            'border_radius': 9,
        },
        'border_radius': 2,
    },
    
    'progress': {
        'circular': {
            'background': D['background']['tertiary'],
            'progress': C['primary']['main'],
            'gradient_end': C['primary']['light'],
            'text': D['text']['primary'],
        },
    },
    
    'groupbox': {
        'background': D['groupbox']['background'],
        'border': D['groupbox']['border'],
        'title': {
            'color': D['text']['primary'],
            'font_size': F['size']['header'],
            'font_weight': 'bold',
        },
        'border_radius': 8,
        'border_width': 1,
        'margin_top': 24,
    },
    
    'scrollarea': {
        'background': 'transparent',
        'border': 'transparent',
        'border_radius': 0,
        'border_width': 0,
    },
    
    'scrollbar': {
        'background': D['scrollbar']['background'],
        'handle': {
            'normal': D['scrollbar']['handle'],
            'hover': D['scrollbar']['handle_hover'],
        },
        'width': 12,
        'border_radius': 6,
        'margin': 2,
    },
    
    'toast': {
        'info': {
            'background': '#1a3a4a',
            'border': C['info']['main'],
            'text': D['text']['primary'],
            'icon': C['info']['main'],
        },
        'success': {
            'background': '#1a3a2a',
            'border': C['success']['main'],
            'text': D['text']['primary'],
            'icon': C['success']['main'],
        },
        'warning': {
            'background': '#3a3a1a',
            'border': C['warning']['main'],
            'text': D['text']['primary'],
            'icon': C['warning']['main'],
        },
        'error': {
            'background': '#3a1a1a',
            'border': C['error']['main'],
            'text': D['text']['primary'],
            'icon': C['error']['main'],
        },
        'border_radius': 8,
        'shadow_blur': 10,
    },
    
    'tooltip': {
        'background': '#4a4a4a',
        'text': D['text']['primary'],
        'border': '#5a5a5a',
    },
    
    'menu': {
        'background': D['background']['secondary'],
        'border': D['border']['default'],
        'shadow': QColor(0, 0, 0, 80),
        'border_radius': 8,
        'item': {
            'text': D['text']['primary'],
            'text_disabled': D['text']['disabled'],
            'hover': D['button']['background_hover'],
            'shortcut': D['text']['secondary'],
            'check': C['primary']['main'],
        },
        'separator': D['border']['default'],
    },
    
    'pivot': {
        'background': 'transparent',
        'item': {
            'text': D['text']['secondary'],
            'text_selected': D['text']['primary'],
            'hover': D['button']['background_hover'],
        },
        'underline': C['primary']['main'],
    },
    
    'tabbar': {
        'background': D['background']['secondary'],
        'item': {
            'text': D['text']['secondary'],
            'text_selected': D['text']['primary'],
            'background_selected': D['background']['primary'],
            'hover': D['button']['background_hover'],
        },
        'indicator': C['primary']['main'],
        'close_icon': QColor(120, 120, 120),
        'close_hover': QColor(70, 70, 70),
        'close_pressed': QColor(50, 50, 50),
        'scroll_icon': D['text']['secondary'],
    },
    
    'mediabar': {
        'background': QColor(40, 40, 40),
        'groove': QColor(60, 60, 60),
        'filled': C['primary']['main'],
        'handle': QColor(255, 255, 255),
        'text': QColor(180, 180, 180),
    },
    
    'icon': {
        'normal': D['text']['primary'],
        'disabled': D['text']['disabled'],
        'hover': C['primary']['light'],
        'pressed': C['primary']['main'],
    },
    
    'card': {
        'background': D['background']['secondary'],
        'border': D['border']['default'],
        'shadow': '#40000000',
    },
    
    'font': F,
}
