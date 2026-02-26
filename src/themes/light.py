"""
亮色主题定义

使用 colors.py 中定义的颜色变量，确保颜色一致性。
"""

from .colors import COLORS, LIGHT_COLORS, FONT_CONFIG, WINDOW_CONFIG

C = COLORS
L = LIGHT_COLORS
F = FONT_CONFIG
W = WINDOW_CONFIG

LIGHT_THEME = {
    'name': 'light',
    
    'window': {
        'background': L['background']['primary'],
        'border': L['border']['default'],
        'border_radius': W['border_radius'],
    },
    
    'titlebar': {
        'background': L['titlebar']['background'],
        'text': L['text']['primary'],
        'height': W['titlebar_height'],
        'button': {
            'hover': L['titlebar']['button_hover'],
            'close_hover': L['titlebar']['close_hover'],
        },
    },
    
    'label': {
        'text': {
            'title': L['text']['primary'],
            'header': L['text']['primary'],
            'body': L['text']['primary'],
            'small': L['text']['secondary'],
            'disabled': L['text']['disabled'],
        },
        'background': 'transparent',
    },
    
    'button': {
        'background': {
            'normal': L['button']['background'],
            'hover': L['button']['background_hover'],
            'pressed': L['button']['background_pressed'],
            'disabled': L['button']['background_disabled'],
        },
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'icon': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border': {
            'normal': L['border']['light'],
            'hover': C['primary']['main'],
            'pressed': C['primary']['dark'],
            'disabled': L['border']['default'],
        },
        'border_radius': 6,
        'padding': '8px 16px',
    },
    
    'primary': {
        'background': {
            'normal': C['primary']['main'],
            'hover': C['primary']['dark'],
            'pressed': C['primary']['active'],
            'disabled': L['button']['background_disabled'],
        },
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border_radius': 6,
        'padding': '8px 16px',
    },
    
    'input': {
        'background': {
            'normal': L['input']['background'],
            'disabled': L['input']['background_disabled'],
            'error': '#fff5f5',
        },
        'text': {
            'normal': L['text']['primary'],
            'placeholder': L['text']['placeholder'],
            'disabled': L['text']['disabled'],
        },
        'border': {
            'normal': L['input']['border'],
            'focus': L['input']['border_focus'],
            'error': C['error']['main'],
            'disabled': L['border']['default'],
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
            'normal': L['checkbox']['border'],
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': L['border']['default'],
        },
        'checkmark': L['checkbox']['checkmark'],
        'checkmark_disabled': L['text']['disabled'],
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border_radius': 4,
        'size': 18,
    },
    
    'slider': {
        'groove': {
            'background': L['slider']['groove'],
            'disabled': L['background']['tertiary'],
            'height': 6,
        },
        'handle': {
            'background': L['slider']['handle'],
            'hover': L['slider']['handle_hover'],
            'pressed': C['primary']['dark'],
            'disabled': L['slider']['handle_disabled'],
            'size': 18,
            'border_radius': 9,
        },
    },
    
    'progress': {
        'circular': {
            'background': L['background']['tertiary'],
            'progress': C['primary']['main'],
            'gradient_end': C['primary']['light'],
            'text': L['text']['primary'],
        },
    },
    
    'groupbox': {
        'background': L['groupbox']['background'],
        'border': L['groupbox']['border'],
        'title': {
            'color': L['text']['primary'],
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
        'background': L['scrollbar']['background'],
        'handle': {
            'normal': L['scrollbar']['handle'],
            'hover': L['scrollbar']['handle_hover'],
        },
        'width': 12,
        'border_radius': 6,
        'margin': 2,
    },
    
    'toast': {
        'info': {
            'background': '#e8f4fc',
            'border': C['info']['main'],
            'text': L['text']['primary'],
            'icon': C['info']['main'],
        },
        'success': {
            'background': '#e8fce8',
            'border': C['success']['main'],
            'text': L['text']['primary'],
            'icon': C['success']['main'],
        },
        'warning': {
            'background': '#fcfce8',
            'border': C['warning']['main'],
            'text': L['text']['primary'],
            'icon': C['warning']['main'],
        },
        'error': {
            'background': '#fce8e8',
            'border': C['error']['main'],
            'text': L['text']['primary'],
            'icon': C['error']['main'],
        },
        'border_radius': 8,
        'shadow_blur': 10,
    },
    
    'tooltip': {
        'background': '#ffffff',
        'text': '#333333',
        'border': '#cccccc',
    },
    
    'card': {
        'background': L['background']['secondary'],
        'border': L['border']['default'],
        'shadow': '#20000000',
    },
    
    'font': F,
}
