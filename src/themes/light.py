"""
WinUI3 亮色主题定义

遵循 WinUI3 设计规范，使用 Fluent Design System。
"""

from PyQt6.QtGui import QColor
from .colors import COLORS, WINUI3_LIGHT_COLORS, FONT_CONFIG, WINDOW_CONFIG, WINUI3_CONTROL_SIZING

C = COLORS
L = WINUI3_LIGHT_COLORS
F = FONT_CONFIG
W = WINDOW_CONFIG
S = WINUI3_CONTROL_SIZING

LIGHT_THEME = {
    'name': 'light',
    'is_dark': False,
    
    'window': {
        'background': L['background']['mica'],
        'border': L['border']['surface'],
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
            'caption': L['text']['secondary'],
            'body': L['text']['primary'],
            'body_strong': L['text']['primary'],
            'body_large': L['text']['primary'],
            'subtitle': L['text']['primary'],
            'title': L['text']['primary'],
            'title_large': L['text']['primary'],
            'display': L['text']['primary'],
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
            'checked': C['primary']['main'],
            'checked_hover': C['primary']['hover'],
            'checked_pressed': C['primary']['active'],
        },
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
            'checked': '#FFFFFF',
        },
        'icon': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
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
            'normal': L['button']['background'],
            'hover': L['button']['background_hover'],
            'disabled': L['button']['background_disabled'],
            'checked': C['primary']['main'],
            'checked_hover': C['primary']['hover'],
        },
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
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
            'normal': L['button']['background'],
            'hover': L['button']['background_hover'],
            'pressed': L['button']['background_pressed'],
            'disabled': L['button']['background_disabled'],
        },
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border': {
            'normal': 'transparent',
            'hover': 'transparent',
            'pressed': 'transparent',
            'disabled': 'transparent',
        },
        'arrow': {
            'normal': L['text']['secondary'],
            'disabled': L['text']['disabled'],
        },
        'border_radius': S['dropdown']['border_radius'],
        'padding': f"{S['dropdown']['padding_v']}px {S['dropdown']['padding_h']}px",
        'min_height': S['dropdown']['min_height'],
        'arrow_size': S['dropdown']['arrow_size'],
        'arrow_margin': S['dropdown']['arrow_margin'],
    },
    
    'combobox': {
        'background': {
            'normal': QColor(0, 0, 0, 6),
            'hover': QColor(0, 0, 0, 11),
            'pressed': QColor(0, 0, 0, 4),
            'disabled': QColor(0, 0, 0, 3),
            'focused': QColor(0, 0, 0, 6),
        },
        'text': {
            'normal': L['text']['primary'],
            'placeholder': QColor(0, 0, 0, 133),
            'disabled': L['text']['disabled'],
        },
        'border': {
            'normal': QColor(0, 0, 0, 0),
            'hover': QColor(0, 0, 0, 0),
            'pressed': QColor(0, 0, 0, 0),
            'disabled': QColor(0, 0, 0, 0),
            'focused': QColor(0, 0, 0, 0),
        },
        'arrow': {
            'normal': QColor(0, 0, 0, 153),
            'hover': QColor(0, 0, 0, 204),
            'disabled': QColor(0, 0, 0, 92),
        },
        'border_radius': S['dropdown']['border_radius'],
        'padding': f"{S['dropdown']['padding_v']}px {S['dropdown']['padding_h']}px",
        'min_height': S['dropdown']['min_height'],
    },
    
    'primary': {
        'background': {
            'normal': C['primary']['main'],
            'hover': C['primary']['hover'],
            'pressed': C['primary']['active'],
            'disabled': L['button']['background_disabled'],
        },
        'text': {
            'normal': '#FFFFFF',
            'disabled': L['text']['disabled'],
        },
        'border_radius': 4,
        'padding': '8px 16px',
    },
    
    'link': {
        'normal': C['primary']['main'],
        'hover': C['primary']['dark'],
    },
    
    'input': {
        'background': {
            'normal': L['input']['background'],
            'disabled': L['input']['background_disabled'],
            'readonly': '#FAFAFA',
            'error': '#FFF5F5',
        },
        'text': {
            'normal': L['text']['primary'],
            'placeholder': L['text']['placeholder'],
            'disabled': L['text']['disabled'],
        },
        'border': {
            'normal': L['border']['subtle'],
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
        'background': L['input']['background'],
        'background_readonly': '#FAFAFA',
        'current_line': {
            'background': QColor(230, 255, 230),
        },
        'line_number': {
            'color': L['text']['tertiary'],
            'background': '#FAFAFA',
            'current': L['text']['secondary'],
        },
        'toolbar': {
            'background': L['background']['secondary'],
            'border': L['border']['default'],
            'text': L['text']['primary'],
            'hover': L['button']['background_hover'],
            'pressed': L['button']['background_pressed'],
            'checked': QColor(0, 120, 212, 30),
        },
        'padding': 8,
    },
    
    'checkbox': {
        'background': {
            'normal': QColor(0, 0, 0, 0),
            'hover': QColor(0, 0, 0, 0),
            'pressed': QColor(0, 0, 0, 12),
            'checked': C['primary']['main'],
            'disabled': QColor(0, 0, 0, 0),
        },
        'border': {
            'normal': QColor(0, 0, 0, 35),
            'hover': QColor(0, 0, 0, 35),
            'pressed': QColor(0, 0, 0, 60),
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': QColor(0, 0, 0, 25),
        },
        'checkmark': QColor(255, 255, 255),
        'checkmark_disabled': L['text']['disabled'],
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border_radius': S['checkbox']['border_radius'],
        'size': S['checkbox']['size'],
        'checkmark_size': S['checkbox']['checkmark_size'],
    },
    
    'radiobutton': {
        'background': {
            'normal': 'transparent',
            'hover': 'transparent',
            'disabled': 'transparent',
        },
        'border': {
            'normal': L['border']['default'],
            'focus': C['primary']['main'],
            'checked': C['primary']['main'],
            'disabled': L['text']['disabled'],
        },
        'indicator': C['primary']['main'],
        'indicator_disabled': L['text']['disabled'],
        'text': {
            'normal': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
        'border_radius': 10,
        'size': 20,
    },
    
    'switch': {
        'track': {
            'off': L['text']['disabled'],
            'on': C['primary']['main'],
            'disabled': L['text']['disabled'],
        },
        'handle': '#FFFFFF',
        'handle_disabled': L['text']['tertiary'],
    },
    
    'datepicker': {
        'background': L['input']['background'],
        'background_disabled': L['input']['background_disabled'],
        'border': L['input']['border'],
        'border_focus': L['input']['border_focus'],
        'text': L['text']['primary'],
        'text_disabled': L['text']['disabled'],
        'border_radius': 4,
    },
    
    'timepicker': {
        'background': L['input']['background'],
        'background_disabled': L['input']['background_disabled'],
        'border': L['input']['border'],
        'border_focus': L['input']['border_focus'],
        'text': L['text']['primary'],
        'text_disabled': L['text']['disabled'],
        'border_radius': 4,
        'icon': {
            'normal': L['text']['secondary'],
            'hover': L['text']['primary'],
        },
    },
    
    'timewheel': {
        'selection': {
            'background': L['background']['tertiary'],
        },
        'text': {
            'normal': L['text']['secondary'],
            'selected': L['text']['primary'],
            'disabled': L['text']['disabled'],
        },
    },
    
    'calendar': {
        'background': L['background']['secondary'],
        'border': L['border']['default'],
        'header': {
            'background': L['background']['tertiary'],
            'text': L['text']['primary'],
        },
        'item': {
            'normal': L['text']['primary'],
            'selected': '#FFFFFF',
            'hover': L['text']['secondary'],
            'disabled': L['text']['disabled'],
        },
        'selection': C['primary']['main'],
        'border_radius': S['tab']['min_height'] // 2,
        'min_height': S['tab']['min_height'],
        'min_width': S['tab']['min_width'],
        'padding_h': S['tab']['padding_h'],
        'padding_v': S['tab']['padding_v'],
    },
    
    'slider': {
        'groove': {
            'background': L['slider']['groove'],
            'disabled': L['background']['tertiary'],
            'height': S['slider']['groove_height'],
        },
        'progress': L['slider']['progress'],
        'handle': {
            'background': L['slider']['handle'],
            'hover': L['slider']['handle_hover'],
            'pressed': C['primary']['dark'],
            'disabled': L['slider']['handle_disabled'],
            'size': S['slider']['handle_size'],
            'border_radius': S['slider']['handle_radius'],
        },
        'border_radius': 2,
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
        'background_hover': L['groupbox']['background_hover'],
        'border': L['groupbox']['border'],
        'title': {
            'color': L['text']['primary'],
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
        'background': L['scrollbar']['background'],
        'handle': {
            'normal': L['scrollbar']['handle'],
            'hover': L['scrollbar']['handle_hover'],
        },
        'width': 8,
        'border_radius': 4,
        'margin': 0,
    },
    
    'toast': {
        'info': {
            'background': '#E8F4FC',
            'border': C['info']['main'],
            'text': L['text']['primary'],
            'icon': C['info']['main'],
        },
        'success': {
            'background': '#E8FCE8',
            'border': C['success']['main'],
            'text': L['text']['primary'],
            'icon': C['success']['main'],
        },
        'warning': {
            'background': '#FCFCE8',
            'border': C['warning']['main'],
            'text': L['text']['primary'],
            'icon': C['warning']['main'],
        },
        'error': {
            'background': '#FCE8E8',
            'border': C['error']['main'],
            'text': L['text']['primary'],
            'icon': C['error']['main'],
        },
        'border_radius': 4,
        'shadow_blur': 0,
    },
    
    'tooltip': {
        'background': L['background']['elevated'],
        'text': L['text']['primary'],
        'border': L['border']['default'],
    },
    
    'menu': {
        'background': L['background']['secondary'],
        'border': 'transparent',
        'shadow': QColor(0, 0, 0, 30),
        'border_radius': 8,
        'item': {
            'text': L['text']['primary'],
            'text_disabled': L['text']['disabled'],
            'hover': L['button']['background_hover'],
            'shortcut': L['text']['secondary'],
            'check': C['primary']['main'],
        },
        'separator': L['border']['subtle'],
    },
    
    'pivot': {
        'background': 'transparent',
        'item': {
            'text': L['text']['secondary'],
            'text_selected': L['text']['primary'],
            'hover': L['button']['background_hover'],
        },
        'underline': C['primary']['main'],
    },
    
    'tabbar': {
        'background': L['background']['secondary'],
        'item': {
            'text': L['text']['secondary'],
            'text_selected': L['text']['primary'],
            'background_selected': L['background']['primary'],
            'hover': L['button']['background_hover'],
        },
        'indicator': C['primary']['main'],
        'close_icon': L['text']['tertiary'],
        'close_icon_hover': L['text']['primary'],
        'close_hover': L['button']['background_hover'],
        'close_pressed': L['button']['background_pressed'],
        'scroll_icon': L['text']['secondary'],
    },
    
    'mediabar': {
        'background': L['background']['tertiary'],
        'groove': L['slider']['groove'],
        'filled': C['primary']['main'],
        'handle': '#FFFFFF',
        'text': L['text']['secondary'],
    },
    
    'icon': {
        'normal': L['text']['primary'],
        'disabled': L['text']['disabled'],
        'hover': C['primary']['dark'],
        'pressed': C['primary']['main'],
    },
    
    'card': {
        'background': L['background']['elevated'],
        'border': L['border']['card'],
        'shadow': 'transparent',
    },
    
    'statusbar': {
        'background': L['background']['secondary'],
        'border': L['border']['default'],
        'text': L['text']['primary'],
        'icon': L['text']['secondary'],
        'badge': C['error']['main'],
        'warning': C['warning']['main'],
        'success': C['success']['main'],
        'error': C['error']['main'],
    },
    
    'font': F,
}
