# PyQt6 组件库

一个现代化的 PyQt6 组件库，遵循 Microsoft WinUI 3 / Fluent Design 设计规范，具有完整的主题系统集成。

## 特性

- 🎨 **主题系统** - 支持暗色/亮色主题切换，自动更新所有组件
- 🧩 **组件化** - 模块化组件设计，易于扩展和定制
- ⚡ **性能优化** - 样式缓存机制，减少重复计算
- 🔧 **类型安全** - 完整的类型注解支持
- 🎯 **WinUI 3 规范** - 遵循微软 Fluent Design 设计语言

## 组件列表

### 按钮组件 (9个)
- `CustomPushButton` - 自定义按钮
- `PrimaryPushButton` - 主要按钮
- `DropDownPushButton` - 下拉按钮
- `TogglePushButton` - 切换按钮
- `PillPushButton` - 药丸按钮
- `ToolButton` - 工具按钮
- `HyperlinkButton` - 超链接按钮
- `RadioButton` - 单选按钮
- `SwitchButton` - 开关按钮

### 输入组件 (5个)
- `ModernLineEdit` - 现代化输入框
- `PlainTextEdit` - 纯文本编辑器
- `TextEdit` - 富文本编辑器
- `TextEditWithToolbar` - 带工具栏的文本编辑器
- `SpinBox` - 数值输入框

### 容器组件 (9个)
- `ThemedWidget` - 主题化容器
- `ThemedGroupBox` - 主题化分组框
- `ThemedScrollArea` - 主题化滚动区域
- `CustomScrollBar` - 自定义滚动条
- `ElevatedCardWidget` - 卡片容器
- `Splitter` - 分割器
- `AnimatedSplitter` - 动画分割器

### 导航组件 (8个)
- `TabBar` - 标签栏
- `TabWidget` - 标签容器
- `Pivot` - 枢轴导航
- `BreadcrumbBar` - 面包屑导航

### 列表/树/表格组件 (7个)
- `CustomListWidget` - 列表控件
- `CustomListView` - 列表视图
- `CustomTreeWidget` - 树控件
- `CustomTableWidget` - 表格控件

### 对话框组件 (3个)
- `MessageBox` - 消息框
- `ColorDialog` - 颜色对话框
- `FileDialog` - 文件对话框

### 其他组件
- `RoundMenu` - 圆角菜单
- `AnimatedSlider` - 动画滑块
- `CircularProgress` - 圆形进度条
- `Toast` - Toast 通知
- `ThemedLabel` - 主题化标签
- `CustomCheckBox` - 复选框
- `ComboBox` - 下拉框
- `DatePicker` - 日期选择器
- `SimpleMediaPlayBar` - 媒体播放栏
- `SplashScreen` - 启动画面
- `StatusBar` - 状态栏
- `FlowLayout` - 流式布局

## 快速开始

### 安装依赖

```bash
pip install PyQt6
```

### 基本使用

```python
from PyQt6.QtWidgets import QApplication
from src.core.theme_manager import ThemeManager
from src.components import (
    CustomPushButton, 
    ModernLineEdit, 
    ThemedLabel,
    TabBar
)

app = QApplication([])

# 初始化主题管理器
theme_mgr = ThemeManager.instance()
theme_mgr.register_theme('dark')
theme_mgr.set_theme('dark')

# 使用组件
button = CustomPushButton("Click Me")
line_edit = ModernLineEdit()
label = ThemedLabel("Hello, PyQt6!", font_role='title')
tab_bar = TabBar()

# 切换主题
theme_mgr.set_theme('light')
```

### 使用无边框窗口

```python
from src.containers import FramelessWindow

window = FramelessWindow()
window.setWindowTitle("My App")
window.resize(800, 600)
window.show()
```

### 添加标题栏自定义组件

```python
from src.containers import FramelessWindow
from src.components import ModernLineEdit

window = FramelessWindow()

# 添加搜索框到标题栏
search_box = ModernLineEdit()
search_box.setPlaceholderText("Search...")
window.add_titlebar_widget(search_box, position='center')
```

## 项目结构

```
src/
├── core/                        # 核心模块
│   ├── theme_manager.py         # 主题管理器（单例）
│   ├── themed_component_base.py # 组件基类
│   ├── style_override.py        # 样式覆盖混入
│   ├── stylesheet_cache_mixin.py# 样式缓存
│   ├── animation.py             # 动画系统
│   ├── icon_manager.py          # 图标管理器
│   ├── font_manager.py          # 字体管理器
│   └── platform/                # 平台适配
│
├── themes/                      # 主题定义
│   ├── colors.py                # WinUI3 颜色系统
│   ├── dark.py                  # 暗色主题
│   ├── light.py                 # 亮色主题
│   └── default.py               # 默认主题
│
├── components/                  # UI 组件
│   ├── buttons/                 # 按钮组件
│   ├── inputs/                  # 输入组件
│   ├── containers/              # 容器组件
│   ├── navigation/              # 导航组件
│   ├── widgets/                 # 通用组件
│   ├── dialogs/                 # 对话框
│   ├── lists/                   # 列表组件
│   ├── trees/                   # 树组件
│   ├── tables/                  # 表格组件
│   ├── menus/                   # 菜单组件
│   ├── labels/                  # 标签组件
│   ├── checkboxes/              # 复选框组件
│   ├── sliders/                 # 滑块组件
│   ├── progress/                # 进度组件
│   ├── toasts/                  # Toast 通知
│   ├── media/                   # 媒体组件
│   ├── splash/                  # 启动画面
│   ├── statusbar/               # 状态栏
│   └── layouts/                 # 布局组件
│
├── containers/                  # 顶层容器
│   └── frameless_window.py      # 无边框窗口
│
└── resources/                   # 资源文件
    └── icons/                   # SVG 图标库
```

## 核心概念

### 主题系统

主题系统采用观察者模式，组件订阅主题变化通知：

```python
from src.core import ThemedComponentBase

class MyComponent(ThemedComponentBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_initial_theme()
    
    def _apply_theme(self, theme):
        bg = self.get_theme_color('background.primary', QColor(30, 30, 30))
        # 应用样式...
```

### 样式覆盖

支持组件级别的样式覆盖，不修改全局主题：

```python
button = CustomPushButton("Custom")
button.set_border_radius(8)
button.set_padding('12px 24px')
```

### 动画系统

支持全局动画控制和组件动画混入：

```python
from src.core.animation import AnimationManager, AnimatableMixin

# 全局控制
anim_mgr = AnimationManager.instance()
anim_mgr.set_enabled(False)  # 禁用所有动画

# 组件使用动画
class MyPopup(QWidget, AnimatableMixin):
    def __init__(self):
        super().__init__()
        self.setup_animation(AnimationPreset.FLYOUT)
```

## 开发指南

### 创建新组件

1. 继承 `ThemedComponentBase`（QWidget 子类）或 `ThemedMixin`（其他 Qt 控件）
2. 实现 `_apply_theme(theme)` 方法
3. 调用 `_apply_initial_theme()` 应用初始主题

```python
from src.core import ThemedMixin
from PyQt6.QtWidgets import QSlider

class MySlider(QSlider, ThemedMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_theme()
        self._apply_initial_theme()
    
    def _apply_theme(self, theme):
        groove_color = self.get_theme_color('slider.groove', QColor(60, 60, 60))
        # 应用样式...
```

## 依赖

- Python 3.10+
- PyQt6

## 许可证

MIT License
