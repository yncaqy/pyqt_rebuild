"""
颜色变量定义

定义所有主题共享的颜色变量，确保颜色一致性。
所有颜色使用十六进制格式定义，便于跨主题复用。

WinUI 3 设计规范:
- 使用带透明度的颜色值降低对比度
- Light Theme: 文字使用 #E4000000 (89%黑) 而非纯黑
- Dark Theme: 文字使用 #FFFFFFFF (白) 和带透明度的白色
- 边框使用低透明度颜色 (6-9%)

使用方式:
    from themes.colors import COLORS, DARK_COLORS, LIGHT_COLORS
"""

COLORS = {
    'primary': {
        'main': '#0078D4',
        'light': '#60CDFF',
        'dark': '#005A9E',
        'hover': '#006CBD',
        'active': '#004578',
    },
    'success': {
        'main': '#0F7B0F',
        'light': '#6CCB6F',
        'dark': '#0B5C0B',
    },
    'warning': {
        'main': '#FFD639',
        'light': '#FFF4CE',
        'dark': '#C19C00',
    },
    'error': {
        'main': '#C42B1C',
        'light': '#F27B72',
        'dark': '#8A1A1A',
    },
    'info': {
        'main': '#0078D4',
        'light': '#60CDFF',
        'dark': '#005A9E',
    },
}

WINUI3_DARK_COLORS = {
    'background': {
        'primary': '#202020',
        'secondary': '#1C1C1C',
        'tertiary': '#282828',
        'elevated': '#2D2D2D',
        'mica': '#1C1C1C',
    },
    'text': {
        'primary': '#FFFFFF',
        'secondary': '#C5FFFFFF',
        'tertiary': '#87FFFFFF',
        'disabled': '#5CFFFFFF',
        'placeholder': '#87FFFFFF',
    },
    'border': {
        'default': '#15FFFFFF',
        'light': '#18FFFFFF',
        'card': '#15FFFFFF',
        'surface': '#0F000000',
        'subtle': '#0AFFFFFF',
    },
    'input': {
        'background': '#1C1C1C',
        'background_disabled': '#1C1C1C',
        'border': '#15FFFFFF',
        'border_focus': '#0078D4',
    },
    'slider': {
        'groove': '#292929',
        'progress': '#0078D4',
        'handle': '#FFFFFF',
        'handle_hover': '#F0F0F0',
        'handle_disabled': '#666666',
    },
    'checkbox': {
        'background': 'transparent',
        'background_hover': 'transparent',
        'border': '#87FFFFFF',
        'checkmark': '#FFFFFF',
    },
    'button': {
        'background': '#2D2D2D',
        'background_hover': '#3D3D3D',
        'background_pressed': '#1D1D1D',
        'background_disabled': '#1C1C1C',
    },
    'groupbox': {
        'background': '#1C1C1C',
        'background_hover': '#252525',
        'border': '#15FFFFFF',
    },
    'scrollbar': {
        'background': 'transparent',
        'handle': '#56FFFFFF',
        'handle_hover': '#76FFFFFF',
    },
    'titlebar': {
        'background': '#202020',
        'button_hover': '#18FFFFFF',
        'close_hover': '#C42B1C',
    },
    'acrylic': {
        'background': '#2C2C2C',
        'tint': '#2C2C2C',
        'fallback': '#2C2C2C',
    },
}

WINUI3_LIGHT_COLORS = {
    'background': {
        'primary': '#F3F3F3',
        'secondary': '#EEEEEE',
        'tertiary': '#F9F9F9',
        'elevated': '#FFFFFF',
        'mica': '#F3F3F3',
    },
    'text': {
        'primary': '#E4000000',
        'secondary': '#9E000000',
        'tertiary': '#72000000',
        'disabled': '#5C000000',
        'placeholder': '#72000000',
    },
    'border': {
        'default': '#0A000000',
        'light': '#0D000000',
        'card': '#0A000000',
        'surface': '#0D000000',
        'subtle': '#06000000',
    },
    'input': {
        'background': '#FFFFFF',
        'background_disabled': '#F3F3F3',
        'border': '#0A000000',
        'border_focus': '#0078D4',
    },
    'slider': {
        'groove': '#CACACA',
        'progress': '#0078D4',
        'handle': '#0078D4',
        'handle_hover': '#106EBE',
        'handle_disabled': '#CACACA',
    },
    'checkbox': {
        'background': '#FFFFFF',
        'border': '#72000000',
        'checkmark': '#FFFFFF',
    },
    'button': {
        'background': '#F3F3F3',
        'background_hover': '#E9E9E9',
        'background_pressed': '#F9F9F9',
        'background_disabled': '#F3F3F3',
    },
    'groupbox': {
        'background': '#FFFFFF',
        'background_hover': '#F5F5F5',
        'border': '#0A000000',
    },
    'scrollbar': {
        'background': 'transparent',
        'handle': '#5C000000',
        'handle_hover': '#76000000',
    },
    'titlebar': {
        'background': '#F3F3F3',
        'button_hover': '#0A000000',
        'close_hover': '#C42B1C',
    },
    'acrylic': {
        'background': '#F9F9F9',
        'tint': '#F9F9F9',
        'fallback': '#F9F9F9',
    },
}

DARK_COLORS = WINUI3_DARK_COLORS

LIGHT_COLORS = WINUI3_LIGHT_COLORS

FONT_CONFIG = {
    'family': 'Segoe UI',
    'fallback': 'Microsoft YaHei UI',
    'size': {
        'caption': 12,
        'body': 14,
        'body_strong': 14,
        'body_large': 18,
        'subtitle': 20,
        'title': 28,
        'title_large': 40,
        'display': 68,
    },
    'weight': {
        'caption': 'normal',
        'body': 'normal',
        'body_strong': 'semibold',
        'body_large': 'normal',
        'subtitle': 'semibold',
        'title': 'semibold',
        'title_large': 'semibold',
        'display': 'semibold',
    },
    'line_height': {
        'caption': 16,
        'body': 20,
        'body_strong': 20,
        'body_large': 24,
        'subtitle': 28,
        'title': 36,
        'title_large': 52,
        'display': 92,
    }
}

WINUI3_CONTROL_SIZING = {
    'button': {
        'min_height': 24,
        'min_width': 0,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 4,
        'icon_size': 14,
    },
    'dropdown': {
        'min_height': 24,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 4,
        'arrow_size': 10,
        'arrow_margin': 6,
        'icon_size': 14,
    },
    'input': {
        'min_height': 32,
        'padding_h': 10,
        'padding_v': 5,
        'border_radius': 4,
        'border_width': 1,
    },
    'checkbox': {
        'size': 20,
        'border_radius': 4,
        'checkmark_size': 12,
    },
    'radiobutton': {
        'size': 20,
        'border_radius': 10,
        'indicator_size': 10,
    },
    'slider': {
        'groove_height': 4,
        'handle_size': 20,
        'handle_radius': 10,
    },
    'switch': {
        'width': 40,
        'height': 20,
        'handle_size': 12,
    },
    'tab': {
        'min_height': 40,
        'min_width': 80,
        'padding_h': 12,
        'padding_v': 8,
    },
    'menu': {
        'item_height': 28,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 4,
        'icon_size': 14,
    },
    'list': {
        'item_height': 40,
        'padding_h': 12,
        'padding_v': 8,
    },
    'card': {
        'padding': 16,
        'border_radius': 8,
        'border_width': 1,
    },
    'spacing': {
        'xsmall': 4,
        'small': 8,
        'medium': 12,
        'large': 16,
        'xlarge': 24,
        'xxlarge': 32,
    },
    'icon': {
        'small': 12,
        'medium': 16,
        'large': 20,
        'xlarge': 24,
        'xxlarge': 32,
        'xxxlarge': 48,
    },
}

WINDOW_CONFIG = {
    'border_radius': 8,
    'titlebar_height': 32,
}

FALLBACK_COLORS = {
    'text': {
        'primary': '#FFFFFF',
        'secondary': '#C5FFFFFF',
        'tertiary': '#87FFFFFF',
        'disabled': '#5CFFFFFF',
    },
    'background': {
        'normal': '#2D2D2D',
        'hover': '#3D3D3D',
        'pressed': '#1D1D1D',
        'disabled': '#1C1C1C',
        'elevated': '#454545',
    },
    'border': {
        'default': '#15FFFFFF',
        'subtle': '#0AFFFFFF',
        'focus': '#0078D4',
    },
    'accent': {
        'primary': '#0078D4',
        'success': '#0F7B0F',
        'warning': '#FFD639',
        'error': '#C42B1C',
    },
    'state': {
        'hover_overlay': '#18FFFFFF',
        'pressed_overlay': '#10FFFFFF',
        'selection': '#0078D4',
    },
}

FALLBACK_COLORS_LIGHT = {
    'text': {
        'primary': '#E4000000',
        'secondary': '#9E000000',
        'tertiary': '#72000000',
        'disabled': '#5C000000',
    },
    'background': {
        'normal': '#F3F3F3',
        'hover': '#E9E9E9',
        'pressed': '#F9F9F9',
        'disabled': '#F3F3F3',
        'elevated': '#FFFFFF',
    },
    'border': {
        'default': '#0A000000',
        'subtle': '#06000000',
        'focus': '#0078D4',
    },
    'accent': {
        'primary': '#0078D4',
        'success': '#0F7B0F',
        'warning': '#FFD639',
        'error': '#C42B1C',
    },
    'state': {
        'hover_overlay': '#0A000000',
        'pressed_overlay': '#06000000',
        'selection': '#0078D4',
    },
}

def get_fallback_color(path: str, is_dark: bool = True) -> str:
    """
    获取回退颜色值。
    
    Args:
        path: 颜色路径，使用点号分隔（如 'text.primary'）
        is_dark: 是否为暗色主题
        
    Returns:
        颜色字符串值
    """
    colors = FALLBACK_COLORS if is_dark else FALLBACK_COLORS_LIGHT
    parts = path.split('.')
    value = colors
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
            if value is None:
                return '#808080'
        else:
            return '#808080'
    return value if isinstance(value, str) else '#808080'
