"""
默认主题定义

使用 colors.py 中定义的颜色变量，确保颜色一致性。
默认主题基于暗色主题，作为系统启动时的初始主题。
"""

from .colors import COLORS, DARK_COLORS, FONT_CONFIG, WINDOW_CONFIG

C = COLORS
D = DARK_COLORS
F = FONT_CONFIG
W = WINDOW_CONFIG

DEFAULT_THEME = {
    'name': 'default',
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
    
    'input': {
        'background': {
            'normal': D['input']['background'],
            'disabled': D['input']['background_disabled'],
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
    
    'font': F,
}
