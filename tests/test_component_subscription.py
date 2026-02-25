#!/usr/bin/env python3
"""测试组件主题订阅状态"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from core.theme_manager import ThemeManager
from components.buttons.custom_push_button import CustomPushButton
from components.checkboxes.custom_check_box import CustomCheckBox
from components.inputs.modern_line_edit import ModernLineEdit
from components.sliders.animated_slider import AnimatedSlider
from components.progress.circular_progress import CircularProgress

def test_component_subscriptions():
    print("=== 组件主题订阅状态检查 ===")
    
    # 创建 QApplication
    app = QApplication([])
    
    # 创建组件实例
    btn = CustomPushButton('Test Button')
    cb = CustomCheckBox('Test Checkbox')
    le = ModernLineEdit()
    slider = AnimatedSlider()
    progress = CircularProgress()
    
    # 获取主题管理器
    theme_mgr = ThemeManager.instance()
    
    print(f"当前订阅者总数: {len(theme_mgr._subscribers)}")
    print()
    
    # 检查各组件订阅状态
    components = [
        ('按钮', btn),
        ('复选框', cb),
        ('输入框', le),
        ('滑块', slider),
        ('进度条', progress)
    ]
    
    for name, component in components:
        is_subscribed = component in theme_mgr._subscribers
        print(f"{name} 订阅状态: {'✓ 已订阅' if is_subscribed else '✗ 未订阅'}")
    
    print()
    print("=== 订阅者类型统计 ===")
    subscriber_types = {}
    for subscriber in theme_mgr._subscribers:
        type_name = type(subscriber).__name__
        subscriber_types[type_name] = subscriber_types.get(type_name, 0) + 1
    
    for type_name, count in subscriber_types.items():
        print(f"{type_name}: {count}")

if __name__ == "__main__":
    test_component_subscriptions()