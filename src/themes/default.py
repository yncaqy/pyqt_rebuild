"""
WinUI3 默认主题定义

遵循 WinUI3 设计规范，使用 Fluent Design System。
默认主题基于暗色主题，作为系统启动时的初始主题。
"""

from PyQt6.QtGui import QColor
from .colors import COLORS, WINUI3_DARK_COLORS, FONT_CONFIG, WINDOW_CONFIG, WINUI3_CONTROL_SIZING

C = COLORS
D = WINUI3_DARK_COLORS
F = FONT_CONFIG
W = WINDOW_CONFIG
S = WINUI3_CONTROL_SIZING

DEFAULT_THEME = {
    'name': 'default',
    'is_dark': True,
    
    'window': {
        'background': D['background']['mica'],
        'border': D['border']['surface'],
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
            'subtitle': D['text']['secondary'],
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
            'checked_hover': C['primary']['hover'],
            'checked_pressed': C['primary']['active'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
            'checked': '#FFFFFF',
        },
        'icon': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': 'transparent',
            'hover': 'transparent',
            'pressed': 'transparent',
            'disabled': 'transparent',
            'checked': C['primary']['main'],
        },
        'border_radius': S['button']['border_radius'],
        'padding': f"{S['button']['padding_v']}px {S['button']['padding_h']}px",
        'min_height': S['button']['min_height'],
        'min_width': S['button']['min_width'],
        'icon_size': S['button']['icon_size'],
    },
    
    'pill': {
        'background': {
            'normal': D['button']['background'],
            'hover': D['button']['background_hover'],
            'disabled': D['button']['background_disabled'],
            'checked': C['primary']['main'],
            'checked_hover': C['primary']['hover'],
        },
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
            'checked': '#FFFFFF',
        },
        'border': {
            'normal': 'transparent',
            'hover': 'transparent',
            'disabled': 'transparent',
            'checked': C['primary']['main'],
        },
        'padding': '6px 12px',
        'border_radius': 16,
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
            'normal': 'transparent',
            'hover': 'transparent',
            'pressed': C['primary']['main'],
            'disabled': 'transparent',
        },
        'arrow': {
            'normal': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 4,
        'padding': '4px 12px',
        'min_height': 32,
        'arrow_size': 12,
        'arrow_margin': 8,
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
            'normal': D['border']['subtle'],
            'hover': D['border']['subtle'],
            'pressed': C['primary']['main'],
            'disabled': D['border']['subtle'],
        },
        'arrow': {
            'normal': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 4,
        'padding': '8px 12px',
    },
    
    'primary': {
        'background': {
            'normal': C['primary']['main'],
            'hover': C['primary']['hover'],
            'pressed': C['primary']['active'],
            'disabled': D['button']['background_disabled'],
        },
        'text': {
            'normal': '#FFFFFF',
            'disabled': D['text']['disabled'],
        },
        'border_radius': 4,
        'padding': '8px 16px',
    },
    
    'link': {
        'normal': C['primary']['light'],
        'hover': C['primary']['main'],
    },
    
    'input': {
        'background': {
            'normal': D['input']['background'],
            'disabled': D['input']['background_disabled'],
            'readonly': '#1C1C1C',
            'error': '#3A1F1F',
        },
        'text': {
            'normal': D['text']['primary'],
            'placeholder': D['text']['placeholder'],
            'disabled': D['text']['disabled'],
        },
        'border': {
            'normal': D['border']['subtle'],
            'focus': C['primary']['main'],
            'error': C['error']['main'],
            'disabled': 'transparent',
        },
        'border_radius': 4,
        'padding': '3px 8px',
        'selection': {
            'background': C['primary']['main'],
            'text': '#FFFFFF',
        },
    },
    
    'textedit': {
        'background': D['input']['background'],
        'background_readonly': '#1C1C1C',
        'current_line': {
            'background': QColor(40, 55, 40),
        },
        'line_number': {
            'color': D['text']['tertiary'],
            'background': '#1C1C1C',
            'current': D['text']['secondary'],
        },
        'toolbar': {
            'background': D['background']['secondary'],
            'border': D['border']['default'],
            'text': D['text']['primary'],
            'hover': D['button']['background_hover'],
            'pressed': D['button']['background_pressed'],
            'checked': QColor(0, 120, 212, 40),
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
            'disabled': D['text']['disabled'],
        },
        'checkmark': D['checkbox']['checkmark'],
        'checkmark_disabled': D['text']['disabled'],
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 4,
        'size': 20,
    },
    
    'radiobutton': {
        'background': {
            'normal': 'transparent',
            'hover': 'transparent',
            'disabled': 'transparent',
        },
        'border': {
            'normal': D['border']['default'],
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': D['text']['disabled'],
        },
        'indicator': C['primary']['main'],
        'indicator_disabled': D['text']['disabled'],
        'text': {
            'normal': D['text']['primary'],
            'disabled': D['text']['disabled'],
        },
        'border_radius': 10,
        'size': 20,
    },
    
    'switch': {
        'track': {
            'off': D['text']['disabled'],
            'on': C['primary']['main'],
            'disabled': D['text']['disabled'],
        },
        'handle': '#FFFFFF',
        'handle_disabled': D['text']['tertiary'],
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
            'selected': '#FFFFFF',
            'hover': D['text']['secondary'],
            'disabled': D['text']['disabled'],
        },
        'selection': C['primary']['main'],
        'border_radius': 4,
    },
    
    'slider': {
        'groove': {
            'background': D['slider']['groove'],
            'disabled': D['background']['tertiary'],
            'height': 4,
        },
        'progress': D['slider']['progress'],
        'handle': {
            'background': D['slider']['handle'],
            'hover': D['slider']['handle_hover'],
            'pressed': C['primary']['light'],
            'disabled': D['slider']['handle_disabled'],
            'size': 20,
            'border_radius': 10,
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
        'background_hover': D['groupbox']['background_hover'],
        'border': D['groupbox']['border'],
        'title': {
            'color': D['text']['primary'],
            'font_size': F['size']['body'],
            'font_weight': 'semibold',
        },
        'border_radius': S['card']['border_radius'],
        'border_width': S['card']['border_width'],
        'margin_top': S['spacing']['xlarge'],
        'padding': S['card']['padding'],
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
        'width': 8,
        'border_radius': 4,
        'margin': 0,
    },
    
    'toast': {
        'info': {
            'background': '#1A3A4A',
            'border': C['info']['main'],
            'text': D['text']['primary'],
            'icon': C['info']['light'],
        },
        'success': {
            'background': '#1A3A2A',
            'border': C['success']['main'],
            'text': D['text']['primary'],
            'icon': C['success']['light'],
        },
        'warning': {
            'background': '#3A3A1A',
            'border': C['warning']['main'],
            'text': D['text']['primary'],
            'icon': C['warning']['main'],
        },
        'error': {
            'background': '#3A1A1A',
            'border': C['error']['main'],
            'text': D['text']['primary'],
            'icon': C['error']['light'],
        },
        'border_radius': 4,
        'shadow_blur': 0,
    },
    
    'tooltip': {
        'background': D['background']['elevated'],
        'text': D['text']['primary'],
        'border': D['border']['default'],
    },
    
    'menu': {
        'background': D['background']['secondary'],
        'border': 'transparent',
        'shadow': QColor(0, 0, 0, 60),
        'border_radius': 8,
        'item': {
            'text': D['text']['primary'],
            'text_disabled': D['text']['disabled'],
            'hover': D['button']['background_hover'],
            'shortcut': D['text']['secondary'],
            'check': C['primary']['main'],
        },
        'separator': D['border']['subtle'],
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
        'close_icon': D['text']['tertiary'],
        'close_icon_hover': D['text']['primary'],
        'close_hover': D['button']['background_hover'],
        'close_pressed': D['button']['background_pressed'],
        'scroll_icon': D['text']['secondary'],
    },
    
    'mediabar': {
        'background': D['background']['tertiary'],
        'groove': D['slider']['groove'],
        'filled': C['primary']['main'],
        'handle': '#FFFFFF',
        'text': D['text']['secondary'],
    },
    
    'icon': {
        'normal': D['text']['primary'],
        'disabled': D['text']['disabled'],
        'hover': C['primary']['light'],
        'pressed': C['primary']['main'],
    },
    
    'card': {
        'background': D['background']['elevated'],
        'border': D['border']['card'],
        'shadow': 'transparent',
    },
    
    'statusbar': {
        'background': D['background']['secondary'],
        'border': D['border']['default'],
        'text': D['text']['primary'],
        'icon': D['text']['secondary'],
        'badge': C['error']['main'],
        'warning': C['warning']['main'],
        'success': C['success']['main'],
        'error': C['error']['main'],
    },
    
    'font': F,
}
