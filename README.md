# PyQt6 重构组件库

一个现代化的 PyQt6 组件库，具有完整的主题系统集成。

## 特性

- 🎨 **主题系统** - 支持暗色/亮色主题切换，自动更新所有组件
- 🧩 **组件化** - 模块化组件设计，易于扩展和定制
- ⚡ **性能优化** - 样式缓存机制，减少重复计算
- 🔧 **类型安全** - 完整的类型注解支持

## 组件列表

### 基础组件
- `ThemedLabel` - 主题化标签
- `ThemedWidget` - 主题化容器
- `ThemedGroupBox` - 主题化分组框
- `ThemedScrollArea` - 主题化滚动区域

### 输入组件
- `ModernLineEdit` - 现代化输入框
- `CustomCheckBox` - 自定义复选框
- `AnimatedSlider` - 动画滑块

### 按钮组件
- `CustomPushButton` - 自定义按钮

### 进度组件
- `CircularProgress` - 圆形进度条

### 通知组件
- `Toast` - 消息提示

### 容器组件
- `FramelessWindow` - 无边框窗口

## 快速开始

```python
from PyQt6.QtWidgets import QApplication
from src.core.theme_manager import ThemeManager
from src.components.labels import ThemedLabel
from src.components.buttons import CustomPushButton

app = QApplication([])

# 初始化主题管理器
theme_mgr = ThemeManager.instance()
theme_mgr.register_theme('dark')
theme_mgr.set_theme('dark')

# 使用组件
label = ThemedLabel("Hello, PyQt6!", font_role='title')
button = CustomPushButton("Click Me")

# 切换主题
theme_mgr.set_theme('light')
```

## 项目结构

```
src/
├── core/                   # 核心模块
│   ├── theme_manager.py    # 主题管理器
│   ├── font_manager.py     # 字体管理器
│   └── animation_controller.py
├── themes/                 # 主题定义
│   ├── dark.py            # 暗色主题
│   ├── light.py           # 亮色主题
│   └── colors.py          # 颜色定义
├── components/            # UI组件
│   ├── labels/
│   ├── buttons/
│   ├── inputs/
│   ├── checkboxes/
│   ├── sliders/
│   ├── progress/
│   ├── toasts/
│   └── containers/
└── containers/            # 容器组件
    └── frameless_window.py
```

## 依赖

- Python 3.10+
- PyQt6

## 安装

```bash
pip install PyQt6
```

## 许可证

MIT License
