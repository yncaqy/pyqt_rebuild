"""
TabView 组件包

严格遵循 WinUI3 TabView 设计规范。
参考: https://learn.microsoft.com/zh-cn/windows/apps/design/controls/tab-view

组件结构:
- TabView: 主控件，包含标签条和内容区域
- TabViewItem: 单个标签项
- TabViewTabStrip: 标签条
- TabViewItemCloseButton: 关闭按钮
- TabViewAddButton: 添加按钮
- TabViewScrollButton: 滚动按钮

使用示例:
    from components.tabview import TabView, TabViewItem
    
    # 创建 TabView
    tab_view = TabView()
    
    # 添加标签
    tab_view.addTab("首页", home_widget)
    tab_view.addTab("设置", settings_widget)
    
    # 连接信号
    tab_view.currentChanged.connect(on_tab_changed)
    tab_view.tabCloseRequested.connect(on_tab_close)
"""

from .config import (
    TabViewConfig,
    TabViewColors,
    TabViewVisualStates,
    TabViewWidthMode,
    TabViewCloseButtonOverlayMode,
)
from .styles import TabViewStyle
from .tab_view_item import TabViewItem, TabViewItemCloseButton, TabItem
from .tab_view_tab_strip import (
    TabViewTabStrip,
    TabViewAddButton,
    TabViewScrollButton,
)
from .tab_view import TabView, TabBar, TabWidget

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
