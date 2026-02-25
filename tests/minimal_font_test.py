#!/usr/bin/env python3
"""
Minimal test to verify font switching in complete_theme_demo
"""

import sys
from PyQt6.QtWidgets import QApplication
from examples.complete_theme_demo import CompleteThemeDemo

def test_minimal():
    """Minimal test focusing on title font switching."""
    app = QApplication(sys.argv)
    
    # Create window
    window = CompleteThemeDemo()
    window.show()
    
    print("=== Minimal Font Switching Test ===")
    print("观察要点:")
    print("1. 窗口标题文字: 'Complete Application Theme Switching Demo'")
    print("2. 点击不同主题按钮")
    print("3. 观察标题文字的字体是否发生变化")
    print("4. 如果没变化，请告诉我具体现象")
    
    # 添加一些调试输出
    original_font = window._title_label.font()
    print(f"\n初始字体信息:")
    print(f"字体族: {original_font.family()}")
    print(f"字体大小: {original_font.pointSize()}")
    print(f"是否粗体: {original_font.bold()}")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_minimal())