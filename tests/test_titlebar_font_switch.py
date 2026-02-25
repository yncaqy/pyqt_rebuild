#!/usr/bin/env python3
"""
Test script to verify titlebar font switching functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication
from examples.complete_theme_demo import CompleteThemeDemo

def test_titlebar_font_switch():
    """Test titlebar font switching functionality."""
    app = QApplication(sys.argv)
    
    # Create the demo window
    window = CompleteThemeDemo()
    window.show()
    
    print("=== Titlebar Font Switch Test ===")
    print("观察以下内容:")
    print("1. 窗口标题栏的字体是否随着主题切换而改变")
    print("2. 标题栏按钮的字体是否跟随主题切换")
    print("3. 切换主题后，标题栏文字是否清晰可读")
    print("\n操作说明:")
    print("- 点击不同的主题按钮测试字体切换")
    print("- 观察标题栏文字的字体族、大小、粗细变化")
    print("- 按 Ctrl+C 或关闭窗口结束测试")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_titlebar_font_switch())