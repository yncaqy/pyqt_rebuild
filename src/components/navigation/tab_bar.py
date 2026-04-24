"""
TabView 组件 - 向后兼容导入

此文件保留用于向后兼容，所有实现已移至 components.tabview 包。

新代码请使用:
    from components.tabview import TabView, TabViewItem, TabItem
"""

from src.components.tabview import (
    TabView,
    TabViewItem,
    TabViewItemCloseButton,
    TabViewTabStrip,
    TabViewAddButton,
    TabViewScrollButton,
    TabViewConfig,
    TabViewColors,
    TabViewVisualStates,
    TabViewWidthMode,
    TabViewCloseButtonOverlayMode,
    TabViewStyle,
    TabItem,
    TabBar,
    TabWidget,
)

__all__ = [
    'TabView',
    'TabViewItem',
    'TabViewItemCloseButton',
    'TabViewTabStrip',
    'TabViewAddButton',
    'TabViewScrollButton',
    'TabViewConfig',
    'TabViewColors',
    'TabViewVisualStates',
    'TabViewWidthMode',
    'TabViewCloseButtonOverlayMode',
    'TabViewStyle',
    'TabItem',
    'TabBar',
    'TabWidget',
]
