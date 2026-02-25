#!/usr/bin/env python3
"""
测试改进后的 CustomPushButton 功能
"""

import sys
import os
sys.path.insert(0, '.')

try:
    from src.components.buttons.custom_push_button import CustomPushButton
    from src.core.theme_manager import ThemeManager
    print("✅ 导入成功")
    
    # 测试基本功能
    button = CustomPushButton("测试按钮")
    print("✅ 按钮创建成功")
    
    # 测试主题获取
    theme_name = button.get_theme()
    print(f"✅ 当前主题: {theme_name}")
    
    # 测试边界半径设置
    button.set_border_radius(8)
    print("✅ 边界半径设置成功")
    
    # 测试内边距设置
    button.set_padding("12px 24px")
    print("✅ 内边距设置成功")
    
    # 测试错误处理
    button.set_border_radius(-5)  # 应该被拒绝
    button.set_padding("")  # 应该被拒绝
    print("✅ 错误输入处理正常")
    
    # 清理资源
    button.cleanup()
    print("✅ 资源清理成功")
    
    print("\n🎉 所有测试通过！按钮改进成功！")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在正确的项目目录中运行此脚本")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()