"""
重构组件验证Demo

只使用重构过的组件，不包含任何原生PyQt组件（除布局类和QApplication外）

重构组件列表:
- FramelessWindow (容器)
- CustomPushButton (按钮)
- ModernLineEdit (输入框)
- CustomCheckBox (复选框)
- CircularProgress (圆形进度条)
- AnimatedSlider (动画滑块)
- ThemedLabel (主题化标签)
- Toast + ToastManager (通知)
- ThemedGroupBox (分组框)
- ThemedScrollArea (滚动区域)
- ThemedWidget (主题化容器)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, QAbstractItemView

from containers.frameless_window import FramelessWindow
from components.buttons.custom_push_button import CustomPushButton
from components.inputs.modern_line_edit import ModernLineEdit
from components.checkboxes.custom_check_box import CustomCheckBox
from components.progress.circular_progress import CircularProgress
from components.sliders.animated_slider import AnimatedSlider
from components.labels.themed_label import ThemedLabel
from components.toasts.toast import Toast, ToastType, ToastPosition
from components.toasts.toast_manager import ToastManager
from components.containers.themed_group_box import ThemedGroupBox
from components.containers.themed_scroll_area import ThemedScrollArea
from components.containers.themed_widget import ThemedWidget
from components.dialogs.message_box import MessageBox
from components.lists.custom_list_widget import CustomListWidget, CustomListWidgetItem
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME, DEFAULT_THEME


class RefactoredComponentsDemo(FramelessWindow):
    """重构组件验证窗口"""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_content()
        
    def _setup_window(self):
        """设置窗口属性"""
        self.setTitle("重构组件验证Demo")
        self.resize(900, 700)
        
    def _setup_content(self):
        """设置内容"""
        scroll = ThemedScrollArea()
        scroll.setWidgetResizable(True)
        
        content = self._create_content_widget()
        scroll.setWidget(content)
        
        self.setCentralWidget(scroll)
        
    def _create_content_widget(self):
        """创建内容区域"""
        content = ThemedWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_title_section())
        layout.addWidget(self._create_theme_section())
        layout.addWidget(self._create_buttons_section())
        layout.addWidget(self._create_inputs_section())
        layout.addWidget(self._create_checkbox_section())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_slider_section())
        layout.addWidget(self._create_toast_section())
        layout.addWidget(self._create_messagebox_section())
        layout.addWidget(self._create_list_section())
        layout.addStretch()
        
        return content
        
    def _create_title_section(self):
        """创建标题区域"""
        widget = ThemedWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 10)
        
        title = ThemedLabel("PyQt 重构组件验证", font_role='title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = ThemedLabel("所有组件均为重构版本，无原生组件", font_role='body')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return widget
        
    def _create_theme_section(self):
        """创建主题控制区域"""
        group = ThemedGroupBox("主题切换")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        dark_btn = CustomPushButton("暗色主题")
        dark_btn.clicked.connect(lambda: self._switch_theme('dark'))
        
        light_btn = CustomPushButton("亮色主题")
        light_btn.clicked.connect(lambda: self._switch_theme('light'))
        
        default_btn = CustomPushButton("默认主题")
        default_btn.clicked.connect(lambda: self._switch_theme('default'))
        
        layout.addWidget(dark_btn)
        layout.addWidget(light_btn)
        layout.addWidget(default_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_buttons_section(self):
        """创建按钮区域"""
        group = ThemedGroupBox("CustomPushButton 按钮")
        container = ThemedWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 普通按钮
        normal_layout = QHBoxLayout()
        btn1 = CustomPushButton("普通按钮")
        btn1.set_tooltip("这是一个普通按钮")
        btn1.clicked.connect(lambda: self._show_toast("普通按钮被点击", ToastType.INFO))
        
        btn2 = CustomPushButton("成功操作")
        btn2.set_tooltip("执行成功操作")
        btn2.clicked.connect(lambda: self._show_toast("操作成功!", ToastType.SUCCESS))
        
        btn3 = CustomPushButton("警告")
        btn3.set_tooltip("显示警告信息")
        btn3.clicked.connect(lambda: self._show_toast("这是警告信息", ToastType.WARNING))
        
        btn4 = CustomPushButton("错误")
        btn4.set_tooltip("显示错误信息")
        btn4.clicked.connect(lambda: self._show_toast("发生错误!", ToastType.ERROR))
        
        btn5 = CustomPushButton("禁用状态")
        btn5.set_tooltip("此按钮已禁用")
        btn5.setEnabled(False)
        
        normal_layout.addWidget(btn1)
        normal_layout.addWidget(btn2)
        normal_layout.addWidget(btn3)
        normal_layout.addWidget(btn4)
        normal_layout.addWidget(btn5)
        normal_layout.addStretch()
        
        # 带图标按钮
        icon_layout = QHBoxLayout()
        btn6 = CustomPushButton("关闭", icon_name="window_close")
        btn6.set_tooltip("关闭窗口")
        btn6.clicked.connect(lambda: self._show_toast("关闭按钮被点击", ToastType.INFO))
        
        btn7 = CustomPushButton("最小化", icon_name="window_minimize")
        btn7.set_tooltip("最小化窗口")
        btn7.clicked.connect(lambda: self._show_toast("最小化按钮被点击", ToastType.INFO))
        
        btn8 = CustomPushButton("最大化", icon_name="window_maximize")
        btn8.set_tooltip("最大化窗口")
        btn8.clicked.connect(lambda: self._show_toast("最大化按钮被点击", ToastType.INFO))
        
        btn9 = CustomPushButton("恢复", icon_name="window_restore")
        btn9.set_tooltip("恢复窗口大小")
        btn9.clicked.connect(lambda: self._show_toast("恢复按钮被点击", ToastType.INFO))
        
        icon_layout.addWidget(btn6)
        icon_layout.addWidget(btn7)
        icon_layout.addWidget(btn8)
        icon_layout.addWidget(btn9)
        icon_layout.addStretch()
        
        layout.addLayout(normal_layout)
        layout.addLayout(icon_layout)
        
        group.setLayout(layout)
        return group
        
    def _create_inputs_section(self):
        """创建输入框区域"""
        group = ThemedGroupBox("ModernLineEdit 输入框")
        container = ThemedWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label1 = ThemedLabel("用户名:")
        self.username_input = ModernLineEdit()
        self.username_input.set_placeholder_text("请输入用户名...")
        
        label2 = ThemedLabel("密码:")
        self.password_input = ModernLineEdit()
        self.password_input.set_placeholder_text("请输入密码...")
        self.password_input.set_echo_mode(ModernLineEdit.EchoMode.Password)
        
        label3 = ThemedLabel("年龄:")
        self.age_input = ModernLineEdit()
        self.age_input.set_placeholder_text("18-99")
        self.age_input.setValidator(QIntValidator(18, 99, self.age_input))
        
        label4 = ThemedLabel("邮箱:")
        self.email_input = ModernLineEdit()
        self.email_input.set_placeholder_text("example@email.com")
        self.email_input.textChanged.connect(self._validate_email)
        
        self.email_status = ThemedLabel("")
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(label3, 2, 0)
        layout.addWidget(self.age_input, 2, 1)
        layout.addWidget(label4, 3, 0)
        layout.addWidget(self.email_input, 3, 1)
        layout.addWidget(self.email_status, 4, 1)
        
        group.setLayout(layout)
        return group
        
    def _create_checkbox_section(self):
        """创建复选框区域"""
        group = ThemedGroupBox("CustomCheckBox 复选框")
        container = ThemedWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        row1 = ThemedWidget()
        layout1 = QHBoxLayout(row1)
        layout1.setContentsMargins(0, 0, 0, 0)
        
        self.cb1 = CustomCheckBox("功能A")
        self.cb2 = CustomCheckBox("功能B")
        self.cb3 = CustomCheckBox("功能C")
        self.cb1.stateChanged.connect(self._update_checkbox_status)
        self.cb2.stateChanged.connect(self._update_checkbox_status)
        self.cb3.stateChanged.connect(self._update_checkbox_status)
        
        layout1.addWidget(self.cb1)
        layout1.addWidget(self.cb2)
        layout1.addWidget(self.cb3)
        layout1.addStretch()
        
        row2 = ThemedWidget()
        layout2 = QHBoxLayout(row2)
        layout2.setContentsMargins(0, 0, 0, 0)
        
        self.cb4 = CustomCheckBox("接收通知")
        self.cb5 = CustomCheckBox("同意条款")
        self.cb5.setChecked(True)
        
        layout2.addWidget(self.cb4)
        layout2.addWidget(self.cb5)
        layout2.addStretch()
        
        self.checkbox_status = ThemedLabel("已启用: 0/3 个功能")
        
        main_layout.addWidget(row1)
        main_layout.addWidget(row2)
        main_layout.addWidget(self.checkbox_status)
        
        group.setLayout(main_layout)
        return group
        
    def _create_progress_section(self):
        """创建进度条区域"""
        group = ThemedGroupBox("CircularProgress 圆形进度条")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        for value, label_text in [(25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]:
            col = ThemedWidget()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(0, 0, 0, 0)
            
            progress = CircularProgress()
            progress.setValue(value)
            progress.setFixedSize(80, 80)
            
            center = ThemedWidget()
            center_layout = QHBoxLayout(center)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.addStretch()
            center_layout.addWidget(progress)
            center_layout.addStretch()
            
            label = ThemedLabel(label_text, font_role='small')
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            col_layout.addWidget(center)
            col_layout.addWidget(label)
            
            layout.addWidget(col)
            
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_slider_section(self):
        """创建滑块区域"""
        group = ThemedGroupBox("AnimatedSlider 动画滑块")
        container = ThemedWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label1 = ThemedLabel("音量:")
        self.volume_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_label = ThemedLabel("70%", font_role='small')
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        
        label2 = ThemedLabel("亮度:")
        self.brightness_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_label = ThemedLabel("50%", font_role='small')
        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_label.setText(f"{v}%")
        )
        
        label3 = ThemedLabel("进度:")
        self.progress_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(50)
        self.progress_value_label = ThemedLabel("50%", font_role='small')
        self.progress_slider.valueChanged.connect(
            lambda v: self.progress_value_label.setText(f"{v}%")
        )
        
        animate_btn = CustomPushButton("动画到100%")
        animate_btn.clicked.connect(self._animate_slider)
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.volume_slider, 0, 1)
        layout.addWidget(self.volume_label, 0, 2)
        
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.brightness_slider, 1, 1)
        layout.addWidget(self.brightness_label, 1, 2)
        
        layout.addWidget(label3, 2, 0)
        layout.addWidget(self.progress_slider, 2, 1)
        layout.addWidget(self.progress_value_label, 2, 2)
        layout.addWidget(animate_btn, 2, 3)
        
        group.setLayout(layout)
        return group
        
    def _create_toast_section(self):
        """创建Toast区域"""
        group = ThemedGroupBox("Toast 通知组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_btn = CustomPushButton("Info通知")
        info_btn.clicked.connect(
            lambda: self._show_toast("这是一条信息通知", ToastType.INFO)
        )
        
        success_btn = CustomPushButton("Success通知")
        success_btn.clicked.connect(
            lambda: self._show_toast("操作成功完成!", ToastType.SUCCESS)
        )
        
        warning_btn = CustomPushButton("Warning通知")
        warning_btn.clicked.connect(
            lambda: self._show_toast("请注意检查输入", ToastType.WARNING)
        )
        
        error_btn = CustomPushButton("Error通知")
        error_btn.clicked.connect(
            lambda: self._show_toast("发生了一个错误!", ToastType.ERROR)
        )
        
        layout.addWidget(info_btn)
        layout.addWidget(success_btn)
        layout.addWidget(warning_btn)
        layout.addWidget(error_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _create_messagebox_section(self):
        """创建MessageBox区域"""
        group = ThemedGroupBox("MessageBox 消息对话框")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_btn = CustomPushButton("信息对话框")
        info_btn.clicked.connect(self._show_info_dialog)
        
        warning_btn = CustomPushButton("警告对话框")
        warning_btn.clicked.connect(self._show_warning_dialog)
        
        error_btn = CustomPushButton("错误对话框")
        error_btn.clicked.connect(self._show_error_dialog)
        
        question_btn = CustomPushButton("询问对话框")
        question_btn.clicked.connect(self._show_question_dialog)
        
        layout.addWidget(info_btn)
        layout.addWidget(warning_btn)
        layout.addWidget(error_btn)
        layout.addWidget(question_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
        
    def _show_info_dialog(self):
        MessageBox.information(self, "信息", "这是一条信息提示对话框。")
        
    def _show_warning_dialog(self):
        MessageBox.warning(self, "警告", "这是一条警告提示对话框。")
        
    def _show_error_dialog(self):
        MessageBox.critical(self, "错误", "这是一条错误提示对话框。")
        
    def _show_question_dialog(self):
        result = MessageBox.question(self, "确认", "确定要执行此操作吗？")
        if result == MessageBox.OK:
            self._show_toast("用户点击了确定", ToastType.SUCCESS)
        else:
            self._show_toast("用户点击了取消", ToastType.INFO)
    
    def _create_list_section(self):
        """创建ListWidget区域"""
        group = ThemedGroupBox("CustomListWidget 列表组件")
        container = ThemedWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        single_list = CustomListWidget()
        single_list.setFixedHeight(150)
        single_list.addItems(["项目 1", "项目 2", "项目 3", "项目 4", "项目 5"])
        single_list.itemClicked.connect(self._on_list_item_clicked)
        
        multi_list = CustomListWidget()
        multi_list.setFixedHeight(150)
        multi_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for i in range(1, 6):
            item = CustomListWidgetItem(f"可多选项目 {i}")
            multi_list.addItem(item)
        multi_list.itemSelectionChanged.connect(self._on_multi_selection_changed)
        
        layout.addWidget(single_list)
        layout.addWidget(multi_list)
        
        group.setLayout(layout)
        return group
    
    def _on_list_item_clicked(self, item: CustomListWidgetItem):
        self._show_toast(f"点击了: {item.text()}", ToastType.INFO)
    
    def _on_multi_selection_changed(self):
        pass
        
    def _switch_theme(self, theme_name: str):
        """切换主题"""
        ThemeManager.instance().set_theme(theme_name)
        
    def _show_toast(self, message: str, toast_type: ToastType):
        """显示Toast通知"""
        ToastManager.get_instance().show(
            message,
            toast_type,
            duration=3000,
            position=ToastPosition.TOP_CENTER,
            parent=self
        )
        
    def _validate_email(self, text: str):
        """验证邮箱"""
        if text and '@' not in text:
            self.email_input.set_error(True)
            self.email_status.setText("请输入有效的邮箱地址")
        else:
            self.email_input.set_error(False)
            self.email_status.setText("")
            
    def _update_checkbox_status(self):
        """更新复选框状态"""
        count = sum([
            self.cb1.isChecked(),
            self.cb2.isChecked(),
            self.cb3.isChecked()
        ])
        self.checkbox_status.setText(f"已启用: {count}/3 个功能")
        
    def _animate_slider(self):
        """动画滑块到100%"""
        self.progress_slider.set_value_animated(100, 1000)


def main():
    """运行验证Demo"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ToastManager.prewarm()
    
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict('dark', DARK_THEME)
    theme_mgr.register_theme_dict('light', LIGHT_THEME)
    theme_mgr.register_theme_dict('default', DEFAULT_THEME)
    theme_mgr.set_theme('dark')
    
    window = RefactoredComponentsDemo()
    
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
