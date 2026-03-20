"""
PyQt6 组件库

提供完整的主题化 UI 组件，遵循 Microsoft WinUI 3 / Fluent Design 设计规范。

组件分类:
- buttons: 按钮组件
- inputs: 输入组件
- containers: 容器组件
- navigation: 导航组件
- widgets: 通用组件
- dialogs: 对话框
- lists: 列表组件
- trees: 树组件
- tables: 表格组件
- menus: 菜单组件
- labels: 标签组件
- checkboxes: 复选框组件
- sliders: 滑块组件
- progress: 进度组件
- toasts: Toast 通知
- media: 媒体组件
- splash: 启动画面
- statusbar: 状态栏
- layouts: 布局组件
"""

from .buttons import (
    CustomPushButton,
    ToolButton,
    PrimaryPushButton,
    HyperlinkButton,
    TogglePushButton,
    PillPushButton,
    DropDownPushButton,
    RadioButton,
    SwitchButton,
)

from .inputs import (
    ModernLineEdit,
    PlainTextEdit,
    TextEditConfig,
    LineNumberArea,
    TextEdit,
    TextFormatState,
    TextEditWithToolbar,
    FormatToolbar,
)

from .containers import (
    ThemedWidget,
    ThemedGroupBox,
    ThemedScrollArea,
    CustomScrollBar,
    ElevatedCardWidget,
    Splitter,
    AnimatedSplitter,
    SplitterHandle,
    SplitterPanel,
)

from .navigation import (
    Pivot,
    PivotItem,
    TabBar,
    TabItem,
    TabWidget,
    BreadcrumbBar,
    BreadcrumbItem,
    BreadcrumbSeparator,
)

from .widgets import (
    IconWidget,
    IconSize,
    IconSource,
    IconCard,
    ComboBox,
    ComboBoxConfig,
    EditableComboBox,
    EditableComboBoxConfig,
    DatePicker,
    DatePickerConfig,
    DropDownColorPalette,
    ColorPaletteConfig,
    DropDownColorPicker,
    ColorPickerConfig,
    ScreenColorPicker,
    ScreenColorPickerButton,
    ScreenColorPickerConfig,
    ColorPickerOverlay,
    ColorHistoryWidget,
    NotificationBadge,
    BadgeConfig,
)

from .dialogs import (
    MessageBox,
    MessageBoxBase,
    ColorDialog,
)

from .lists import (
    CustomListWidget,
    CustomListWidgetItem,
    CustomListView,
    ListSelectionIndicator,
)

from .trees import (
    CustomTreeWidget,
    CustomTreeWidgetItem,
)

from .tables import (
    CustomTableWidget,
    CustomTableWidgetItem,
)

from .menus import (
    RoundMenu,
    MenuActionItem,
    MenuSeparator,
)

from .labels import (
    ThemedLabel,
    ImageLabel,
)

from .checkboxes import (
    CustomCheckBox,
)

from .sliders import (
    AnimatedSlider,
)

from .progress import (
    CircularProgress,
)

from .toasts import (
    Toast,
    ToastPosition,
    ToastType,
    ToastManager,
)

from .media import (
    SimpleMediaPlayBar,
)

from .splash import (
    SplashScreen,
)

from .statusbar import (
    StatusBar,
    StatusItem,
    TimeStatusItem,
    BatteryStatusItem,
    NetworkStatusItem,
    NotificationStatusItem,
    StatusBarConfig,
)

from .layouts import (
    FlowLayout,
)

__all__ = [
    'CustomPushButton',
    'ToolButton',
    'PrimaryPushButton',
    'HyperlinkButton',
    'TogglePushButton',
    'PillPushButton',
    'DropDownPushButton',
    'RadioButton',
    'SwitchButton',
    
    'ModernLineEdit',
    'PlainTextEdit',
    'TextEditConfig',
    'LineNumberArea',
    'TextEdit',
    'TextFormatState',
    'TextEditWithToolbar',
    'FormatToolbar',
    
    'ThemedWidget',
    'ThemedGroupBox',
    'ThemedScrollArea',
    'CustomScrollBar',
    'ElevatedCardWidget',
    'Splitter',
    'AnimatedSplitter',
    'SplitterHandle',
    'SplitterPanel',
    
    'Pivot',
    'PivotItem',
    'TabBar',
    'TabItem',
    'TabWidget',
    'BreadcrumbBar',
    'BreadcrumbItem',
    'BreadcrumbSeparator',
    
    'IconWidget',
    'IconSize',
    'IconSource',
    'IconCard',
    'ComboBox',
    'ComboBoxConfig',
    'EditableComboBox',
    'EditableComboBoxConfig',
    'DatePicker',
    'DatePickerConfig',
    'DropDownColorPalette',
    'ColorPaletteConfig',
    'DropDownColorPicker',
    'ColorPickerConfig',
    'ScreenColorPicker',
    'ScreenColorPickerButton',
    'ScreenColorPickerConfig',
    'ColorPickerOverlay',
    'ColorHistoryWidget',
    'NotificationBadge',
    'BadgeConfig',
    
    'MessageBox',
    'MessageBoxBase',
    'ColorDialog',
    
    'CustomListWidget',
    'CustomListWidgetItem',
    'CustomListView',
    'ListSelectionIndicator',
    
    'CustomTreeWidget',
    'CustomTreeWidgetItem',
    
    'CustomTableWidget',
    'CustomTableWidgetItem',
    
    'RoundMenu',
    'MenuActionItem',
    'MenuSeparator',
    
    'ThemedLabel',
    'ImageLabel',
    
    'CustomCheckBox',
    
    'AnimatedSlider',
    
    'CircularProgress',
    
    'Toast',
    'ToastPosition',
    'ToastType',
    'ToastManager',
    
    'SimpleMediaPlayBar',
    
    'SplashScreen',
    
    'StatusBar',
    'StatusItem',
    'TimeStatusItem',
    'BatteryStatusItem',
    'NetworkStatusItem',
    'NotificationStatusItem',
    'StatusBarConfig',
    
    'FlowLayout',
]
