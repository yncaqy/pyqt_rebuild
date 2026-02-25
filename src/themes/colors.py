"""
颜色变量定义

定义所有主题共享的颜色变量，确保颜色一致性。
所有颜色使用十六进制格式定义，便于跨主题复用。

使用方式:
    from themes.colors import COLORS, DARK_COLORS, LIGHT_COLORS
"""

COLORS = {
    'primary': {
        'main': '#5dade2',
        'light': '#7fb3d5',
        'dark': '#3498db',
        'hover': '#3498db',
        'active': '#2980b9',
    },
    'success': {
        'main': '#27ae60',
        'light': '#58d68d',
        'dark': '#1e8449',
    },
    'warning': {
        'main': '#f39c12',
        'light': '#f4d03f',
        'dark': '#b7950b',
    },
    'error': {
        'main': '#e74c3c',
        'light': '#ec7063',
        'dark': '#c0392b',
    },
    'info': {
        'main': '#3498db',
        'light': '#5dade2',
        'dark': '#2980b9',
    },
}

DARK_COLORS = {
    'background': {
        'primary': '#1e1e1e',
        'secondary': '#2a2a2a',
        'tertiary': '#333333',
        'elevated': '#3a3a3a',
    },
    'text': {
        'primary': '#e0e0e0',
        'secondary': '#999999',
        'disabled': '#666666',
        'placeholder': '#777777',
    },
    'border': {
        'default': '#333333',
        'light': '#444444',
        'medium': '#555555',
        'dark': '#666666',
    },
    'input': {
        'background': '#2a2a2a',
        'background_disabled': '#252525',
        'border': '#444444',
        'border_focus': '#5dade2',
    },
    'slider': {
        'groove': '#3a3a3a',
        'handle': '#5dade2',
        'handle_hover': '#3498db',
        'handle_disabled': '#555555',
    },
    'checkbox': {
        'background': 'transparent',
        'background_hover': 'transparent',
        'border': '#555555',
        'checkmark': '#5dade2',
    },
    'button': {
        'background': '#3a3a3a',
        'background_hover': '#4a4a4a',
        'background_pressed': '#5a5a5a',
        'background_disabled': '#2a2a2a',
    },
    'groupbox': {
        'background': '#252525',
        'border': '#444444',
    },
    'scrollbar': {
        'background': '#2a2a2a',
        'handle': '#4a4a4a',
        'handle_hover': '#5a5a5a',
    },
    'titlebar': {
        'background': '#2d2d2d',
        'button_hover': 'rgba(255, 255, 255, 0.1)',
        'close_hover': '#e74c3c',
    },
}

LIGHT_COLORS = {
    'background': {
        'primary': '#ffffff',
        'secondary': '#f5f5f5',
        'tertiary': '#e0e0e0',
        'elevated': '#ffffff',
    },
    'text': {
        'primary': '#333333',
        'secondary': '#666666',
        'disabled': '#999999',
        'placeholder': '#999999',
    },
    'border': {
        'default': '#dddddd',
        'light': '#e0e0e0',
        'medium': '#cccccc',
        'dark': '#bbbbbb',
    },
    'input': {
        'background': '#ffffff',
        'background_disabled': '#fafafa',
        'border': '#dddddd',
        'border_focus': '#3498db',
    },
    'slider': {
        'groove': '#e8e8e8',
        'handle': '#3498db',
        'handle_hover': '#2980b9',
        'handle_disabled': '#cccccc',
    },
    'checkbox': {
        'background': '#ffffff',
        'border': '#cccccc',
        'checkmark': '#3498db',
    },
    'button': {
        'background': '#e8e8e8',
        'background_hover': '#d8d8d8',
        'background_pressed': '#c8c8c8',
        'background_disabled': '#f5f5f5',
    },
    'groupbox': {
        'background': '#fafafa',
        'border': '#dddddd',
    },
    'scrollbar': {
        'background': '#f5f5f5',
        'handle': '#d0d0d0',
        'handle_hover': '#c0c0c0',
    },
    'titlebar': {
        'background': '#f5f5f5',
        'button_hover': 'rgba(0, 0, 0, 0.05)',
        'close_hover': '#e74c3c',
    },
}

FONT_CONFIG = {
    'family': 'Segoe UI',
    'size': {
        'title': 16,
        'header': 14,
        'body': 12,
        'small': 10,
    },
    'weight': {
        'title': 'bold',
        'header': 'bold',
        'body': 'normal',
        'small': 'normal',
    }
}

WINDOW_CONFIG = {
    'border_radius': 12,
    'titlebar_height': 40,
}
