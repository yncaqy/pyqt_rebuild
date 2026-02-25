#!/usr/bin/env python3
"""调试演示程序的主题订阅问题"""

import sys
import os
# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# 添加项目根目录到 Python 路径，以便找到 examples 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from core.theme_manager import ThemeManager

def debug_theme_subscription():
    print("=== 演示程序主题订阅调试 ===")
    
    # 创建 QApplication
    app = QApplication([])
    
    # 导入演示程序
    from examples.complete_theme_demo import CompleteThemeDemo
    
    # 创建演示窗口（但不显示）
    window = CompleteThemeDemo()
    
    # 检查主题管理器状态
    theme_mgr = ThemeManager.instance()
    print(f"注册的主题: {list(theme_mgr._themes.keys())}")
    print(f"当前订阅者总数: {len(theme_mgr._subscribers)}")
    
    # 分析订阅者类型
    print("\n=== 订阅者类型分析 ===")
    subscriber_types = {}
    for i, subscriber in enumerate(theme_mgr._subscribers):
        type_name = type(subscriber).__name__
        if type_name not in subscriber_types:
            subscriber_types[type_name] = []
        subscriber_types[type_name].append(i)
    
    for type_name, indices in subscriber_types.items():
        print(f"{type_name}: {len(indices)} 个 (索引: {indices[:10]}{'...' if len(indices) > 10 else ''})")
    
    # 特别关注关键组件
    print("\n=== 关键组件检查 ===")
    key_components = ['CustomPushButton', 'CustomCheckBox', 'ModernLineEdit', 
                     'AnimatedSlider', 'CircularProgress', 'Toast']
    
    for component_type in key_components:
        count = len(subscriber_types.get(component_type, []))
        print(f"{component_type}: {count} 个")
    
    # 测试主题切换
    print("\n=== 测试主题切换 ===")
    print("切换到 light 主题...")
    theme_mgr.set_theme('light')
    
    print("切换到 dark 主题...")
    theme_mgr.set_theme('dark')
    
    print("\n调试完成")

if __name__ == "__main__":
    debug_theme_subscription()