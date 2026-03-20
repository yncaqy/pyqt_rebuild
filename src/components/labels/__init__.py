"""
WinUI3 风格标签组件包

包含主题化标签和图片标签组件，遵循 WinUI3 设计规范。

组件:
- ThemedLabel: 主题化文本标签，支持 WinUI3 字体层级系统
- ImageLabel: 图片标签，支持高 DPI、圆角和阴影效果

字体层级 (Type Ramp):
- caption: 12px, 辅助说明文字
- body: 14px, 正文内容
- body_strong: 14px semibold, 强调正文
- body_large: 18px, 大号正文
- subtitle: 20px semibold, 副标题
- title: 28px semibold, 标题
- title_large: 40px semibold, 大标题
- display: 68px semibold, 展示文字
"""

from .themed_label import ThemedLabel, ThemedLabelConfig
from .image_label import ImageLabel, ImageLabelConfig

__all__ = [
    'ThemedLabel',
    'ThemedLabelConfig',
    'ImageLabel',
    'ImageLabelConfig',
]
