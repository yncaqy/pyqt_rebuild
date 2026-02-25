#!/usr/bin/env python3
"""
ThemedLabel主题切换详细测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from components.labels.themed_label import ThemedLabel
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME


class DetailedTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThemedLabel 详细主题测试")
        self.resize(600, 500)
        
        # 存储测试结果
        self.test_results = []
        
        main_layout = QVBoxLayout()
        
        # 标题
        title = ThemedLabel("ThemedLabel 主题切换测试", font_role='title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 创建多个ThemedLabel进行测试
        self.test_labels = []
        
        # 不同字体角色的标签
        roles_layout = QHBoxLayout()
        
        label1 = ThemedLabel("标题样式 (title)", font_role='title')
        label1.setObjectName("label1")
        self.test_labels.append(label1)
        roles_layout.addWidget(label1)
        
        label2 = ThemedLabel("头部样式 (header)", font_role='header')
        label2.setObjectName("label2")
        self.test_labels.append(label2)
        roles_layout.addWidget(label2)
        
        label3 = ThemedLabel("正文样式 (body)", font_role='body')
        label3.setObjectName("label3")
        self.test_labels.append(label3)
        roles_layout.addWidget(label3)
        
        main_layout.addLayout(roles_layout)
        
        # 控制按钮
        controls_layout = QHBoxLayout()
        
        self.dark_btn = QPushButton("深色主题")
        self.dark_btn.clicked.connect(self.switch_to_dark)
        controls_layout.addWidget(self.dark_btn)
        
        self.light_btn = QPushButton("浅色主题")
        self.light_btn.clicked.connect(self.switch_to_light)
        controls_layout.addWidget(self.light_btn)
        
        self.toggle_btn = QPushButton("自动切换")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self.toggle_auto_switch)
        controls_layout.addWidget(self.toggle_btn)
        
        main_layout.addLayout(controls_layout)
        
        # 状态显示区域
        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(200)
        self.status_display.setReadOnly(True)
        main_layout.addWidget(self.status_display)
        
        self.setLayout(main_layout)
        
        # 初始化
        self.init_themes()
        self.log_message("测试窗口初始化完成")
        self.update_status_display()
        
        # 自动切换定时器
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_switch_theme)
        self.auto_switch_count = 0
        
    def init_themes(self):
        """初始化主题"""
        theme_mgr = ThemeManager.instance()
        
        # 注册主题
        theme_mgr.register_theme_dict('dark', DARK_THEME)
        theme_mgr.register_theme_dict('light', LIGHT_THEME)
        
        # 设置初始主题
        theme_mgr.set_theme('light')
        
        self.log_message(f"主题初始化完成 - 当前主题: {theme_mgr.current_theme().name}")
        self.log_message(f"订阅者数量: {len(theme_mgr._subscribers)}")
        
        # 检查每个标签的初始状态
        self.check_label_states()
        
    def switch_to_dark(self):
        """切换到深色主题"""
        theme_mgr = ThemeManager.instance()
        old_theme = theme_mgr.current_theme().name if theme_mgr.current_theme() else "None"
        theme_mgr.set_theme('dark')
        new_theme = theme_mgr.current_theme().name if theme_mgr.current_theme() else "None"
        
        self.log_message(f"手动切换: {old_theme} -> {new_theme}")
        self.log_message(f"订阅者数量: {len(theme_mgr._subscribers)}")
        
        # 检查标签状态变化
        QTimer.singleShot(100, self.check_label_states)
        
    def switch_to_light(self):
        """切换到浅色主题"""
        theme_mgr = ThemeManager.instance()
        old_theme = theme_mgr.current_theme().name if theme_mgr.current_theme() else "None"
        theme_mgr.set_theme('light')
        new_theme = theme_mgr.current_theme().name if theme_mgr.current_theme() else "None"
        
        self.log_message(f"手动切换: {old_theme} -> {new_theme}")
        self.log_message(f"订阅者数量: {len(theme_mgr._subscribers)}")
        
        # 检查标签状态变化
        QTimer.singleShot(100, self.check_label_states)
        
    def toggle_auto_switch(self):
        """切换自动切换模式"""
        if self.toggle_btn.isChecked():
            self.log_message("启动自动切换模式")
            self.auto_timer.start(2000)  # 每2秒切换一次
            self.dark_btn.setEnabled(False)
            self.light_btn.setEnabled(False)
        else:
            self.log_message("停止自动切换模式")
            self.auto_timer.stop()
            self.dark_btn.setEnabled(True)
            self.light_btn.setEnabled(True)
            
    def auto_switch_theme(self):
        """自动切换主题"""
        theme_mgr = ThemeManager.instance()
        current_theme = theme_mgr.current_theme().name if theme_mgr.current_theme() else "None"
        
        if current_theme == "light":
            self.switch_to_dark()
        else:
            self.switch_to_light()
            
        self.auto_switch_count += 1
        if self.auto_switch_count >= 10:  # 10次后自动停止
            self.toggle_btn.setChecked(False)
            self.toggle_auto_switch()
            
    def check_label_states(self):
        """检查所有标签的当前状态"""
        theme_mgr = ThemeManager.instance()
        current_theme = theme_mgr.current_theme()
        
        if not current_theme:
            self.log_message("警告: 当前没有活动主题")
            return
            
        self.log_message(f"\n=== 标签状态检查 ({current_theme.name}) ===")
        
        for i, label in enumerate(self.test_labels, 1):
            # 获取标签的颜色信息
            palette = label.palette()
            text_color = palette.color(label.foregroundRole())
            
            # 检查样式表
            stylesheet = label.styleSheet()
            
            self.log_message(f"标签{i} ({label.objectName()}):")
            self.log_message(f"  文本: {label.text()}")
            self.log_message(f"  字体角色: {getattr(label, '_font_category', 'unknown')}")
            self.log_message(f"  文本颜色: {text_color.name()}")
            self.log_message(f"  样式表长度: {len(stylesheet)} 字符")
            self.log_message(f"  是否启用: {label.isEnabled()}")
            
        self.log_message("=" * 40)
        
    def log_message(self, message):
        """记录消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.test_results.append(log_entry)
        print(log_entry)  # 同时打印到控制台
        
    def update_status_display(self):
        """更新状态显示"""
        # 只显示最新的50条记录
        recent_logs = self.test_results[-50:] if len(self.test_results) > 50 else self.test_results
        self.status_display.setPlainText("\n".join(recent_logs))
        # 滚动到底部
        self.status_display.verticalScrollBar().setValue(
            self.status_display.verticalScrollBar().maximum()
        )


def main():
    app = QApplication(sys.argv)
    
    # 设置定时更新状态显示
    window = DetailedTestWindow()
    
    def periodic_update():
        window.update_status_display()
        
    timer = QTimer()
    timer.timeout.connect(periodic_update)
    timer.start(500)  # 每500ms更新一次
    
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())