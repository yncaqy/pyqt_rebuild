# Core modules for PyQt component refactoring
from .logger_config import setup_logging, get_logger, LoggerMixin, log_function_call
from .theme_manager import ThemeManager, Theme
from .animation_controller import AnimationController, Transition, AnimationType
from .state_manager import StateManager, WidgetState
from .style_override import StyleOverrideMixin
from .stylesheet_cache_mixin import StylesheetCacheMixin
from .themed_component_base import ThemedComponentBase, ThemedObjectBase, ThemedDelegateBase

# 自动初始化日志配置（可通过环境变量 LOG_LEVEL 控制级别）
setup_logging()

__all__ = [
    'setup_logging', 'get_logger', 'LoggerMixin', 'log_function_call',
    'ThemeManager', 'Theme',
    'AnimationController', 'Transition', 'AnimationType',
    'StateManager', 'WidgetState',
    'StyleOverrideMixin', 'StylesheetCacheMixin',
    'ThemedComponentBase', 'ThemedObjectBase', 'ThemedDelegateBase',
]
